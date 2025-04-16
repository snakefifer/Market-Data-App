from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import requests

app = Flask(__name__)
CORS(app)

API_KEY = '88e12fc888293e6c01a7246e02ec8fdf'

tickers_indexes = {
    'S&P 500': '^GSPC',
    'Dow Jones': '^DJI',
    'NASDAQ': '^IXIC',
    'Russell 2000': '^RUT',
}

tickers_commodities = {
    'Gold': 'GC=F',
    'Silver': 'SI=F',
    'Oil (Crude)': 'CL=F'
}

tickers_treasury = {
    '2 Year Treasury': '2YY=F',
    '5 Year Treasury': '^FVX',
    '10 Year Treasury': '^TNX',
    '30 Year Treasury': '^TYX'
}

tickers_forex = {
    'USD/EUR': 'USDEUR=X',
    'USD/POUND': 'USDGBP=X',
    'USD/YEN': 'USDJPY=X'
}

tickers_crypto = {
    'BTC-USD': 'BTC-USD',
    'ETH-USD': 'ETH-USD',
    'SOL-USD': 'SOL-USD'
}

def fetch_yfinance_data(tickers, format_func, absolute_change=False):
    results = {}
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='5d')
            if len(data) < 2:
                latest_close = data['Close'].iloc[-1]
                change_str = 'Error'
            else:
                latest_close = data['Close'].iloc[-1]
                previous_close = data['Close'].iloc[-2]
                if absolute_change:
                    change_val = latest_close - previous_close
                    change_str = f'{change_val:+.3f}'
                else:
                    percent_change = ((latest_close - previous_close) / previous_close) * 100
                    change_str = f'{percent_change:+.2f}%'
            price_str = format_func(name, latest_close)
            results[name] = {'price': price_str, 'change': change_str}
        except Exception:
            results[name] = {'price': 'Error', 'change': 'Error'}
    return results

def format_index_price(name, price):
    return f'{price:,.2f}'

def format_commodity_price(name, price):
    return f'${price:,.2f}'

def format_treasury_price(name, price):
    return f'{price:.3f}%'

def format_forex_price(name, price):
    return f'{price:,.3f}'

def format_crypto_price(name, price):
    return f'${price:,.2f}'

