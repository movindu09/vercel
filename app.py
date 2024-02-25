from flask import Flask,render_template,session,redirect,url_for,flash,request
from datetime import timedelta
from flask_mail import Mail,Message
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import validators,ValidationError
import os
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'  # Fix the URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY']='random key'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='isuruchandika321@gmail.com'
app.config['MAIL_PASSWORD']='smot jwzf tpou qtax'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail=Mail(app)


db = SQLAlchemy(app)

class Users(db.Model):  # Fix the typo
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    code=db.Column(db.Integer, nullable=True)
    password = db.Column(db.String(100))

    def __init__(self,username,email,password):
        self.username=username
        self.email = email
        self.password=password

@app.route("/send",methods=["GET","POST"])
def send():
    random_number=random.randint(1000, 9999)
    user_email = request.form["email"]
    session["trier"]=user_email
    user = Users.query.filter_by(email=user_email).first()
    if user:
            user.code = random_number
            db.session.commit()
    else:
        flash("The entered email doesn't register in the system!")
        return "hellow"
    msg=Message('OTP Vocal Wizards',sender='isuruchandika321@gmail.com',recipients=[user_email])
    msg.body= f"Hello user use this OTP code :{random_number} "
    mail.send(msg)
    return redirect(url_for("sendOTP"))


@app.route('/')
def hello():
    #session['username']="isuru"
    return render_template("home.html")

@app.route("/login",methods=['GET','POST'])
def login():
    if 'username' in session:
        redirect(url_for("hello"))
    if request.method == "POST":
        
        email=request.form["email"]
        password=request.form["password"]
        if email !="" and password !="":
        

            found_user = Users.query.filter_by(email=email).first()  
            if found_user:
                session["username"]=found_user.username
                session["email"] = found_user.email
                flash("OK! logged in!")
                return redirect(url_for("home"))
            else:
                flash("Error in loginn to the session!")
        else:
            flash("User name and password both required!")

            
    return render_template("Login.html")

@app.route("/register", methods=['POST', 'GET'])
def register():
   
        if 'username' in session:
            return redirect(url_for("hello"))
        
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            
            new_user = Users(username, email, password)
            db.session.add(new_user)
            db.session.commit()
 
  

        return render_template("register.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("hello"))

@app.route("/equalizer")
def equalizer():
    if 'username' not in session: 
        flash("Login required to use the functionality!!", "info")
        return redirect(url_for("login"))
    return render_template("EqualizerPage.html")

@app.route("/find")
def find():
    if 'username' in session:
        return redirect(url_for("hello"))
    return render_template("find.html")

@app.route("/sendOTP")
def sendOTP():
    if 'username' in session:
        return redirect(url_for("hello"))
    
    return render_template("sendOTP.html")
@app.route("/check", methods=["POST"])
def check():
    if request.method == "POST":
        code_OTP = request.form['OTP']
        user = Users.query.filter_by(code=code_OTP).first()

        if user and user.code == int(code_OTP):
            flash("OTP is valid! Change the password from here!","success")
            # Perform any additional actions you need upon successful validation
            return redirect(url_for("retype"))
        else:
            flash("Invalid OTP. Please try again.","danger")
            return "hello"
        
@app.route("/view")
def view():
    return render_template("view.html",values=Users.query.all())

@app.route("/retype")
def retype():
    return render_template("retypepass.html")

@app.route("/check2",methods=["POST"])
def check2():
    if request.method=="POST":
        password1=request.form['password1']
        password2=request.form['password2']
        if password1 !="" and password2 !="":
            if(password1==password2):
                user = Users.query.filter_by(email=session['trier']).first()
                if user:
                    user.password = password1
                    db.session.commit()
                    return redirect(url_for("hello"))
                else:
                    return "Something went wrong!"    

            else:
                flash("Missmatch Password!","error")
                return redirect(url_for("retype")) 
        else:
            flash("Password retyping required!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5009)
