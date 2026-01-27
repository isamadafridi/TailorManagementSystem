from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import text 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import or_
import sys
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- DATABASE SETUP ---
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(application_path, 'tailor.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db = SQLAlchemy(app)

# --- HELPER FUNCTIONS ---
def generate_unique_id(prefix, model, column):
    last_user = model.query.order_by(column.desc()).first()
    if last_user:
        last_id = getattr(last_user, column.name)
        try:
            number = int(last_id.replace(prefix, '')) + 1
        except:
            number = 1
    else:
        number = 1
    return f"{prefix}{number:03d}"

def update_database_schema():
    """ Auto-Fixer: Checks for new columns and adds them if missing. """
    print("Checking Database Schema...")
    with app.app_context():
        inspector = db.inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('user')]

        new_columns_to_add = [
            ("kaj_count", "VARCHAR(50)"),
            ("pocket_size", "VARCHAR(50)"),
            ("style_patti", "VARCHAR(50)"),
        ]

        with db.engine.connect() as conn:
            for col_name, col_type in new_columns_to_add:
                if col_name not in existing_columns:
                    print(f"🔧 Update: Adding missing column '{col_name}'...")
                    conn.execute(text(f'ALTER TABLE user ADD COLUMN {col_name} {col_type}'))
                    conn.commit()

