import os
from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_restful import Api

app = None
api=None
def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api=Api(app)
    app.app_context().push()
    return app,api

app,api = create_app()

# Import all the controllers so they are loaded
from application.controllers import *
#Import all restful APIs
from  application.api import TrackerAPI, LogAPI
api.add_resource(TrackerAPI, "/api/tracker/<int:tracker_id>", "/api/<string:username>/tracker")
api.add_resource(LogAPI, "/api/log/<int:log_id>", "/api/<int:tracker_id>/log")

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        debug = True,
        port = 5000
    )