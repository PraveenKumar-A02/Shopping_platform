from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from datetime import timedelta
from functools import wraps
import re
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Mysql%4002@localhost:3306/shopping_platform'
app.config['JWT_SECRET_KEY'] = 'secret-key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'neevarp02082003@gmail.com'
app.config['MAIL_PASSWORD'] = 'Passcode01gle@G'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(app)
api = Api(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(45), nullable=False)
    lastName = db.Column(db.String(45), nullable=False)
    username = db.Column(db.String(45), nullable=False, unique=True)
    email = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    isDeleted = db.Column(db.Boolean, default=False)

class Account(db.Model):
    __tablename__ = 'accounts'
    account_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    isDeleted = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(255), nullable=False)

class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

def send_email(subject, body, to_email):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = app.config['MAIL_USERNAME']
    msg['To'] = to_email

    with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.sendmail(app.config['MAIL_USERNAME'], to_email, msg.as_string())

        

# Resources
class UserResource(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', password):
            return {'status': False, 'message': 'Password must be at least 8 characters long and include one letter, one number, and one special character.'}, 400

        if password != confirm_password:
            return {'status': False, 'message': 'Passwords do not match.'}, 400

        user = User.query.filter_by(username=username).first()
        if user:
            return {'status': False, 'message': 'Username already exists.'}, 400

        email = data.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            return {'status': False, 'message': 'Email already exists.'}, 400
        
        hashed_password = generate_password_hash(password)
        new_user = User(
            firstName=data['firstName'],
            lastName=data['lastName'],
            username=username,
            email=email,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        
       
        send_email(
            subject="Welcome to the Shopping Platform",
            body="Thank you for registering!",
            to_email=email
        )

        return {'message': 'User account created'}, 201

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username, isDeleted=False).first()
        if user and check_password_hash(user.password, password):
            expires = timedelta(minutes=15)
            access_token = create_access_token(identity={'user_id': user.user_id, 'username': user.username}, expires_delta=expires)
            return {'status': True, 'message': 'Login successful.', 'access_token': access_token}
        else:
            return {'status': False, 'message': 'Invalid username or password.'}, 401

class UserProfileResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        username = current_user['username']
        return {'status': True, 'username': username}

class ProductResource(Resource):
    def get(self, product_id=None):
        if product_id:
            product = Product.query.filter_by(product_id=product_id).first_or_404()
            product_data = {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'description': product.description,
                'price': product.price
            }
            return jsonify({'status': True, 'data': product_data})
        else:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            pagination = Product.query.paginate(page=page, per_page=per_page, error_out=False)
            products = pagination.items
            products_data = [{
                'product_id': product.product_id,
                'product_name': product.product_name,
                'description': product.description,
                'price': product.price
            } for product in products]
            return jsonify({
                'status': True,
                'data': products_data,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page
            })

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        data = request.get_json()
        product = Product(
            product_name=data['product_name'],
            description=data.get('description'),
            price=data['price']
        )
        db.session.add(product)
        db.session.commit()

      
        send_email(
            subject="New Product Added",
            body=f"A new product '{product.product_name}' has been added.",
            to_email=current_user['email']
        )

        return {'message': 'Product created'}, 201

    @jwt_required()
    def delete(self, product_id):
        product = Product.query.filter_by(product_id=product_id).first_or_404()
        db.session.delete(product)
        db.session.commit()
        return {'message': 'Product deleted'}

    @jwt_required()
    def put(self, product_id):
        product = Product.query.filter_by(product_id=product_id).first_or_404()
        data = request.get_json()
        product.product_name = data['product_name']
        product.description = data.get('description', product.description)
        product.price = data['price']
        db.session.commit()
        return {'message': 'Product updated'}

api.add_resource(UserResource, '/users')
api.add_resource(LoginResource, '/login')
api.add_resource(ProductResource, '/products', '/products/<int:product_id>')
api.add_resource(UserProfileResource, '/profile')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/add-product')
@jwt_required()
def add_product():
    return render_template('add_product.html')

@app.route('/products')
def display_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    pagination = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    products_data = [{
        'product_id': product.product_id,
        'product_name': product.product_name,
        'description': product.description,
        'price': product.price
    } for product in products]
    return render_template('display_products.html', products=products_data, 
                           total=pagination.total, pages=pagination.pages, 
                           current_page=pagination.page, per_page=pagination.per_page)




if __name__ == '__main__':
    app.run(debug=True)