# --- DATABASE MODEL ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(20), unique=True, nullable=False)
    userName = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    numberOfSuit = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Measurements
    height = db.Column(db.String(20))
    width = db.Column(db.String(20))
    chestWidth = db.Column(db.String(20))
    arm = db.Column(db.String(20))
    teera = db.Column(db.String(20))
    collar = db.Column(db.String(20))
    
    shalwarLength = db.Column(db.String(20)) 
    poncha = db.Column(db.String(20))        
    shalwarWidth = db.Column(db.String(20))
    asan = db.Column(db.String(20))
    
    # Styles
    style_collar = db.Column(db.String(50))
    style_cuff = db.Column(db.String(50))
    style_pocket = db.Column(db.String(50))
    style_patti = db.Column(db.String(50))
    style_daman = db.Column(db.String(50))
    style_shalwar_pocket = db.Column(db.String(50)) 

    # Sizes
    size_collar = db.Column(db.String(20))
    size_patti = db.Column(db.String(20))
    size_cuff = db.Column(db.String(20))
    
    # NEW FIELDS
    kaj_count = db.Column(db.String(50))
    pocket_size = db.Column(db.String(50))
    special_notes = db.Column(db.String(500))

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            userId = generate_unique_id('AB', User, User.userId)
            
            pocket_list = request.form.getlist('style_pocket')
            pocket_str = ", ".join(pocket_list) if pocket_list else request.form.get('style_pocket')

            try:
                num_suits = int(request.form['numberOfSuit'])
            except:
                num_suits = 1 

            new_user = User(
                userId=userId,
                userName=request.form['userName'],
                phone=request.form['phone'],
                numberOfSuit=num_suits,
                address=request.form['address'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                
                height=request.form.get('height'),
                width=request.form.get('width'),
                chestWidth=request.form.get('chestWidth'),
                arm=request.form.get('arm'),
                teera=request.form.get('teera'),
                collar=request.form.get('collar'),
                
                shalwarLength=request.form.get('shalwarLength'),
                poncha=request.form.get('poncha'),
                shalwarWidth=request.form.get('shalwarWidth'),
                asan=request.form.get('asan'),
                
                style_collar=request.form.get('style_collar'),
                style_cuff=request.form.get('style_cuff'),
                style_pocket=pocket_str,
                style_daman=request.form.get('style_daman'),
                style_patti=request.form.get('style_patti'),
                style_shalwar_pocket=request.form.get('style_shalwar_pocket'),

                size_collar=request.form.get('size_collar'),
                size_patti=request.form.get('size_patti'),
                size_cuff=request.form.get('size_cuff'),
                
                kaj_count=request.form.get('kaj_count'),
                pocket_size=request.form.get('pocket_size'),
                
                special_notes=request.form.get('special_notes')
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Customer Added Successfully!', 'success')
            return redirect(url_for('print_customer', user_id=userId))
            
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
            return redirect(url_for('add_user'))
    
    return render_template('add_user.html')

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
            customer.userName = request.form['userName']
            customer.phone = request.form['phone']
            try:
                customer.numberOfSuit = int(request.form['numberOfSuit'])
            except:
                customer.numberOfSuit = 1

            customer.address = request.form['address']
            customer.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            
            customer.height = request.form.get('height')
            customer.width = request.form.get('width')
            customer.chestWidth = request.form.get('chestWidth')
            customer.arm = request.form.get('arm')
            customer.teera = request.form.get('teera')
            customer.collar = request.form.get('collar')
            
            customer.shalwarLength = request.form.get('shalwarLength')
            customer.poncha = request.form.get('poncha')
            customer.shalwarWidth = request.form.get('shalwarWidth')
            customer.asan = request.form.get('asan')

            customer.style_collar = request.form.get('style_collar')
            customer.style_cuff = request.form.get('style_cuff')
            customer.style_daman = request.form.get('style_daman')
            customer.style_patti = request.form.get('style_patti')
            customer.style_shalwar_pocket = request.form.get('style_shalwar_pocket')

            pocket_list = request.form.getlist('style_pocket')
            if pocket_list:
                 customer.style_pocket = ", ".join(pocket_list)
            else:
                 customer.style_pocket = request.form.get('style_pocket')

            customer.size_collar = request.form.get('size_collar')
            customer.size_patti = request.form.get('size_patti')
            customer.size_cuff = request.form.get('size_cuff')
            
            customer.kaj_count = request.form.get('kaj_count')
            customer.pocket_size = request.form.get('pocket_size')
            
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

@app.route('/search', methods=['POST'])
def search_customer():
    query = request.form.get('search_query')
    customer = User.query.filter(
        or_(
            User.phone == query,
            User.userName.ilike(f"%{query}%")
        )
    ).first()
    
    if customer:
        flash(f'Found: {customer.userName}', 'success')
        return redirect(url_for('view_customer', user_id=customer.userId))
    else:
        flash('No customer found with that Name or Phone!', 'danger')
        return redirect(url_for('home'))

# --- NEW DELETE PAGE LOGIC (REQUIRED FOR THE NEW HTML) ---
@app.route('/deleteCustomer', methods=['GET', 'POST'])
def remove_customer_page():
    found_customer = None
    error = None
    
    if request.method == 'POST':
        search_id = request.form.get('search_id')
        # Search by UserID
        found_customer = User.query.filter_by(userId=search_id).first()
        if not found_customer:
            error = f"No customer found with ID: {search_id}"

    # IMPORTANT: Ensure your HTML file is named 'remove_customer.html'
    return render_template('remove_customer.html', customer=found_customer, error=error)

@app.route('/deleteCustomer_submit', methods=['POST'])
def remove_customer_submit():
    user_id = request.form.get('customer_userId')
    customer = User.query.filter_by(userId=user_id).first_or_404()

@app.route('/delete/<string:user_id>', methods=['POST'])
def delete_customer(user_id):
    # 1. Find the customer
    customer = User.query.filter_by(userId=user_id).first_or_404()
    
    try:
        # 2. Delete from DB
        db.session.delete(customer)
        db.session.commit()
        flash('Customer Deleted Successfully!', 'success')
        return redirect('/user') # Go back to the list
        
    except Exception as e:
        flash(f"Error deleting customer: {str(e)}", 'danger')
        return redirect(url_for('view_customer', user_id=user_id))
    
    try:
        db.session.delete(customer)
        db.session.commit()
        return render_template('remove_customer.html', success=f"Customer {user_id} deleted successfully.")
    except Exception as e:
        return render_template('remove_customer.html', error=f"Error deleting: {str(e)}")

# --- REPORT ROUTE ---
@app.route('/report')
def report():
    # 1. Get all users
    all_users = User.query.all()
    
    # 2. Calculate Totals using Python Math
    # Sum of all 'total_amount' where it is not None
    total_receivable = sum(u.total_amount for u in all_users if u.total_amount)
    
    # Sum of all 'advance_payment'
    total_received = sum(u.advance_payment for u in all_users if u.advance_payment)
    
    # Sum of all 'remaining_balance'
    total_pending = sum(u.remaining_balance for u in all_users if u.remaining_balance)

    # 3. Send these numbers to the HTML page
    return render_template('report.html', 
                           users=all_users, 
                           total_receivable=total_receivable, 
                           total_received=total_received, 
                           total_pending=total_pending)
# --- MAIN EXECUTION ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        update_database_schema() 
    
    app.run(debug=True)