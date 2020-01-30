#pip install flask
#pip install flask-sqlalchemy
#pip install mysqlclient
#pip install flask-Mail


from flask import Flask,render_template,request ,session ,redirect       #render_template renders html files stored in templates
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename        #for better security 
import math
local_server=True

with open("config.json","r") as c:      #reading from config(json) file
    params=json.load(c)["params"]




app=Flask(__name__);

app.secret_key="super key ";    #flask requires secret key

app.config["UPLOAD_FOLDER"]=params["upload_location"]

app.config.update(

MAIL_SERVER="smtp.gmail.com",
MAIL_PORT="465",
MAIL_USE_SSL=True,
MAIL_USERNAME=params["gmail-user"],
MAIL_PASSWORD=params["gmail-password"],
    );

mail=Mail(app);                 #wrap your app around Mail from flask-Mail

#connect to database
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"];
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"];
    
db = SQLAlchemy(app)


#schema contact for flask sqlalchemy
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),  nullable=False)
    phone_num = db.Column(db.String(12),  nullable=False)
    msg = db.Column(db.String(120),  nullable=False)
    date = db.Column(db.String(12),  nullable=True) #cuz database already puts date
    email= db.Column(db.String(20),  nullable=False)


#schema posts for flask sqlalchemy
class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80),  nullable=False)
    slug = db.Column(db.String(20),  nullable=False)
    content = db.Column(db.String(120),  nullable=False)
    tagline = db.Column(db.String(120),  nullable=False)
    date = db.Column(db.String(12),  nullable=True) #cuz database/flask already puts date
    img_file = db.Column(db.String(12),  nullable=True)
    



@app.route('/')

def home():
    #pagination
    #query database for posts
    #posts=Posts.query.filter_by().all()
    #[0:params["no_of_posts"]]
    #last=math.floor(len(posts)/int(params["no_of_posts"]));

    
    #page=request.args.get("page");
    #if(not str(page).isnumeric()):
        #page=1

    #posts=posts[(page-1)*int(params["no_of_posts"]):(page-1)*int(params["no_of_posts"])+int(params["no_of_posts"])]
    #First
    #if(page==1):
        #prev="#";
        #next1="/?page="+str(page+1)
    #elif(page==last):
        #next1="#";
        #prev="/?page="+str(page-1)
    #else:
        #prev="/?page="+str(page-1)
        #prev="/?page="+str(page+1)
        
  
    
    #Middle
    #prev=page-1
    #next=page+1
    #Last
    #prev=page-1
    #next=_#

    
    #query database for posts
    posts=Posts.query.filter_by().all()[0:params["no_of_posts"]]                 #fetching specified number of posts
    return render_template("index.html",params=params,posts=posts);   #this is response to client


@app.route("/about")
def about():
    return render_template("about.html",params=params)  


@app.route("/dashboard",methods=["GET","POST"])
def dashboard():
    if("user" in session and session["user"]==params["admin_user"]):
        posts=Posts.query.all();
        return render_template("dashboard.html",params=params,posts=posts)

    
    if(request.method=="POST"):
        username=request.form.get("name");
        password=request.form.get("password");
        print(username);
        print(password);
        if(username==params["admin_user"] and password==params["admin_pass"]):
            #set the session variable
            session["user"]=username
            posts=Posts.query.all();
            return render_template("dashboard.html",params=params,posts=posts);

    
    
    return render_template("signIn.html",params=params)


@app.route("/edit/<string:sno>",methods=["GET","POST"])  #For getting specific post with sno
def edit(sno):
    if("user" in session and session["user"]==params["admin_user"]):        #so only admin could edit
        if(request.method=="POST"):
            box_title=request.form.get("title");
            tagline=request.form.get("tagline");
            slug=request.form.get("slug");
            content=request.form.get("content");
            img_file=request.form.get("img_file");
            date=datetime.date(datetime.now())

                #This will add new post 
            if(sno=="0"):
                new_post=Posts(title=box_title,slug=slug,content=content,tagline=tagline,img_file=img_file,date=date);
                db.session.add(new_post);
                db.session.commit();
                
                

            #This will edit existing post 
            else:
                post=Posts.query.filter_by(sno=sno).first();
                post.title=box_title;
                post.slug=slug;
                post.content=content;
                post.tagline=tagline
                post.img_file=img_file;
                post.date=date;
                db.session.commit();

                return redirect("/edit/"+sno);
    





        post=Posts.query.filter_by(sno=sno).first();    
        return render_template("edit.html",params=params,post=post)


@app.route("/upload",methods=["GET","POST"])

def uploader():
    if("user" in session and session["user"]==params["admin_user"]):
        if(request.method=="POST"):
            f=request.files["file"];
            f.save(os.path.join(app.config["UPLOAD_FOLDER"],secure_filename(f.filename)))
            print("successful");
            return "Successful";



@app.route("/logout")
def logout():
    session.pop("user");
    return redirect("/dashboard")


@app.route("/delete/<string:sno>",methods=["GET","POST"])
def delete(sno):
    if("user" in session and session["user"]==params["admin_user"]):
        post=Posts.query.filter_by(sno=sno).first();
        db.session.delete(post);
        db.session.commit();
        return redirect("/dashboard")


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
        mail.send_message("New Message from blog " + name,sender=email,
                          recipients=[params["gmail-user"]],
                          body=message + "\n" + phone
                          );          #mail function 

    
    return render_template("contact.html",params=params)

#getting post fro db and putting in html
@app.route("/post/<string:post_slug>",methods=["GET"])              #this variable is also passed into function    post_slug is like request_url
def post_route(post_slug):

    #slug is value in database and post will be fetched according to slug because of filter function
    #query database for posts
    post=Posts.query.filter_by(slug=post_slug).first();             
    return render_template("post.html",params=params,post=post)



#in cmd write python <app>.py to run server

app.run(debug=True);   #debug for hot reload
