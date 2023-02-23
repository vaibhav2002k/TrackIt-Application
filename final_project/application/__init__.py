import os
from flask import Flask
from application import config
from .config import LocalDevelopmentConfig
from .models import db
from flask_restful import Api

app = None
api = None
def create_app():
	# creating app instance
	app = Flask(__name__, template_folder="templates")

	if os.getenv('ENV', "development") == "production":
		print("Set up a production server first!!!")

	else:
		print("Starting Local Server.")

		# Loading Configuration from Python Object.
		app.config.from_object(LocalDevelopmentConfig)

	api = Api(app)
	db.init_app(app)
	app.app_context().push()

	# if database does not exist, create it.
	if not os.path.isfile('./database/tracker.db'):
		db.create_all()

	return app, api
