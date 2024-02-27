# import statements
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, SelectField, EmailField, FileField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileAllowed


class SignUpForm(FlaskForm):
    first_name = StringField(label='First Name', validators=[DataRequired()])
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
    subject = StringField(label='Subject', validators=[DataRequired()])
    grade = SelectField(label='Grade', choices=['A', 'B', 'C', 'D', 'F'], validators=[DataRequired()])
    resume = FileField(label='Resume',
                       validators=[DataRequired(), FileAllowed(['pdf', 'doc', 'docx'], 'PDF, DOC, and DOCX only!')
                                   ])
    submit = SubmitField(label='Submit Application')


class AddSubjectForm(FlaskForm):
    subject_code = StringField(label='Subject Code', validators=[DataRequired()])
    subject_name = StringField(label='Subject Name', validators=[DataRequired()])
    faculty = StringField(label='Faculty Name', validators=[DataRequired()])
    submit = SubmitField(label='Submit')