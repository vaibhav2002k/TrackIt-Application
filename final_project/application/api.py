from flask_restful import Api, Resource
from flask_restful import fields, marshal_with, reqparse
from .models import *
from flask import current_app as app
from .validations import *
from datetime import datetime
api = Api(app)


# -------------- User API -------------- 
user_fields = {
	'id':  fields.Integer,
	'username': fields.String,
}

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('username')

class UserAPI(Resource):
	@marshal_with(user_fields)
	def get(self, username):
		user = User.query.filter_by(username=username).first()

		# If user does not exists
		if not user:
			raise NotFoundError(status_code=404)
		# if the user exists return user
		else:
			return user

	@marshal_with(user_fields)
	def post(self):
		args = create_user_parser.parse_args()
		username = args.get("username", None)

		if username is None:
			error_code, 
			raise BusinessValidationError(status_code=400 , error_code="BVE01", error_message="username is required.")

		user = User.query.filter_by(username=username).first()
		# If username is taken.
		if user:
			raise BusinessValidationError(status_code=400 , error_code="BVE01", error_message="Username already taken.")

		# create the user if all checks passed.
		new_user = User(username=username)
		db.session.add(new_user)
		db.session.commit()
		return new_user

	def delete(self, username):
		user = User.query.filter_by(username=username).first()

		# if user does not exists
		if not user:
			raise NotFoundError(status_code=404)
		# if user exists, delete the user
		else:
			if user.trackers:
				raise BusinessValidationError(400, error_code="BVE07", error_message="Delete trackers first.")
			else:
				db.session.delete(user)
				db.session.commit()

		message = {"message": "deleted successfully"}
		return json.dumps(message)



# -------------- Tracker API -------------- 

tracker_fields = {
	"id":		   fields.Integer,
	"name":		 fields.String,
	"description":  fields.String,
	"tracker_type": fields.String,
	"settings":	 fields.String,
	"user_id":	  fields.Integer
}

create_tracker_parser = reqparse.RequestParser()
create_tracker_parser.add_argument('name')
create_tracker_parser.add_argument('description')
create_tracker_parser.add_argument('tracker_type')
create_tracker_parser.add_argument('settings')
create_tracker_parser.add_argument('user_id')

update_tracker_parser = reqparse.RequestParser()
update_tracker_parser.add_argument('name')
update_tracker_parser.add_argument('description')
update_tracker_parser.add_argument('tracker_type')
update_tracker_parser.add_argument('settings')

class TrackerAPI(Resource):

	@marshal_with(tracker_fields)
	def get(self, tracker_id):
		tracker = Tracker.query.get(tracker_id)

		# If tracker does not exists
		if not tracker:
			raise NotFoundError(status_code=404)
		# if the tracker exists return tracker
		else:
			return tracker

	@marshal_with(tracker_fields)
	def post(self):
		args = create_tracker_parser.parse_args()

		user_id = args.get("user_id", None)
		name = args.get("name", None)
		tracker_type = args.get("tracker_type", None)
		description = args.get("description", None)
		settings = args.get("settings", None)

		allowed_types= ["num", "mct", "td", "bool"]

		user = User.query.filter_by(id=user_id).first()
		if user:
			if tracker_type in allowed_types:
				if name:
					tracker = Tracker.query.filter_by(name=name, user_id=user_id).first()
					if not tracker:
						new_tracker = Tracker(name=name, description=description, 
								tracker_type=tracker_type, user_id=user_id, settings=settings)

						db.session.add(new_tracker)
						db.session.commit()
						return new_tracker
					else:
						raise BusinessValidationError(status_code=400, error_code="BVE05", error_message="Tracker already exists.")
				else:
					raise BusinessValidationError(status_code=400, error_code="BVE04", error_message="Tracker name cannot be empty")

			else:
				raise BusinessValidationError(status_code=400, error_code="BVE03", error_message="Tracker Type not recognized.")
		else:
			raise BusinessValidationError(status_code=400, error_code="BVE02", error_message="User Id is not valid.")

		
		
	@marshal_with(tracker_fields)
	def put(self, tracker_id):
		args = update_tracker_parser.parse_args()

		name = args.get("name", None)
		tracker_type = args.get("tracker_type", None)
		description = args.get("description", None)
		settings = args.get("settings", None)

		allowed_types= ["num", "mct", "td", "bool"]

		tracker = Tracker.query.get(tracker_id)
		# Tracker does not exist
		if tracker:
			if name:
				if tracker_type in allowed_types:
					tracker.name = name
					tracker.tracker_type = tracker_type
					tracker.description = description
					tracker.settings = settings
					db.session.commit()

					return tracker

				else:
					raise BusinessValidationError(status_code=400, error_code="BVE03", error_message="Tracker Type not recognized.")
			else:
				raise BusinessValidationError(status_code=400, error_code="BVE04", error_message="Tracker name cannot be empty")
		else:
			raise NotFoundError(status_code=404)

	def delete(self, tracker_id):
		tracker = Tracker.query.filter_by(id=tracker_id).first()

		# if user does not exists
		if not tracker:
			raise NotFoundError(status_code=404)
		# if user exists, check if logs exist for the tracker.
		else:
			if tracker.logs:
				raise BusinessValidationError(400, error_code="BVE06", error_message="Delete trackers first.")
			else:
				db.session.delete(tracker)
				db.session.commit()

		message = {"message": "Tracker deleted successfully"}
		return json.dumps(message)



