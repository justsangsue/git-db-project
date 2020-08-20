from flask import Flask, flash, redirect, render_template, request, url_for
from flask import session
from datetime import datetime
from database import Database as db
from logging import debug
import forms
from flask_bootstrap import Bootstrap
from flask_table import Table, Col, LinkCol
 
app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'DontTellAnyone'
app.config['WTF_CSRF_ENABLED'] = False

@app.route('/', methods=['GET', 'POST'])

# Search Vehicle
class SearchVehicleResult(Table):
    vehicle_vin = Col('VIN')
    vehicle_type_name = Col('Vehicle Type')
    model_year = Col('Model Year')
    manufacturer_name = Col('Manufacturer')
    model_name = Col('Model')
    color_list = Col('Color')
    mileage = Col('Mileage')
    cost_price = Col('Price')
    view_vehicle_detail = LinkCol('View Details', 'view_vehicle_detail', url_kwargs=dict(vin='vehicle_vin'))
    
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = forms.SearchVehicleForm(request.form)
    if form.validate_on_submit():
        if session:
            rc = db.search_vehicle(form.vin.data, form.model_year.data, form.vehicle_type_name.data, form.manufacturer.data, form.colors.data, form.keyword.data, internal=True)
        else:
            rc = db.search_vehicle(form.vin.data, form.model_year.data, form.vehicle_type_name.data, form.manufacturer.data, form.colors.data, form.keyword.data)
        print('rc', rc)
        table = SearchVehicleResult(rc)
        table.border = True
        return render_template('search_vehicle_result.html', table=table)
    return render_template('home.html', form=form, content_type='application/json')

@app.route('/<vin>', methods=['GET'])
def view_vehicle_detail(vin):
    res = db.view_vehicle_detail(vin)
    print('res', res)
    return render_template('vehicle_details.html', result=res, content_type='application/json')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')

@app.route('/getuser', methods=['GET', 'POST'])
def getuser():
    username = request.args.get('username')
    password = request.args.get('password')
    user = db.getUser(username,password)
    if not user:
        return render_template('login.html',inValidUser = True)
    else:
        session['username'] = username
        session['firstname'] = user.get('firstname')
        session['saleperson'] = user.get('saleperson')
        session['clerk'] = user.get('clerk')
        session['manager'] = user.get('manager')
        return redirect(url_for('home'))

@app.route('/addrepair',methods=['GET', 'POST'])
def add_repair():
    form = forms.AddRepairForm(request.form)
    form.vendor_name.choices = [(i, i) for i in db.get_vendors()] + [('add','add new Vendor')]
    message = None
    success = None
    if form.validate_on_submit():
        if form.start_date.data > form.end_date.data:
            message = 'Invalid entry'
        elif db.check_repair(form.vin.data,form.start_date.data.strftime('%Y-%m-%d'),form.end_date.data.strftime('%Y-%m-%d')):
            message = "Date overlapping"
        else:
            success = db.add_repair(form.vin.data, form.start_date.data.strftime('%Y-%m-%d'), form.end_date.data.strftime('%Y-%m-%d'),form.description.data,form.cost.data,form.vendor_name.data)
            if not success:
                message = 'Invalid entry'
            else:
                message = 'User Added'
    return render_template('add_repair.html',message = message, success = success, form=form, content_type='application/json')

@app.route('/addvendor', methods=['GET', 'POST'])
def add_vendor():
    vendorname =  request.form['vendorname']
    phone = request.form['phone']
    street =  request.form['street']
    city = request.form['city']
    zipcode =  request.form['zipcode']
    state = request.form['state']
    if request.method == 'POST':
        db.add_vendor(vendorname,phone,street,city,zipcode,state)
        return vendorname

@app.route('/addrecall', methods=['GET', 'POST'])
def add_recall():
    result = db.get_manufacturer()
    add_recall_form = forms.AddRecallForm(request.form)
    add_manufacturer_form = forms.AddManufacturer(request.form)
    if result:
        add_recall_form.manufacturer.choices = [(i, i) for i in result]
    if add_recall_form.validate_on_submit():
        rc = db.add_recall(add_recall_form.nhtsa.data, add_recall_form.manufacturer.data, add_recall_form.description.data)
        flash(rc)
        return redirect(url_for('add_recall'))
    if add_manufacturer_form.validate_on_submit():
        rc = db.add_manufacturer(add_manufacturer_form.manufacturer.data)
        flash(rc)
        return redirect(url_for('add_recall'))

    return render_template('add_recall.html',
        add_recall_form=add_recall_form,
        add_manufacturer_form=add_manufacturer_form,
        content_type='application/json')

@app.route('/addvehicle', methods=['GET', 'POST'])
def add_vehicle():
    form = forms.AddVehicleForm(request.form)
    username_result = db.get_inventory_clerk()
    vehicle_type_result = db.get_vehicle_type()
    manufacturer_result = db.get_manufacturer()
    form.username.choices = [(i, i) for i in username_result]
    form.vehicle_type_name.choices = [(i, i) for i in vehicle_type_result]
    form.manufacturer.choices = [(i, i) for i in manufacturer_result]
    form.colors.choices = [(i, i) for i in ('Aluminum', 'Beige', 'Black', 'Blue', 'Brown', 'Bronze', 'Claret', 'Copper', 'Cream', 'Gold', 'Gray', 'Green',
                           'Maroon', 'Metallic', 'Navy', 'Orange', 'Pink', 'Purple', 'Red', 'Rose', 'Rust', 'Silver', 'Tan', 'Turquoise',
                           'White', 'Yellow')]
    if form.validate_on_submit():
        rc = db.add_vehicle(form.vin.data, form.model_name.data, form.model_year.data, form.cost_price.data, form.invent_start_dt.data,
                        form.car_condition.data, form.mileage.data, form.description.data, form.username.data, form.customerID.data, 
                        form.vehicle_type_name.data, form.manufacturer.data, form.colors.data)
        flash(rc)
        return redirect(url_for('add_vehicle'))
    return render_template('add_vehicle.html', form=form, content_type='application/json')

