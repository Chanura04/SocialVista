#request use for get and post request in database
#redirect for different pages
#generate_password_hash,check_password_hash password encrypting and decrypting
import os,glob
from datetime import datetime
import pytz
from flask import Flask,render_template,request,redirect,session,url_for,flash
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
import tweepy

import psycopg2

app = Flask(__name__)
app.secret_key="123"

app.config["APP_STARTED"] = True

def clear_session_files():
    for file in glob.glob("flask_session/*"):
        os.remove(file)

clear_session_files()


def get_pg_connection():
    conn = psycopg2.connect(
        host= os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")

    )
    return conn

#configure sql alchemy
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///userData.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app)



#Database model => represent single raw
class User(db.Model):


    #class variables
    id = db.Column(db.Integer,primary_key=True)
    FirstName = db.Column(db.String(20),nullable=False)
    LastName = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(50),unique=True,nullable=False)
    password = db.Column(db.String(200), nullable=False)  # increase length for hash

    twitter_api_key = db.Column(db.String(100))
    twitter_api_secret = db.Column(db.String(100))
    twitter_access_token = db.Column(db.String(100))
    twitter_access_token_secret = db.Column(db.String(100))
    screen_name = db.Column(db.String(100))
    client_id=db.Column(db.String(100))
    client_secret=db.Column(db.String(100))
    isFilledApiDetails=db.Column(db.Boolean,default=False)
    canPost=db.Column(db.Boolean,default=False)
    signupStatus=db.Column(db.Boolean, default=False)



    accountCreatedOn = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone("Asia/Colombo")),onupdate=lambda: datetime.now(pytz.timezone("Asia/Colombo")))

    accountUpdatedOn = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone("Asia/Colombo")),onupdate=lambda: datetime.now(pytz.timezone("Asia/Colombo")))
    accountStatus = db.Column(db.Boolean, default=False)

def set_password(self,password):
        self.password = generate_password_hash(password)

def check_password(self,password):
        return check_password_hash(self.password,password)



@app.route("/")
def dashboard():
    if session.get("username") and session.get("toDashboard"):
        return render_template("dashboard.html", username=session.get('username'))
    else:
        return render_template("dashboard.html")



#Login
@app.route("/login",methods=["POST","GET"])
def login():
    #collect info from the login form
    #check if info in db
    if request.method == "POST":
        email = request.form.get("email")
        session['email']=email
        password = request.form.get("password")
        user = User.query.filter_by(email=session['email']).first()
        if user:
            session[email]=email
            if user.check_password(password):
                print(user.FirstName)
                session['username'] = user.FirstName
                session['toDashboard'] = True
                user.accountUpdatedOn = datetime.now(pytz.timezone("Asia/Colombo"))
                db.session.commit()
                return redirect(url_for("dashboard"))
            else:
                return render_template("login.html", error="Invalid Password...Please try again!", email=session[email])

        else:
            # otherwise show homepages
            return render_template("login.html", error="User does not exist...Please signup first!")
    if request.method == "GET":
        return render_template("login.html", error="")


