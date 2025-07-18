import os
import json
from pathlib import Path
from datetime import date

from flask import (
    Blueprint, render_template, redirect,
    url_for, request, flash
)
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit, ImageReader
from reportlab.pdfgen import canvas

from extensions import db
from models import Student, Contact
from forms import (
    StudentForm, ContactForm,
    MediaReleaseForm, WaiverForm
)

registration_bp = Blueprint('registration', __name__, url_prefix='/register')

BASE_DIR      = Path(__file__).parent.resolve()
UPLOAD_FOLDER = BASE_DIR / 'uploads'
PDF_FOLDER    = BASE_DIR / 'generated_pdfs'

UPLOAD_FOLDER.mkdir(exist_ok=True)
PDF_FOLDER.mkdir(exist_ok=True)


def generate_media_pdf(student, media_form):
    out_fname = f"{student.id}_media_release.pdf"
    out_path  = PDF_FOLDER / out_fname
    logo_path = BASE_DIR / 'assets' / 'liahonalogo.png'

    c = canvas.Canvas(str(out_path), pagesize=letter)
    page_w, page_h = letter

    # Logo (1" high)
    reader   = ImageReader(str(logo_path))
    img_w, img_h = reader.getSize()
    max_h    = 72
    aspect   = img_w / img_h
    draw_w   = max_h * aspect
    draw_h   = max_h
    x_logo   = (page_w - draw_w) / 2
    y_logo   = page_h - 40 - draw_h
    c.drawImage(str(logo_path), x_logo, y_logo,
                width=draw_w, height=draw_h, mask='auto')

    # Title
    title = "Media Release & Photo Consent"
    c.setFont("Helvetica-Bold", 18)
    tw = c.stringWidth(title, "Helvetica-Bold", 18)
    c.drawString((page_w - tw)/2, y_logo - 30, title)

    # Body text
    c.setFont("Helvetica", 10)
    body = (
        f"I give permission to Liahona Preparatory Academy to use the image or words "
        f"of my child, {student.first_name} {student.last_name}, in its promotional materials. "
        "I understand these materials may be presented in any format including paper, electronic, "
        "and all other media, social or otherwise. Neither my child nor I will receive any money "
        "or compensation in exchange for this permission. Liahona Preparatory Academy will own the "
        "copyright to these materials, and I waive on behalf of my child the right to sue for any "
        "use of my child(ren)’s image or words that is done in good faith by Liahona Preparatory Academy."
    )
    lines = simpleSplit(body, "Helvetica", 10, page_w - 80)
    y = y_logo - 60
    for line in lines:
        if y < 150:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = page_h - 40
        c.drawString(40, y, line)
        y -= 14

    # Footer with signature
    footer_y = y - 20
    c.setFont("Helvetica", 10)
    c.drawString(40, footer_y,
                 f"Student Name: {student.first_name} {student.last_name}")

    label   = "Parent/Guardian Signature: "
    c.drawString(40, footer_y - 25, label)
    c.setFont("Helvetica-BoldOblique", 16)
    c.drawString(40 + c.stringWidth(label, "Helvetica", 10),
                 footer_y - 25,
                 media_form.signature.data)

    # Date
    date_str = date.today().strftime("%Y-%m-%d")
    c.setFont("Helvetica", 10)
    c.drawString(40, footer_y - 50,
                 f"Date Signed: {date_str}")

    c.save()
    student.media_pdf = out_fname


