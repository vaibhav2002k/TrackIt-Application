from application import create_app
from flask_bcrypt import Bcrypt

app, api = create_app()
bcrypt = Bcrypt(app)
app.config["SECRET_KEY"] = 'e4f8208f58546222c432c8a0'

# Warning: Always import controllers after app creation to avoid circular imports.
from application.controllers import *

from application.api import UserAPI, TrackerAPI, LogAPI
api.add_resource(UserAPI, "/api/user", "/api/user/<string:username>")
api.add_resource(TrackerAPI, "/api/tracker", "/api/tracker/<int:tracker_id>")
api.add_resource(LogAPI, "/api/log", "/api/log/<int:log_id>")


if __name__ == '__main__':

  print("Running Flask App")
  app.run(host='0.0.0.0', port=8080)


