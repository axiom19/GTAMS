## Graduate Teaching Assistant (GTA) Management System

# import statements
from flask import Flask, render_template, redirect, url_for, request, flash, current_app, send_file
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from forms import SignUpForm, ApplicationForm, AddSubjectForm, TaEvaluationForm
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, LargeBinary
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import datetime
import os
from resume_matcher import ResumeMatcher
from resume_parser import ResumeParser
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict
from email.mime.multipart import MIMEMultipart

# Flask constructor
app = Flask(__name__)
Bootstrap5(app)
app.secret_key = "CSRF secret key"

csrf = CSRFProtect(app)

app.config['UPLOAD_FOLDER'] = 'path/to/upload/folder'
upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)


# Create Database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)

# TODO: Login Configuration
login_manager = LoginManager()
login_manager.init_app(app)


class Users(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(250), nullable=False)
    last_name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    dob: Mapped[str] = mapped_column(String(250), nullable=False)
    user_type: Mapped[str] = mapped_column(String(250), nullable=False)

    def get_user_type(self):
        return self.user_type


# TODO: Create a relational database for the application
class StudentApplication(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_date: Mapped[str] = mapped_column(String(250), nullable=False)
    first_name: Mapped[str] = mapped_column(String(250), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(250), nullable=False)
    last_name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    dob: Mapped[str] = mapped_column(String(250), nullable=False)
    phone: Mapped[str] = mapped_column(String(250), nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    subject: Mapped[str] = mapped_column(String(250), nullable=False)
    grade: Mapped[str] = mapped_column(String(250), nullable=False)
    resume: Mapped[str] = mapped_column(LargeBinary, nullable=False)
    match_score: Mapped[str] = mapped_column(String(250))
    referred: Mapped[bool] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(250), default='Pending')


class Subjects(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    code: Mapped[str] = mapped_column(String(250), nullable=False)
    faculty: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)


class TA_Evaluation(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    faculty_id: Mapped[int] = mapped_column(Integer, nullable=False)
    ta_id: Mapped[int] = mapped_column(Integer, nullable=False)
    subject: Mapped[str] = mapped_column(String(250), nullable=False)
    hours_done: Mapped[str] = mapped_column(String(1000), nullable=False)
    communication: Mapped[str] = mapped_column(String(1000), nullable=False)
    office_hours_put_in: Mapped[str] = mapped_column(String(1000), nullable=False)
    assignment_checking: Mapped[str] = mapped_column(String(1000), nullable=False)
    overall_rating: Mapped[str] = mapped_column(String(1000), nullable=False)


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)


############## SIGN UP ##############
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(Users).where(Users.email == form.email.data)).scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('home'))
        new_user = Users(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=hash_password(form.password.data),
            dob=form.dob.data,
            user_type=form.user_type.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        if new_user.user_type == 'Student':
            return redirect(url_for('student_dashboard'))
        elif new_user.user_type == 'Admin':
            return redirect(url_for('admin_dashboard'))
        elif new_user.user_type == 'Committee Member':
            return redirect(url_for('committee'))
        elif new_user.user_type == 'Faculty':
            return redirect(url_for('faculty'))

    return render_template('signup.html', form=form, current_user=current_user)


############## Home Login PAGE ##############

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.session.execute(db.select(Users).where(Users.email == email)).scalar()
        if user:
            if check_hashed_password(password, user.password):
                login_user(user)
                if user.user_type == 'Student':
                    return redirect(url_for('student_dashboard'))
                # TODO: Fix these after
                elif user.user_type == 'Admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.user_type == 'Committee Member':
                    return redirect(url_for('committee'))
                elif user.user_type == 'Faculty':
                    return redirect(url_for('faculty'))
            else:
                flash('Invalid password')
                return redirect(url_for('home'))
        else:
            flash('Invalid email')
            return redirect(url_for('home'))

    return render_template('index.html', current_user=current_user)


############## APPLICANT PAGE ##############
@app.route('/student', methods=['GET', 'POST'])
@login_required
def student_dashboard():
    # get all the applications submitted by the student
    applications = db.session.execute(
        db.select(StudentApplication).where(StudentApplication.email == current_user.email)).scalars()
    print(StudentApplication.query.filter_by(email=current_user.email).all())
    return render_template('student.html', student_name=current_user.first_name, applications=applications)


@app.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    form = ApplicationForm()
    subject_choices = get_subject_names()
    form.subject.choices = subject_choices
    date = datetime.datetime.now().strftime('%m-%d-%Y')
    if form.validate_on_submit():
        cv_file = form.resume.data

        # resume to text
        filename = secure_filename(cv_file.filename)
        resume_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'resumes')
        if not os.path.exists(resume_dir):
            os.makedirs(resume_dir)
        resume_path = os.path.join(resume_dir, filename)

        cv_file.save(resume_path)

        cv_file.seek(0)
        cv_content = cv_file.read()

        parser = ResumeParser(resume_path)
        resume_text = parser.parse_resume()

        selected_subject = form.subject.data
        subject_data = db.session.execute(db.select(Subjects).where(Subjects.name == selected_subject)).scalar()
        subject_description = subject_data.description

        # match resume to subject
        matcher = ResumeMatcher(subject_description)
        match_score = round(matcher.compute_match_score(resume_text), 4)

        new_application = StudentApplication(
            resume=cv_content,
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            dob=form.dob.data.strftime('%Y-%m-%d'),
            phone=form.phone.data,
            address=form.address.data,
            subject=form.subject.data,
            application_date=date,
            grade=form.grade.data,
            match_score=match_score
        )
        db.session.add(new_application)
        db.session.commit()

        return redirect(url_for('student_dashboard'))
    return render_template('apply.html', form=form)


