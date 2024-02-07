import requests
import json
import re
import datetime
import pytz
import logging

lastElectrPriceUpdateDate: datetime.datetime = datetime.datetime.now()

"""
    returns pricedata dict where keys are timestamps in ISO format
"""

def getPrices(jsonFilename: str) -> dict[str, str]:
    logging.debug("Getting prices")
    pricedata: dict = getJsonFileData(jsonFilename)
    prices: dict[str, str] = {}
    for row_index, row in enumerate(pricedata.get('data', {}).get('Rows', [])):
        # The JSON contains extra data after the hourly prices such as min and max price,
        # In the extra rows, the 'IsExtraRow' field is true
        notRelevant: bool = row.get("IsExtraRow",'')
        if (notRelevant):
            continue

        for column in row.get('Columns', []):
            # TODO: the hours index will be strange for 2 days a year because of daylight savings
            hours: str = str(row_index).rjust(2, '0')
            timestamp: str = column.get('Name','')
            isoTimestamp: str = convertToIsoUtc(timestamp, hours)
            if (isoTimestamp != ''):
                prices[isoTimestamp] = formatPrice(column.get('Value',''))
        
    return prices


def formatPrice(price: str) -> str:
    roundedPrice: float = float(price.replace(',','.').replace(' ',''))
    roundedPrice = roundedPrice / 10
    roundedPrice = round(roundedPrice, 3)
    return str(roundedPrice)


def getJsonFileData(filename: str) -> dict:
    pricedata = ''
    with open(filename, 'r') as f:
        pricedata = json.load(f)

    return pricedata


def downloadJsonData(filename: str) -> None:
    NORDPOOL_URL: str = 'https://www.nordpoolgroup.com/api/marketdata/page/35?currency=,,,EUR'
    response = requests.get(NORDPOOL_URL)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)

        global lastElectrPriceUpdateDate
        lastElectrPriceUpdateDate = datetime.datetime.now()
        logging.debug(f"Updated electricity prices JSON, new last_update_day: {lastElectrPriceUpdateDate}")
    else:
        logging.error("Failed to fetch data")
    

def convertToIsoUtc(date: str, hour: str) -> str:
    DATETIMEREGEX = r'^(\d{2})-(\d{2})-(\d{4})$'
    matches = re.match(DATETIMEREGEX, date)
    if not matches or not hour.isdigit():
        return ""
    day: str = matches[1]
    month: str = matches[2]
    year: str = matches[3]
    return changeTimezoneToUtc(f"{year}-{month}-{day}T{hour}:00:00.000Z")


def changeTimezoneToUtc(date: str) -> str:
    CETTIMEZONECODE: str = 'Europe/Oslo'
    ISODATETIMEFORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"

    utcTimezone = pytz.utc
    cetTimezone = pytz.timezone(CETTIMEZONECODE)

    cetDatetime = datetime.datetime.strptime(date, ISODATETIMEFORMAT)
    return cetTimezone.localize(cetDatetime).astimezone(utcTimezone).strftime(ISODATETIMEFORMAT)