@app.route('/report')
def report_homepage():
    return render_template('report_homepage.html', content_type='application/json')

@app.route('/report/seller_history')
def seller_history_report():
    def db_query():
        seller_history_report = db.seller_history_report()
        return seller_history_report
    res = db_query()
    return render_template('seller_history.html', result=res, content_type='application/json')

@app.route('/report/inventory_age')
def inventory_age_report():
    res = db.inventory_age_report()
    return render_template('inventory_age.html', result=res, content_type='application/json')

@app.route('/report/average_inventory')
def average_inventory_report():
    res = db.average_inventory_report()
    return render_template('average_inventory.html', result=res, content_type='application/json')

@app.route('/report/price_condition')
def price_condition_report():
    def db_query():
        price_per_condition_report = db.price_per_condition()
        return price_per_condition_report
    res = db_query()
    return render_template('price_condition.html', result=res, content_type='application/json')

@app.route('/report/repair_statistics')
def repair_statistics_report():
    def db_query():
        repair_statistics_report = db.repair_statistics()
        return repair_statistics_report
    res = db_query()
    return render_template('repair_statistics.html', result=res, content_type='application/json')

@app.route('/report/monthly_sales')
def monthly_sales_report():
    def db_query():
        monthly_sales_report = db.monthly_sales()
        return monthly_sales_report
    res = db_query()
    return render_template('monthly_sales.html', result=res, content_type='application/json')

@app.route('/report/monthly_sales_rank/<year>/<month>')
def monthly_sales_rank(year, month):
    def db_query(year, month):
        monthly_sales_rank = db.monthly_sales_rank(year, month)
        return monthly_sales_rank
    res = db_query(year, month)
    return render_template('monthly_sales_rank.html', result=res, year = year, month = month, content_type='application/json')

@app.route('/report/yearly_sales_rank/<year>')
def yearly_sales_rank(year):
    def db_query(year):
        yearly_sales_rank = db.yearly_sales_rank(year)
        return yearly_sales_rank
    res = db_query(year)
    return render_template('yearly_sales_rank.html', result=res, year = year, content_type='application/json')

@app.route('/recordsales', methods=['GET', 'POST'])
def record_sales():
    session['vin'] = "036JZFZ8I3K433701"
    search_customer_form = forms.SearchCustomerForm(request.form)
    msg, sales_price = db.calculate_sales_price(session['vin'])
    if msg == "Record found":
        session['sales_price'] = sales_price
    record_sales_form = forms.RecordSalesForm(request.form)
    if "search_customer_button" in request.form and search_customer_form.validate_on_submit():
        msg, result = db.get_customer(
            search_customer_form.customer_type.data,
            search_customer_form.identification_num.data)
        flash(msg)
        if result:
            session['customerID'] = result['customerID']
            session['customerName'] = result['customer_name']
        return redirect(url_for('record_sales'))

    if "record_sales_button" in request.form \
        and record_sales_form.validate_on_submit():
        if session['customerID'] and session['sales_price'] \
        and session['username'] and session['vin']:
            msg = db.record_sales(
                session['customerID'],
                session['username'],
                session['vin'],
                session['sales_price'],
                record_sales_form.sales_date.data)
            flash(msg)
        else:
            flash('Please search for customer first')
        return redirect(url_for('record_sales'))

    return render_template('record_sales.html',
        search_customer_form=search_customer_form,
        record_sales_form=record_sales_form,
        content_type='application/json')

@app.route('/addcustomer', methods=['GET', 'POST'])
def add_customer():
    add_individual_form = forms.AddIndividualForm(request.form)
    add_business_form = forms.AddBusinessForm(request.form)
    if "add_individual_customer_button" in request.form \
        and add_individual_form.validate_on_submit():
        msg, result = db.add_individual_customer(
            add_individual_form.customer_form.email.data,
            add_individual_form.customer_form.phone_num.data,
            add_individual_form.customer_form.street.data,
            add_individual_form.customer_form.city.data,
            add_individual_form.customer_form.state.data,
            add_individual_form.customer_form.zip_code.data,
            add_individual_form.driver_license_num.data,
            add_individual_form.first_name.data,
            add_individual_form.last_name.data)
        flash(msg)
        if result:
            session['customerID'] = result['customerID']
            session['customerName'] = result['customer_name']
        return redirect(url_for('add_customer'))

    if "add_business_customer_button" in request.form \
        and add_business_form.validate_on_submit():
        msg, result = db.add_business_customer(
            add_business_form.customer_form.email.data,
            add_business_form.customer_form.phone_num.data,
            add_business_form.customer_form.street.data,
            add_business_form.customer_form.city.data,
            add_business_form.customer_form.state.data,
            add_business_form.customer_form.zip_code.data,
            add_business_form.tin.data,
            add_business_form.company_name.data,
            add_business_form.primary_contact.data,
            add_business_form.primary_contact_title.data)
        flash(msg)
        if result:
            session['customerID'] = result['customerID']
            session['customerName'] = result['customer_name']
        return redirect(url_for('add_customer'))

    return render_template('add_customer.html',
        add_individual_form=add_individual_form,
        add_business_form=add_business_form,
        content_type='application/json')

#tobe deleted
@app.route('/customers')
def customers():

    def db_query():
        customers = db.list_customers()

        return customers

    res = db_query()

    return render_template('customers.html', result=res, content_typeSET='application/json')

if __name__ == '__main__':
    app.run(debug=True)