@app.route('/view-application/<int:application_id>', methods=['GET', 'POST'])
def view_application(application_id):
    application = db.get_or_404(StudentApplication, application_id)

    # download resume
    if request.method == 'POST':
        resume_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'resumes', 'resume.pdf')
        with open(resume_path, 'wb') as f:
            f.write(application.resume)
        return send_file(resume_path, as_attachment=True)

    return render_template('view_application.html', application_data=application, current_user=current_user)


def download_resume(application):
    resume_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'resumes', 'resume.pdf')
    with open(resume_path, 'wb') as f:
        f.write(application.resume)
    return send_file(resume_path, as_attachment=True)


@app.route('/delete-application/<int:application_id>', methods=['GET', 'POST'])
def delete_application(application_id):
    application = db.get_or_404(StudentApplication, application_id)
    db.session.delete(application)
    db.session.commit()
    return redirect(url_for('student_dashboard'))


############## ADMIN PAGE ##############

@login_required
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    subject_scalars = get_all_subjects()
    subjects = [{"id": subject.id, "code": subject.code, "name": subject.name, "faculty": subject.faculty} for subject
                in
                subject_scalars]
    return render_template('admin.html', admin_name=current_user.first_name, subjects=subjects)


@login_required
@app.route('/add-subject', methods=['GET', 'POST'])
def add_subject():
    form = AddSubjectForm()
    if form.validate_on_submit():
        new_subject = Subjects(
            name=form.subject_name.data,
            code=form.subject_code.data,
            faculty=form.faculty.data,
            description=form.description.data
        )
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add-subject.html', form=form)


@login_required
@app.route('/view_subject/<int:subject_id>', methods=['GET', 'POST'])
def view_subject(subject_id):
    subject = db.get_or_404(Subjects, subject_id)
    return render_template('view_subject.html', subject=subject)


@login_required
@app.route('/edit-subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    subject = db.get_or_404(Subjects, subject_id)
    edit_form = AddSubjectForm(
        subject_name=subject.name,
        subject_code=subject.code,
        faculty=subject.faculty
    )
    if edit_form.validate_on_submit():
        subject.name = edit_form.subject_name.data
        subject.code = edit_form.subject_code.data
        subject.faculty = edit_form.faculty.data
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    return render_template("add-subject.html", form=edit_form, current_user=current_user, is_edit=True)


@login_required
@app.route('/delete-subject/<int:subject_id>', methods=['GET', 'POST'])
def delete_subject(subject_id):
    subject = db.get_or_404(Subjects, subject_id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))


@login_required
@app.route('/all-applications', methods=['GET', 'POST'])
def all_applications():
    applications = StudentApplication.query.filter(StudentApplication.grade == 'A').order_by(
        StudentApplication.match_score.desc()).all()
    return render_template('all_applications.html', applications=applications)


@app.route('/refer-student/<int:application_id>', methods=['POST'])
@login_required
def refer_student(application_id):
    try:
        application = db.session.get(StudentApplication, application_id)
        if application:
            application.referred = True
            db.session.commit()
            flash('Student referred to the committee successfully!', 'success')
        else:
            flash('Application not found.', 'error')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred while referring the student.', 'error')
    return redirect(url_for('all_applications'))


############## COMMITTEE PAGE ##############
@login_required
@app.route('/committee', methods=['GET', 'POST'])
def committee():
    all_subjects = get_all_subjects()
    return render_template('committee.html', subjects=all_subjects, name=current_user.first_name)


