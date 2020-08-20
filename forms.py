from flask_wtf import FlaskForm
from wtforms import validators, BooleanField, StringField, PasswordField, SubmitField, SelectField, DecimalField, DateField, IntegerField, SelectMultipleField, FormField
from wtforms.validators import DataRequired
from wtforms.widgets import ListWidget, CheckboxInput
from database import Database as db
from datetime import datetime, date

states_list = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL',
          'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
          'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH',
          'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
          'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI',
          'WY', 'AS', 'GU', 'MH', 'FM', 'MP', 'PW', 'PR', 'VI']
customer_type_list = ['Individual', 'Business']
color_list = ['Aluminum', 'Beige', 'Black', 'Blue', 'Brown', 'Bronze',
              'Claret', 'Copper', 'Cream', 'Gold', 'Gray', 'Green',
              'Maroon', 'Metallic', 'Navy', 'Orange', 'Pink', 'Purple',
              'Red', 'Rose', 'Rust', 'Silver', 'Tan', 'Turquoise', 'White', 'Yellow']
manufacturer_name = ['Acura', 'Alfa Romeo', 'Aston Martin', 'Audi', 'Bentley',
                     'BMW', 'Buick', 'Cadillac', 'Chevrolet', 'Chrysler', 'Dodge',
                     'Ferrari', 'FIAT', 'Ford', 'Freightliner', 'Genesis', 'GMC',
                     'Honda', 'Hyundai', 'INFINITI', 'Jaguar', 'Jeep', 'Kia', 'Lamborghini',
                     'Land Rover', 'Lexus', 'Lincoln', 'Lotus', 'Maserati', 'MAZDA',
                     'McLaren', 'Mercedes-Benz', 'MINI', 'Mitsubishi', 'Nissan', 'Porsche',
                     'Ram', 'Rolls-Royce', 'smart', 'Subaru', 'Tesla', 'Toyota', 'Volkswagen', 'Volvo']


class AddRecallForm(FlaskForm):
    nhtsa = StringField('NHTSA', [DataRequired(), validators.Length(max=250)])
    manufacturer = SelectField(
        label='Manufacturer',
        choices=[(i, i) for i in manufacturer_name],
        validators=[DataRequired(), validators.Length(max=250)])
    description = StringField('Description', [validators.Length(max=250)])
    add_recall_button = SubmitField('Add Recall')

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class SearchVehicleForm(FlaskForm):
    current_year = int(datetime.now().year)
    vin = StringField('VIN', [validators.Length(max=17, message="Not a valid VIN")])
    vehicle_type_result = db.get_vehicle_type()
    manufacturer_result = db.get_manufacturer()
    model_year = SelectField(
        label='Model Year', 
        choices=[('', 'Any')] + [(str(i), str(i)) for i in range(1800, current_year + 2)])
    vehicle_type_name = SelectField(
        label='Vehicle Type', 
        choices=[('', 'Any')] + [(i, i) for i in vehicle_type_result])
    manufacturer = SelectField(
        label='Manufacturer',
        choices=[('', 'Any')] + [(i, i) for i in manufacturer_result])
    colors = SelectField('Color', choices=[('', 'Any')] + [(i, i) for i in color_list])
    keyword = StringField('Keyword', [validators.Length(max=250)])
    submit_button = SubmitField('Search Vehicle')

class AddVehicleForm(FlaskForm):
    current_year = int(datetime.now().year)
    vin = StringField('VIN', [DataRequired(), validators.Length(min=11, max=17, message="Not a valid VIN")])
    model_name = StringField('Model', [DataRequired(), validators.Length(max=250)])
    model_year = SelectField(
        label='Model Year', 
        choices=[(str(i), str(i)) for i in range(1800, current_year + 2)],
        validators=[DataRequired()])
    cost_price = DecimalField(
        label='Cost Price', 
        places=2, 
        validators=[DataRequired('Not a valid input')])
    invent_start_dt = DateField('Start Date', format="%m/%d/%Y")
    car_condition = SelectField(
        label='Condition', 
        choices=[(i, i) for i in ('Excellent', 'Very Good', 'Good', 'Fair')],
        validators=[DataRequired()])
    mileage = IntegerField('Mileage', default=0)
    description = StringField('Description', [validators.Length(max=250)])
    username = SelectField(
        label='Username', 
        choices=[],
        validators=[DataRequired()])
    customerID = StringField('Customer ID', [DataRequired(), validators.Length(max=250)])
    vehicle_type_name = SelectField(
        label='Vehicle Type', 
        choices=[],
        validators=[DataRequired()])
    manufacturer = SelectField(
        label='Manufacturer',
        choices=[],
        validators=[DataRequired()])
    colors = MultiCheckboxField(
        label='Color(s)',
        choices=[],
        validators=[DataRequired()]
    )
    submit_button = SubmitField('Add Vehicle')

