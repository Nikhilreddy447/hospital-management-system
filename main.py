from flask import Flask,redirect,render_template,request,session,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import create_engine
from flask_mail import Mail
import json
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user

'''with open('config.json','r') as c:
    params=json.load(c)['params']'''

#my database connection
local_server=True
app=Flask(__name__)
app.secret_key='nikhil'


#this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

'''#Smpt mail server settings

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USER_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
    
)
mail=Mail(app)'''


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/hms'
db=SQLAlchemy(app)

engine = create_engine('mysql://root:@local/hms')

class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))
    
class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))
    
class Patients(db.Model):
    pid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    gender=db.Column(db.String(50))
    slot=db.Column(db.String(50))
    disease=db.Column(db.String(50))
    time=db.Column(db.String(50),nullable=False)
    date=db.Column(db.String(50),nullable=False)
    dept=db.Column(db.String(50))
    number=db.Column(db.String(50))
    
class Doctors(db.Model):
    did=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    doctorname=db.Column(db.String(50))
    dept=db.Column(db.String(50))

class Trigr(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    action=db.Column(db.String(50))
    timesstamp=db.Column(db.String(50))
      
    
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/test')
def test():
    try:
        a=Test.query.all()
        
        return 'my database is connected'
    except Exception as e:
        print(e)
        return 'my  database is not connected'

#creating endpoints and its functions
@app.route('/doctors',methods=['POST','GET'])
def doctors():
    if request.method=='POST':
        email=request.form.get('email')
        doctorname=request.form.get('doctorname')
        dept=request.form.get('dept')
        newuser=Doctors(email=email,doctorname=doctorname,dept=dept)
        db.session.add(newuser)
        db.session.commit()
        
        flash("Information is stored","primary")
    
    return render_template('doctor.html')


@app.route('/patients',methods=['POST','GET'])
@login_required
def patients():
    doct=Doctors.query.all()
    if request.method=='POST':
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')
        newuser=Patients(email=email,name=name,gender=gender,slot=slot,disease=disease,time=time,date=date,dept=dept,number=number)
        db.session.add(newuser)
        db.session.commit()
        
        
        
        ''' mail.send_message('HOSPITAL MANAGEMENT SYSTEM',
        sender='aletinikhilreddy11@gmail.com',
        recipients=[params['gmail-user']],
        body='your booking is conformed thanks for choosing us'
        )'''
        
        
        
        flash("booking conformed","info")
        
        
    return render_template('patients.html',doct=doct)




@app.route('/bookings')
@login_required
def bookings():
    em=current_user.email
    query=Patients.query.filter_by(email=em)
    print(query)
    
    return render_template('bookings.html',query=query)



@app.route('/edit/<string:pid>',methods=['POST','GET'])
@login_required
def edit(pid):
    posts=Patients.query.filter_by(pid=pid).first()
    if request.method=='POST':
        
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')
        #update operation
       #for windows 10 and below db.engine.execute(UPDATE `patients` SET `email` = 'jugug1@gmail.com', `name` = 'jumangi1', `gender` = 'Male1', `slot` = 'night1', `disease` = 'heartdisease1', `time` = '09:10:00', `date` = '2023-14-15', `dept` = 'ortho', `number` = '5434233554' WHERE `patients`.`pid` = 1;)
        post=Patients.query.filter_by(pid=pid).first()
        post.email=email
        post.name=name
        post.gender=gender
        post.slot=slot
        post.disease=disease
        post.time=time
        post.date=date
        post.dept=dept
        post.number=number
        db.session.commit()
        flash("slot is updated","success")
        return redirect('/bookings')
        
        
    return render_template('edit.html',post=posts)


@app.route("/delete/<string:pid>",methods=['POST','GET'])
@login_required
def delete(pid):
    # db.engine.execute(f"DELETE FROM `patients` WHERE `patients`.`pid`={pid}")
    query=Patients.query.filter_by(pid=pid).first()
    db.session.delete(query)
    db.session.commit()
    flash("Slot Deleted Successful","danger")
    return redirect('/bookings')




@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method =="POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        user= User.query.filter_by(email = email).first()
        if user:
            flash("email alredy exist","warning")
            return render_template('signup.html')
        enpassword=generate_password_hash(password)
       # new_user=db.engine.execute(f"INSERT INTO `user`  (`username`,`email`,`password`)VALUES('{username}','{email}','{enpassword}')")
        newuser=User(username=username,email=email,password=enpassword)
        db.session.add(newuser)
        db.session.commit()
        flash("Signup success please login","success")
        return render_template('login.html')
    
    return render_template('signup.html')




@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return render_template('index.html')
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')  

    return render_template('login.html')
 



        
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("logout successful","warning")
    return redirect(url_for('login'))

@app.route('/details')
@login_required
def details():
    posts=Trigr.query.all()
    return render_template('triggers.html',posts=posts)

@app.route('/search',methods=['POST','GET'])
@login_required
def search():
    if request.method=='POST':
        query=request.form.get('search')
        dept=Doctors.query.filter_by(dept=query).first()
        name=Doctors.query.filter_by(doctorname=query).first()
        if dept or name:
            flash("Doctor is available","info")
        else:
            flash("Doctor is not available","danger")    
    return render_template('index.html')

app.run(debug=True)  




