from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Length, ValidationError
from .models import User, Tracker, db
from flask_login import current_user
from wtforms.fields.html5 import TimeField, DateTimeLocalField

class Registration(FlaskForm):
	username = StringField(label="Username:", validators=[DataRequired(), Length(min=2, max=20)])
	password = PasswordField(label="Password: ")
	submit = SubmitField(label="Register")

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data.rstrip()).first()
		if user:
			raise ValidationError("The username is already taken.")


class Login(FlaskForm):
	username = StringField(label="Username:", validators=[DataRequired(), Length(min=2, max=20)])
	password = PasswordField(label="Password: ")
	submit = SubmitField(label="Login")
	remember = BooleanField("Remember me")


class AddTrackerForm(FlaskForm):
	name = StringField(label="Name: ", validators=[DataRequired(), Length(min=2, max=55)])
	description = StringField(label="Description: ", validators=[Length(max=1000)])
	tracker_type = SelectField(label="Type: ", choices=[("num", "Numerical"), ("mct", "Multiple Choice"),
												 ("td", "TIme Duration"), ("bool", "Yes/No")])
	settings = StringField(label="Custom Options: ")
	submit = SubmitField(label="Add It")

	def validate_name(self, name):
		tracker = Tracker.query.filter_by(name=name.data.rstrip(), user_id=current_user.id).first()
		if tracker:
			raise ValidationError("The Tracker already exists.")


class LogFormNum(FlaskForm):
	timestamp = DateTimeLocalField("time:" ,format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
	value = IntegerField("Done: " , validators=[DataRequired()])
	note = StringField("note: ")
	submit = SubmitField(label="Log It")


class LogFormBool(FlaskForm):
	timestamp = DateTimeLocalField("time:" ,format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
	value = BooleanField("Task Completed " )
	note = StringField("note: ")
	submit = SubmitField(label="Log It")


class LogFormTime(FlaskForm):
	timestamp = DateTimeLocalField("time:" ,format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
	value = TimeField("value: " , validators=[DataRequired()])
	note = StringField("note: ")
	submit = SubmitField(label="Log It")


class LogFormMCT(FlaskForm):
	timestamp = DateTimeLocalField("time:" ,format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
	value = SelectField("value: ", coerce=str)
	note = StringField("note: ")
	submit = SubmitField(label="Log It")