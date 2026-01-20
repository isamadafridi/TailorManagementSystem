from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import or_
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

# --- DATABASE MODEL ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(20), unique=True, nullable=False)
    userName = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    numberOfSuit = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Kameez Measurements
    height = db.Column(db.String(20))       # Length
    width = db.Column(db.String(20))        # Chaati
    chestWidth = db.Column(db.String(20))
    arm = db.Column(db.String(20))
    teera = db.Column(db.String(20))        # Shoulder
    collar = db.Column(db.String(20))       # Neck
    
    # Shalwar Measurements
    shalwarLength = db.Column(db.String(20)) 
    poncha = db.Column(db.String(20))        
    shalwarWidth = db.Column(db.String(20))  # Ghair
    asan = db.Column(db.String(20))          # Crotch
    
    # Styling Options
    style_collar = db.Column(db.String(50))
    style_cuff = db.Column(db.String(50))
    style_pocket = db.Column(db.String(50))
    style_patti = db.Column(db.String(50))          # This was missing in your DB
    style_daman = db.Column(db.String(50))          
    style_shalwar_pocket = db.Column(db.String(50)) 

    # Size Options (New fields for the numbers like 1.0, 1.5 etc)
    size_collar = db.Column(db.String(20))
    size_patti = db.Column(db.String(20))
    size_cuff = db.Column(db.String(20))
    
    special_notes = db.Column(db.String(500))

# --- ROUTES ---

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            userId = generate_unique_id('AB', User, User.userId)
            
            # Handling Style Pocket (List to String)
            # Checkbox lists need special handling
            pocket_list = request.form.getlist('style_pocket')
            pocket_str = ", ".join(pocket_list) if pocket_list else request.form.get('style_pocket')

            new_user = User(
                userId=userId,
                userName=request.form['userName'],
                phone=request.form['phone'],
                numberOfSuit=int(request.form['numberOfSuit']),
                address=request.form['address'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                
                # Kameez
                height=request.form.get('height'),
                width=request.form.get('width'),
                chestWidth=request.form.get('chestWidth'),
                arm=request.form.get('arm'),
                teera=request.form.get('teera'),
                collar=request.form.get('collar'),
                
                # Shalwar
                shalwarLength=request.form.get('shalwarLength'),
                poncha=request.form.get('poncha'),
                shalwarWidth=request.form.get('shalwarWidth'),
                asan=request.form.get('asan'),
                
                # Styles
                style_collar=request.form.get('style_collar'),
                style_cuff=request.form.get('style_cuff'),
                style_pocket=pocket_str, # Using the processed string
                style_daman=request.form.get('style_daman'),
                style_patti=request.form.get('style_patti'),
                style_shalwar_pocket=request.form.get('style_shalwar_pocket'),

                # Sizes
                size_collar=request.form.get('size_collar'),
                size_patti=request.form.get('size_patti'),
                size_cuff=request.form.get('size_cuff'),
                
                special_notes=request.form.get('special_notes')
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Customer Added Successfully!', 'success')
            return redirect(url_for('print_customer', user_id=userId))
            
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
            return redirect(url_for('add_user')) # Redirect back to form on error
    
    return render_template('add_user.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user')
def user():
    all_users = User.query.all()
    return render_template('user.html', users=all_users)

@app.route('/print/<string:user_id>')
def print_customer(user_id):
    customer = User.query.filter_by(userId=user_id).first_or_404()
    return render_template('print_customer.html', customer=customer)

@app.route('/update/<string:user_id>', methods=['GET', 'POST'])
def update_customer(user_id):
    customer = User.query.filter_by(userId=user_id).first_or_404()

    if request.method == 'POST':
        try:
            # 1. Update Basic Info
            customer.userName = request.form['userName']
            customer.phone = request.form['phone']
            customer.numberOfSuit = int(request.form['numberOfSuit'])
            customer.address = request.form['address']
            customer.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            
            # 2. Update Measurements
            customer.height = request.form.get('height')
            customer.width = request.form.get('width')
            customer.chestWidth = request.form.get('chestWidth')
            customer.arm = request.form.get('arm')
            customer.teera = request.form.get('teera')
            customer.collar = request.form.get('collar')
            
            # 3. Update Shalwar
            customer.shalwarLength = request.form.get('shalwarLength')
            customer.poncha = request.form.get('poncha')
            customer.shalwarWidth = request.form.get('shalwarWidth')
            customer.asan = request.form.get('asan')

            # 4. Update Styles (Radio Buttons)
            customer.style_collar = request.form.get('style_collar')
            customer.style_cuff = request.form.get('style_cuff')
            customer.style_daman = request.form.get('style_daman')
            customer.style_patti = request.form.get('style_patti')
            customer.style_shalwar_pocket = request.form.get('style_shalwar_pocket')

            # Handle Pockets (List to String)
            pocket_list = request.form.getlist('style_pocket')
            if pocket_list:
                 customer.style_pocket = ", ".join(pocket_list)
            else:
                 # If user didn't check anything new, keep old or set empty? 
                 # Usually better to overwrite if empty means "None". 
                 # Let's assume if they send nothing, they mean "None" or we check single val
                 customer.style_pocket = request.form.get('style_pocket')

            # 5. Update Sizes
            customer.size_collar = request.form.get('size_collar')
            customer.size_patti = request.form.get('size_patti')
            customer.size_cuff = request.form.get('size_cuff')
            
            customer.special_notes = request.form.get('special_notes')

            db.session.commit()
            flash('Customer Updated Successfully!', 'success')
            return redirect('/user')
            
        except Exception as e:
            flash(f"Update Error: {str(e)}", 'danger')

    return render_template('update_customer.html', customer=customer)


@app.route('/view/<string:user_id>')
def view_customer(user_id):
    customer = User.query.filter_by(userId=user_id).first_or_404()
    return render_template('view_customer.html', customer=customer)

@app.route('/delete/<string:user_id>', methods=['POST'])
def delete_customer(user_id):
    customer = User.query.filter_by(userId=user_id).first_or_404()

    try:
        db.session.delete(customer)
        db.session.commit()
        flash('Customer Deleted Successfully!', 'success')
    except Exception as e:
        flash(f"Delete Error: {str(e)}", 'danger')

    return redirect('/user')

@app.route('/search', methods=['POST'])
def search_customer():
    # Get the text from the search bar
    query = request.form.get('search_query')
    
    # Search logic: Check if Phone matches OR if Name contains the text
    customer = User.query.filter(
        or_(
            User.phone == query,                 # Exact phone match
            User.userName.ilike(f"%{query}%")    # Name contains text (Case-insensitive)
        )
    ).first()
    
    if customer:
        flash(f'Found: {customer.userName}', 'success')
        # CHANGED: Now redirects to VIEW instead of PRINT
        return redirect(url_for('view_customer', user_id=customer.userId))
    else:
        flash('No customer found with that Name or Phone!', 'danger')
        return redirect(url_for('home'))

# Initialize Database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)