# Imports.
import os
from flask import current_app as app
from flask import render_template, request, flash, redirect, url_for, abort
from .forms import Registration, Login, AddTrackerForm, LogFormNum, LogFormBool, LogFormTime, LogFormMCT
from .models import db, User, Tracker, Log
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
from matplotlib import pyplot as plt

# Initial Setup
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.template_filter()
def get_latest_time(timestamp):
	timediff = datetime.now()-timestamp
	if timediff > timedelta(days=1):
		val = str(datetime.now()-timestamp).split(", ")[0]
	else:
		val = str(datetime.now()-timestamp).split(".")[0]
	return (val)

def time_to_minutes(str_time):
	timeobject = datetime.strptime(str_time, '%H:%M').time()
	minutes = timeobject.hour*60 + timeobject.minute
	return minutes

# Routes
@app.route('/')
@app.route('/home')
@login_required
def home():
	trackers = Tracker.query.filter_by(user_id=current_user.id)
	logs = Log.query.all()
	return render_template("home.html", trackers=trackers, logs=logs, title="Home Page")



@app.route('/register', methods=["GET", "POST"] )
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	form = Registration()

	if form.validate_on_submit():
		hashed_pw = None
		# if password was entered by the user, generate a hashed password.
		if form.password.data:
			hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
			
		user = User(username=form.username.data.rstrip(), password=hashed_pw)
		db.session.add(user)
		db.session.commit()

		flash(f'User Account for {form.username.data} has been created successfully! You can login now.', 'success')
		return redirect(url_for("login"))

	return render_template("registration.html", form = form, title="Registration Page")



@app.route('/login', methods=["GET", "POST"] )
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	form = Login()
	if form.validate_on_submit():

		# Check if the user exists and password is same.
		user = User.query.filter_by(username=form.username.data.rstrip()).first()
		valid_user = None
		if user:
			valid_user = True
			if user.password:
				try:
					valid_user = bcrypt.check_password_hash(user.password, form.password.data)
				except:
					valid_user = False

		if valid_user:	
			login_user(user, remember=form.remember.data)
			flash(f'Congratulations {form.username.data}! you have logged in successfully.', 'success')
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for("home"))
		else:
			flash(f"Login Unsuccessful. Invalid username or password.", 'danger')

	return render_template("login.html", form = form , title="Login Page")



@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for("login"))




@app.route('/tracker/add', methods=["GET", "POST"])
@login_required
def add_tracker():
	form = AddTrackerForm()
	if form.validate_on_submit():
		if form.tracker_type.data != "mct":
			form.settings.data = None
		tracker = Tracker(name=form.name.data.rstrip(), description=form.description.data, 
							tracker_type=form.tracker_type.data, user_id=current_user.id, settings=form.settings.data)
		db.session.add(tracker)
		db.session.commit()
		flash("Tracker created successfully.", "success")
		return redirect(url_for("home"))
	return render_template("add_tracker.html", form=form, title="New Tracker")


@app.route('/tracker/<int:tracker_id>')
@login_required
def tracker(tracker_id):
	tracker = Tracker.query.get_or_404(tracker_id)
	if tracker.user_id != current_user.id:
		abort(403)
	else:
		graph = request.args.get("graph", "week")
		if graph == "week":
			lastdate = datetime.now()-timedelta(days=7)
		elif graph == "month":
			lastdate = datetime.now()-timedelta(days=7)
		elif graph == "alltime":
			lastdate = datetime.now()-timedelta(days=999999)
		elif graph == "today":
			lastdate = datetime.now()-timedelta(days=1)

		logs = db.session.query(Log).filter(Log.tracker_id == tracker_id)\
		.filter(Log.timestamp>lastdate)\
		.order_by(Log.timestamp)

		image_url = os.path.join(os.getcwd(), "application", "static\images\plot.png")

		if tracker.tracker_type == "num":

			data = [int(log.value) for log in logs]
			timestamps = [log.timestamp for log in logs]
			plt.clf()
			plt.plot(timestamps, data)
			plt.savefig(image_url)

		elif tracker.tracker_type == "td":
			data = [time_to_minutes(log.value) for log in logs]
			timestamps = [log.timestamp for log in logs]

			plt.clf()
			plt.ylim(0, 1.2*max(data))
			plt.plot(timestamps, data)
			plt.ylabel("minutes")
			plt.savefig(image_url)

		elif tracker.tracker_type == "bool":
			data = [log.value for log in logs]
			plt.clf()
			plt.hist(data)
			plt.savefig(image_url)

		elif tracker.tracker_type == "mct":
			data = [log.value for log in logs]
			plt.clf()
			plt.hist(data)
			plt.savefig(image_url)
		
		return render_template("tracker.html", tracker = tracker, logs=logs)



