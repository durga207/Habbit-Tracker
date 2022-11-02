import datetime
from flask import render_template, request
from flask import current_app as app
from application.models import User,Tracker,Log
from werkzeug.utils import redirect
from .database import db
from sqlalchemy.sql.expression import func
import csv
from datetime import date,datetime as dt
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
from dateutil.relativedelta import relativedelta

matplotlib.use('Agg')
@app.route("/", methods=["GET"])
def home():
    return render_template("signin.html")

@app.route("/signin", methods=["GET","POST"])
def signin():
    if request.method=="GET":
        return render_template("signin.html")
    elif request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        user=User.query.filter_by(username=username).scalar()
        if username=="":
            error="Please enter your username and password"
            return render_template("signin.html",error=error)
        if user== None:
            error="You do not have an account"
            return render_template("signin.html",error=error)
        if user.password==password:
            return redirect("/"+username+"/trackers/display")
        else:
            error="Your Username and Password do not match. Please Try Again"
            return render_template("signin.html",error=error)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="GET":
        return render_template("register.html")
    elif request.method=="POST" :
        username=request.form["username"]
        name=request.form["name"]
        password= request.form["password"]
        confirm_pass=request.form["confirm_pass"]
        user=User.query.filter_by(username=username).scalar()
        if user!=None:
            error="User already exists"
            return render_template("register.html",error=error)
        if password==confirm_pass:
            new_user = User(username=username, name=name, password=password)
            db.session.add(new_user)
            db.session.commit()
            User.query.filter_by(username=username).scalar()
            return redirect("/"+username+"/trackers/display")
        if password!=confirm_pass:
            error="Password mismatch"
            return render_template("register.html",error=error)


@app.route("/<string:username>/trackers/display", methods=["GET","POST"])
def display_trackers(username):
    if request.method=="GET":
        user=User.query.filter_by(username=username).scalar()
        trackers=db.session.query(Tracker).filter_by(user_id=user.user_id).all()
        latest_logs= db.session.query(Log.tracker_id,func.max(Log.time_stamp),Log.time_stamp,Log.value,Log.log_id).filter_by(user_id=user.user_id).group_by(Log.tracker_id).all()
        return render_template("tracker_display.html",username=username, name=user.name, trackers=trackers,latest_logs=latest_logs)

@app.route("/<string:username>/tracker/add", methods=["GET","POST"])
def add_tracker(username):
    user=User.query.filter_by(username=username).scalar()
    if request.method=="GET":
        return render_template("add_tracker.html",name=user.name, username=username)
    if request.method=="POST":
        tracker_name=request.form["tracker_name"]
        desc=request.form["description"]
        tracker_type = request.form["tracker_type"]
        settings = request.form["settings"]
        new_tracker = Tracker(user_id=user.user_id, tracker_name=tracker_name, tracker_description=desc, tracker_type=tracker_type, settings=settings)
        
        db.session.add(new_tracker)
        db.session.commit()
        return redirect("/"+username+"/trackers/display")


@app.route("/<string:username>/tracker/<int:tracker_id>/delete", methods=["GET","POST"])
def delete_tracker(username,tracker_id):
    if request.method=="GET":    
        db.session.query(Log).filter_by(tracker_id=tracker_id).delete()
        db.session.commit()
        Tracker.query.filter_by(tracker_id=tracker_id).delete()
        db.session.commit()
        return redirect("/"+username+"/trackers/display")

@app.route("/<string:username>/tracker/<int:tracker_id>/edit", methods=["GET","POST"])
def edit_tracker(username,tracker_id):
    user=User.query.filter_by(username=username).scalar()
    tracker=Tracker.query.filter_by(tracker_id=tracker_id,user_id=user.user_id).scalar()

    if request.method=="GET":
        return render_template("edit_tracker.html",username=username,tracker=tracker)
    if request.method=="POST":
        tracker_name=request.form["tracker_name"]
        desc=request.form["description"]
        tracker_type = request.form["tracker_type"]
        settings = request.form["settings"]
        Tracker.query.filter_by(tracker_id=tracker_id,user_id=user.user_id).update({Tracker.tracker_name : tracker_name, Tracker.tracker_description : desc, Tracker.tracker_type : tracker_type, Tracker.settings:settings})
        db.session.commit()
        return redirect("/"+username+"/trackers/sdisplay")

@app.route("/<string:username>/tracker/<int:tracker_id>/view", methods=["GET","POST"])
def view_tracker(username,tracker_id):
    user=User.query.filter_by(username=username).scalar()
    tracker=Tracker.query.filter_by(tracker_id=tracker_id,user_id=user.user_id).scalar()
    if request.method=="GET":
        return render_template("view_tracker.html",username=username,tracker=tracker)
    
