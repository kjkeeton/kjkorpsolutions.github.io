from flask import Flask, render_template, request, redirect, url_for, session, flash
from . import login_user, current_user, logout_user, login_required, LoginManager
from flaskblog.config import Config
from flaskblog.models import User
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object(Config)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['STATIC_AUTO_RELOAD'] = True
app.template_folder = 'flaskblog/templates'
app.static_folder = 'flaskblog/static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from flask import Bcrypt
# Set the secret key to some random bytes
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_message_category = 'info'
login_manager.login_view = 'login'
from datetime import datetime
with app.app_context():
    user = User(username='KOKO', email='ty@demo.com', password='1234')
    db.session.add(user)
    db.session.commit()

app.secret_key = '123456789'

services = {
    'graphic_design': [
        {'id': 1, 'name': 'Logo Design', 'description': 'Professional logo design service.', 'price': 100, 'img': 'images/jetplane.jpg'},
        {'id': 2, 'name': 'Brochure Design', 'description': 'Creative brochure design service.', 'price': 150, 'img': 'images/klasixhat.jpg'},
        {'id': 3, 'name': 'Business Card Design', 'description': 'Stylish business card design service.', 'price': 50, 'img': 'images/yellow_boot.jpg'}
    ],
    'consultations': [
        {'id': 5, 'name': 'Marketing Consultation', 'description': 'Effective marketing strategies.', 'price': 180, 'img': 'images/jetplane.jpg'},
        {'id': 6, 'name': 'Financial Consultation', 'description': 'Comprehensive financial advice.', 'price': 220, 'img': 'images/klasixhat.jpg'}
    ],
    'business_startup': [
        {'id': 7, 'name': 'Business Plan', 'description': 'Detailed business plan creation.', 'price': 300, 'img': 'images/blktie.jpg'},
        {'id': 8, 'name': 'Startup Funding', 'description': 'Assistance with securing startup funding.', 'price': 400, 'img': 'images/blkwtepic.jpg'},
        {'id': 9, 'name': 'Mentorship Program', 'description': 'Guidance and mentorship for startups.', 'price': 250, 'img': 'images/yellow_boot.jpg'}
    ],
    'growth_plan': [
        {'id': 10, 'name': 'Growth Plan A', 'description': 'Professional growth plan service.', 'price': 100, 'img': 'images/jetplane.jpg'},
        {'id': 11, 'name': 'Growth Plan B', 'description': 'Advanced growth plan service.', 'price': 150, 'img': 'images/yellow_boot.jpg'},
        {'id': 12, 'name': 'Growth Plan C', 'description': 'Complete growth plan service.', 'price': 50, 'img': 'images/klasixhat.jpg'}
    ],
    'financial_review': [
        {'id': 13, 'name': 'Financial Analysis', 'description': 'In-depth financial analysis.', 'price': 180, 'img': 'images/yellow_boot.jpg'},
        {'id': 14, 'name': 'Investment Review', 'description': 'Comprehensive investment review.', 'price': 220, 'img': 'images/jetplane.jpg'}
    ],
    'document_services': [
        {'id': 15, 'name': 'Legal Documents', 'description': 'Preparation of legal documents.', 'price': 300, 'img': 'images/jetplane.jpg'},
        {'id': 16, 'name': 'Healthcare Documents', 'description': 'Preparation of healthcare documents.', 'price': 400, 'img': 'images/jetplane.jpg'},
        {'id': 17, 'name': 'Contract Documents', 'description': 'Preparation of contract documents.', 'price': 250, 'img': 'images/klasixhat.jpg'}
    ]
}

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/index_growth')
def index_growth():
    return render_template('index_growth.html')

