#request use for get and post request in database
#redirect for different pages
#generate_password_hash,check_password_hash password encrypting and decrypting
import os

import tweepy
from flask import Flask,render_template,request,redirect,session,url_for
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from dotenv import load_dotenv
  # if inside a package
load_dotenv()
consumer_key = os.getenv("TWITTER_API_KEY")
consumer_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
app = Flask(__name__)
app.secret_key="123"


# Authenticate with the API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

try:
    public_tweets = api.user_timeline(screen_name='@__Chanura__')
    for tweet in public_tweets:
        print("text is:",tweet.text)
except tweepy.TweepyException as e:
    print(f"Error: {e}")


#configure sql alchemy
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///userData.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app)

celery = Celery(
    __name__,
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)
@celery.task
def divide(x, y):
    import time
    time.sleep(5)
    return x / y


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

    def set_password(self,password):
        self.password = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)



@app.route("/",methods=["GET","POST"])
def dashboard():
    if request.method=="POST":
        return redirect(url_for("login"))
    if request.method=="GET":
        redirect(url_for("connect_twitter"))


        return render_template("get_api_details.html",  username=session['username'])


import tweepy
from flask import request, redirect, url_for


# ... (rest of your imports and code)

@app.route("/post_tweet", methods=["POST"])
def post_tweet():
    """
    Handles a form submission to post a new tweet.
    """
    tweet_text = request.form.get("tweet_content")
    if not tweet_text:
        # Handle case where tweet content is missing
        return "Tweet content is required", 400

    user = User.query.filter_by(email=session['email']).first()
    if not user or not user.twitter_access_token:
        # Redirect to the connect page if user is not authenticated
        return redirect(url_for("connect_twitter"))

    # Use the v2 client for posting tweets on the free tier
    client = tweepy.Client(
        consumer_key=user.twitter_api_key,
        consumer_secret=user.twitter_api_secret,
        access_token=user.twitter_access_token,
        access_token_secret=user.twitter_access_token_secret
    )

    try:
        response = client.create_tweet(text=tweet_text)
        print("✅ Tweet posted successfully:", response.data)
        # You could add a success flash message here
    except Exception as e:
        print("❌ Error posting tweet:", e)
        # Add an error flash message here

    return redirect(url_for("dashboard"))























# def get_user_tweets():
#     """Fetch user tweets using Tweepy and user’s stored credentials"""
#     if  User.query.filter_by(email=session['email']).first():
#             user = User.query.filter_by(email=session['email']).first()
#             auth = tweepy.OAuthHandler(user.twitter_api_key, user.twitter_api_secret)
#             auth.set_access_token(user.twitter_access_token, user.twitter_access_token_secret)
#             api = tweepy.API(auth)
#
#             try:
#                 # Fetch recent tweets (e.g., last 10 tweets from timeline)
#                 tweets = api.user_timeline(
#                     screen_name=user.screen_name,  # Twitter username stored in DB
#                     count=10,
#                     tweet_mode="extended"  # ensures full text
#                 )
#                 return tweets
#             except Exception as e:
#                 print("❌ Error fetching tweets:", e)
#                 return []
#     else:
#         return None

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
                return redirect(url_for("dashboard"))
            else:
                return render_template("login.html", error="Invalid Password...Please try again!",email=session[email])

        else:
            # otherwise show homepages
            return render_template("login.html",error="User does not exist...Please signup first!")
    if request.method == "GET":
        return render_template("login.html",error="")


#register
@app.route("/signup",methods=["POST","GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]

        new_user =User.query.filter_by(email=email).first()
        if new_user:
            return render_template("login.html",error="username already exists here!")

        else:

            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            email = request.form.get("email")
            password = request.form.get("password")
            print("📌 DEBUG Signup values:", first_name, last_name, email, password)

            new_user = User(FirstName=first_name,LastName=last_name,email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = first_name
            return redirect(url_for("login"))
    if request.method == "GET":
        return render_template("signup.html")



@app.route("/connect_twitter", methods=["POST"])
def connect_twitter():
    user = User.query.filter_by(email=session['email']).first()
    user.twitter_api_key = request.form.get("api_key")
    user.twitter_api_secret = request.form.get("api_secret")
    user.twitter_access_token = request.form.get("access_token")
    user.twitter_access_token_secret = request.form.get("access_token_secret")
    user.screen_name = request.form.get("screen_name")
    db.session.commit()
    # tweets = get_user_tweets()
    # return redirect(url_for("dashboard"))
    return render_template("dashboard.html" )









#logout
@app.route("/logout")
def logout():
    session.pop("username",None)
    session.pop("email",None)
    return redirect(url_for("login"))





if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)