from flask import request, render_template, Blueprint, redirect, session
from datetime import datetime
from models import db, MedicalEquipment, Rent, Client, Payment
from sqlalchemy import or_

bp = Blueprint("views", __name__)

@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/register')
def register():
    return render_template('register.html')

@bp.route('/')
def home():
    equipment = MedicalEquipment.query.all()
    print(equipment)
    return render_template('home.html', equipment=enumerate(equipment))

@bp.route('/equipment', methods=['GET'])
def equipment():
    equipment = MedicalEquipment.query.all()
    error = session.get('error')
    success = session.get('success')
    session['error'] = None
    session['success'] = None
    return render_template('equipment.html', equipment=enumerate(equipment), error=error, success=success)

@bp.route('/equipment/edit/<int:equipment_id>', methods=['GET', 'POST'])
def edit_equipment(equipment_id):
    equipment = MedicalEquipment.query.get_or_404(equipment_id)
    if request.method == 'POST':
        data = request.form
        print(data)
        equipment.name = data['name']
        equipment.manufacturer = data['manufacturer']
        equipment.description = data['description']
        equipment.quantity = data['quantity']
        equipment.rent = data['rent']
        db.session.commit()
        return redirect('/equipment')
    return render_template('edit-equipment.html', equipment=equipment)

@bp.route('/equipment/add', methods=['GET','POST'])
def add_equipment():
    if request.method == 'POST':
        data = request.form
        print(data)
        equipment = MedicalEquipment(
            name=data['name'],
            manufacturer=data['manufacturer'],
            description=data['description'],
            quantity=data['quantity'],
            rent=data['rent']
        )
        db.session.add(equipment)
        db.session.commit()
        return redirect('/equipment')
    return render_template('add-equipment.html')

@bp.route('/rent', methods=['POST'])
def rent():
    data = request.form
    print(data)
    item_id = data['id']
    rent_date = datetime.strptime(data['rentDate'], '%Y-%m-%d')
    return_date = datetime.strptime(data['returnDate'], '%Y-%m-%d')
    print(item_id, rent_date, return_date)
    equipment = MedicalEquipment.query.filter_by(id=item_id).first()
    if equipment.quantity == 0:
        next_available_date = Rent.query.filter_by(equipment_id=item_id).order_by(Rent.end_date.desc()).first().end_date
        session['error'] = f"Equipment not available. Next available date is {next_available_date.strftime('%d %B %Y')}"
        return redirect('/equipment')
    price = equipment.rent
    num_days = (return_date - rent_date).days + 1
    print(num_days)
    # with lock:
    with db.session.begin_nested():
        rent = Rent(client_id=17, equipment_id=item_id, start_date=rent_date, end_date=return_date, total_price=num_days*price)
        MedicalEquipment.query.filter_by(id=item_id).update({'quantity': MedicalEquipment.quantity - 1})
        db.session.add(rent)
        db.session.commit()
    
    session['success']=f"Equipment rented successfully. Total price is {rent.total_price}"
    return redirect('/equipment')

@bp.route('/customer/<int:customer_id>', methods=['GET'])
def customer_report(customer_id):
    customer = Client.query.get_or_404(customer_id)
    rents = Rent.query.filter_by(client_id=customer_id).join(MedicalEquipment).all()
    print(rents[0].equipment)
    return render_template('customer-report.html', customer=customer, rents=enumerate(rents))

@bp.route('/customer', methods=['GET'])
def all_customers_report():
    customers = Client.query.join(Rent, Client.id==Rent.client_id).filter(Rent.end_date > datetime.now()).all()
    data = []
    for c in customers:
        data.append({"customer":c, "equipment": ", ".join(map(lambda x: x.equipment.name,c.rents))})

    return render_template('all-customers.html', data=enumerate(data))

@bp.route('/unpaid-customer', methods=['GET'])
def unpaid_customer():
    # find all customers with rents but no payments
    data = []
    customers = Client.query.join(Rent, Client.id==Rent.client_id).all()
    for c in customers:
        for r in c.rents:
            print(r.payment)
            if r.payment is None:
                data.append({"customer":c, "equipment": r.equipment, "rent": r})

    return render_template('unpaid-customers.html', data=enumerate(data))

@bp.route('/payments', methods=['GET'])
def payments():
    payments = Payment.query.join(Rent, Payment.rent_id==Rent.id).join(Client, Rent.client_id==Client.id).all()
    data = []
    for p in payments:
        data.append({"customer":p.rent.client, "equipment": p.rent.equipment, "rent": p.rent, "payment": p})
    return render_template('payments.html', data=enumerate(data))

@bp.route('/new-rent', methods=['GET', 'POST'])
def new_rent():
    if request.method == 'POST':
        data = request.form
        print(data)
        client = Client.query.get_or_404(data['customer'])
        equipment = MedicalEquipment.query.get_or_404(data['equipment'])
        rent_date = datetime.strptime(data['rentDate'], '%Y-%m-%d')
        return_date = datetime.strptime(data['returnDate'], '%Y-%m-%d')
        print(rent_date, return_date)
        num_days = (return_date - rent_date).days + 1
        rent = Rent(client_id=client.id, equipment_id=equipment.id, start_date=rent_date, end_date=return_date, total_price=num_days*equipment.rent)
        db.session.add(rent)
        db.session.commit()
        db.session.refresh(rent)
        print(data['paid'])
        if data['paid'] == 'on':
            payment = Payment(rent_id=rent.id, amount=rent.total_price, date=datetime.now())
            db.session.add(payment)
            db.session.commit()

        return redirect(f'/customer/{client.id}')
    equipments = MedicalEquipment.query.all()
    customers = Client.query.all()
    return render_template('new-rent.html', equipments=equipments, customers=customers)