from flask import request, render_template, Blueprint, redirect
from datetime import datetime
from models import db, MedicalEquipment, Rent

bp = Blueprint("views", __name__)

@bp.route('/')
def home():
    equipment = MedicalEquipment.query.all()
    print(equipment)
    return render_template('home.html', equipment=enumerate(equipment))

@bp.route('/rent', methods=['GET', 'POST'])
def rent():
    if request.method == 'POST':
        data = request.form
        print(data)
        item_id = data['id']
        rent_date = datetime.strptime(data['rentDate'], '%Y-%m-%d')
        return_date = datetime.strptime(data['returnDate'], '%Y-%m-%d')
        print(item_id, rent_date, return_date)
        price = MedicalEquipment.query.filter_by(id=item_id).first().rent
        num_days = (return_date - rent_date).days + 1
        print(num_days)
        rent = Rent(client_id=17, equipment_id=item_id, start_date=rent_date, end_date=return_date, total_price=num_days*price)
        db.session.add(rent)
        db.session.commit()
        return redirect('/')

    return render_template('index.html')