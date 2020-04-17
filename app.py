

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import and_, create_engine, func,  desc
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station= Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Honolulu, Hawaii API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start_date<br/>"
        f"/api/v1.0/<str:start_date>/<str:end_date>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session from Python to the Hawaii DB
    session = Session(engine)
    """Return a query from Measurement table and convert the 
       query results to a dictionary using `date` as the key and `prcp` 
       as the value."""
    results= session.query(Measurement.date, Measurement.prcp).\
       filter(and_(Measurement.date > '2016-08-22'), (Measurement.prcp!=None))
    session.close()
    precipitation=[]
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict={date:prcp}
        precipitation.append(precipitation_dict)
    info=['Date', 'Precipitation']
    return jsonify(info, precipitation)
    
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station=  session.query(Measurement.station, Station.name,\
        Station.latitude, Station.longitude, Station.elevation).\
    filter(Measurement.station == Station.station).\
    group_by(Measurement.station).order_by(desc(func.count(Measurement.tobs)))
    session.close()

    stan=[]
    for item in station:
        # s= list(np.ravel(item))
        stan.append(item)
    info= ['Station', 'Name', 'Latitude', 'Longitude', 'Elevation']
    return jsonify(info, stan)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    rec= session.query(Measurement.date, Measurement.tobs).\
        filter(and_(Measurement.date>='2016-08-23'),
               (Measurement.station=='USC00519281')).\
                group_by(Measurement.date)
    session.close()
    temp=[]
    for tobs in rec:
        temp.append(tobs)
    info= ['Date', 'Temperature']
    return jsonify(info, temp)

@app.route("/api/v1.0/temp/<start_date>")
def stats(start_date):
    session= Session(engine)
    result= session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(and_(Measurement.date >= start_date), (Measurement.date <= '2017-08-23')).all()
    session.close()
    
    info= ['Min Temp', 'Max Temp', 'Avg Temp']
    return jsonify(info, result)

@app.route("/api/v1.0/temp/<startdate>/<enddate>") 
def calc(startdate, enddate):
    
    session= Session(engine)
    aa= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(and_(Measurement.date >= startdate),(Measurement.date <= enddate)).all()
    session.close()
    
    return jsonify(aa)
    


if __name__ == "__main__":
    app.run(debug=True)
