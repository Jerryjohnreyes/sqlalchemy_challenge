import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite', echo=False)
# Base would be the reflected model to the existing database
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station


#funtion that gives back information

def calc_temps(start_date, end_date,session_obj):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session_obj.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


#print(inspect(engine).get_columns('measurement'))
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List of all available api routes."""
    return (
        f"<strong>Available Routes</strong>:<br/>"
        f"<li> /api/v1.0/precipitation<br/> </li>"
        f"<li> /api/v1.0/stations <br/> </li>"
        f"<li> /api/v1.0/tobs <br/> </li>"
        f"<li> /api/v1.0/2017-01-01 <br/> </li>"
        f"<li> /api/v1.0/2017-07-15/2017-07-30 </li>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #"""Dictionary of Date and Precipitation"""
    # Query date and prcp into a dictionary
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    dictionary = []
    for result in results:
        prcp_dict = {}
        prcp_dict[f"{result.date}"] = result.prcp
        dictionary.append(prcp_dict)

    return jsonify(dictionary)

@app.route("/api/v1.0/stations")
def stations():
    #create our session from python to the DB
    session = Session(engine)
    #query to acces to the stations
    result = session.query(Station.name, Measurement.station)\
                    .join(Station, Measurement.station == Station.station)\
                    .group_by(Measurement.station).all()
    session.close()
    station_list = []
    for item in result:
        station_dict = {}
        station_dict["station"] = item.station
        station_dict["name"] = item.name
        station_list.append(station_dict)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    #create the connectino to the database
    session = Session(engine)
    count_per_station = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station)\
        .order_by(func.count(Measurement.tobs).desc()).all()
    #the most active station is stored at: count_per_station[0][0]
    one_year_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date<= '2017-08-18',\
        Measurement.date >= '2016-08-18', Measurement.station == count_per_station[0][0]).all()
    #saving the results into a dictionay
    session.close()
    dictionary = []
    for result in one_year_temp:
        prcp_dict = {}
        prcp_dict[f"{result.date}"] = result.tobs
        dictionary.append(prcp_dict)

    return jsonify(dictionary)

@app.route("/api/v1.0/<start_d>")
def start_retrieve_temp(start_d):
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date).all()
    #the last date in the DB in stored in: last_date[-1]
    values = calc_temps(f"{start_d}", last_date[-1][0], session)
    dictionary = []
    for value in values:
        diction = {}
        diction["Mininum Temperature"] = value[0]
        diction["Average Temperature"] = value[1]
        diction["Maximun Temperature"] = value[2]
        dictionary.append(diction)
    return jsonify(dictionary)

@app.route("/api/v1.0/<start_d>/<end_d>")
def start_end_retrieve_temp(start_d, end_d):
    session = Session(engine)
    values = calc_temps(f"{start_d}", f"{end_d}", session)
    dictionary = []
    for value in values:
        diction = {}
        diction["Mininum Temperature"] = value[0]
        diction["Average Temperature"] = value[1]
        diction["Maximun Temperature"] = value[2]
        dictionary.append(diction)
    return jsonify(dictionary)

if __name__ == '__main__':
    app.run(debug=True)