from math import dist
from os import name, stat
import re
from typing import ValuesView
import flask
from flask import Flask, render_template, request, redirect, url_for
import requests
import pandas as pd
import plotly
import plotly.express as px
import json
import csv
from flask import Flask, render_template, jsonify, request, flash
from flask_mysqldb import MySQL,MySQLdb 
import psycopg2 
import pandas as pd
import json


# Create Flask's `app` object
app = Flask(
    __name__,
    template_folder="templates"
)

@app.route("/" )
def index():
    return render_template('index.html')

state = ''
commodity = ''
sdistrict = ''
variety = ""



app.secret_key = "caircocoders-ednalan"
      
app.config['MYSQL_HOST'] = 'postgresql://postgres:12345@localhost/commodity'

app.config['MYSQL_DB'] = 'prices'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
   
@app.route('/graphs.html')
def main():
    con = psycopg2.connect(
        host = "localhost",
        database = "commodity",
        user = "postgres",
        password = 12345
    )
    cur = con.cursor()
    result = cur.execute("SELECT DISTINCT state from prices order by state")
    state = cur.fetchall()
    state_list = []
    for value in state:
        state_list.append(value[0])
   
    return render_template('graphs.html', state=state_list)


@app.route("/district/<state>")
def district(state):  
    
    con = psycopg2.connect(
        host = "localhost",
        database = "commodity",
        user = "postgres",
        password = 12345
    )
    cur = con.cursor()
    
    result = cur.execute("SELECT DISTINCT district FROM prices WHERE state = %s ORDER BY district ASC", [state] )
    district_value = cur.fetchall()  
    
    OutputArray = []
    for row in district_value:
        OutputArray.append(row)
    return jsonify({'districtArray': OutputArray})


@app.route("/market/<district>")
def market(district):  
    
    con = psycopg2.connect(
        host = "localhost",
        database = "commodity",
        user = "postgres",
        password = 12345
    )
    cur = con.cursor()
    
    result = cur.execute("SELECT DISTINCT market FROM prices WHERE district = %s ORDER BY market ASC", [district] )
    commodity_value = cur.fetchall()  
    
    OutputArray = []
    for row in commodity_value:
        OutputArray.append(row)

    return jsonify({'marketArray': OutputArray})



@app.route("/commodity/<market>")
def commodity(market):  
    
    con = psycopg2.connect(
        host = "localhost",
        database = "commodity",
        user = "postgres",
        password = 12345
    )
    cur = con.cursor()
    
    result = cur.execute("SELECT DISTINCT commodity FROM prices WHERE market = %s ORDER BY commodity ASC", [market] )
    commodity_value = cur.fetchall()  
    
    OutputArray = []
    for row in commodity_value:
        OutputArray.append(row)

    return jsonify({'commodityArray': OutputArray})


@app.route("/variety/<commodity>")
def variety(commodity):  
    
    con = psycopg2.connect(
        host = "localhost",
        database = "commodity",
        user = "postgres",
        password = 12345
    )
    cur = con.cursor()
    
    result = cur.execute("SELECT DISTINCT variety FROM prices WHERE commodity = %s ORDER BY variety ASC", [commodity] )
    commodity_value = cur.fetchall()  
    
    OutputArray = []
    for row in commodity_value:
        OutputArray.append(row)

    return jsonify({'varietyArray': OutputArray})


def plotprice(state, district, market, commodity, variety) :
    str1 = 'static/csv/06-05-2021 Mandi Rates.csv'
    df = pd.read_csv(str1)
    # df= df[df['state']== state]
    # df = df[df['district']== district] 
    # df = df[df['market']== market]
    # df = df[df['commodity']== commodity]
    # df = df[df['variety']== variety]
    values = df[(df['state']== state) & (df['district']== district)  & (df['commodity']== commodity) & (df['variety']== variety)][['market','modal_price','min_price', 'max_price']]
    price = px.bar(values, x="market", y=[ 'modal_price'])
    priceJSON = json.dumps(price, cls=plotly.utils.PlotlyJSONEncoder)
    return priceJSON

def historicalprice(item,state,sdistrict,market1) :
    str1 = 'static/csv/Tomato15-21.csv'
    df = pd.read_csv(str1)
    df['Arrival_Date'] = pd.to_datetime(df['Arrival_Date'])
    df= df[df['Commodity']== item]
    df = df[df['State']== state] 
    df = df[df['District']== sdistrict]
    df= df[df['Market']== market1]
    df = pd.concat([
	            df['Arrival_Date'],
	            df['Modal_x0020_Price'],
                ], axis=1)
    df = df.sort_values(['Arrival_Date'])
    histprice = px.line(df, x="Arrival_Date", y="Modal_x0020_Price", labels={ "Arrival_Date": "Years", "Modal_x0020_Price": "Average Price (Rs)"})
    histpriceJSON = json.dumps(histprice, cls=plotly.utils.PlotlyJSONEncoder)
    return histpriceJSON

@app.route("/forecast.html" , methods = ['POST', 'GET'])
def forecast():
    return render_template("/forecast.html")


@app.route("/graphs" , methods = ['POST', 'GET'])
def graphs():
    if request.method == 'POST' :
        state = request.form.get('state')
        district =  request.form.get('district')
        market = request.form.get('market')
        commodity = request.form.get('commodity')
        variety = request.form.get('variety')
        
    
    # Ploting graphs
        priceJSON= plotprice(state, district, market, commodity, variety)
    try:
        return render_template('graphs.html', price = priceJSON )
    except:
        return redirect(url_for('main'))


@app.route("/histgraphs" , methods = ['POST', 'GET'])
def histgraphs():
   
    if request.method == 'POST' :
        state = request.form['state']
        commodity =  request.form['item']
        sdistrict = request.form['sdistrict']
        market1 = request.form['market1']
    else :
        state = 'Punjab'
        sdistrict = 'Bhatinda'
        market1 = 'Maur'
        commodity = 'Tomato'

    # Ploting graphs
    histpriceJSON= historicalprice(commodity,state,sdistrict,market1)
    
    return render_template('graphs.html', histprice = histpriceJSON , data=commodity, State = state,sdistrict = sdistrict, market1 = market1)



@app.route('/render', methods = ['POST' , 'GET'])
def render():
    if request.method == 'POST':
        results = []
        #user_csv = request.form.get('user_csv').split('\n')
        reader = csv.DictReader(open('static/csv/06-05-2021 Mandi Rates.csv'))
        
        for row in reader:
            results.append(dict(row))

        fieldnames = [key for key in results[0].keys()]

        return render_template('index.html', results=results, fieldnames=fieldnames, len=len)


if __name__ == '__main__':
    app.run(debug=True)