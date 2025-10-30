from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from configdb import Config
from models_auto import Base, Customers, Services, Supplies, Record, ServicesSupplies

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db = SQLAlchemy(app)


# Инициализация базы данных
@app.before_request
def create_tables():
    Base.metadata.create_all(db.engine)

# Страницы
@app.route('/')
@app.route('/records-page')
def records_page():
    return render_template('records.html')

@app.route('/clients-page')
def clients_page():
    return render_template('clients.html')

@app.route('/expenses-page')
def expenses_page():
    return render_template('expenses.html')

@app.route('/prices-page')
def prices_page():
    return render_template('prices.html')

@app.route('/finance-page')
def finance_page():
    return render_template('finance.html')

# Клиенты
@app.route('/customers', methods=['GET', 'POST'])
def handle_customers():
    if request.method == 'GET':
        customers = db.session.query(Customers).all()
        return jsonify([{
            'ID': c.ID,
            'surname': c.surname,
            'name': c.name,
            'patronymic': c.patronymic,
            'phone': c.phone
        } for c in customers])

    elif request.method == 'POST':
        data = request.json
        new_customer = Customers(
            surname=data.get('surname'),
            name=data.get('name'),
            patronymic=data.get('patronymic'),
            phone=data.get('phone')
        )
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({'message': 'Клиент добавлен', 'ID': new_customer.ID}), 201


@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = db.session.query(Customers).filter(Customers.ID == customer_id).first()
    if customer:
        return jsonify({
            'ID': customer.ID,
            'surname': customer.surname,
            'name': customer.name,
            'patronymic': customer.patronymic,
            'phone': customer.phone
        })
    return jsonify({'error': 'Клиент не найден'}), 404


# Услуги
@app.route('/services', methods=['GET', 'POST'])
def handle_services():
    if request.method == 'GET':
        services = db.session.query(Services).all()
        return jsonify([{
            'ID': s.ID,
            'name': s.name,
            'price': s.price
        } for s in services])

    elif request.method == 'POST':
        data = request.json
        new_service = Services(
            name=data.get('name'),
            price=data.get('price')
        )
        db.session.add(new_service)
        db.session.commit()
        return jsonify({'message': 'Услуга добавлена', 'ID': new_service.ID}), 201


# Материалы
@app.route('/supplies', methods=['GET', 'POST'])
def handle_supplies():
    if request.method == 'GET':
        supplies = db.session.query(Supplies).all()
        return jsonify([{
            'ID': s.ID,
            'name': s.name,
            'price': s.price
        } for s in supplies])

    elif request.method == 'POST':
        data = request.json
        new_supply = Supplies(
            name=data.get('name'),
            price=data.get('price')
        )
        db.session.add(new_supply)
        db.session.commit()
        return jsonify({'message': 'Материал добавлен', 'ID': new_supply.ID}), 201


# Записиz
@app.route('/records', methods=['GET', 'POST'])
def handle_records():
    if request.method == 'GET':
        records = db.session.query(Record).all()
        return jsonify([{
            'ID': r.ID,
            'id_customers': r.id_customers,
            'id_services': r.id_services,
            'date': r.date.isoformat() if r.date else None,
            'name': r.name  # Добавьте это поле
        } for r in records])

    elif request.method == 'POST':
        data = request.json
        new_record = Record(
            id_customers=data.get('id_customers'),
            id_services=data.get('id_services'),
            date=data.get('date'),
            name=data.get('name')  # Добавьте это поле
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify({'message': 'Запись добавлена', 'ID': new_record.ID}), 201

@app.route('/records/<int:record_id>', methods=['GET'])
def get_record(record_id):
    record = db.session.query(Record).filter(Record.ID == record_id).first()
    if record:
        return jsonify({
            'ID': record.ID,
            'id_customers': record.id_customers,
            'id_services': record.id_services,
            'date': record.date.isoformat() if record.date else None,
            'name': record.name
        })
    return jsonify({'error': 'Запись не найдена'}), 404

# Обновить запись
@app.route('/records/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    record = db.session.query(Record).filter(Record.ID == record_id).first()
    if not record:
        return jsonify({'error': 'Запись не найдена'}), 404

    data = request.json
    record.id_customers = data.get('id_customers', record.id_customers)
    record.id_services = data.get('id_services', record.id_services)
    record.date = data.get('date', record.date)
    record.name = data.get('name', record.name)

    db.session.commit()
    return jsonify({'message': 'Запись обновлена'})

# Удалить запись
@app.route('/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    record = db.session.query(Record).filter(Record.ID == record_id).first()
    if not record:
        return jsonify({'error': 'Запись не найдена'}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': 'Запись удалена'})

# Расходные материалы
@app.route('/services_supplies', methods=['GET', 'POST'])
def handle_services_supplies():
    if request.method == 'GET':
        services_supplies = db.session.query(ServicesSupplies).all()
        return jsonify([{
            'ID': ss.ID,
            'id_services': ss.id_services,
            'id_supplies': ss.id_supplies,
            'material_consumption': ss.material_consumption,
            'units_measurement': ss.units_measurement
        } for ss in services_supplies])

    elif request.method == 'POST':
        data = request.json
        new_service_supply = ServicesSupplies(
            id_services=data.get('id_services'),
            id_supplies=data.get('id_supplies'),
            material_consumption=data.get('material_consumption'),
            units_measurement=data.get('units_measurement')
        )
        db.session.add(new_service_supply)
        db.session.commit()
        return jsonify({'message': 'Расход материала добавлен', 'ID': new_service_supply.ID}), 201
    
    





# # ========== СЛОЖНЫЕ ЗАПРОСЫ ==========
# @app.route('/records/details', methods=['GET'])
# def get_records_details():
#     records = (db.session.query(Record, Customers, Services)
#                .join(Customers, Record.id_customers == Customers.ID)
#                .join(Services, Record.id_services == Services.ID)
#                .all())
#
#     result = []
#     for record, customer, service in records:
#         result.append({
#             'record_id': record.ID,
#             'date': record.date.isoformat() if record.date else None,
#             'customer': f"{customer.surname} {customer.name}",
#             'customer_phone': customer.phone,
#             'service': service.name,
#             'service_price': service.price
#         })
#
#     return jsonify(result)
#
#
# @app.route('/services/<int:service_id>/materials', methods=['GET'])
# def get_service_materials(service_id):
#     materials = (db.session.query(ServicesSupplies, Supplies)
#                  .join(Supplies, ServicesSupplies.id_supplies == Supplies.ID)
#                  .filter(ServicesSupplies.id_services == service_id)
#                  .all())
#
#     result = []
#     for service_supply, supply in materials:
#         result.append({
#             'material_name': supply.name,
#             'consumption': service_supply.material_consumption,
#             'units': service_supply.units_measurement,
#             'material_price': supply.price
#         })
#
#     return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)