def generate_waiver_pdf(student, waiver_form):
    out_fname = f"{student.id}_fieldtrip_waiver.pdf"
    out_path  = PDF_FOLDER / out_fname
    logo_path = BASE_DIR / 'assets' / 'liahonalogo.png'

    c = canvas.Canvas(str(out_path), pagesize=letter)
    page_w, page_h = letter

    # Logo centered
    reader   = ImageReader(str(logo_path))
    img_w, img_h = reader.getSize()
    max_h    = 72
    aspect   = img_w / img_h
    draw_w   = max_h * aspect
    draw_h   = max_h
    x_logo   = (page_w - draw_w) / 2
    y_logo   = page_h - 40 - draw_h
    c.drawImage(str(logo_path), x_logo, y_logo,
                width=draw_w, height=draw_h, mask='auto')

    # Title
    title = "Field Trip & Activity Waiver"
    c.setFont("Helvetica-Bold", 18)
    tw = c.stringWidth(title, "Helvetica-Bold", 18)
    c.drawString((page_w - tw)/2, y_logo - 30, title)

    # Body text
    c.setFont("Helvetica", 10)
    body = (
        f"I, the above named parent/guardian, grant permission for {student.first_name} {student.last_name} "
        "to participate in any school sponsored field trip or activity. I acknowledge that participation "
        "in this field trip or activity may involve moderate to strenuous physical activity and may cause "
        "physical or emotional distress to participants. There may also be associated health risks. I warrant "
        "that student is free from any known heart, respiratory or other health problems that could prevent student "
        "from safely participating in any of the activities. I certify that I have medical insurance or otherwise "
        "agree to be personally responsible for costs of any emergency or other medical care that the student receives. "
        "I agree to release Liahona Academy and their agencies, departments, owners, employees, agents, and all sponsors, "
        "officials and staff or volunteers from the cost of any medical care that the student receives as a result of participation. "
        "I further agree to release Liahona Academy, their owners, employees, sponsors, staff and volunteers from any and all "
        "liability and causes of actions whatsoever for any loss, claim, damage, injury, illness, attorney’s fees or harm of any kind. "
        "This release extends to any claim made by parents or guardians or their assigns arising from or in any way connected with the field trip. "
        "I agree to inform and explain to my child the safety procedures and precautions necessary to participate, and I also agree to explain to my child "
        "the importance of behaving and adhering to any and all instructions or rules of conduct given by the teacher or supervisor in charge."
    )
    lines = simpleSplit(body, "Helvetica", 10, page_w - 80)
    y = y_logo - 60
    for line in lines:
        if y < 150:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = page_h - 40
        c.drawString(40, y, line)
        y -= 14

    # Footer with signature
    footer_y = y - 20
    c.setFont("Helvetica", 10)
    c.drawString(40, footer_y,
                 f"Student Name: {student.first_name} {student.last_name}")

    label   = "Parent Signature: "
    c.drawString(40, footer_y - 25, label)
    c.setFont("Helvetica-BoldOblique", 16)
    c.drawString(40 + c.stringWidth(label, "Helvetica", 10),
                 footer_y - 25,
                 waiver_form.signature.data)

    # Date
    date_str = date.today().strftime("%Y-%m-%d")
    c.setFont("Helvetica", 10)
    c.drawString(40, footer_y - 50,
                 f"Date Signed: {date_str}")

    c.save()
    student.waiver_pdf = out_fname


