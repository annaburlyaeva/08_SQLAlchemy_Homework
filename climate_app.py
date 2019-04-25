from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# We can view all of the classes that automap found
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp as the value"""

    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=366)
    last_year_precipitation_data = session.query(Measurement.prcp, Measurement.date).\
                                                filter(Measurement.date > query_date).all()
   
    prcp_data = []
    for prcp, date in last_year_precipitation_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        prcp_data.append(prcp_dict)
    

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset"""

    results = session.query(Measurement.station).distinct().all()

    all_stations = [i[0] for i in results]

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""
    # Query all passengers
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=366)
    results = session.query(Measurement.tobs, Measurement.date).\
                                                filter(Measurement.date > query_date).all()
    tobs_data = []
    for tobs, date in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def tobs_start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    tobs_stat_dict = {}
    tobs_stat_dict["tobs_min"] = results[0][0]
    tobs_stat_dict["tobs_max"] = results[0][1]
    tobs_stat_dict["tobs_avg"] = results[0][2]
    
    last = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    temp_list = [start, last[0], tobs_stat_dict]

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end_date).all()
    
    tobs_stat_dict = {}
    tobs_stat_dict["tobs_min"] = results[0][0]
    tobs_stat_dict["tobs_max"] = results[0][1]
    tobs_stat_dict["tobs_avg"] = results[0][2]
        
    temp_list = [start, end, tobs_stat_dict]

    return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)