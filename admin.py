# admin.py
from pathlib import Path
import io, csv

from flask import (
    Blueprint,
    render_template,
    send_from_directory,
    Response,
    url_for
)

from flask_login import login_required
from models import Student, Contact
import json
from forms import StudentForm


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

BASE_DIR      = Path(__file__).parent.resolve()
PDF_FOLDER    = BASE_DIR / 'generated_pdfs'
UPLOAD_FOLDER = BASE_DIR / 'uploads'

@admin_bp.route('/')
@login_required
def dashboard():
    students = Student.query.order_by(Student.id).all()
    # build label lookup
    form = StudentForm()
    committee_labels = dict(form.volunteer_committees.choices)
    # parse each student’s assignments JSON
    for s in students:
        s.vol_assign = json.loads(s.volunteer_assignments or "{}")
    return render_template('admin.html',
                           students=students,
                           committee_labels=committee_labels)

@admin_bp.route('/download_csv')
@login_required
def download_csv():
    student_fields = [
        'id','school','first_name','preferred_name','last_name',
        'grade_level','primary_phone','gender','date_of_birth',
        'enrollment_status','address_street','address_city',
        'address_state','address_zip','has_iep','has_504',
        'transferring','prev_school_name','prev_school_address',
        'health_issues','otc_permission', 'health_issues','authorized_pickups','immunizations_current',
        'immunization_record','media_pdf','waiver_pdf','guardian_relationship_status'
    ]
    contact_fields = [
        'priority','relationship','first_name','last_name','gender',
        'email','phone','address_street','address_city',
        'address_state','address_zip','has_custody','lives_with',
        'can_pickup','receives_mail','emergency_contact'
    ]

    # build header
    header = student_fields[:]
    for i in (1,2,3):
        header += [f'contact{i}_{f}' for f in contact_fields]

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(header)

    for s in Student.query.order_by(Student.id):
        row = []
        for f in student_fields:
            v = getattr(s,f)
            if isinstance(v,bool):    v = 'Yes' if v else 'No'
            elif getattr(v,'isoformat',None): v = v.isoformat()
            row.append(v or '')
        for i, c in enumerate(s.contacts[:3], start=1):
            for f in contact_fields:
                v = getattr(c,f)
                if isinstance(v,bool): v = 'Yes' if v else 'No'
                row.append(v or '')
        # pad if fewer than 3 contacts
        missing = (3 - len(s.contacts)) * len(contact_fields)
        row += [''] * missing

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

@admin_bp.route('/volunteers')
@login_required
def volunteers():
    # 1) build mapping: committee code → list of "Student Name (via ContactName)"
    roster = {}
    for s in Student.query:
        # load back the JSON map we stored
        assignments = json.loads(s.volunteer_assignments or "{}")
        for code, name in assignments.items():
            roster.setdefault(code, []).append(
                f"{s.first_name} {s.last_name} (via {name or '—'})"
            )

    # 2) grab human-readable labels by instantiating the form
    form = StudentForm()
    labels = dict(form.volunteer_committees.choices)

    return render_template(
        'admin_volunteers.html',
        roster=roster,
        labels=labels,
    )

