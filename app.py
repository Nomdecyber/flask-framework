from flask import Flask, render_template, request, redirect,Markup
from datetime import date, timedelta
import requests
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource

#port = int(os.environ.get("PORT",5000))
app = Flask(__name__)

@app.route('/index',methods=['GET','POST'])
def index():
  if request.method == 'GET':
    return render_template('index.html', placeholder='GOOG')
  else:
    apiKey = "tmRqcoTZhAiTzz5pZp9g"
    startingDate = date.today() - timedelta(30)
    ticker = request.form['ticker'].upper()
    params = {
      'ticker': ticker,
      'api_key': apiKey,
      'qopts.columns': 'date,close',
      'date.gte': startingDate.isoformat()
    }

    req = requests.get('https://www.quandl.com/api/v3/datatables/WIKI/PRICES', params=params)

    response = req.json()
    if ('datatable' not in response) or ('data' not in response['datatable']) or (len(response['datatable']['data']) == 0):
      errorDiv = "<div><p>Error getting data for ticker " + ticker + "</p></div>"
      return render_template('index.html', bokehdiv=Markup(errorDiv),
                             placeholder='GOOG')
    df = pd.DataFrame(response['datatable']['data'],columns=['Date','Closing'])
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date')

    data = ColumnDataSource(df)
    plot = figure(x_axis_type="datetime",
                  title="Daily closing prices for " + ticker)
    plot.xaxis.axis_label = 'Date'
    plot.yaxis.axis_label = 'Closing Price (USD)'
    plot.line(x = "Date", y="Closing", source=data)
    script, div = components(plot)
    
    return render_template('index.html', bokehdiv=Markup(div),
                           bokehscript=Markup(script),placeholder=ticker)
    
      

@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port = 5000, debug = True)
