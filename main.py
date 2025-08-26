#request use for get and post request in database
#redirect for different pages
#generate_password_hash,check_password_hash password encrypting and decrypting
from flask import Flask,render_template,request,redirect,session,url_for
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
app = Flask(__name__)
app.secret_key="123"
current_user = ""

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

    def set_password(self,password):
        self.password = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)



@app.route("/",methods=["GET","POST"])
def dashboard():
    if request.method=="POST":
        return redirect(url_for("login"))
    if request.method=="GET":
        return render_template("dashboard.html", username=session['username'])



#Login
@app.route("/login",methods=["POST","GET"])
def login():
    #collect info from the login form
    #check if info in db
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
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
            return render_template("login.html")
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








            #
            # new_user = User(username=username)
            # new_user.set_password(password)
            # db.session.add(new_user)
            # db.session.commit()
            # session["username"] = username
            # return redirect(url_for("dashboard"))












#dashboard
# @app.route("/dashboard")
# def dashboard():
#     return render_template("dashboard.html",username=session["username"])










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