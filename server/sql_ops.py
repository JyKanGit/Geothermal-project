import logging
import sqlite3

DATABASENAME: str = "data.db"

electricityPriceColId:str = "price"
ELECTRICITY_PRICE_TABLE_NAME: str = "electricity_price"
ELECTRICITY_PRICE_TABLE_SCHEMA: str = f"{electricityPriceColId} REAL, date TEXT PRIMARY KEY"

temperatureInColId: str = "t_in_C"
temperatureOutColId: str = "t_out_C"
temperatureSetColId: str = "t_set_C"
TEMPERATURES_TABLE_NAME: str = "temperatures"
TEMPERATURES_TABLE_SCHEMA: str = f"{temperatureInColId} REAL, {temperatureOutColId} REAL, {temperatureSetColId} REAL, date TEXT PRIMARY KEY"

consumptionColId: str = "consumption_Wh"
CONSUMPTION_TABLE_NAME: str = "consumption"
CONSUMPTION_TABLE_SCHEMA: str = f"{consumptionColId} INTEGER, date TEXT PRIMARY KEY"

def initTable(con: sqlite3.Connection, tableName: str, schema: str) -> sqlite3.Cursor:
    cur: sqlite3.Cursor = con.cursor()
    query: str = f"CREATE TABLE IF NOT EXISTS {tableName} ({schema})"
    cur.execute(query)
    return cur
    

def insertData(tableName: str, tableSchema: str, data: dict[str, str], date: str, log: bool = False):
    con: sqlite3.Connection = sqlite3.connect(DATABASENAME)
    cur: sqlite3.Cursor = initTable(con, tableName, tableSchema)
    
    columns = ', '.join(data.keys())
    values = ', '.join(data.values())

    query: str = f"INSERT INTO {tableName} ({columns}, date) VALUES ({values}, '{date}')"
    if (log):
        logging.debug(query)

    try:
        cur.execute(query)
    except sqlite3.Error as e:
        logging.error(f"SQLite error: {e}")
    
    con.commit()
    con.close()


def insertTemperatures(t_in: str, t_out: str, t_set: str, date: str):
    insertData(
        tableName=TEMPERATURES_TABLE_NAME,
        tableSchema=TEMPERATURES_TABLE_SCHEMA,
        data={temperatureInColId: t_in,
                temperatureOutColId: t_out,
                temperatureSetColId: t_set},
        date=date)


def insertConsumption(consumption: str, date: str):
    insertData(
        tableName=CONSUMPTION_TABLE_NAME,
        tableSchema=CONSUMPTION_TABLE_SCHEMA,
        data={consumptionColId: consumption},
        date=date)


def insertElectricityPrice(price: str, date: str):
    insertData(
        tableName=ELECTRICITY_PRICE_TABLE_NAME,
        tableSchema=ELECTRICITY_PRICE_TABLE_SCHEMA,
        data={electricityPriceColId: price},
        date=date)


def getLatestUpdateDate(tableName: str, schema: str) -> str:
    con: sqlite3.Connection = sqlite3.connect(DATABASENAME)
    cur: sqlite3.Cursor = initTable(con, tableName, schema)

    query: str = f"SELECT  date FROM {tableName} ORDER BY date DESC LIMIT 1"
    res: sqlite3.Cursor = cur.execute(query)
    retVal: str = res.fetchone()[0]
    con.close()
    return retVal


def getLatestData(tableName: str, schema: str, columns: list[str], limit: int, groupByHour: bool, orderDir: str = "DESC", aggregation_func=None) -> dict[str, str]:
    con: sqlite3.Connection = sqlite3.connect(DATABASENAME)
    cur: sqlite3.Cursor = initTable(con, tableName, schema)

    aggregated_columns: list[str]
    groupBy: str = "GROUP BY strftime('%dT%H', date)" if groupByHour else ""
    if aggregation_func:
        aggregated_columns = [aggregation_func(col) for col in columns]
    else:
        aggregated_columns = columns

    columns_string: str = ",".join(aggregated_columns)

    query: str = f"SELECT  date, {columns_string} FROM {tableName} {groupBy} ORDER BY date {orderDir} LIMIT {limit}"
    logging.debug(query)

    response: dict[str, str] = {}
    for row in cur.execute(query):
        date: str = row[0]
        value: str = row[1]

        response[date] = value

    con.close()
    return response


def getLatesElectricityPrices() -> dict[str, str]:
    return getLatestData(
        tableName=ELECTRICITY_PRICE_TABLE_NAME,
        schema=ELECTRICITY_PRICE_TABLE_SCHEMA,
        columns=[electricityPriceColId],
        limit=48,
        groupByHour=False,
        aggregation_func=lambda col: f"ROUND(({col} + {col} * 0.24), 2)"
    )


def getLatesConsumptions() -> dict[str, str]:
    return getLatestData(
        tableName=CONSUMPTION_TABLE_NAME,
        schema=CONSUMPTION_TABLE_SCHEMA,
        columns=[consumptionColId],
        limit=24,
        groupByHour=True,
        aggregation_func=lambda col: f"ROUND(SUM({col}), 1)"
    )


def getLatesTemperatures(column: str) -> dict[str, str]:
    return getLatestData(
        tableName=TEMPERATURES_TABLE_NAME,
        schema=TEMPERATURES_TABLE_SCHEMA,
        columns=[column],
        limit=24,
        groupByHour=True,
        aggregation_func=lambda col: f"ROUND(AVG({col}), 1)"
    )


def getLatestTempUpdateDate() -> str:
    return getLatestUpdateDate(
        tableName=TEMPERATURES_TABLE_NAME,
        schema=TEMPERATURES_TABLE_SCHEMA
    )


def getLatestConsumptionUpdateDate() -> str:
    return getLatestUpdateDate(
        tableName=CONSUMPTION_TABLE_NAME,
        schema=CONSUMPTION_TABLE_SCHEMA
    )


def getDashboardValues(date: str) -> str:
    con: sqlite3.Connection = sqlite3.connect(DATABASENAME)
    cur: sqlite3.Cursor = con.cursor()
    res: sqlite3.Cursor = cur.execute(f"SELECT ROUND(({electricityPriceColId} + {electricityPriceColId} * 0.24), 3) FROM electricity_price WHERE date='{date}';")
    price: str = res.fetchone()[0]
    res: sqlite3.Cursor = cur.execute(f"SELECT {temperatureOutColId}, {temperatureInColId} FROM temperatures ORDER BY date DESC LIMIT 1;")
    vals = res.fetchone()
    retstring: str = f"{price};{vals[0]};{vals[1]}"
    return retstring
