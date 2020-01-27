#pip install flask
#pip install flask-sqlalchemy
#pip install mysqlclient


from flask import Flask,render_template,request         #render_template renders html files stored in templates
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app=Flask(__name__);

#connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/codingthunder'
db = SQLAlchemy(app)


#schema for flask sqlalchemy
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),  nullable=False)
    phone_num = db.Column(db.String(12),  nullable=False)
    msg = db.Column(db.String(120),  nullable=False)
    date = db.Column(db.String(12),  nullable=True) #cuz database already puts date
    email= db.Column(db.String(20),  nullable=False)


@app.route('/')

def home():
    return render_template("index.html");   #this is response to client


@app.route("/about")
def about():
    return render_template("about.html")  




@app.route("/contact",methods=["GET","POST"])
def contact():
    if(request.method=="POST"):             #import request from flask
        #getting all values from post 
        name=request.form.get("name");
        email=request.form.get("email");
        phone=request.form.get("phone");
        message=request.form.get("message");
        date=datetime.date(datetime.now())

        entry=Contacts(name=name, phone_num=phone, msg=message , email=email,date=date);

        db.session.add(entry);
        db.session.commit();

    
    return render_template("contact.html")


@app.route("/post")
def post():
    return render_template("post.html")



#in cmd write python <app>.py to run server

app.run(debug=True);   #debug for hot reload
