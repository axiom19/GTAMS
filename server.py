## Graduate Teaching Assistant (GTA) Management System

# import statements
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField, EmailField, FileField
from wtforms.validators import DataRequired, Email, Length
import csv

# Flask constructor
app = Flask(__name__)
Bootstrap5(app)
app.secret_key = "CSRF secret key"


# Form class
class SignUpForm(FlaskForm):
    first_name = StringField(label='First Name', validators=[DataRequired()])
    middle_name = StringField(label='Middle Name')
    last_name = StringField(label='Last Name', validators=[DataRequired()])
    email = EmailField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=8)])
    dob = DateField(label='Date of Birth', validators=[DataRequired()])
    user_type = SelectField(label='User Type', choices=['Student', 'Admin', 'Committee Member', 'Faculty'],
                            validators=[DataRequired()])
    submit = SubmitField(label='Sign Up')


class ApplicationForm(FlaskForm):
    first_name = StringField(label='First Name', validators=[DataRequired()])
    middle_name = StringField(label='Middle Name')
    last_name = StringField(label='Last Name', validators=[DataRequired()])
    email = EmailField(label='Email', validators=[DataRequired(), Email()])
    dob = DateField(label='Date of Birth', validators=[DataRequired()])
    phone = StringField(label='Phone Number', validators=[DataRequired()])
    address = StringField(label='Address', validators=[DataRequired()])
    subject1 = StringField(label='Subject 1', validators=[DataRequired()])
    subject2 = StringField(label='Subject 2', validators=[DataRequired()])
    subject3 = StringField(label='Subject 3', validators=[DataRequired()])
    resume = FileField(label='Resume', validators=[DataRequired()])
    submit = SubmitField(label='Sign Up')


############## HOME PAGE ##############

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with open('users.txt', 'r') as file:
            users = file.readlines()
            for user in users:
                user_details = user.strip().split(', ')  # Strip newline characters
                # Debug print statement to check values
                print(f"Email: {user_details[3]}, Password: {user_details[4]}, User Type: {user_details[6]}")

                if email == user_details[3] and password == user_details[4]:
                    user_type = user_details[6]  # Assuming no leading/trailing whitespace
                    if user_type == 'Student':
                        print('Logged in as Student')
                        return redirect(url_for('student'))  # Corrected route name
                    elif user_type == 'Admin':
                        return redirect(url_for('admin'))
                    elif user_type == 'Committee Member':
                        return redirect(url_for('committee'))
                    elif user_type == 'Faculty':
                        return redirect(url_for('faculty'))
    return render_template('index.html')


############## SIGN UP ##############
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        with open('users.txt', 'a') as file:
            file.write(f"{form.first_name.data}, {form.middle_name.data}, {form.last_name.data}, {form.email.data}, "
                       f"{form.password.data}, {form.dob.data}, {form.user_type.data}\n")
        return redirect(url_for('home'))
    return render_template('signup.html', form=form)


############## APPLICANT PAGE ##############
@app.route('/student', methods=['GET', 'POST'])
def student():
    return render_template('student.html')


# have to change the redirect to student dashboard after submit and also have to do something about resume file
@app.route('/apply', methods=['GET', 'POST'])
def apply():
    form = ApplicationForm()
    if form.validate_on_submit():
        with open('applications.txt', 'a') as file:
            file.write(f"{form.first_name.data}, {form.middle_name.data}, {form.last_name.data}, {form.email.data}, "
                       f"{form.dob.data}, {form.phone.data}, {form.address.data}, {form.subject1.data}, "
                       f"{form.subject2.data}, {form.subject3.data}\n")
        return redirect(url_for('student'))
    return render_template('apply.html', form=form)


@app.route('/student/dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')


############## ADMIN PAGE ##############
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    pass


############## COMMITTEE PAGE ##############
@app.route('/committee', methods=['GET', 'POST'])
def committee():
    pass


############## FACULTY PAGE ##############
@app.route('/faculty', methods=['GET', 'POST'])
def faculty():
    pass


if __name__ == '__main__':
    app.run(debug=True, port=3000)