@app.route('/add_to_cart/<service_type>/<service_name>')
def add_to_cart(service_type, service_name):
    cart = session.get('cart', [])
    service = next((s for s in services[service_type] if s['name'] == service_name), None)
    if service:
        existing_item = next((item for item in cart if item['name'] == service_name), None)
        if existing_item:
            existing_item['quantity'] += 1
        else:
            cart.append({'type': service_type, 'name': service_name, 'description': service['description'], 'price': service['price'], 'quantity': 1})
        session['cart'] = cart
        flash(f"Added {service_name} to cart!")
    return redirect(url_for('service_detail', service_type=service_type))

@app.route('/service_detail/<service_type>')
def service_detail(service_type):
    if service_type not in services:
        return redirect(url_for('index'))
    services_data = services[service_type]
    cart_summary = get_cart_summary()
    return render_template('service_detail.html', service_type=service_type, services=services_data, cart_quantity=cart_summary['total_quantity'], cart_total=cart_summary['total'])

@app.route('/services/<service_type>')
def list_services(service_type):
    if service_type not in services:
        return redirect(url_for('index'))
    cart_summary = get_cart_summary()
    return render_template('services.html', service_type=service_type, services=services[service_type], cart_quantity=cart_summary['total_quantity'], cart_total=cart_summary['total'])

@app.route('/update_cart/<service_name>', methods=['POST'])
def update_cart(service_name):
    cart = session.get('cart', [])
    for item in cart:
        if item['name'] == service_name:
            item['quantity'] = int(request.form['quantity'])
            if item['quantity'] == 0:
                cart.remove(item)
            break
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<service_name>')
def remove_from_cart(service_name):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['name'] != service_name]
    session['cart'] = cart
    flash(f"Removed {service_name} from cart!")
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    total_quantity = sum(item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total, total_quantity=total_quantity)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        customer_info = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'zip': request.form.get('zip')
        }
        session['customer_info'] = customer_info
        return redirect(url_for('receipt'))
    return render_template('checkout.html')

@app.route('/receipt')
def receipt():
    cart = session.get('cart', [])
    customer_info = session.get('customer_info', {})
    total = sum(item['price'] * item['quantity'] for item in cart)
    total_quantity = sum(item['quantity'] for item in cart)
    return render_template('receipt.html', cart=cart, customer_info=customer_info, total=total, total_quantity=total_quantity)

def get_cart_summary():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    total_quantity = sum(item['quantity'] for item in cart)
    return {'total': total, 'total_quantity': total_quantity}

from flask import render_template, request
# Add this route in your Flask app
@app.route('/contact_submit', methods=['POST'])
def contact_submit():
    if request.method == 'POST':
        # Get the form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        services = request.form.getlist('services')
        message = request.form['message']

        # You can process the form data here, such as sending an email notification,
        # saving the data to a database, etc.

        # For now, let's just flash a message acknowledging that the form has been submitted
        flash('Thank you, {}! Your message has been received.'.format(first_name))

        # Redirect the user to the thank you page
        return redirect(url_for('thank_you'))

    # If the request method is not POST, redirect the user to the contact page
    return redirect(url_for('contact'))

# Add this route in your Flask app
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        service_choices = request.form.getlist('service_choices')
        message = request.form.get('message')

        # Here, you can process the form data as needed, such as sending an email, storing in a database, etc.
        # For now, let's just print the data to the console
        print("First Name:", first_name)
        print("Last Name:", last_name)
        print("Email:", email)
        print("Phone:", phone)
        print("Service Choices:", service_choices)
        print("Message:", message)

        # Redirect to a thank you page or back to the landing page
        return redirect(url_for('thank_you'))

    # Render the contact form template
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image = db.Column(db.String(120), nullable=True)  # Added image field
    orders = db.relationship('Order', back_populates='user')

from flaskblog.forms import RegistrationForm, LoginForm

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        image_file = None
        if form.image.data:
            image_file = save_image(form.image.data)  # Implement save_image to handle file saving
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=hashed_password, image=image_file)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

from flaskblog.models import Order
@app.route("/dashboard")
@login_required
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', orders=orders)


if __name__ == '__main__':
    app.run(debug=True)
