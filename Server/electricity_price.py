import requests
import json
from datetime import datetime
import pytz

NORDPOOL_URL = "https://www.nordpoolgroup.com/api/marketdata/page/35?currency=,,,EUR"
TAX = 10
DATE_HOUR_FORMAT = "%Y-%m-%dT%H:00:00"

prices = {}
checked = 1


def update():
    """
    Creates a dictionary with the current dates and tomorrow's prices
    Dictionary key is a date in format "%d-%m-%YT%H:00:00" and the value is
    th electricity price in Finland at that time in EUR/kWH + tax. Nordpools
    dates are in CET time. The dat etimes are transformed into Finnish time
    :return:
    """
    request = requests.get(NORDPOOL_URL)
    json_request = request.json()
    json_dump = json.dumps(json_request)
    pricedata = json.loads(json_dump)

    global prices
    prices.clear()
    for column in range(0, 2):
        for row in range(0, 24):
            date = datetime.strptime((str(
                pricedata['data']['Rows'][row]['Columns'][column]
                ['Name'] + "T" + str(row).rjust(2, '0'))), "%d-%m-%YT%H")
            
            old_tz = pytz.timezone('Europe/Oslo')
            new_tz = pytz.timezone('Europe/Helsinki')
            new_timezone_timestamp = old_tz.localize(date).astimezone(new_tz). \
                strftime(DATE_HOUR_FORMAT)
            
            unformatted_price = pricedata['data']['Rows'][row]['Columns'][column]['Value']
            price_wo_tax = float(unformatted_price.replace(",", ".")) / 10
            prices[new_timezone_timestamp] = round(
                price_wo_tax + price_wo_tax * TAX / 100, 3)


def get_price(datetime_w_hour):
    try:
        if datetime_w_hour not in prices:
            update()
            print('updated')
        return prices[datetime_w_hour]
    except KeyError:
        print("ERROR, NO ELECTRICITY PRICE FOUND FOR TIMESTAMP")
        return -100
