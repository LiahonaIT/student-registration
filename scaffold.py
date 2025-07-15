# Student Registration App Scaffold
# Directory structure and stubbed file contents for a Flask-based registration app

registration_app/
├── app.py             # Main application
├── config.py          # Configuration (DB URI, SECRET_KEY)
├── models.py          # SQLAlchemy models
├── forms.py           # WTForms definitions
├── registration.py    # Registration blueprint (routes and logic)
├── admin.py           # Admin interface blueprint
├── auth.py            # Authentication blueprint
├── requirements.txt   # Python dependencies
├── static/            # Static assets
│   ├── css/
│   │   └── style.css  # Global styles
│   └── js/
│       └── signature_pad_setup.js  # Signature Pad integration
└── templates/         # Jinja2 templates
    ├── base.html
    ├── registration.html
    ├── success.html
    ├── admin.html
    └── login.html

# ---------------------------
# app.py (entrypoint)
# ---------------------------
from flask import Flask
from config import Config
from models import db
from registration import registration_bp
from admin import admin_bp
from auth import auth_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(registration_bp, url_prefix='/register')
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    app.run(debug=True)

# ---------------------------
# config.py
# ---------------------------
import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///registration.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SIGNATURE_UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'signatures')

# ---------------------------
# models.py
# ---------------------------
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    # TODO: add additional fields per Student Info doc

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    relationship = db.Column(db.String(32))
    # TODO: add remaining fields matching contacts-text.xlsx headers

class Signature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    sig_type = db.Column(db.String(32))  # "media_release" or "field_trip"
    image_path = db.Column(db.String(128))

# ---------------------------
# forms.py
# ---------------------------
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, FileField, HiddenField
from wtforms.validators import DataRequired

class StudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    # TODO: add all student info fields (grade, DOB, address, etc.)

class ContactForm(FlaskForm):
    relationship = SelectField('Relationship', choices=[('mother','Mother'),('father','Father'),('guardian','Guardian')])
    name = StringField('Full Name', validators=[DataRequired()])
    # TODO: add email, phone, address, and flags

class SignatureForm(FlaskForm):
    name = StringField('Printed Name', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    signature = HiddenField('Signature Data', validators=[DataRequired()])

# ---------------------------
# registration.py
# ---------------------------
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Student, Contact, Signature
from forms import StudentForm, ContactForm, SignatureForm
import base64, os
from config import Config

registration_bp = Blueprint('registration', __name__, template_folder='templates')

@registration_bp.route('/', methods=['GET','POST'])
def register():
    student_form = StudentForm(prefix='student')
    contact_forms = [ContactForm(prefix=f'contact-{i}') for i in range(1,4)]  # 3 contacts
    media_form = SignatureForm(prefix='media')
    waiver_form = SignatureForm(prefix='waiver')

    if request.method == 'POST':
        # Populate and validate
        valid = student_form.validate_on_submit() and all(cf.validate() for cf in contact_forms)
        valid = valid and media_form.validate() and waiver_form.validate()
        if valid:
            # Save student
            student = Student(
                first_name=student_form.first_name.data,
                last_name=student_form.last_name.data,
                # ... other fields
            )
            db.session.add(student)
            db.session.commit()

            # Save contacts
            for cf in contact_forms:
                if cf.name.data:
                    contact = Contact(
                        student_id=student.id,
                        relationship=cf.relationship.data,
                        # ... other cf fields
                    )
                    db.session.add(contact)

            # Save signatures
            for sig_type, sf in [('media_release', media_form), ('field_trip', waiver_form)]:
                sig_data = sf.signature.data
                header, encoded = sig_data.split(',',1)
                img_data = base64.b64decode(encoded)
                os.makedirs(Config.SIGNATURE_UPLOAD_FOLDER, exist_ok=True)
                filename = f"{sig_type}_{student.id}.png"
                path = os.path.join(Config.SIGNATURE_UPLOAD_FOLDER, filename)
                with open(path, 'wb') as img_file:
                    img_file.write(img_data)
                sig = Signature(student_id=student.id, sig_type=sig_type, image_path=path)
                db.session.add(sig)

            db.session.commit()
            flash('Registration submitted!', 'success')
            return redirect(url_for('registration.success'))
        else:
            flash('Please correct the errors and submit again.', 'danger')

    return render_template('registration.html',
                           student_form=student_form,
                           contact_forms=contact_forms,
                           media_form=media_form,
                           waiver_form=waiver_form)

@registration_bp.route('/success')
def success():
    return render_template('success.html')

# ---------------------------
# requirements.txt
# ---------------------------
Flask
Flask-WTF
Flask-SQLAlchemy
gunicorn
signature-pad

# ---------------------------
# templates/base.html
# ---------------------------
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{ title or 'Registration' }}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
  <nav>...</nav>
  <div class="container">
    {% block content %}{% endblock %}
  </div>
  <script src="{{ url_for('static', filename='js/signature_pad_setup.js') }}"></script>
</body>
</html>