@app.route('/tracker/<int:tracker_id>/update', methods=["GET", "POST"])
@login_required
def update_tracker(tracker_id):
	tracker = Tracker.query.get_or_404(tracker_id)
	if tracker.user_id != current_user.id:
		abort(403)

	form = AddTrackerForm()

	if form.validate_on_submit():
		tracker.name = form.name.data
		tracker.description = form.description.data
		tracker.settings = form.settings.data
		db.session.commit()
		flash("Tracker has been updated.", "success")
		return redirect(url_for("tracker", tracker_id=tracker.id))

	form.name.data = tracker.name
	form.description.data = tracker.description
	form.tracker_type.data = tracker.tracker_type
	form.settings.data = tracker.settings

	return render_template("add_tracker.html", form=form, title="Update Tracker")



@app.route('/tracker/<int:tracker_id>/delete')
@login_required
def delete_tracker(tracker_id):
	tracker = Tracker.query.get_or_404(tracker_id)
	if tracker.user_id != current_user.id:
		abort(403)
	Log.query.filter_by(tracker_id=tracker.id).delete()
	db.session.delete(tracker)
	db.session.commit()
	flash("Successfully deleted.", "success")
	return redirect(url_for("home"))



@app.route('/log/new/<int:tracker_id>', methods=["GET", "POST"])
@login_required
def add_log(tracker_id):
	tracker = Tracker.query.get_or_404(tracker_id)
	if tracker.user_id != current_user.id:
		abort(403)

	# Form Setup
	logforms = {"num":LogFormNum(), "mct":LogFormMCT(), 
			"td":LogFormTime(), "bool":LogFormBool()}

	form = logforms[tracker.tracker_type]

	if tracker.tracker_type == "mct":
		settings = tracker.settings.split(',')
		form.value.choices = settings



	form.timestamp.data = datetime.utcnow()+timedelta(hours=5, minutes=30)
	
	if form.validate_on_submit():
		if tracker.tracker_type == 'td':
			form.value.data = form.value.data.strftime("%H:%M")

		log = Log(timestamp=form.timestamp.data, value=form.value.data, note=form.note.data, tracker_id = tracker.id)
		db.session.add(log)
		db.session.commit()
		flash("Successfully Logged.", "success")
		return redirect(url_for('tracker', tracker_id=tracker.id))

	return render_template("add_log.html", form=form, tracker=tracker)



@app.route('/tracker/<int:tracker_id>/log/<int:log_id>/update', methods=["GET", "POST"])
@login_required
def update_log(tracker_id, log_id):
	tracker = Tracker.query.get_or_404(tracker_id)
	log = Log.query.get_or_404(log_id)

	if tracker.user_id != current_user.id or tracker_id != log.tracker_id:
		abort(403)

	# Form Setup
	logforms = {"num":LogFormNum(), "mct":LogFormMCT(), 
			"td":LogFormTime(), "bool":LogFormBool()}

	form = logforms[tracker.tracker_type]

	if tracker.tracker_type == "mct":
		if tracker.settings:
			settings = tracker.settings.split(',')
		else:
			settings = ""
		form.value.choices = settings

	if form.validate_on_submit():
		form.value.data = form.value.data
		log.timestamp = form.timestamp.data

		if tracker.tracker_type == 'td':
			form.value.data = form.value.data.strftime("%H:%M")

		log.value = form.value.data
		log.note = form.note.data
		db.session.commit()
		flash("Log has been updated.", "success")
		return redirect(url_for("tracker", tracker_id=tracker.id))

	form.timestamp.data = log.timestamp
	if tracker.tracker_type == "td":
		form.value.data = datetime.strptime(log.value, '%H:%M').time()
	else:
		form.value.data = log.value

	form.note.data = log.note
	return render_template("add_log.html", form=form, title="Update Tracker", tracker=tracker)



@app.route('/tracker/<int:tracker_id>/log/<int:log_id>/delete')
@login_required
def delete_log(tracker_id, log_id):
	tracker = Tracker.query.get_or_404(tracker_id)
	log = Log.query.get_or_404(log_id)
	if tracker.user_id != current_user.id and tracker_id != log.tracker_id:
		abort(403)

	db.session.delete(log)
	db.session.commit()
	flash("Successfully deleted.", "success")
	return redirect(url_for("tracker", tracker_id=tracker.id))



 