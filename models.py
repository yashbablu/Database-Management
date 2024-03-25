from db import db
import enum

class MedicalEquipment(db.Model):
    __tablename__ = "medical_equipment"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    manufacturer = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250))
    rent = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer)
    
class Supplier(db.Model):
    __tablename__ = "suppliers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.Text)
    stock_id = db.Column(db.Integer, db.ForeignKey('medical_equipment.id'), nullable=False)

    # A foreign key relationship
    # stock = db.relationship('MedicalEquipment', backref='suppliers', lazy=True)

class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(12), unique=True, nullable=False)


class Rent(db.Model):
    __tablename__ = "rents"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('medical_equipment.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    # A foreign key relationship
    client = db.relationship('Client', backref='rents', lazy=True)
    equipment = db.relationship('MedicalEquipment', backref='rents', lazy=True)
    payment = db.relationship('Payment', backref='rent',uselist=False, lazy=True)

class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    rent_id = db.Column(db.Integer, db.ForeignKey('rents.id'), nullable=False)
