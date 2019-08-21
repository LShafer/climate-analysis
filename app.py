# import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, request

# create connection to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# Create an app, being sure to pass __name__
app = Flask(__name__)

# show main list of all available routes
@app.route('/')
def welcome():
    return (
        f"Welcome to the Hawaiian Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# route to show a list of dates and precip amounts
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    allprecip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        allprecip.append(precip_dict)
    return jsonify(allprecip)

# route to show list of station names and id numbers
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    stations = session.query(Station.station, Station.name).all()
    session.close()
    
    allstations = []
    for station, name in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        allstations.append(station_dict)
    return jsonify(allstations)


# route to query list of dates and temperature observations
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '08-23-2016').all()
    session.close()

    alltobs = []
    for date, tobs in tobs:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        alltobs.append(tobs_dict)

    return jsonify(alltobs)


# route to query temperature info (min, avg and max) for a given date
@app.route('/api/v1.0/<start>')
def alldates(start):
    
    session = Session(engine)
    # sel code from bonus section in jupyter notebook
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    alldates = (session.query(*sel).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) == start).\
        group_by(Measurement.date).all())
    session.close()
  
    alltemps = []
    for tobs in alldates:
        temps_dict = {}
        temps_dict["date"] = tobs[0]
        temps_dict["tmin"] = tobs[1]
        temps_dict["tavg"] = tobs[2]
        temps_dict["tmax"] = tobs[3]
        alltemps.append(temps_dict)

    return jsonify(alldates)

# route to query temperature info (min, avg and max) for a given range of dates
@app.route('/api/v1.0/<start>/<end>')
def daterange(start, end):

    session = Session(engine)
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    daterange = (session.query(*sel).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).\
        group_by(Measurement.date).all())
    session.close()

    temprange = []
    for tobs in daterange:
        range_dict = {}
        range_dict["date"] = tobs[0]
        range_dict["tmin"] = tobs[1]
        range_dict["tavg"] = tobs[2]
        range_dict["tmax"] = tobs[3]
        temprange.append(range_dict)

    return jsonify(daterange)    

if __name__ == '__main__':
    app.run(debug=True)