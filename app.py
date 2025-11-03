from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from configdb import Config
from models_auto import Base, Customers, Services, Supplies, Record, ServicesSupplies
import datetime

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


@app.route('/customers/<int:customer_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_customer(customer_id):
    customer = db.session.query(Customers).filter(Customers.ID == customer_id).first()

    if not customer:
        return jsonify({'error': 'Клиент не найден'}), 404

    if request.method == 'GET':
        return jsonify({
            'ID': customer.ID,
            'surname': customer.surname,
            'name': customer.name,
            'patronymic': customer.patronymic,
            'phone': customer.phone
        })

    elif request.method == 'PUT':
        data = request.json
        customer.surname = data.get('surname', customer.surname)
        customer.name = data.get('name', customer.name)
        customer.patronymic = data.get('patronymic', customer.patronymic)
        customer.phone = data.get('phone', customer.phone)

        db.session.commit()
        return jsonify({'message': 'Клиент обновлен'})

    elif request.method == 'DELETE':
        # Проверяем, есть ли связанные записи
        related_records = db.session.query(Record).filter(Record.id_customers == customer_id).first()
        if related_records:
            return jsonify({'error': 'Нельзя удалить клиента, у которого есть записи'}), 400

        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Клиент удален'})


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


@app.route('/services/<int:service_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_service(service_id):
    service = db.session.query(Services).filter(Services.ID == service_id).first()

    if not service:
        return jsonify({'error': 'Услуга не найдена'}), 404

    if request.method == 'GET':
        return jsonify({
            'ID': service.ID,
            'name': service.name,
            'price': service.price
        })

    elif request.method == 'PUT':
        data = request.json
        service.name = data.get('name', service.name)
        service.price = data.get('price', service.price)

        db.session.commit()
        return jsonify({'message': 'Услуга обновлена'})

    elif request.method == 'DELETE':
        # Проверяем, есть ли связанные записи
        related_records = db.session.query(Record).filter(Record.id_services == service_id).first()
        related_supplies = db.session.query(ServicesSupplies).filter(ServicesSupplies.id_services == service_id).first()

        if related_records or related_supplies:
            return jsonify({'error': 'Нельзя удалить услугу, у которой есть связанные записи или материалы'}), 400

        db.session.delete(service)
        db.session.commit()
        return jsonify({'message': 'Услуга удалена'})


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


@app.route('/supplies/<int:supply_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_supply(supply_id):
    supply = db.session.query(Supplies).filter(Supplies.ID == supply_id).first()

    if not supply:
        return jsonify({'error': 'Материал не найден'}), 404

    if request.method == 'GET':
        return jsonify({
            'ID': supply.ID,
            'name': supply.name,
            'price': supply.price
        })

    elif request.method == 'PUT':
        data = request.json
        supply.name = data.get('name', supply.name)
        supply.price = data.get('price', supply.price)

        db.session.commit()
        return jsonify({'message': 'Материал обновлен'})

    elif request.method == 'DELETE':
        # Проверяем, есть ли связанные записи
        related_supplies = db.session.query(ServicesSupplies).filter(ServicesSupplies.id_supplies == supply_id).first()

        if related_supplies:
            return jsonify({'error': 'Нельзя удалить материал, который используется в услугах'}), 400

        db.session.delete(supply)
        db.session.commit()
        return jsonify({'message': 'Материал удален'})


# Записи
@app.route('/records', methods=['GET', 'POST'])
def handle_records():
    if request.method == 'GET':
        records = db.session.query(Record).all()
        return jsonify([{
            'ID': r.ID,
            'id_customers': r.id_customers,
            'id_services': r.id_services,
            'date': r.date.isoformat() if r.date else None,
            'name': r.name
        } for r in records])

    elif request.method == 'POST':
        data = request.json
        new_record = Record(
            id_customers=data.get('id_customers'),
            id_services=data.get('id_services'),
            date=data.get('date'),
            name=data.get('name')
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify({'message': 'Запись добавлена', 'ID': new_record.ID}), 201


@app.route('/records/<int:record_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_record(record_id):
    record = db.session.query(Record).filter(Record.ID == record_id).first()

    if not record:
        return jsonify({'error': 'Запись не найдена'}), 404

    if request.method == 'GET':
        return jsonify({
            'ID': record.ID,
            'id_customers': record.id_customers,
            'id_services': record.id_services,
            'date': record.date.isoformat() if record.date else None,
            'name': record.name
        })

    elif request.method == 'PUT':
        data = request.json
        record.id_customers = data.get('id_customers', record.id_customers)
        record.id_services = data.get('id_services', record.id_services)
        record.date = data.get('date', record.date)
        record.name = data.get('name', record.name)

        db.session.commit()
        return jsonify({'message': 'Запись обновлена'})

    elif request.method == 'DELETE':
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


@app.route('/services_supplies/<int:service_supply_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_service_supply(service_supply_id):
    service_supply = db.session.query(ServicesSupplies).filter(ServicesSupplies.ID == service_supply_id).first()

    if not service_supply:
        return jsonify({'error': 'Расходный материал не найден'}), 404

    if request.method == 'GET':
        return jsonify({
            'ID': service_supply.ID,
            'id_services': service_supply.id_services,
            'id_supplies': service_supply.id_supplies,
            'material_consumption': service_supply.material_consumption,
            'units_measurement': service_supply.units_measurement
        })

    elif request.method == 'PUT':
        data = request.json
        service_supply.id_services = data.get('id_services', service_supply.id_services)
        service_supply.id_supplies = data.get('id_supplies', service_supply.id_supplies)
        service_supply.material_consumption = data.get('material_consumption', service_supply.material_consumption)
        service_supply.units_measurement = data.get('units_measurement', service_supply.units_measurement)

        db.session.commit()
        return jsonify({'message': 'Расходный материал обновлен'})

    elif request.method == 'DELETE':
        db.session.delete(service_supply)
        db.session.commit()
        return jsonify({'message': 'Расходный материал удален'})


# Финансовые отчеты
@app.route('/finance/report', methods=['GET'])
def get_finance_report():
    date_str = request.args.get('date')
    period = request.args.get('period', 'day')
    report_type = request.args.get('type', 'revenue')

    if not date_str:
        return jsonify({'error': 'Дата не указана'}), 400

    try:
        base_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Неверный формат даты'}), 400

    # Определяем период для фильтрации
    if period == 'day':
        start_date = base_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = base_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'month':
        start_date = base_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = base_date.replace(day=28) + datetime.timedelta(days=4)
        end_date = next_month - datetime.timedelta(days=next_month.day)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'year':
        start_date = base_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = base_date.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    else:
        start_date = base_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = base_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    response_data = {
        'summary': {
            'revenue': 0,
            'expenses': 0,
            'profit': 0
        },
        'records': [],
        'expenses': [],
        'chartData': {
            'labels': [],
            'values': []
        }
    }

    # Получаем записи за период
    records = db.session.query(Record, Services, Customers). \
        join(Services, Record.id_services == Services.ID). \
        join(Customers, Record.id_customers == Customers.ID). \
        filter(Record.date >= start_date, Record.date <= end_date).all()

    # Рассчитываем выручку и собираем статистику по услугам
    total_revenue = 0
    records_data = []
    service_stats = {}  # Считаем сколько раз каждая услуга была выполнена

    for record, service, customer in records:
        service_price = service.price or 0
        total_revenue += service_price

        # Собираем статистику по услугам
        if service.ID not in service_stats:
            service_stats[service.ID] = {
                'service': service,
                'count': 0,
                'total_revenue': 0
            }
        service_stats[service.ID]['count'] += 1
        service_stats[service.ID]['total_revenue'] += service_price

        records_data.append({
            'date': record.date.isoformat() if record.date else None,
            'service_name': service.name,
            'service_id': service.ID,
            'client_name': f"{customer.surname or ''} {customer.name or ''}".strip(),
            'price': service_price
        })

    # Получаем ВСЕ расходные материалы для услуг
    services_supplies = db.session.query(ServicesSupplies, Services, Supplies). \
        join(Services, ServicesSupplies.id_services == Services.ID). \
        join(Supplies, ServicesSupplies.id_supplies == Supplies.ID). \
        all()

    total_expenses = 0
    expenses_data = []

    # Рассчитываем расходы с учетом количества выполненных услуг
    for service_supply, service, supply in services_supplies:
        # Получаем количество выполненных услуг за период
        service_count = service_stats.get(service.ID, {}).get('count', 0)

        # Рассчитываем стоимость материалов для ВСЕХ выполненных услуг этого типа
        material_cost_per_service = (supply.price or 0) * (service_supply.material_consumption or 0)
        total_material_cost = material_cost_per_service * service_count

        total_expenses += total_material_cost

        if service_count > 0:  # Добавляем только если услуга была выполнена
            expenses_data.append({
                'service_name': service.name,
                'material_name': supply.name,
                'consumption_per_service': service_supply.material_consumption or 0,
                'total_consumption': (service_supply.material_consumption or 0) * service_count,
                'unit': service_supply.units_measurement or 'шт',
                'cost_per_service': material_cost_per_service,
                'total_cost': total_material_cost,
                'services_count': service_count
            })

    # Заполняем ответ
    response_data['summary']['revenue'] = total_revenue
    response_data['summary']['expenses'] = total_expenses
    response_data['summary']['profit'] = total_revenue - total_expenses
    response_data['records'] = records_data
    response_data['expenses'] = expenses_data

    # Генерируем данные для графика
    chart_labels = []
    chart_values = []

    if period == 'day':
        # Для дня - разбиваем по часам
        for hour in range(0, 24):
            hour_start = start_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            hour_end = start_date.replace(hour=hour, minute=59, second=59, microsecond=999999)

            # Выручка по часам
            hour_records = [r for r in records_data if r['date'] and
                            hour_start <= datetime.datetime.fromisoformat(r['date'].replace('Z', '+00:00')) <= hour_end]
            hour_revenue = sum(r['price'] for r in hour_records)

            # Расходы по часам (распределяем пропорционально выручке)
            if total_revenue > 0:
                hour_expenses = total_expenses * (hour_revenue / total_revenue)
            else:
                hour_expenses = 0

            hour_profit = hour_revenue - hour_expenses

            chart_labels.append(f"{hour:02d}:00")

            if report_type == 'revenue':
                chart_values.append(hour_revenue)
            elif report_type == 'expenses':
                chart_values.append(hour_expenses)
            else:  # profit
                chart_values.append(hour_profit)

    elif period == 'month':
        # Для месяца - разбиваем по дням
        current_date = start_date
        while current_date <= end_date:
            day_records = [r for r in records_data if r['date'] and
                           datetime.datetime.fromisoformat(
                               r['date'].replace('Z', '+00:00')).date() == current_date.date()]
            day_revenue = sum(r['price'] for r in day_records)

            # Расходы по дням (распределяем пропорционально выручке)
            if total_revenue > 0:
                day_expenses = total_expenses * (day_revenue / total_revenue)
            else:
                day_expenses = 0

            day_profit = day_revenue - day_expenses

            chart_labels.append(current_date.strftime('%d.%m'))

            if report_type == 'revenue':
                chart_values.append(day_revenue)
            elif report_type == 'expenses':
                chart_values.append(day_expenses)
            else:  # profit
                chart_values.append(day_profit)

            current_date += datetime.timedelta(days=1)

    elif period == 'year':
        # Для года - разбиваем по месяцам
        for month in range(1, 13):
            month_date = base_date.replace(month=month, day=1)
            next_month = month_date.replace(day=28) + datetime.timedelta(days=4)
            month_end = next_month - datetime.timedelta(days=next_month.day)
            month_end = month_end.replace(hour=23, minute=59, second=59, microsecond=999999)

            month_records = [r for r in records_data if r['date'] and
                             month_date <= datetime.datetime.fromisoformat(
                r['date'].replace('Z', '+00:00')) <= month_end]
            month_revenue = sum(r['price'] for r in month_records)

            # Расходы по месяцам (распределяем пропорционально выручке)
            if total_revenue > 0:
                month_expenses = total_expenses * (month_revenue / total_revenue)
            else:
                month_expenses = 0

            month_profit = month_revenue - month_expenses

            chart_labels.append(month_date.strftime('%B'))

            if report_type == 'revenue':
                chart_values.append(month_revenue)
            elif report_type == 'expenses':
                chart_values.append(month_expenses)
            else:  # profit
                chart_values.append(month_profit)

    response_data['chartData'] = {
        'labels': chart_labels,
        'values': chart_values
    }

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(debug=True)