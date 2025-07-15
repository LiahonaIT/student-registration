# forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    BooleanField,
    FileField,
    DateField,
    TextAreaField,
)

# forms.py
from wtforms import RadioField

from flask_wtf import FlaskForm
from wtforms import (
    HiddenField, SelectField, StringField, BooleanField,
    DateField, FileField, TextAreaField, EmailField
)
from wtforms.validators import DataRequired, Optional, Email
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import Optional

from wtforms import SelectMultipleField, widgets, ValidationError

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

def min_two(form, field):
    if len(field.data) < 2:
        raise ValidationError("Please choose at least two committees.")

class StudentForm(FlaskForm):
    school = SelectField(
        'School',
        choices=[('HS', 'High School/Jr. High'),
                 ('ES', 'Elementary'),
],
        validators=[DataRequired()]
    )
    first_name = StringField('First Name', validators=[DataRequired()])
    preferred_name = StringField('Preferred Name', validators=[Optional()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    grade_level = SelectField(
        'Grade Level',
        choices=[('Pre-K', 'Pre-K')] + [(str(i), str(i)) for i in range(0,13)],
        validators=[DataRequired()]
    )
    immunization_record = FileField(
        'Upload Immunization Record (JPEG, PNG or PDF; max 5 MB)',
        validators=[
            Optional(),
            FileAllowed(['jpg','jpeg','png','pdf'],
                        'Only images or PDFs are allowed')
        ]
    )
    primary_phone = StringField('Primary Home Phone', validators=[DataRequired()])
    gender = SelectField(
        'Gender',
        choices=[('Male','Male'),('Female','Female')],
        validators=[DataRequired()]
    )
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    address_street = StringField('Street Address', validators=[DataRequired()])
    address_city   = StringField('City',           validators=[DataRequired()])
    address_state  = StringField('State',          validators=[DataRequired()])
    address_zip    = StringField('ZIP Code',       validators=[DataRequired()])
    has_iep        = BooleanField('Has IEP')
    iep_details  = TextAreaField(
        "IEP Details (if applicable)",
        validators=[Optional()],
        render_kw={"rows": 3, "placeholder": "Accommodations, goals, etc."}
    )
    has_504        = BooleanField('Has 504 Plan')
    plan504_details = TextAreaField(
        "504 Plan Details (if applicable)",
        validators=[Optional()],
        render_kw={"rows": 3, "placeholder": "Accommodations, goals, etc."}
    )
    transferring   = SelectField(
        'Transferring from another school?',
        choices=[('No','No'),('Yes','Yes')],
        validators=[DataRequired()]
    )
    prev_school_name    = StringField('Previous School Name',    validators=[Optional()])
    prev_school_address = StringField('Previous School Address', validators=[Optional()])
    otc_permission = RadioField(
    'Permission to administer OTC (Over-the-Counter) medications such as aspirin, ibuprofen, etc.',
    choices=[('Yes','Yes'), ('No','No')],
    validators=[DataRequired(message="Please select Yes or No")],
    coerce=str
)

    authorized_pickups  = TextAreaField(
       'List the people who you authorize to check out this student (one name per line)',
       description="You will be entering emergency & family contacts below. This is just for people you authorize to pick up/checkout your student.",
       validators=[Optional()],
       render_kw={"rows": 3, "placeholder": "Jane Doe\nJohn Smith\n…"}
   )
    guardian_relationship_status = TextAreaField(
        "Parent/Guardian Relationship Status",
        validators=[Optional()],
        render_kw={
          "rows": 3,
          "placeholder": "e.g. Parents are divorced; mother has primary custody; no-contact order for John Doe"
        }
    )
    health_issues   = TextAreaField('Health Alerts for this Student: Please describe any conditions that the staff should be aware of. (Allergies, mental, etc.)',validators=[Optional()])
    immunizations_current = SelectField(
        'Immunizations up-to-date?',
        choices=[('No','No'),('Yes','Yes')],
        validators=[DataRequired()]
    )
    immunization_record = FileField('Upload Immunization Record (5 MB Limit - PDFs and Image files allowed)', validators=[Optional()])

    volunteer_committees = MultiCheckboxField(
        'Parent Volunteer Committees',
        choices=[
            ('service_students','Service committee to help Liahona students perform service'),
            ('service_improvement','Service committee for school improvement (grounds, leaves)'),
            ('valentine','Valentine-O-Gram'),
            ('prom','Liahona Prom Committee'),
            ('graduation','Graduation Committee'),
            ('holiday','Holiday Committee (decorations, treats, etc)'),
            ('dance','Dance Committee'),
            ('youth_conf','Youth Conference (carpool, service project)'),
            ('elementary','Elementary Classes'),
            ('warriors_waffles','Warriors and Waffles'),
            ('lead_committee','I’m interested in Leading a committee')
        ],
        validators=[min_two],
    )



class ContactForm(FlaskForm):
    # hidden from the user, but needed to round-trip IDs
    contact_id               = HiddenField()

    # 1. Priority & Relationship (keep these)
    #priority      = SelectField("Priority",
    #                  choices=[('1','1'),('2','2'),('3','3'),('4','4')],
    #                  validators=[Optional()])
    relationship  = SelectField("Relationship",
                      choices=[('Mother','Mother'),('Father','Father'),
                               ('Guardian','Guardian'),('Other','Other')],
                      validators=[Optional()])

    # 2. Name
    first_name    = StringField("First Name", validators=[DataRequired()])
    last_name     = StringField("Last Name",  validators=[DataRequired()])

    # 3. Gender & State Contact #
    gender               = SelectField("Gender",
                            choices=[("Male","Male"),("Female","Female"),("Other","Other")],
                            validators=[Optional()])
    state_contact_number = StringField("State Contact Number", validators=[Optional()])

    # 4. Email
    email_address = EmailField("Email Address", validators=[Optional(), Email()])

    # 5. Phone → split into two fields
    mobile_phone = StringField("Mobile Phone Number", validators=[Optional()])
    home_phone   = StringField("Home/Alternate Phone Number", validators=[Optional()])

    # 6. Address
    street            = StringField("Street Address", validators=[Optional()])
    line_two          = StringField("Address Line 2", validators=[Optional()])
    unit              = StringField("Unit", validators=[Optional()])
    city              = StringField("City", validators=[Optional()])
    state             = StringField("State", validators=[Optional()])
    postal_code       = StringField("ZIP Code", validators=[Optional()])
    geocode_latitude  = StringField("Latitude", validators=[Optional()])
    geocode_longitude = StringField("Longitude", validators=[Optional()])
    address_type      = SelectField("Address Type",
                         choices=[("Home","Home"),("Work","Work")],
                         validators=[Optional()])

    # 7. Relationship flags
    has_custody       = BooleanField("Has Custody")
    lives_with        = BooleanField("Lives with Student")
    can_pickup        = BooleanField("Can pick up Student")
    receives_mail     = BooleanField("Receives Mailings")
    emergency_contact = BooleanField("Is Emergency Contact")


class MediaReleaseForm(FlaskForm):

    signature = StringField(
        'Type your full name here (this will serve as your signature)',
        validators=[DataRequired()],
    )
    agree     = BooleanField(
        "I hereby acknowledge that typing my name above constitutes my electronic signature.",
        validators=[DataRequired(message="You must acknowledge your electronic signature.")],
    )

class WaiverForm(FlaskForm):


    signature = StringField(
        'Type your full name here (this will serve as your signature)',
        validators=[DataRequired()],
    )
    agree     = BooleanField(
        "I hereby acknowledge that typing my name above constitutes my electronic signature.",
        validators=[DataRequired(message="You must acknowledge your electronic signature.")],
    )

from wtforms import PasswordField, SubmitField
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit   = SubmitField('Log In')