class AddManufacturer(FlaskForm):
    manufacturer = StringField('Manufacturer Name', [DataRequired(), validators.Length(max=250)])
    add_manufacturer_button = SubmitField('Add Manufacturer')

class AddVehicleType(FlaskForm):
    vehicle_type = StringField('Vehicle Type', [DataRequired(), validators.Length(max=250)])
    add_vehicle_type_button = SubmitField('Add Vehicle Type')

class AddCustomerForm(FlaskForm):
    email = StringField('Email', [validators.Length(max=250), validators.Email(message=('Invalid email address.'))])
    phone_num = StringField('Phone', [DataRequired(), validators.Length(max=32)])
    street = StringField('Street', [DataRequired(), validators.Length(max=250)])
    city = StringField('City', [DataRequired(), validators.Length(max=250)])
    state = SelectField(
        label='State',
        choices=[(i, i) for i in states_list],
        validators=[DataRequired()])
    zip_code = StringField('Zip Code', [DataRequired(), validators.Length(max=60)])

class AddIndividualForm(FlaskForm):
    driver_license_num = StringField("Driver's License Number", [DataRequired(), validators.Length(max=100)])
    first_name = StringField('First Name', [DataRequired(), validators.Length(max=100)])
    last_name = StringField('Last Name', [DataRequired(), validators.Length(max=100)])
    customer_form = FormField(AddCustomerForm, label='')
    add_individual_customer_button = SubmitField('Add Individual Customer')

class AddBusinessForm(FlaskForm):
    tin = StringField('Tax Identification Number', [DataRequired(), validators.Length(max=100)])
    company_name = StringField('Company Name', [DataRequired(), validators.Length(max=250)])
    primary_contact = StringField('Primary Contact', [DataRequired(), validators.Length(max=250)])
    primary_contact_title = StringField('Primary Contact Title', [DataRequired(), validators.Length(max=100)])
    customer_form = FormField(AddCustomerForm, label='')
    add_business_customer_button = SubmitField('Add Business Customer')

class SearchCustomerForm(FlaskForm):
    customer_type = SelectField(
        label='Customer Type',
        id='customer_type',
        choices=[(i, i) for i in customer_type_list],
        validators=[DataRequired()])
    identification_num = StringField(
        label='Identification Number',
        description="* For Individual, please enter driver's license. For Business, please enter tax identification number.", 
        validators=[DataRequired(), validators.Length(max=100)])
    search_customer_button = SubmitField('Search Customer')

class RecordSalesForm(FlaskForm):
    # option_widget=search, 
    # customerID = IntegerField('Customer ID', validators=[DataRequired("Please enter an Integer"), validators.NumberRange(min=0)])
    # sales_price = DecimalField(label='Sales Price', places=2, validators=[DataRequired()])
    sales_date = DateField('Sales Date', default=date.today(), format='%Y-%m-%d', validators=[DataRequired("Follow the format: YYYY-MM-DD")])
    record_sales_button = SubmitField('Record Sales')
    submit_button = SubmitField('Add Recall')

class AddRepairForm(FlaskForm):
    vin = StringField('Enter VIN number', [validators.Length(max=250)])
    start_date = DateField('Start Date', format="%m/%d/%Y")
    end_date =  DateField('End Date', format="%m/%d/%Y")
    description = StringField('Description', [validators.Length(max=250)])
    cost = IntegerField('Cost')
    vendor_name = SelectField(
        label='Vendor Name')
    submit_button = SubmitField('Add Repair')

