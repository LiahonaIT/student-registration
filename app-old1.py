from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SECRET_KEY'] = 'your-secret-key'
ADMIN_PASSWORD = 'change-this-password'

db = SQLAlchemy(app)

# Define the database model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    first_name = db.Column(db.String(100))
    preferred_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    grade_level = db.Column(db.String(20))
    home_phone = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    dob = db.Column(db.String(20))
    enrollment_type = db.Column(db.String(20))
    address = db.Column(db.String(200))
    iep_504 = db.Column(db.String(10))
    transferring_school = db.Column(db.String(100))
    transferring_address = db.Column(db.String(200))
    health_issues = db.Column(db.Text)
    otc_permission = db.Column(db.Text)
    immunizations = db.Column(db.String(10))
    emergency_contact = db.Column(db.Text)
    media_release = db.Column(db.String(10))
    field_trip_release = db.Column(db.String(10))
    email = db.Column(db.String(100))

@app.route('/')
def index():
    saved_email = session.get('saved_email', '')
    return render_template('form.html', saved_email=saved_email)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    student = Student(**data)
    db.session.add(student)
    db.session.commit()
    flash('Submission successful!')
    session.pop('saved_email', None)
    return redirect(url_for('index'))

@app.route('/save_progress', methods=['POST'])
def save_progress():
    email = request.form.get('email')
    session['saved_email'] = email
    flash('Progress saved. You can resume by returning to the form.')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Incorrect password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out.')
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    students = Student.query.order_by(Student.timestamp.desc()).all()
    return render_template('admin.html', students=students)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        for key, value in request.form.items():
            setattr(student, key, value)
        db.session.commit()
        flash('Student info updated.')
        return redirect(url_for('admin'))
    return render_template('edit.html', student=student)

@app.route('/export')
def export():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    students = Student.query.all()
    filename = 'student_export.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([column.name for column in Student.__table__.columns])
        for s in students:
            writer.writerow([getattr(s, column.name) for column in Student.__table__.columns])
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