@registration_bp.route('/', methods=['GET','POST'])
def register():
    student_form   = StudentForm()
    contact_form1  = ContactForm(prefix='c1')
    contact_form2  = ContactForm(prefix='c2')
    contact_form3  = ContactForm(prefix='c3')
    media_form     = MediaReleaseForm()
    waiver_form    = WaiverForm()

    # Contact #3: only Guardian/Other
    contact_form3.relationship.choices = [
        ('Guardian','Guardian'),
        ('Other',   'Other'),
    ]

    if (
        request.method == 'POST'
        and student_form.validate_on_submit()
        and contact_form1.validate()
        and contact_form2.validate()
        and contact_form3.validate()
        and media_form.validate()
        and waiver_form.validate()
    ):
        # — Build volunteer assignments dict —
        assignments_dict = {}
        for code, _label in student_form.volunteer_committees.choices:
            if code in (student_form.volunteer_committees.data or []):
                name = request.form.get(f"volunteer_name_{code}", "").strip()
                assignments_dict[code] = name

        # — Handle immunization upload —
        uploaded = student_form.immunization_record.data
        if uploaded:
            fname = secure_filename(uploaded.filename)
            uploaded.save(UPLOAD_FOLDER / fname)
            immunization_fname = fname
        else:
            immunization_fname = None

        # — Create Student record —
        student = Student(
            school                = student_form.school.data,
            first_name            = student_form.first_name.data,
            preferred_name        = student_form.preferred_name.data,
            last_name             = student_form.last_name.data,
            grade_level           = student_form.grade_level.data,
            primary_phone         = student_form.primary_phone.data,
            gender                = student_form.gender.data,
            date_of_birth         = student_form.date_of_birth.data,
            address_street        = student_form.address_street.data,
            address_city          = student_form.address_city.data,
            address_state         = student_form.address_state.data,
            address_zip           = student_form.address_zip.data,
            has_iep               = student_form.has_iep.data,
            iep_details           = student_form.iep_details.data,
            has_504               = student_form.has_504.data,
            plan504_details       = student_form.plan504_details.data,
            otc_permission        = (student_form.otc_permission.data == 'Yes'),
            authorized_pickups    = student_form.authorized_pickups.data,
            health_issues         = student_form.health_issues.data,
            immunizations_current = (student_form.immunizations_current.data == 'Yes'),
            immunization_record   = immunization_fname,
            transferring          = (student_form.transferring.data == 'Yes'),
            prev_school_name      = student_form.prev_school_name.data,
            prev_school_address   = student_form.prev_school_address.data,
            volunteer_committees  = ",".join(student_form.volunteer_committees.data or []),
            volunteer_assignments = json.dumps(assignments_dict),
            guardian_relationship_status = student_form.guardian_relationship_status.data
        )
        db.session.add(student)
        db.session.flush()  # now student.id is available

        # — Generate PDFs —
        generate_media_pdf(student, media_form)
        generate_waiver_pdf(student, waiver_form)

        # — Build and add 3 Contacts —
        def make_contact(cf, sid, priority):
            return Contact(
                student_id    = sid,
                priority      = str(priority),
                relationship  = cf.relationship.data,
                first_name    = cf.first_name.data,
                last_name     = cf.last_name.data,
                gender        = cf.gender.data or None,
                email         = cf.email_address.data or None,
                phone         = cf.mobile_phone.data or None,
                address_street= cf.street.data or None,
                address_city  = cf.city.data or None,
                address_state = cf.state.data or None,
                address_zip   = cf.postal_code.data or None,
                has_custody       = bool(cf.has_custody.data),
                lives_with        = bool(cf.lives_with.data),
                can_pickup        = bool(cf.can_pickup.data),
                receives_mail     = bool(cf.receives_mail.data),
                emergency_contact = bool(cf.emergency_contact.data)
            )

        contacts = [
            make_contact(contact_form1, student.id, 1),
            make_contact(contact_form2, student.id, 2),
            make_contact(contact_form3, student.id, 3),
        ]
        db.session.add_all(contacts)

        db.session.commit()
        flash("Registration submitted successfully!", "success")
        return redirect(url_for('registration.success'))

    # GET or validation failure
    return render_template(
        'registration.html',
        student_form   = student_form,
        contact_form1  = contact_form1,
        contact_form2  = contact_form2,
        contact_form3  = contact_form3,
        media_form     = media_form,
        waiver_form    = waiver_form
    )


@registration_bp.route('/select/<token>')
def select_with_token(token):
    sub = Student.query.filter_by(
        selection_token      = token,
        immunization_verified = True
    ).first()
    if not sub or sub.token_used:
        flash("Invalid or expired link. Please register first.", "danger")
        return redirect(url_for('registration.register'))

    sub.token_used = True
    db.session.commit()

    # forward into your course‐picker/edit view
    return redirect(url_for('registration.edit_form', email=sub.email))


@registration_bp.route('/success')
def success():
    return render_template('success.html')