#register
@app.route("/signup",methods=["POST","GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        if email:
            try:
                new_user =User.query.filter_by(email=email).first()
                if new_user:
                    return render_template("login.html", error="username already exists here!")

                else:

                    first_name = request.form.get("first_name")
                    last_name = request.form.get("last_name")
                    email = request.form.get("email")
                    password = request.form.get("password")
                    print("📌 DEBUG Signup values:", first_name, last_name, email, password)

                    new_user = User(FirstName=first_name,LastName=last_name,email=email,signupStatus=True,accountStatus=True,accountCreatedOn=db.func.current_timestamp())
                    new_user.set_password(password)
                    db.session.add(new_user)
                    db.session.commit()
                    session["username"] = first_name
                    return redirect(url_for("login"))
            except Exception as e:
                print(e)
    if request.method == "GET":
        return render_template("signup.html")


def check_api_details():
    user = User.query.filter_by(email=session['email']).first()
    if user:
        client_id = user.client_id
        client_secret = user.client_secret
        user_access_token = user.twitter_access_token
        user_access_token_secret = user.twitter_access_token_secret
        twit_api_key = user.twitter_api_key
        twit_api_secret = user.twitter_api_secret
        if not client_id or not client_secret or not user_access_token or not user_access_token_secret or not twit_api_key or not twit_api_secret:
            print("api details not filled...redirecting to get api details page...!")
            return False
        else:
            return True
    return False

@app.route("/post_tweet", methods=["POST", "GET"])
def post_tweet():
    if request.method == "POST":
        if check_api_details():
            user = User.query.filter_by(email=session['email']).first()

            if user and user.canPost:
                twitter_api_key = user.twitter_api_key
                twitter_api_secret = user.twitter_api_secret
                user_access_token = user.twitter_access_token
                user_access_token_secret = user.twitter_access_token_secret

                if twitter_api_key and twitter_api_secret and user_access_token and user_access_token_secret:
                    client = tweepy.Client(
                        consumer_key=twitter_api_key,
                        consumer_secret=twitter_api_secret,
                        access_token=user_access_token,
                        access_token_secret=user_access_token_secret
                    )
                    texts = request.form.get("tweet_content")

                    try:
                        response = client.create_tweet(text=texts)
                        flash("🎉 Tweet posted successfully!")
                        print(response)
                        user.accountUpdatedOn = datetime.now(pytz.timezone("Asia/Colombo"))
                        db.session.commit()
                    except Exception as e:
                        flash("Error posting tweet! Invalid API details...")
                        print(f"Error posting tweet: {e}")
                else:
                    flash("⚠️ Please fill in the API details first!")
            else:
                flash("⚠️ Please login or check your permissions first!")
        else:
            return redirect(url_for("connect_twitter"))

        # After POST (success or fail), always return something
        return redirect(url_for("post_tweet"))

    # GET request
    return render_template("post_content.html")



@app.route("/connect_twitter", methods=["POST","GET"])
def connect_twitter():
    if request.method == "POST":
        user = User.query.filter_by(email=session['email']).first()
        if user:
            user.twitter_api_key = request.form.get("api_key")
            user.twitter_api_secret = request.form.get("api_secret")
            user.twitter_access_token = request.form.get("access_token")
            user.twitter_access_token_secret = request.form.get("access_token_secret")
            user.screen_name = request.form.get("screen_name")
            user.client_id = request.form.get("client_id")
            user.client_secret = request.form.get("client_secret")
            user.isFilledApiDetails=True
            user.canPost=True
            db.session.commit()

            # tweets = get_user_tweets()
            # return redirect(url_for("dashboard"))
            return render_template("dashboard.html")
        else:
            session['canPost'] = False
            return redirect(url_for("dashboard"))
    if request.method == "GET":
        # return render_template("get_api_details.html")
        user=User.query.filter_by(email=session['email']).first()
        if user:
            if user.isFilledApiDetails:
                redirect(url_for("get_api_details"))

            else:
                user.client_id = None
                user.client_secret = None
                user.twitter_access_token = None
                user.twitter_access_token_secret = None
                user.twitter_api_key = None
                user.twitter_api_secret = None
                user.screen_name = None
                db.session.commit()
                return redirect(url_for("get_api_details"))

        else:
            return redirect(url_for("login"))
    return redirect(url_for("get_api_details"))

@app.route("/get_api_details")
def get_api_details():
    return render_template("get_api_details.html")


@app.route("/show_api_credentials" )
def show_api_credentials():

        user=User.query.filter_by(email=session['email']).first()
        if user:
            client_id = user.client_id
            client_secret = user.client_secret
            user_access_token = user.twitter_access_token
            user_access_token_secret = user.twitter_access_token_secret
            twitter_api_key = user.twitter_api_key
            twitter_api_secret = user.twitter_api_secret
            if not client_id or not client_secret or not user_access_token or not user_access_token_secret or not twitter_api_key or not twitter_api_secret:
                 return render_template("show_api_details.html", client_id=client_id, client_secret=client_secret, user_access_token=user_access_token, user_access_token_secret=user_access_token_secret, twitter_api_key=twitter_api_key, twitter_api_secret=twitter_api_secret)
            else:
                flash("Please fill the API details!")
        else:
            flash("Please login first!")
#logout
@app.route("/logout",methods=["POST"])
def logout():
    if request.method == "POST":
        session.pop("username",None)
        session.pop("email",None)
        session.pop("toDashboard",False)
        return redirect(url_for("login"))




if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