@login_required
@app.route('/committee-applications/', defaults={'view': 1})
@app.route('/committee-applications/<int:view>', methods=['GET', 'POST'])
def committee_applications(view):
    if view == 1:
        applications = db.session.execute(db.select(StudentApplication)).scalars().all()
    elif view == 2:
        applications = get_top_students()
    elif view == 3:
        applications = get_referred_students()
    else:
        applications = []

    return render_template(
        'committee_applications.html',
        applications=applications,
        view=view
    )


@app.route('/accept-student/<int:application_id>', methods=['POST'])
@login_required
def accept_student(application_id):
    try:
        application = db.session.execute(
            db.select(StudentApplication).where(StudentApplication.id == application_id)).scalar()
        if application:
            # accept student
            application.status = 'Accepted'
            # reject all others in that subject
            db.session.query(StudentApplication) \
                .filter(StudentApplication.id != application_id,
                        StudentApplication.subject == application.subject) \
                .update({"status": "Rejected"})
            db.session.commit()
            flash('Student accepted successfully!', 'success')

            # TODO: Send email to student

        else:
            flash('Application not found.', 'error')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred while accepting the student.', 'error')
    return redirect(url_for('committee_applications'))


@app.route('/reject-student/<int:application_id>', methods=['POST'])
@login_required
def reject_student(application_id):
    try:
        application = db.session.execute(
            db.select(StudentApplication).where(StudentApplication.id == application_id)).scalar()
        if application:
            # reject student
            application.status = 'Rejected'
            db.session.commit()
            flash('Student rejected successfully!', 'success')
        else:
            flash('Application not found.', 'error')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred while rejecting the student.', 'error')
    return redirect(url_for('committee_applications'))


############## FACULTY PAGE ##############


@app.route('/faculty', methods=['GET', 'POST'])
@login_required
def faculty():
    # Concatenate first and last names to match the 'faculty' field in 'Subjects' table
    faculty_name = f"{current_user.first_name} {current_user.last_name}"
    form = TaEvaluationForm()
    # Fetch the single subject associated with this faculty member
    subject = db.session.execute(db.select(Subjects).where(Subjects.faculty == faculty_name)).scalar()

    if not subject:
        # if the faculty does not have an assigned subject, display an error message
        flash('You are not added to the system yet. Contact Admin.', 'warning')
        return render_template('faculty_error.html', name=faculty_name)

    # Fetch the single accepted TA for this subject, if any

    ta = db.session.execute(
        db.select(StudentApplication).where(StudentApplication.subject == subject.name,
                                            StudentApplication.status == 'Accepted')).scalar()

    return render_template('faculty.html', current_user=current_user, subject=subject, ta=ta)


@app.route('/faculty/evaluate_ta/<int:ta_id>', methods=['GET', 'POST'])
@login_required
def evaluate_ta(ta_id):
    form = TaEvaluationForm()
    if form.validate_on_submit():
        new_evaluation = TA_Evaluation(
            faculty_id=current_user.id,
            ta_id=ta_id,
            subject=form.subject.data,
            _evaluation=form.hours_done.data,
            date=datetime.datetime.now().strftime('%m-%d-%Y')
        )
        db.session.add(new_evaluation)
        db.session.commit()
        flash('TA evaluation submitted successfully.', 'success')
        # Redirect after form processing. Adjust as needed.
        return redirect(url_for('faculty'))
    return render_template('evaluate_ta.html', form=form)


############## OTHER FUNCTIONS ##############
def hash_password(password):
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)


@app.route('/user-profile')
@login_required
def user_profile():
    return render_template('user-profile.html', user=current_user)


def check_hashed_password(password, hashed_password):
    return check_password_hash(hashed_password, password)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def get_all_subjects():
    subjects = db.session.execute(db.select(Subjects)).scalars()
    return subjects


def get_subject_names():
    subjects = db.session.execute(db.select(Subjects)).scalars()
    return [subject.name for subject in subjects]


def get_referred_students():
    referred_students_query = db.select(StudentApplication).where(StudentApplication.referred.is_(True))
    referred_students = db.session.execute(referred_students_query).scalars().all()
    return referred_students


def get_top_students():
    # Fetch all students with an 'A' grade
    all_A_students_query = db.select(StudentApplication).where(StudentApplication.grade == 'A')
    all_A_students = db.session.execute(all_A_students_query).scalars().all()

    # Organize students by subject
    students_by_subject = defaultdict(list)
    for student in all_A_students:
        students_by_subject[student.subject].append(student)

    # Sort students within each subject by match_score in descending order
    for subject in students_by_subject:
        students_by_subject[subject].sort(key=lambda s: s.match_score, reverse=True)

    # Get top 3 students per subject
    top_students_per_subject = []
    for subject, students in students_by_subject.items():
        top_students_per_subject.extend(students[:3])

    return top_students_per_subject


if __name__ == '__main__':
    app.run(debug=True, port=2000)
