from flask import Flask,render_template,request,session,url_for,redirect,g,session,jsonify
import urllib
from bs4 import BeautifulSoup
from forms import LoginForm,fetchUrl,WishInfo
from dbModel import db,Userinfo,Wishlist
import time
from passlib.apps import custom_app_context as pwd_context



app=Flask(__name__)
app.secret_key="kdsjfiuh&ugiug&&&fkgvi"
router={'loggedin':''}


def hash_password(password):
        return pwd_context.encrypt(password)



def verify_password(password,password_hash):
        return pwd_context.verify(password,password_hash)

@app.route('/testy')
def testy():
	return render_template('test.html')

@app.route('/json')
def json():
	return jsonify(name="hevon",age="10",test=1)


@app.route('/testuser/<int:id>')
def test(id):
	if id>4:
		return render_template('django.html')
	else:
		return render_template('hevon.html')
	return str(id)



@app.route('/user')
def test2():
	name=db.session.query(Userinfo).filter_by(username='hevon').first()
	return redirect(url_for('test',id=name.id))


@app.route("/", methods=['GET','POST'])
def home():
	unique=""
	form=LoginForm(request.form)
	if request.method=='POST' and form.validate():
		try:
			todb=Userinfo(form.username.data,hash_password(form.password.data))
			db.session.add(todb)
			db.session.commit()
			return redirect(url_for('login'))
		except:
			unique="Username is already registered with us"
			db.session.rollback()
	return render_template('index.html',form=form,unique=unique)



@app.route("/login",methods=['GET','POST'])
def login():
	router['loggedin']=''
	notUser=""
	found=0
	form=LoginForm(request.form)
	if request.method=='POST' and form.validate():
		name=db.session.query(Userinfo).filter_by(username=form.username.data).first()
		passFound=verify_password(form.password.data,name.password)
		if name is None or not(passFound):
			notUser="Incorrect username/password combination"
			found+=1
		if found==0:
			session['user']=form.username.data
			session['user_id']=name.id
			return redirect(url_for('wishlist',id=name.id))
	return render_template('login.html',form=form,notUser=notUser)




@app.route('/user/<int:id>/wishlist')
def wishlist(id):
	query=db.session.query(Wishlist).filter_by(user_id=session['user_id'])
	if query.first() is None:
		query={'none':'none'}
	return render_template("wishlist.html",user=session['user'],query=query,userid=session['user_id'])





@app.route('/user/<int:id>/wishlist/add',methods=['GET','POST'])
def addtowishlist(id):
	query=""
	found=""
	href=""
	session['href']=[]
	form=fetchUrl(request.form)
	x=3
	
	# if router['loggedin']=='':
	# 	return redirect(url_for('login'))
	if request.method=="POST" and form.validate():
		url=form.query.data
		session['url']=url
		fetchurl=urllib.urlopen(url)
		content=fetchurl.read()
		fetchurl.close()
		soup=BeautifulSoup(content,'html.parser')
		for i in soup.find_all('img'):
			if str(i.get('src')[-3:])=='gif':
				continue
			if str(i.get('src'))[:4]!='http':
				x=x+session['url'].find('com')
				session['url']=session['url'][:x]
				session['href'].append(session['url']+i.get('src'))
			else:
				session['href'].append(i.get('src'))

		if len(session['href'])==0:
			found="No suitable Wish item could be found on this page!"
		

	# if request.method=="POST":
	# 	return redirect(url_for('wishlist'))

	return render_template('addtowishlist.html',user=session['user'],form=form,thumbs=session['href'],found=found,userid=session['user_id'])


@app.route('/user/<int:id>/wishlist/added',methods=['POST','GET'])
def added(id):
	href=request.args.get('href')
	form=WishInfo(request.form)
	success=""
	if request.method=="POST" and form.validate():
		wish=Wishlist(session['url'],href,time.strftime("%d/%m/%Y"),session['user_id'],form.category.data,form.quantity.data,form.description.data)
		db.session.add(wish)
		db.session.commit()
		success='Your wish has been added!'
		return redirect(url_for('wishlist',id=name.id))
	return render_template("added.html",form=form,user=session['user'],href=href,success=success,userid=session['user_id'])


@app.route('/user/<int:id>/wishlist/delete',methods=['POST','GET'])
def delete(id):
	href=request.args.get('href')
	delete=""
	if request.method=="POST":
		query=db.session.query(Wishlist).filter_by(href=href,user_id=session['user_id']).first()
		db.session.delete(query)
		db.session.commit()
		return(redirect(url_for("wishlist",id=id)))
		
	return render_template('delete.html',href=href,user=session['user'],userid=session['user_id'])
	

@app.route('/wishlist/share')
def share():
	pass

def logout():
	router['loggedin']=''
	return redirect(url_for('login'))	

if __name__=="__main__":
	
	app.run(debug=True,host='0.0.0.0')
