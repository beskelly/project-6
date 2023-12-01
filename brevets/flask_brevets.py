"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""
import requests
import os
import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations

import logging

###
# Globals
###
app = flask.Flask(__name__)
app.debug = True if "DEBUG" not in os.environ else os.environ["DEBUG"]
myport = True if "PORT" not in os.environ else os.environ["PORT"]
app.logger.setLevel(logging.DEBUG)



#############

API_ADDR = os.environ["API_ADDR"]
API_PORT = os.environ["API_PORT"]
API_URL = f"http://{API_ADDR}:{API_PORT}/api/"

#############

def mybrevet():
    brevets = requests.get(f"{API_URL}/brevets").json()
    curr_brevet = brevets[-1]
    return curr_brevet["length"], curr_brevet["start_time"], curr_brevet["checkpoints"]

def allbrevets():
    brevets = requests.get(f"{API_URL}/brevets").json()
    return brevets

def choosebrevet(id):
    mybrevet = requests.get(f"{API_URL}/brevet/{id}").json()
    return mybrevet

def update(id, total_distance, start_date, gates):
    requests.put(f"{API_URL}/brevet/{id}", json = {"length": total_distance, "start_time": start_date, "checkpoints": gates}).json()
    return

def insertbrevet(total_distance, start_date, gates):
    _id = requests.post(f"{API_URL}/brevets", json = {"length": total_distance, "start_time": start_date, "checkpoints": gates}).json()
    return _id

def delete(id):
    requests.delete(f"{API_URL}/brevet/{id}")
    return

############# 

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")

    km = request.args.get("km", 999, type=float)
    total_distance = request.args.get("total_distance", 200, type=float)
    time = request.args.get("time", arrow.now().isoformat)
    
    app.logger.debug("km = {}".format(km)) 
    app.logger.debug("request.args: {}".format(request.args))
    open_time = acp_times.open_time(km, total_distance, time).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, total_distance, time).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

@app.route("/insert", methods=["POST"])
def insert():
    try:
        myjson = request.json
        total_distance = myjson["total_distance"]
        start_date = myjson["start_date"]
        gates = myjson["gates"]

        newitem = insertbrevet(total_distance, start_date, gates)
        return flask.jsonify(result = {}, message = "Success", status = 1, mongo_id = newitem)

    except:
        return flask.jsonify(result = {}, message = "Error", status = 0, mongo_id = "None")

@app.route("/fetch")
def fetch():
    try:
        total_distance, start_date, gates = mybrevet()
        return flask.jsonify(result = {"total_distance": total_distance, "start_date": start_date, "gates": gates}, status = 1, message = "Data fetched")
    
    except:
        return flask.jsonify(result = {}, status = 0, message = "Error")

@app.route("/api/brevets", methods=["GET", "POST"])
def brevets():
    if request.method == "GET":
        try:
            rtval = []

            for brevet in allbrevets():
                _id = brevet["_id"]["$oid"]
                checkpoints = brevet["checkpoints"]
                length = brevet["length"]
                start_time = brevet["start_time"]
                mydata = {"id": _id, "total_distance": length, "start_date": start_time, "gates": checkpoints}
                rtval.append(mydata)

            return flask.jsonify(rtval)

        except:
            return flask.jsonify(result = {}, status = 0, message = "Error")

    elif request.method == "POST":
        try:
            myjson = request.json
            total_distance = myjson["total_distance"]
            start_date = myjson["start_date"]
            gates = myjson["gates"]
            myid = insertbrevet(total_distance, start_date, gates)

            return flask.jsonify(result = {}, status = 1, message = "Success", mongo_id = myid)

        except:
            return flask.jsonify(result = {}, status = 0, message = "Error", mongo_id = None)

@app.route("/api/brevet/<id>", methods=["GET", "PUT", "DELETE"])
def getbrevet(id):
    if request.method == "GET":
        try:
            brevet = choosebrevet(id)
            _id = brevet["_id"]["$oid"]
            checkpoints = brevet["checkpoints"]
            length = brevet["length"]
            start_time = brevet["start_time"]
            rtval = {"id": _id, "total_distance": length, "start_time": start_time, "gates": checkpoints}

            return flask.jsonify(rtval)

        except:
            return flask.jsonify(result = {}, status = 0, message = "Error")

    elif request.method == "PUT":
        try:
            myjson = request.json
            total_distance = myjson["total_distance"]
            start_date = myjson["start_date"]
            gates = myjson["gates"]
            update(id, total_distance, start_date, gates)
            
            return flask.jsonify(result = {}, status = 1, message = "Success - ID: {id}")

        except:
            return flask.jsonify(result = {}, status = 0, message = "Error")

    elif request.method == "DELETE":
        try:
            delete(id)
            return flask.jsonify(result = {}, status = 1, message = "Deleted - ID: {id}")

        except:
            return flask.jsonify(result = {}, status = 0, message = "Error")

#############
if __name__ == "__main__":
    app.run(port=myport, host="0.0.0.0")
