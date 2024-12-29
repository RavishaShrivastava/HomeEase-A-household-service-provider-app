from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.secret_key = 'supersecretkey' 
db = SQLAlchemy(app)
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(100), nullable=False)
    def check_password(self, password):
        return self.password == password
class Professional(db.Model):   
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    service= db.Column(db.String(100), nullable=True)
    experience = db.Column(db.String(100), nullable=True)
    address= db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')
class Admin(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100), unique=True,nullable=False)
    password=db.Column(db.String(100),nullable=False)
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String(100), nullable=False)  
    description = db.Column(db.String(100), nullable=False)
class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id')) 
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id')) 
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'))  
    date_of_request = db.Column(db.Date, nullable=False) 
    date_of_completion = db.Column(db.Date, nullable=True)
    service_status = db.Column(db.String(100), nullable=False)
    remark = db.Column(db.String(100), nullable=True)
with app.app_context():
    db.create_all()