@app.route("/<string:username>/tracker/<int:tracker_id>/log/add", methods=["GET","POST"])
def add_log(username,tracker_id):
    user=User.query.filter_by(username=username).scalar()
    tracker=Tracker.query.filter_by(tracker_id=tracker_id).scalar()
    settings=(tracker.settings).split(',')
    settings=[x.strip(' ') for x in settings]
    if request.method=="GET":
        return render_template("add_log.html",username=username,tracker=tracker,settings=settings)
    if request.method=="POST":
        time_stamp=request.form["timestamp"]
        value=request.form["value"]
        note=request.form["note"]
        new_log=Log(user_id=user.user_id,tracker_id=tracker_id,time_stamp=time_stamp,value=value,note=note)
        db.session.add(new_log)
        db.session.commit()
        return redirect("/"+username+"/trackers/display")

@app.route("/<string:username>/tracker/<int:tracker_id>/log/view", methods=["GET","POST"])
def view_logs(username,tracker_id):
    if request.method=="GET":
        user=User.query.filter_by(username=username).scalar()
        tracker=Tracker.query.filter_by(tracker_id=tracker_id,user_id=user.user_id).scalar()
        logs=Log.query.filter_by(tracker_id=tracker_id,user_id=user.user_id).order_by(Log.time_stamp).all()
        return render_template("logs.html",username=username,name=user.name,tracker=tracker,logs=logs)

@app.route("/<string:username>/tracker/<int:tracker_id>/log/<int:log_id>/edit", methods=["GET","POST"])
def edit_log(username,tracker_id,log_id):
    user=User.query.filter_by(username=username).scalar()
    tracker=Tracker.query.filter_by(tracker_id=tracker_id,user_id=user.user_id).scalar()
    log=Log.query.filter_by(log_id=log_id).scalar()
    settings=(tracker.settings).split(',')
    settings=[x.strip(' ') for x in settings]
    if request.method=="GET":
        return render_template("edit_log.html",username=username,tracker=tracker,log=log,settings=settings)
    if request.method=="POST":
        time_stamp=request.form["timestamp"]
        value=request.form["value"]
        note=request.form["note"]
        Log.query.filter_by(log_id=log_id).update({Log.time_stamp : time_stamp, Log.value : value, Log.note :note })
        db.session.commit()
        return redirect("/"+username+"/tracker/"+str(tracker_id)+"/log/view")

@app.route("/<string:username>/tracker/<int:tracker_id>/log/<int:log_id>/delete", methods=["GET","POST"])
def delete_log(username,tracker_id,log_id):
    if request.method=="GET":
        Log.query.filter_by(log_id=log_id).delete()
        db.session.commit()
        return redirect(("/"+username+"/tracker/"+str(tracker_id)+"/log/view"))

@app.route("/<string:username>/tracker/<int:tracker_id>/log/view-today", methods=["GET","POST"])
def today_log(username,tracker_id):
    if request.method=="GET":
        filePath = 'static/trendline.jpeg'
        if os.path.exists(filePath):
            os.remove(filePath)
        user=User.query.filter_by(username=username).scalar()
        tracker=Tracker.query.filter_by(tracker_id=tracker_id,user_id=user.user_id).scalar()
        logs=Log.query.filter_by(tracker_id=tracker_id,user_id=user.user_id).all()
        today=db.session.query(Log).filter(func.date(Log.time_stamp)== date.today(),Log.tracker_id==tracker_id).order_by(Log.time_stamp).all()
        print(today)
        if today!=[]:
            plt.clf()
            fig, ax = plt.subplots()
            majorFmt = mdates.DateFormatter('%H:%M')  
            locator = mdates.HourLocator()
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(majorFmt)
            plt.xticks(rotation=45)
        
            x_values = [dt.strptime(x.time_stamp[:16], "%Y-%m-%dT%H:%M") for x in today]
            if tracker.tracker_type=="Multiple Choice" or tracker.tracker_type=="Boolean":
                y_values = [y.value for y in today]
                plt.ylabel("Value")

            elif tracker.tracker_type=="Time Duration":
                y_values = [y.value for y in today]
                y_values = [int(y[0:2])*60*60+int(y[3:5])*60+int(y[6:]) for y in y_values]
                y_values = [y/60 for y in y_values]
                plt.ylabel("Value (in min)")
            else:
                y_values = [int(y.value) for y in today]
                plt.ylabel("Value")

            plt.plot(x_values,y_values,marker='o')
            ax.set_xlim((np.datetime64(today[0].time_stamp[:10]+ ' 00:00'), np.datetime64(today[0].time_stamp[:10]+ ' 23:59')))
            plt.xlabel("Time")
            plt.savefig("static/trendline.jpeg",bbox_inches='tight')
        return render_template("view_trends.html",username=username,tracker=tracker,logs=logs,name=user.name)

