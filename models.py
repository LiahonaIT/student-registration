from extensions import db
from datetime import date


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    school = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    preferred_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64), nullable=False)
    grade_level = db.Column(db.String(10), nullable=False)
    primary_phone = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    enrollment_status = db.Column(db.String(10), nullable=True)
    address_street = db.Column(db.String(128), nullable=False)
    address_city = db.Column(db.String(64), nullable=False)
    address_state = db.Column(db.String(64), nullable=False)
    address_zip = db.Column(db.String(10), nullable=False)
    has_iep  = db.Column(db.Boolean, default=False)
    iep_details   = db.Column(db.Text)            # ← new
    has_504  = db.Column(db.Boolean, default=False)
    plan504_details = db.Column(db.Text)          # ← new
    transferring = db.Column(db.Boolean, default=False)
    prev_school_name = db.Column(db.String(128))
    prev_school_address = db.Column(db.String(256))
    health_issues = db.Column(db.Text)
    otc_permission = db.Column(db.Boolean, default=False)
    authorized_pickups    = db.Column(db.Text)   # ← new column
    immunizations_current = db.Column(db.Boolean, default=False)
    immunization_record = db.Column(db.String(256))
    media_pdf           = db.Column(db.String(200))
    waiver_pdf          = db.Column(db.String(200))
    volunteer_committees  = db.Column(db.String(512))   # comma-separated keys
    volunteer_assignments = db.Column(db.Text)           # JSON map key→name
    guardian_relationship_status = db.Column(db.Text)
    immunization_verified  = db.Column(db.Boolean, default=False, nullable=False)
    selection_token        = db.Column(db.String(36), nullable=True)
    token_used             = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    contacts = db.relationship('Contact', backref='student', lazy=True)
    signatures = db.relationship('Signature', backref='student', cascade='all, delete-orphan')

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    priority         = db.Column(db.String(2),   nullable=False)
    relationship     = db.Column(db.String(20))
    prefix           = db.Column(db.String(10))
    first_name       = db.Column(db.String(50))
    middle_name      = db.Column(db.String(50))   # ← Add this
    last_name        = db.Column(db.String(50))
    suffix           = db.Column(db.String(10))
    gender           = db.Column(db.String(10))
    employer         = db.Column(db.String(50))

    email            = db.Column(db.String(100))
    email_type       = db.Column(db.String(10))
    email_primary    = db.Column(db.Boolean, default=False)

    phone            = db.Column(db.String(20))
    phone_type       = db.Column(db.String(10))
    phone_primary    = db.Column(db.Boolean, default=False)

    address_street   = db.Column(db.String(100))
    address_city     = db.Column(db.String(50))
    address_state    = db.Column(db.String(20))
    address_zip      = db.Column(db.String(10))

    has_custody      = db.Column(db.Boolean, default=False)
    lives_with       = db.Column(db.Boolean, default=False)
    can_pickup       = db.Column(db.Boolean, default=False)
    receives_mail    = db.Column(db.Boolean, default=False)
    emergency_contact= db.Column(db.Boolean, default=False)

    

class Signature(db.Model):
    __tablename__ = 'signatures'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    sig_type = db.Column(db.String(32))  # 'media_release' or 'field_trip'
    image_path = db.Column(db.String(256))
