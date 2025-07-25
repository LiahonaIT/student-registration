# admin.py

import io
import csv
import uuid
import json
from pathlib import Path

from flask import (
    Blueprint, render_template,
    send_from_directory, Response,
    url_for, flash, redirect
)
from flask_login import login_required
from flask_mail import Message

from extensions    import db, mail
from models        import Student, Contact
from forms         import StudentForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

BASE_DIR      = Path(__file__).parent.resolve()
PDF_FOLDER    = BASE_DIR / 'generated_pdfs'
UPLOAD_FOLDER = BASE_DIR / 'uploads'


@admin_bp.route('/')
@login_required
def dashboard():
    students = Student.query.order_by(Student.id).all()
    form     = StudentForm()
    committee_labels = dict(form.volunteer_committees.choices)
    for s in students:
        s.vol_assign = json.loads(s.volunteer_assignments or "{}")
    return render_template(
        'admin.html',
        students=students,
        committee_labels=committee_labels
    )


@admin_bp.route('/download_csv')
@login_required
def download_csv():
    student_fields = [
      'id','school','first_name','preferred_name','last_name',
      'grade_level','primary_phone','gender','date_of_birth',
      'enrollment_status','address_street','address_city',
      'address_state','address_zip','has_iep','has_504',
      'transferring','prev_school_name','prev_school_address',
      'health_issues','otc_permission','authorized_pickups',
      'immunizations_current','immunization_record',
      'media_pdf','waiver_pdf','guardian_relationship_status'
    ]
    contact_fields = [
      'priority','relationship','first_name','last_name','gender',
      'email','phone','address_street','address_city',
      'address_state','address_zip','has_custody','lives_with',
      'can_pickup','receives_mail','emergency_contact'
    ]

    header = student_fields[:]
    for i in (1,2,3):
        header += [f'contact{i}_{f}' for f in contact_fields]

    si     = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(header)

    for s in Student.query.order_by(Student.id):
        row = []
        for f in student_fields:
            v = getattr(s,f)
            if isinstance(v,bool):    v = 'Yes' if v else 'No'
            elif hasattr(v,'isoformat'): v = v.isoformat()
            row.append(v or '')
        for c in s.contacts[:3]:
            for f in contact_fields:
                v = getattr(c,f)
                if isinstance(v,bool): v = 'Yes' if v else 'No'
                row.append(v or '')
        row += [''] * ((3 - len(s.contacts)) * len(contact_fields))
        writer.writerow(row)

    return Response(
      si.getvalue(),
      mimetype='text/csv',
      headers={'Content-Disposition':'attachment;filename=registrations.csv'}
    )


@admin_bp.route('/download/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory(str(PDF_FOLDER), filename, as_attachment=True)


@admin_bp.route('/view/<path:filename>')
@login_required
def view_file(filename):
    return send_from_directory(str(PDF_FOLDER), filename, as_attachment=False)


@admin_bp.route('/uploads/<path:filename>')
@login_required
def download_upload(filename):
    return send_from_directory(str(UPLOAD_FOLDER), filename, as_attachment=True)


@admin_bp.route('/view/uploads/<path:filename>')
@login_required
def view_upload(filename):
    return send_from_directory(str(UPLOAD_FOLDER), filename, as_attachment=False)


# ─── Approve & Send One-Time Course Link ─────────────────────────────────────
@admin_bp.route('/approve/<int:student_id>', methods=['POST'])
@login_required
def approve_student(student_id):
    s = Student.query.get_or_404(student_id)
    if not s.immunization_verified:
        s.immunization_verified = True
        s.selection_token      = str(uuid.uuid4())
        db.session.commit()

        link = url_for('registration.select_with_token',
                       token=s.selection_token,
                       _external=True)
        msg = Message(
            subject="Your Course Selection Link",
            recipients=[s.contacts[0].email]
        )
        msg.body = (
            f"Hi {s.first_name},\n\n"
            "Your registration is approved!  Please pick courses here:\n\n"
            f"{link}\n\n"
            "This link will only work once."
        )
        mail.send(msg)
        flash(f"Sent course-selection link to {s.contacts[0].email}", "success")
    else:
        flash("Student already approved.", "info")

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/volunteers')
@login_required
def volunteers():
    roster = {}
    for s in Student.query:
        assignments = json.loads(s.volunteer_assignments or "{}")
        for code, name in assignments.items():
            roster.setdefault(code, []).append(
                f"{s.first_name} {s.last_name} (via {name or '—'})"
            )
    form   = StudentForm()
    labels = dict(form.volunteer_committees.choices)
    return render_template('admin_volunteers.html', roster=roster, labels=labels)
