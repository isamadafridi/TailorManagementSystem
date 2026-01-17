from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tailor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def generate_unique_id(prefix, model, column):
    last_user = model.query.order_by(column.desc()).first()
    if last_user:
        last_id = getattr(last_user, column.name)
        number = int(last_id.replace(prefix, '')) + 1
    else:
        number = 1
    return f"{prefix}{number:03d}"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(20), unique=True, nullable=False)
    userName = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    numberOfSuit = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Shalwar measurements
    width = db.Column(db.String(20), nullable=False)
    height = db.Column(db.String(20), nullable=False)
    arm = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    pocket = db.Column(db.String(20), nullable=False)
    frontPocket = db.Column(db.String(20), nullable=False)
    chestWidth = db.Column(db.String(20), nullable=False)
    daman = db.Column(db.String(20), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user')
def user():
    all_users = User.query.all()
    return render_template('user.html', users=all_users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            userId = generate_unique_id('AB', User, User.userId)
            
            userName = request.form['userName']
            phone = request.form['phone']
            numberOfSuit = int(request.form['numberOfSuit'])
            address = request.form['address']
            date_str = request.form['date']
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            width = request.form['width']
            height = request.form['height']
            arm = request.form['arm']
            color = request.form['color']
            pocket = request.form['pocket']
            frontPocket = request.form['frontPocket']
            chestWidth = request.form['chestWidth']
            daman = request.form['daman']

            new_user = User(
                userId=userId,
                userName=userName,
                phone=phone,
                numberOfSuit=numberOfSuit,
                address=address,
                date=date_obj,
                width=width,
                height=height,
                arm=arm,
                color=color,
                pocket=pocket,
                frontPocket=frontPocket,
                chestWidth=chestWidth,
                daman=daman
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Customer Added Successfully!', 'success')
            return redirect(url_for('print_customer', user_id=userId))
            
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
    
    return render_template('add_user.html')
# ... (baaki code same rahega, sirf neeche wale routes add kar ya replace kar)

@app.route('/update/<string:user_id>', methods=['GET', 'POST'])
def update_customer(user_id):
    customer = User.query.filter_by(userId=user_id).first()
    if not customer:
        flash("Customer not found!", 'danger')
        return redirect('/user')

    if request.method == 'POST':
        try:
            customer.userName = request.form['userName']
            customer.phone = request.form['phone']
            customer.numberOfSuit = int(request.form['numberOfSuit'])
            customer.address = request.form['address']
            customer.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            
            customer.width = request.form['width']
            customer.height = request.form['height']
            customer.arm = request.form['arm']
            customer.color = request.form['color']
            customer.pocket = request.form['pocket']
            customer.frontPocket = request.form['frontPocket']
            customer.chestWidth = request.form['chestWidth']
            customer.daman = request.form['daman']

            db.session.commit()
            flash('Customer Updated Successfully!', 'success')
            return redirect('/user')
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')

    return render_template('update_customer.html', customer=customer)

@app.route('/delete/<string:user_id>', methods=['POST'])
def delete_customer(user_id):
    customer = User.query.filter_by(userId=user_id).first()
    if not customer:
        flash("Customer not found!", 'danger')
        return redirect('/user')

    db.session.delete(customer)
    db.session.commit()
    flash('Customer Deleted Successfully!', 'success')
    return redirect('/user')
@app.route('/print/<string:user_id>')
def print_customer(user_id):
    customer = User.query.filter_by(userId=user_id).first()
    if not customer:
        flash("Customer not found!", 'danger')
        return redirect('/user')
    
    return render_template('print_customer.html', customer=customer)

if __name__ == '__main__':
    app.run(debug=True)