def fetch_fed_data():
    cpi_data = requests.get(f'https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={API_KEY}&file_type=json&sort_order=desc&units=pc1&limit=10').json()
    latest_inflation = float(cpi_data['observations'][0]['value'])
    previous_inflation = float(cpi_data['observations'][1]['value'])
    inflation_change = latest_inflation - previous_inflation
    latest_inflation = f'{latest_inflation:.3f}%'
    inflation_change = f'{inflation_change:+.3f}'
    real_gdp_data = requests.get(f'https://api.stlouisfed.org/fred/series/observations?series_id=GDPC1&api_key={API_KEY}&file_type=json&sort_order=desc&units=pc1&limit=10').json()
    latest_real_gdp = float(real_gdp_data['observations'][0]['value'])
    previous_real_gdp = float(real_gdp_data['observations'][1]['value'])
    real_gdp_change = latest_real_gdp - previous_real_gdp
    real_gdp = f'{latest_real_gdp:.3f}%'
    real_gdp_change = f'{real_gdp_change:+.3f}'
    unemployment_data = requests.get(f'https://api.stlouisfed.org/fred/series/observations?series_id=UNRATE&api_key={API_KEY}&file_type=json&sort_order=desc&limit=10').json()
    latest_unemployment = float(unemployment_data['observations'][0]['value'])
    previous_unemployment = float(unemployment_data['observations'][1]['value'])
    unemployment_change = latest_unemployment - previous_unemployment
    unemployment = f'{latest_unemployment:.2f}%'
    unemployment_change = f'{unemployment_change:+.2f}'
    lower_fed_target_data = requests.get(f'https://api.stlouisfed.org/fred/series/observations?series_id=DFEDTARL&api_key={API_KEY}&file_type=json&sort_order=desc&limit=365').json()
    upper_fed_target_data = requests.get(f'https://api.stlouisfed.org/fred/series/observations?series_id=DFEDTARU&api_key={API_KEY}&file_type=json&sort_order=desc&limit=365').json()
    lower_fed_target = lower_fed_target_data['observations'][0]['value']
    upper_fed_target = upper_fed_target_data['observations'][0]['value']
    rate_change_date = 'N/A'
    lower_change_bps = 0
    for i in range(1, len(lower_fed_target_data['observations'])):
        latest_lower = float(lower_fed_target_data['observations'][i - 1]['value'])
        previous_lower = float(lower_fed_target_data['observations'][i]['value'])
        latest_upper = float(upper_fed_target_data['observations'][i - 1]['value'])
        previous_upper = float(upper_fed_target_data['observations'][i]['value'])
        if latest_lower != previous_lower or latest_upper != previous_upper:
            rate_change_date = lower_fed_target_data['observations'][i - 1]['date']
            lower_change_bps = (latest_lower - previous_lower)
            break
    rate_change_date = rate_change_date[-5:]
    mortgage_30_data = requests.get(f'https://api.stlouisfed.org/fred/series/observations?series_id=MORTGAGE30US&api_key={API_KEY}&file_type=json&sort_order=desc&limit=10').json()
    latest_mortgage_30 = float(mortgage_30_data['observations'][0]['value'])
    previous_mortgage_30 = float(mortgage_30_data['observations'][1]['value'])
    mortgage_30_change = latest_mortgage_30 - previous_mortgage_30
    mortgage_30 = f'{latest_mortgage_30:.2f}%'
    mortgage_30_change = f'{mortgage_30_change:+.2f}'
    sofr_data = requests.get(f'https://api.stlouisfed.org/fred/series/observations?series_id=SOFR&api_key={API_KEY}&file_type=json&sort_order=desc&limit=10').json()
    observations = sofr_data['observations']
    latest_sofr = float(observations[0]['value'] if observations[0]['value'] != '.' else observations[1]['value'])
    previous_sofr = float(observations[1]['value'] if observations[1]['value'] != '.' else observations[2]['value'])
    sofr_change = latest_sofr - previous_sofr
    return {
        'Inflation Rate (M/M)': {
            'price': latest_inflation,
            'change': inflation_change
        },
        'Real GDP Growth (Q/Q)': {
            'price': real_gdp,
            'change': real_gdp_change
        },
        'Unemployment Rate (M/M)': {
            'price': unemployment,
            'change': unemployment_change
        },
        f'Fed Target Range ({rate_change_date})': {
            'price': f'{lower_fed_target} - {upper_fed_target}',
            'change': f'{lower_change_bps:+.2f}'
        },
        'Secured Overnight Financing Rate': {
            'price': latest_sofr,
            'change': f'{sofr_change:+.2f}'
        },
        '30 Year Mortgage Rate (W/W)': {
            'price': mortgage_30,
            'change': mortgage_30_change
        }
    }

@app.route('/index_prices')
def get_index_prices():
    return jsonify(fetch_yfinance_data(tickers_indexes, format_index_price))

@app.route('/commodity_prices')
def get_commodity_prices():
    return jsonify(fetch_yfinance_data(tickers_commodities, format_commodity_price))

@app.route('/treasury_rates')
def get_treasury_rates():
    return jsonify(fetch_yfinance_data(tickers_treasury, format_treasury_price, absolute_change=True))

@app.route('/forex_rates')
def get_forex_rates():
    return jsonify(fetch_yfinance_data(tickers_forex, format_forex_price))

@app.route('/crypto_prices')
def get_crypto_prices():
    return jsonify(fetch_yfinance_data(tickers_crypto, format_crypto_price))

@app.route('/fed_data')
def get_fed_data():
    return jsonify(fetch_fed_data())