from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import text 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy import func
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
    """ Auto-Fixer: Adds new columns if missing. """
    print("Checking Database Schema...")
    with app.app_context():
        inspector = db.inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('user')]

        # List of ALL columns to check/add
        new_columns_to_add = [
            ("lambhai", "VARCHAR(50)"),
            ("tera", "VARCHAR(50)"),
            ("bazo", "VARCHAR(50)"),
            ("chati", "VARCHAR(50)"),
            ("kamar", "VARCHAR(50)"),
            ("ghaihr", "VARCHAR(50)"),
            ("shalwar", "VARCHAR(50)"),
            ("ghair", "VARCHAR(50)"),
            ("drzdar", "VARCHAR(50)"),
            ("price", "INTEGER"),
            ("mora", "VARCHAR(50)"),      
            ("darmyan", "VARCHAR(50)"),   
            ("pocket_width", "VARCHAR(50)"), 
            ("kaj_count", "VARCHAR(50)"),
            ("style_patti", "VARCHAR(50)"),
            ("pocket_size", "VARCHAR(50)"),
            ("style_bazo", "VARCHAR(50)"),
            ("side_pocket", "VARCHAR(50)")
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
    
    # --- Measurements ---
    # Keeping old English fields for safety, but primary data goes to Urdu fields now
    height = db.Column(db.String(20))
    width = db.Column(db.String(20))
    chestWidth = db.Column(db.String(20))
    arm = db.Column(db.String(20))
    teera = db.Column(db.String(20))
    shalwarLength = db.Column(db.String(20))
    shalwarWidth = db.Column(db.String(20))
    
    # New Urdu Fields
    lambhai = db.Column(db.String(20))
    tera = db.Column(db.String(20))
    bazo = db.Column(db.String(20))
    collar = db.Column(db.String(20))
    chati = db.Column(db.String(20))
    kamar = db.Column(db.String(20))
    
    ghaihr = db.Column(db.String(20))
    shalwar = db.Column(db.String(20))
    poncha = db.Column(db.String(20))        
    ghair = db.Column(db.String(20))
    asan = db.Column(db.String(20))
    drzdar = db.Column(db.String(20))

    # --- Extra Sizes ---
    mora = db.Column(db.String(20))
    darmyan = db.Column(db.String(20))
    pocket_width = db.Column(db.String(20))

    # --- Styles ---
    style_collar = db.Column(db.String(50))
    style_cuff = db.Column(db.String(50))
    style_pocket = db.Column(db.String(50))
    style_patti = db.Column(db.String(50))
    style_daman = db.Column(db.String(50))
    style_shalwar_pocket = db.Column(db.String(50)) 
    
    style_bazo = db.Column(db.String(50)) # Shoulder Style
    side_pocket = db.Column(db.String(50)) # Side Pocket Style

    # --- Sizes ---
    size_collar = db.Column(db.String(20))
    size_patti = db.Column(db.String(20))
    size_cuff = db.Column(db.String(20))
    kaj_count = db.Column(db.String(50))
    pocket_size = db.Column(db.String(50))
    
    special_notes = db.Column(db.String(500))
    price = db.Column(db.Integer, default=0)

    # --- Financial ---
    total_amount = db.Column(db.Integer, default=0)
    advance_payment = db.Column(db.Integer, default=0)
    remaining_balance = db.Column(db.Integer, default=0)

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            userId = generate_unique_id('AB', User, User.userId)
            
            # Handle Pocket Style (Checkbox/Radio lists)
            pocket_list = request.form.getlist('style_pocket')
            pocket_str = ", ".join(pocket_list) if pocket_list else request.form.get('style_pocket')

            try: num_suits = int(request.form['numberOfSuit'])
            except: num_suits = 1
            
            try: price_val = int(request.form['price'])
            except: price_val = 0

            new_user = User(
                userId=userId,
                userName=request.form['userName'],
                phone=request.form['phone'],
                numberOfSuit=num_suits,
                address=request.form['address'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                price=price_val,

                # New Urdu Fields
                lambhai=request.form.get('lambhai'),
                tera=request.form.get('tera'),
                bazo=request.form.get('bazo'),
                collar=request.form.get('collar'),
                chati=request.form.get('chati'),
                kamar=request.form.get('kamar'),
                
                ghaihr=request.form.get('ghaihr'),
                shalwar=request.form.get('shalwar'),
                poncha=request.form.get('poncha'),
                ghair=request.form.get('ghair'),
                asan=request.form.get('asan'),
                drzdar=request.form.get('drzdar'),

                # Styles
                style_collar=request.form.get('style_collar'),
                style_cuff=request.form.get('style_cuff'),
                style_pocket=pocket_str,
                style_daman=request.form.get('style_daman'),
                style_patti=request.form.get('style_patti'),
                style_shalwar_pocket=request.form.get('style_shalwar_pocket'),
                
                # New Styles (Direct Catch)
                style_bazo=request.form.get('style_bazo'),
                side_pocket=request.form.get('side_pocket'),

                # Sizes
                size_collar=request.form.get('size_collar'),
                size_patti=request.form.get('size_patti'),
                kaj_count=request.form.get('kaj_count'),
                
                # Unique Size Names (Direct Catch - No Lists)
                size_cuff=request.form.get('size_cuff'),
                mora=request.form.get('mora'),       
                darmyan=request.form.get('darmyan'), 
                
                pocket_size=request.form.get('pocket_size'),
                pocket_width=request.form.get('pocket_width'), 
                
                special_notes=request.form.get('special_notes')
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Customer Added Successfully!', 'success')
            return redirect(url_for('view_customer', user_id=userId))
            
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
            try: customer.numberOfSuit = int(request.form['numberOfSuit'])
            except: customer.numberOfSuit = 1
            
            try: customer.price = int(request.form['price'])
            except: customer.price = 0

            customer.address = request.form['address']
            customer.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            
            # Update Urdu Fields
            customer.lambhai = request.form.get('lambhai')
            customer.tera = request.form.get('tera')
            customer.bazo = request.form.get('bazo')
            customer.collar = request.form.get('collar')
            customer.chati = request.form.get('chati')
            customer.kamar = request.form.get('kamar')
            
            customer.ghaihr = request.form.get('ghaihr')
            customer.shalwar = request.form.get('shalwar')
            customer.poncha = request.form.get('poncha')
            customer.ghair = request.form.get('ghair')
            customer.asan = request.form.get('asan')
            customer.drzdar = request.form.get('drzdar')

            # Update Styles
            customer.style_collar = request.form.get('style_collar')
            customer.style_cuff = request.form.get('style_cuff')
            customer.style_daman = request.form.get('style_daman')
            customer.style_patti = request.form.get('style_patti')
            customer.style_shalwar_pocket = request.form.get('style_shalwar_pocket')
            
            # Update New Styles
            customer.style_bazo = request.form.get('style_bazo')
            customer.side_pocket = request.form.get('side_pocket')

            # Handle Pockets
            pocket_list = request.form.getlist('style_pocket')
            if pocket_list:
                 customer.style_pocket = ", ".join(pocket_list)
            else:
                 customer.style_pocket = request.form.get('style_pocket')

            # Update Sizes (Using Unique Names - FIXED LOGIC)
            customer.size_cuff = request.form.get('size_cuff')
            customer.mora = request.form.get('mora')
            customer.darmyan = request.form.get('darmyan')

            customer.pocket_size = request.form.get('pocket_size')
            customer.pocket_width = request.form.get('pocket_width')

            customer.size_collar = request.form.get('size_collar')
            customer.size_patti = request.form.get('size_patti')
            customer.kaj_count = request.form.get('kaj_count')
            
            customer.special_notes = request.form.get('special_notes')

            db.session.commit()
            flash('Customer Updated Successfully!', 'success')
            # Redirect to View 
            return redirect(url_for('view_customer', user_id=user_id))
            
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
    customer = User.query.filter(or_(User.phone == query, User.userName.ilike(f"%{query}%"))).first()
    
    if customer:
        flash(f'Found: {customer.userName}', 'success')
        return redirect(url_for('view_customer', user_id=customer.userId))
    else:
        flash('No customer found with that Name or Phone!', 'danger')
        return redirect(url_for('home'))

@app.route('/delete/<string:user_id>', methods=['POST'])
def delete_customer(user_id):
    customer = User.query.filter_by(userId=user_id).first_or_404()
    try:
        db.session.delete(customer)
        db.session.commit()
        flash('Customer Deleted Successfully!', 'success')
        return redirect('/user')
    except Exception as e:
        flash(f"Error deleting customer: {str(e)}", 'danger')
        return redirect(url_for('view_customer', user_id=user_id))

# --- DELETE PAGE LOGIC ---
@app.route('/deleteCustomer', methods=['GET', 'POST'])
def remove_customer_page():
    found_customer = None
    error = None
    if request.method == 'POST':
        search_id = request.form.get('search_id')
        found_customer = User.query.filter_by(userId=search_id).first()
        if not found_customer:
            error = f"No customer found with ID: {search_id}"
    return render_template('remove_customer.html', customer=found_customer, error=error)

@app.route('/deleteCustomer_submit', methods=['POST'])
def remove_customer_submit():
    user_id = request.form.get('customer_userId')
    customer = User.query.filter_by(userId=user_id).first_or_404()
    try:
        db.session.delete(customer)
        db.session.commit()
        return render_template('remove_customer.html', success=f"Customer {user_id} deleted successfully.")
    except Exception as e:
        return render_template('remove_customer.html', error=f"Error deleting: {str(e)}")

# --- LEDGER (KHATA) ROUTES ---

@app.route('/ledger', methods=['GET', 'POST'])
def ledger():
    search_query = ""
    
    # --- 1. Global Stats Calculation ---
    # Using specific entities makes it faster than fetching whole objects
    all_data = User.query.with_entities(User.total_amount, User.advance_payment, User.price).all()
    
    total_receivable = sum((u.total_amount or 0) for u in all_data)
    total_received = sum((u.advance_payment or 0) for u in all_data)
    total_pending = sum((u.price or 0) for u in all_data)

    # --- 2. List Fetching Logic ---
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            # Filtered List (Search)
            users = User.query.filter(
                or_(
                    User.userId == search_query,
                    User.phone == search_query,
                    User.userName.ilike(f"%{search_query}%")
                )
            ).all()
            if not users:
                flash("No customer found with those details.", "danger")
        else:
            # If search is empty, show all
            users = User.query.order_by(User.date.desc()).all()
    else:
        # Default View: Show ALL users (Newest First)
        users = User.query.order_by(User.date.desc()).all()

    return render_template('ledger.html', 
                           users=users, 
                           search_query=search_query,
                           total_receivable=total_receivable,
                           total_received=total_received,
                           total_pending=total_pending)

@app.route('/process_transaction', methods=['POST'])
def process_transaction():
    user_id = request.form.get('user_id')
    try:
        amount = int(request.form.get('amount', 0))
    except ValueError:
        amount = 0

    transaction_type = request.form.get('type') # 'add_debt' or 'payment'
    
    customer = User.query.filter_by(userId=user_id).first_or_404()
    
    try:
        # Initialize values if they are None (null in database)
        if customer.price is None: customer.price = 0
        if customer.total_amount is None: customer.total_amount = 0
        if customer.advance_payment is None: customer.advance_payment = 0

        if transaction_type == 'add_debt':
            # Logic: Add Remaining -> Increases Total Bill & Increases Pending Balance
            customer.price += amount
            customer.total_amount += amount
            flash(f"Added {amount} to remaining. New Balance: {customer.price}", "warning")
            
            # Updates the date to RIGHT NOW whenever add remaining
            customer.date = datetime.now()

        elif transaction_type == 'payment':
            # Logic: Payment -> Increases Received & Decreases Pending Balance
            customer.price -= amount
            customer.advance_payment += amount
            flash(f"Payment of {amount} received. Remaining Balance: {customer.price}", "success")

        db.session.commit()
        
    except Exception as e:
        flash(f"Error processing transaction: {str(e)}", "danger")
        
    # Reload ledger to show updated values
    return render_template('ledger.html', 
                           users=[customer], # Show the updated user immediately
                           search_query=customer.phone, # Keep the search active
                           total_receivable=User.query.with_entities(func.sum(User.total_amount)).scalar() or 0,
                           total_received=User.query.with_entities(func.sum(User.advance_payment)).scalar() or 0,
                           total_pending=User.query.with_entities(func.sum(User.price)).scalar() or 0)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        update_database_schema() 
    app.run(debug=True)