from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
#from werkzeug.utils import secure_filename
from datetime import datetime, date
#import qrcode
# from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tailor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)


#***************************Models*******************
class User(db.Model):
    id  = db.Column(db.Integer,primary_key=True)
    userId = db.Column(db.String(20), unique=True, nullable=False)
    userName = db.Column(db.String(20),nullable=False)
    phone = db.Column(db.String(20),nullable=False)
    numberOfSuit = db.Column(db.String(20),nullable=False)
    address = db.Column(db.String(50),nullable=False)
    date = db.Column(db.Date,nullable=False)
#***************************Shalwar*****************************
    width = db.Column(db.String(20),nullable=False)
    height = db.Column(db.String(20),nullable=False)
    arm = db.Column(db.String(20),nullable=False)
    color = db.Column(db.String(20),nullable=False)
    pocket = db.Column(db.String(20),nullable=False)
    frontPocket = db.Column(db.String(20),nullable=False)
    chestWidth = db.Column(db.String(20),nullable=False)
    daman = db.Column(db.String(20),nullable=False)
#**************************Kameeeas******************************
    height = db.Column(db.String(20),nullable=False)
    width = db.Column(db.String(20),nullable=False)
    pocket = db.Column(db.String(20),nullable=False)


# Create Database 
with app.app_context():
    db.create_all()



# ************************************Routes*****************************************************
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user')
def user():
    all_users = User.query.all()

app.route('/add_user', methods=['GET','POST'])
def add_user():
    if request.method == 'POST':
        try:
            userId = generate_unique_id('ab',User,User.userId)
            userName = request.form['Customer Name']
            phone = request.form['Phone Number']
            numberOfSuit = request.form['Number Of Suit']
            address = request.formp['Address']
            date = datetime.strptime(request.form['Date'],'%d-%m-%Y').date()
            width = request.form['Width']
            height = request.form['Height']
            arm = request.form['Arm']
            color = request.form['Color']
            pocket = request.form['Pocketr']
            frontPocket = request.form['Front Pocket']
            chestWidth = request.form['Chest Width']
            daman = request.form['Daman']
            ####kameeeas Data check and change accordingly 
            # height = request.form['Height kamees']
            # width = request.form['Width Kamees']
            # pocket = request.form['Pocket Kamees']


            new_user = User(
                userId = userId,
                userName = userName,
                phone = phone,
                numberOfSuit = numberOfSuit,
                date = date,
                address = address ,
                width=width,
                height=height,
                arm = arm,
                color = color,
                pocket = pocket,
                frontPocket = frontPocket,
                chestWidth = chestWidth,
                daman = daman,
                # height = height,
                # width = width ,
                # pocket = pocket
                #let us check the name and then we will change this too beacues it become two time with same name 

                
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Customer Added Successfully!','Success')
            return redirect('/user')
        except Exception as e:
            flash(f"Error:{str(e),'Danger'}")
    return render_template('add_user.html')

if __name__ == '__main__':
    app.run(debug=True)
#The following code is about to add measurment no sure is it at all according to talior system but i haven't check and run code i have added sectio too 
# let me run the code and add fucntiolaty like upadate and delete button in this where update will work to update the user data and delete you know 