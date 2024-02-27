## Graduate Teaching Assistant (GTA) Management System

# import statements
from flask import Flask, render_template, redirect, url_for, request, flash, current_app, send_file
from flask_bootstrap import Bootstrap5
from forms import SignUpForm, ApplicationForm, AddSubjectForm
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, LargeBinary
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import datetime
import io

# Flask constructor
app = Flask(__name__)
Bootstrap5(app)
app.secret_key = "CSRF secret key"


# Create Database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

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


class Subjects(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    code: Mapped[str] = mapped_column(String(250), nullable=False)
    faculty: Mapped[str] = mapped_column(String(250), nullable=False)
    # students = relationship('StudentApplication', backref='subject')


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


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
    date = datetime.datetime.now().strftime('%m-%d-%Y')
    if form.validate_on_submit():
        cv_file = form.resume.data
        cv_content = cv_file.read()
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
            grade=form.grade.data
        )
        db.session.add(new_application)
        db.session.commit()
        return redirect(url_for('student_dashboard'))
    return render_template('apply.html', form=form)


@app.route('/view-application/<int:application_id>', methods=['GET', 'POST'])
def view_application(application_id):
    application = db.get_or_404(StudentApplication, application_id)
    return render_template('view_application.html', application_data=application)


@app.route('/delete-application/<int:application_id>', methods=['GET', 'POST'])
def delete_application(application_id):
    application = db.get_or_404(StudentApplication, application_id)
    db.session.delete(application)
    db.session.commit()


############## ADMIN PAGE ##############

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    subject_scalars = db.session.execute(db.select(Subjects)).scalars()
    subjects = [{"id": subject.id, "code": subject.code, "name": subject.name, "faculty": subject.faculty} for subject
                in
                subject_scalars]
    return render_template('admin.html', admin_name=current_user.first_name, subjects=subjects,
                           applications=get_all_applications())


@login_required
@app.route('/add-subject', methods=['GET', 'POST'])
def add_subject():
    form = AddSubjectForm()
    if form.validate_on_submit():
        new_subject = Subjects(
            name=form.subject_name.data,
            code=form.subject_code.data,
            faculty=form.faculty.data
        )
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add-subject.html', form=form)


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
    applications = get_all_applications()
    return render_template('all_applications.html', applications=applications)


############## COMMITTEE PAGE ##############

@app.route('/committee', methods=['GET', 'POST'])
def committee():
    pass


############## FACULTY PAGE ##############
@app.route('/faculty', methods=['GET', 'POST'])
def faculty():
    pass


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


def get_all_applications():
    applications = db.session.execute(db.select(StudentApplication)).scalars()
    return applications


if __name__ == '__main__':
    app.run(debug=True, port=3000)
