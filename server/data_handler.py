import datetime
import logging
import sql_ops
import electricity_price
import os
from dataclasses import dataclass

@dataclass
class chartData:
    chartTitle: str
    chartDataPoints: dict[str, str]
    lastUpdate: str
    yAxisTitle: str
    
@dataclass
class responseData:
    valid: bool
    data: chartData
    message: str

JSONFILENAME: str = 'current_price_data.json'

def handlePostTemperatures(data: bytes):
    values_str: str = data.decode('UTF-8')
    values: list[str] = values_str.split(",")
    # out, in, set, previous set
    # received temperature values need to be scaled by 1/10
    logging.debug(f"handlePostTemperatures: {values_str}")
    for i in range (len(values) - 1):
        if not checkIfStringNumerical(values[i]):
            logging.error(f"One tempereture value is not numerical, value={i}")
            return

        val: float = round(float(values[i]) / 10, 2)
        values[i] = str(val)

    allowedColumns: int = 4
    if len(values) != allowedColumns:
        logging.error(f"Too few colums in temperature POST, amount={len(values)}, string={values_str}")
        return

    sql_ops.insertTemperatures(t_in=values[1], t_out=values[0], t_set=values[2], date=getIsoUtcTimestamp(datetime.datetime.now()))


def handlePostConsumption(data: bytes):
    consumptionW: str = data.decode('UTF-8')
    if (not checkIfStringNumerical(consumptionW)):
        logging.error(f"Consumption value is not numerical, value={consumptionW}")
        return
    consumptionKw: str = str(float(consumptionW)/1000)
    sql_ops.insertConsumption(consumption=consumptionKw, date=getIsoUtcTimestamp(datetime.datetime.now()))


def handleGetDashboard() -> str:
    checkAndUpdateElectricityPrices()
    return sql_ops.getDashboardValues(getIsoUtcTimestampAtStartOfHour(datetime.datetime.now()))


def handleGetElectricity() -> responseData:
    checkAndUpdateElectricityPrices()
    return responseData(valid=True, 
                        data=chartData(chartTitle="Electricity prices",
                                    chartDataPoints=sql_ops.getLatesElectricityPrices(),
                                    lastUpdate=getIsoUtcTimestamp(electricity_price.lastElectrPriceUpdateDate),
                                    yAxisTitle="kW/c"),
                        message="")


def handleGetConsumption() -> responseData:
    return responseData(valid=True, 
                        data=chartData(chartTitle="Consumption Wh",
                                    chartDataPoints=sql_ops.getLatesConsumptions(),
                                    lastUpdate=sql_ops.getLatestConsumptionUpdateDate(),
                                    yAxisTitle="kW"),
                        message="")


def handleGetTemperatureById(name: str) -> responseData:
   columnId: str = getTemperatureColumnByName(name)
   if (not columnId):
       logging.error(f"Illegal argument in /api/getTemperature, argument={name}")
       return buildErrorResponse("Illegal argument")

   return responseData(valid=True, 
                       data=chartData(chartTitle=f"Temperature {name}",
                                   chartDataPoints=sql_ops.getLatesTemperatures(columnId),
                                   lastUpdate=sql_ops.getLatestTempUpdateDate(),
                                   yAxisTitle="°C"),
                       message="")


def getTemperatureColumnByName(name: str) -> str:
   if (name == "in"):
       return sql_ops.temperatureInColId
   elif (name == "out"):
       return sql_ops.temperatureOutColId
   elif (name == "set"):
       return sql_ops.temperatureSetColId
   else:
       return ""


def getIsoUtcTimestamp(date: datetime.datetime) -> str:
    return date.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def getIsoUtcTimestampAtStartOfHour(date: datetime.datetime) -> str:
    return date.utcnow().strftime("%Y-%m-%dT%H:00:00.000000Z")


def handleForceElectricityUpdate() -> None:
    logging.debug(f"Force update electricity prices")
    addElectricityPricesToDB()


def checkIfStringNumerical(string: str) -> bool:
    return string.replace("-", "", 1).isdigit()


def checkAndUpdateElectricityPrices() -> None:
    if not os.path.isfile(JSONFILENAME):
        logging.debug(f"No electricity price JSON found, updating, file={JSONFILENAME}")
        addElectricityPricesToDB()
        return

    now: datetime.date = datetime.datetime.now()
    if now.day != electricity_price.lastElectrPriceUpdateDate.day and now.hour >= 14:
        logging.debug(f"Now.day={now.day}, lastUpdateDay={getIsoUtcTimestamp(electricity_price.lastElectrPriceUpdateDate)}")
        addElectricityPricesToDB()
        return


def addElectricityPricesToDB() -> None:
    electricity_price.downloadJsonData(JSONFILENAME)
    prices: dict[str, str] = electricity_price.getPrices(JSONFILENAME)
    for date, price in prices.items():
        sql_ops.insertElectricityPrice(price, date)
    return


def buildErrorResponse(errorString: str) -> responseData:
    return responseData(valid=False,
                        data=chartData("", {}, "", ""),
                        message=errorString,)