# -------------- Log API -------------- 

log_fields = {
	"id":          	fields.Integer,
	"tracker_id":   fields.Integer,
	"timestamp":  	fields.DateTime,
	"value": 		fields.String,
	"note":	 		fields.String
}

create_log_parser = reqparse.RequestParser()
create_log_parser.add_argument('tracker_id')
create_log_parser.add_argument('timestamp')
create_log_parser.add_argument('value')
create_log_parser.add_argument('note')

update_log_parser = reqparse.RequestParser()
update_log_parser.add_argument('timestamp')
update_log_parser.add_argument('value')
update_log_parser.add_argument('note')


class LogAPI(Resource):

	@marshal_with(log_fields)
	def get(self, log_id):
		log = Log.query.get(log_id)

		# If tracker does not exists
		if not log:
			raise NotFoundError(status_code=404)
		# if the tracker exists return tracker
		else:
			return log


	@marshal_with(log_fields)
	def post(self):
		args = create_log_parser.parse_args()

		tracker_id = args.get("tracker_id", None)
		timestamp = args.get("timestamp", None)
		timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
		value = args.get("value", None)
		note = args.get("note", None)

		if tracker_id:
			tracker = Tracker.query.get(tracker_id)
			if tracker.tracker_type == "mct":
				if not value in tracker.settings:
					raise BusinessValidationError(400, error_code="BVE09", error_message="value not valid.")
					
			elif tracker.tracker_type == "td":
				try:
					value = value.strftime("%H:%M")
				except:
					raise BusinessValidationError(400, error_code="BVE09", error_message="value not valid.")

			elif tracker.tracker_type == "bool":
				print(value)
				if (value in [0,1]):
					raise BusinessValidationError(400, error_code="BVE09", error_message="value not valid.")

			elif tracker.tracker_type == "num":
				if not (type(value) is int):
					raise BusinessValidationError(400, error_code="BVE09", error_message="value not valid.")

			new_log = Log(timestamp=timestamp, value=value, note=note, tracker_id = tracker_id)
			db.session.add(new_log)
			db.session.commit()
			return new_log

		else:
			raise BusinessValidationError(400, error_code="BVE08", error_message="Tracker Id not valid.")


	@marshal_with(log_fields)
	def put(self, log_id):
		args = update_log_parser.parse_args()
		log = Log.query.filter_by(id=log_id).first()

		if log:
			pass
		else:
			raise NotFoundError(status_code=404)

		timestamp = args.get("timestamp", None)
		timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
		value = int(args.get("value", None))
		note = args.get("note", None)

		if value is not None:
			tracker = Tracker.query.filter_by(id=log.tracker_id).first()
			if tracker.tracker_type == "mct":
				if not value in tracker.settings:
					raise BusinessValidationError(400, error_code="BVE09", error_message="value not valid.")
					
			elif tracker.tracker_type == "td":
				try:
					value = value.strftime("%H:%M")
				except:
					raise BusinessValidationError(400, error_code="BVE09", error_message="value not valid.")

			elif tracker.tracker_type == "bool":
				if not (value == 0 or value == 1):
					raise BusinessValidationError(400, error_code="BVE09", error_message="value not valid.")

			elif tracker.tracker_type == "num":
				if not (type(value) is int):
					raise BusinessValidationError(400, error_code="BVE09", error_message="value not valid.")

			log.value = value

		if timestamp is not None:
			log.timestamp = timestamp

		if note is not None:
			log.note = note

		db.session.commit()
		return log

	def delete(self, log_id):
		log = Log.query.filter_by(id=log_id).first()

		# if log does not exists
		if not log:
			raise NotFoundError(status_code=404)

		# if log exists, delete it.
		else:
			db.session.delete(log)
			db.session.commit()

		message = {"message": "Log deleted successfully"}
		return json.dumps(message)