@app.route("/<string:username>/tracker/<int:tracker_id>/log/view-week", methods=["GET","POST"])
def week_log(username,tracker_id):
    if request.method=="GET":
        user=User.query.filter_by(username=username).scalar()
        tracker=Tracker.query.filter_by(tracker_id=tracker_id,user_id=user.user_id).scalar()
        logs=Log.query.filter_by(tracker_id=tracker_id,user_id=user.user_id).all()
        current_time = datetime.datetime.utcnow()
        week_ago = current_time - datetime.timedelta(weeks=1)
        week=db.session.query(Log).filter(Log.time_stamp>week_ago,Log.tracker_id==tracker_id).order_by(Log.time_stamp).all()
        if week!=[]:
            plt.clf()
            fig, ax = plt.subplots()
            majorFmt = mdates.DateFormatter("%Y-%m-%d")  
            locator = mdates.AutoDateLocator()
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(majorFmt)
            plt.xticks(rotation=45)
        
            x_values = [dt.strptime(x.time_stamp[:16], "%Y-%m-%dT%H:%M") for x in week]
            if tracker.tracker_type=="Multiple Choice" or tracker.tracker_type=="Boolean":
                y_values = [y.value for y in week]
                plt.ylabel("Value")

            elif tracker.tracker_type=="Time Duration":
                y_values = [y.value for y in week]
                y_values = [int(y[0:2])*60*60+int(y[3:5])*60+int(y[6:]) for y in y_values]
                y_values = [y/60 for y in y_values]
                plt.ylabel("Value (in min)")
            else:
                y_values = [int(y.value) for y in week]
                plt.ylabel("Value")

            plt.plot(x_values,y_values,marker='o')
            ax.set_xlim((np.datetime64(str(week_ago)[:10]), np.datetime64(str(current_time)[:10])+1))
            plt.xlabel("Time")
            plt.savefig("static/trendline.jpeg",bbox_inches='tight')
        return render_template("view_trends.html",username=username,tracker=tracker,logs=logs,name=user.name)

@app.route("/<string:username>/tracker/<int:tracker_id>/log/view-month", methods=["GET","POST"])
def month_log(username,tracker_id):
    if request.method=="GET":
        user=User.query.filter_by(username=username).scalar()
        tracker=Tracker.query.filter_by(tracker_id=tracker_id,user_id=user.user_id).scalar()
        logs=Log.query.filter_by(tracker_id=tracker_id,user_id=user.user_id).all()
        current_time = datetime.datetime.utcnow()
        month_ago = current_time +relativedelta(months=-1)
        month=db.session.query(Log).filter(Log.time_stamp>month_ago,Log.tracker_id==tracker_id).order_by(Log.time_stamp).all()
        if month!=[]:
            plt.clf()
            fig, ax = plt.subplots()
            majorFmt = mdates.DateFormatter("%Y-%m-%d")  
            locator = mdates.AutoDateLocator()
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(majorFmt)
            plt.xticks(rotation=45)
        
            x_values = [dt.strptime(x.time_stamp[:16], "%Y-%m-%dT%H:%M") for x in month]
            if tracker.tracker_type=="Multiple Choice" or tracker.tracker_type=="Boolean":
                y_values = [y.value for y in month]
                plt.ylabel("Value")

            elif tracker.tracker_type=="Time Duration":
                y_values = [y.value for y in month]
                y_values = [int(y[0:2])*60*60+int(y[3:5])*60+int(y[6:]) for y in y_values]
                y_values = [y/60 for y in y_values]
                plt.ylabel("Value (in min)")
            else:
                y_values = [int(y.value) for y in month]
                plt.ylabel("Value")

            plt.plot(x_values,y_values,marker='o')
            ax.set_xlim((np.datetime64(str(month_ago)[:10]), np.datetime64(str(current_time)[:10])+2))
            plt.xlabel("Time")
            plt.savefig("static/trendline.jpeg",bbox_inches='tight')
        return render_template("view_trends.html",username=username,tracker=tracker,logs=logs,name=user.name)

@app.route("/<string:username>/tracker/<int:tracker_id>/log/export", methods=['GET', 'POST'])
def export(username,tracker_id):
    data = db.session.query(Log.time_stamp,Log.value,Log.note).filter_by(tracker_id=tracker_id).all()
    with open('Tracker'+str(tracker_id)+'_logs_export.csv','w') as f:
        writer_obj = csv.writer(f)
        writer_obj.writerow(["Timestamp","Value","Note"])
        for row in data:
            writer_obj.writerow(row)
    return redirect(("/"+username+"/tracker/"+str(tracker_id)+"/log/view"))

@app.route("/<string:username>/tracker/<int:tracker_id>/log/import", methods=['GET', 'POST'])
def import_log(username,tracker_id):
    user=User.query.filter_by(username=username).scalar()
    with open('Tracker'+str(tracker_id)+'_logs_import.csv','r') as f:
        reader_obj = csv.reader(f)
        count=1
        for row in reader_obj:
            if count==1:
                count=0
                continue
            new_log=Log(user_id=user.user_id,tracker_id=tracker_id,time_stamp=row[0],value=row[1],note=row[2])
            db.session.add(new_log)
            db.session.commit()
    return redirect(("/"+username+"/tracker/"+str(tracker_id)+"/log/view"))

@app.route("/<string:username>/tracker/<int:tracker_id>/log/download_template", methods=['GET', 'POST'])
def download_template(username,tracker_id):
    with open('Tracker'+str(tracker_id)+'_logs_import.csv','w') as f:
        writer_obj = csv.writer(f)
        writer_obj.writerow(["Timestamp","Value","Note"])
    return redirect(("/"+username+"/tracker/"+str(tracker_id)+"/log/view"))
