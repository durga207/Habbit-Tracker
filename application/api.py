from flask_restful import Resource
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from application.validation import BusinessValidationError, NotFoundError
from application.models import User, Tracker, Log
from application.database import db
from flask import abort

create_tracker_parser = reqparse.RequestParser()
create_tracker_parser.add_argument("tracker_name")
create_tracker_parser.add_argument("tracker_type")
create_tracker_parser.add_argument("settings")
create_tracker_parser.add_argument("tracker_description")

update_tracker_parser = reqparse.RequestParser()
update_tracker_parser.add_argument("tracker_name")
update_tracker_parser.add_argument("tracker_description")

create_log_parser = reqparse.RequestParser()
create_log_parser.add_argument("time_stamp")
create_log_parser.add_argument("value")
create_log_parser.add_argument("note")

update_log_parser = reqparse.RequestParser()
update_log_parser.add_argument("time_stamp")
update_log_parser.add_argument("value")
update_log_parser.add_argument("note")


tracker_fields = {
    'tracker_id': fields.Integer,
    'user_id': fields.Integer,
    'tracker_name': fields.String,
    'tracker_description': fields.String,
    'tracker_type': fields.String,
    'settings' :fields.String
}

log_fields = {
    "log_id": fields.Integer,
    "user_id": fields.Integer,
    "tracker_id": fields.Integer,
    "time_stamp": fields.String,
    "value": fields.String,
    "note": fields.String
}
class TrackerAPI(Resource):
    @marshal_with(tracker_fields)
    def get(self,tracker_id):
        tracker=Tracker.query.filter_by(tracker_id=tracker_id).scalar()
        if tracker:
            return tracker,200
        else:
            raise NotFoundError(status_code = 404,x="Tracker")


    @marshal_with(tracker_fields)
    def put(self, tracker_id):     
        tracker=Tracker.query.filter_by(tracker_id=tracker_id).scalar()
        
        if tracker is None:
            raise NotFoundError(status_code= 404, x="Tracker")
        
        args = update_tracker_parser.parse_args()
        tracker_name = args.get("tracker_name", None)
        tracker_description = args.get("tracker_description", None)
        
        if (tracker_name is None or tracker_name==""):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "TRACKER001",
                error_message= "Tracker Name is required"                
            )
        
        tracker.tracker_name = tracker_name
        tracker.tracker_description = tracker_description
        db.session.commit()
        return tracker,200

    @marshal_with(tracker_fields)
    def post(self, username):     
        args = create_tracker_parser.parse_args()
        tracker_name = args.get("tracker_name", None)
        tracker_type = args.get("tracker_type", None)
        settings = args.get("settings", None)
        tracker_description = args.get("tracker_description", None)

        if tracker_name is None or tracker_name == "":
            raise BusinessValidationError(status_code= 400,
                error_code= "TRACKER001",
                error_message= "Tracker Name is required"                
            )
        
        if (tracker_type is None or tracker_type == "") or not(isinstance(tracker_type,str)):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "TRACKER002",
                error_message= "Tracker Type is required and should be string."                
            )
            
        user=User.query.filter_by(username=username).scalar()
        tracker = Tracker(
            user_id = user.user_id,
            tracker_name = tracker_name,
            tracker_type = tracker_type,
            settings = settings,
            tracker_description = tracker_description
        )
        
        db.session.add(tracker)
        db.session.commit()
                
        return tracker,201
    
    def delete(self,tracker_id):        
        tracker=Tracker.query.filter_by(tracker_id=tracker_id).scalar()
        if tracker is None:
            raise NotFoundError(status_code= 404, x="Tracker")
        logs = Log.query.filter(Log.tracker_id == tracker_id).all()
        for log in logs:
            db.session.delete(log)
        db.session.commit()
        db.session.delete(tracker)
        db.session.commit()
        return "",200
       

class LogAPI(Resource):
    @marshal_with(log_fields)
    def get(self, log_id):
        log=Log.query.filter_by(log_id=log_id).scalar()
        if log:
            return log,200
        else:
            raise NotFoundError(status_code = 404, x="Log")


    @marshal_with(log_fields)
    def put(self,log_id):     
        log=Log.query.filter_by(log_id=log_id).scalar()
        
        if log is None:
            raise NotFoundError(status_code= 404, x="Log")
        
        args = update_log_parser.parse_args()
        time_stamp = args.get("time_stamp", None)
        value = args.get("value", None)
        note = args.get("note", None)

        if (time_stamp is None or time_stamp==""):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "LOG001",
                error_message= "Time stamp is required"                
            )
        if (value is None or value==""):
            raise BusinessValidationError(
                status_code= 400,
                error_code= "LOG002",
                error_message= "Value is required"                
            )
        
        log.time_stamp=time_stamp
        log.value=value
        log.note = note
        db.session.commit()
        return log,200
       

    @marshal_with(log_fields)
    def post(self, tracker_id):
        args = create_log_parser.parse_args()
        print(args)
        time_stamp = args.get("time_stamp", None)
        value = args.get("value", None)
        note = args.get("note", None)
        tracker=Tracker.query.filter_by(tracker_id=tracker_id).scalar()

        log = Log.query.filter(Log.time_stamp==time_stamp, Log.value==value, Log.tracker_id==tracker_id).scalar()
        if log is not None:
            abort(409, "Log already exists")

        if time_stamp is None or time_stamp=="":
            raise BusinessValidationError(
                status_code= 400,
                error_code= "LOG001",
                error_message= "Time stamp is required"          
            )
        
        if value is None or value=="":
            raise BusinessValidationError(
                status_code= 400,
                error_code= "LOG002",
                error_message= "Value is required"                
            )
        
        log = Log(
            user_id = tracker.user_id,
            tracker_id = tracker_id,
            time_stamp = time_stamp,
            value = value,
            note = note
        )
        print(log)
        db.session.add(log)
        db.session.commit()
        return log,201
         

    def delete(self,log_id):        
        log = Log.query.filter(Log.log_id == log_id).scalar()
        if log is None:
            raise NotFoundError(status_code= 404, x="Log")
        db.session.delete(log)
        db.session.commit()
        return "",200
