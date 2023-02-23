import os
# basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	# Declared a parent class. This can be used when multiple Config class are present.
	SECRET_KEY = None

class LocalDevelopmentConfig():
	# Local Development Configurations to be sent to WSGI object.
	SQLITE_DB_DIR = './database'
	SQLALCHEMY_DATABASE_URI = "sqlite:///./database/tracker.db"
	DEBUG = True