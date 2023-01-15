import csv
from flask import Flask, request, render_template
import datetime
import electricity_price

app = Flask(__name__)

CSV_COLUMNS = 4
DATE_HOUR_FORMAT = "%Y-%m-%dT%H:00:00"

prev_date_w_hour = -1
event_count = 0
sums_data = []


def add_to_average(data):
    global sums_data, event_count
    event_count += 1
    if not sums_data:
        for i in range(len(data)):
            sums_data.append(data[i])
    else:
        for i in range(len(data)):
            sums_data[i] += data[i]


def clear_average():
    global sums_data, event_count
    event_count = 0
    for i in range(len(sums_data)):
        sums_data[i] = 0


def get_averages():
    global event_count
    if event_count == 0:
        event_count = 1
    average_list = []
    for i in range(len(sums_data)):
        average_list.append(round(sums_data[i] / event_count, 2))
    clear_average()
    return average_list


def check_values(data):
    # Indoor temperature
    if not -40 < float(data[0]) < 30:
        print("Indoor")
        return 1
    # Outdoor temperature
    if not 15 < float(data[1]) < 40:
        print("Outoor")
        return 1
    # Previous Room temperature Setting value
    if not 15 < float(data[2]) < 30:
        print("Setting")
        return 1
    # Updated Room temperature Setting value
    if not 15 < float(data[3]) < 30:
        print("Set value")
        return 1
    return 0


def remove_dots(list):
    for i in range(len(list)):
        list[i] = str(list[i]).replace(".", ",")
    return list


def handle_POST(data):
    values = str(data).split(",")
    
    for i in range(len(values)):
        values[i] = float(values[i]) * 0.1
    if len(values) != CSV_COLUMNS:
        print("ERROR, TOO FEW VALUES")
        return
    if check_values(values):
        print("ERROR, ERRANEOUS VALUES NOT ADDED TO LOG")
        return

    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
    date_w_hour = datetime.datetime.now().strftime(DATE_HOUR_FORMAT)

    with open(r'log.csv', mode='a') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='|')
        temp_values = values[:]
        temp_values.insert(0, timestamp)
        current_price = electricity_price.get_price(date_w_hour)
        temp_values.insert(1, current_price)
        writer.writerow(remove_dots(temp_values))

    global prev_date_w_hour
    if prev_date_w_hour != date_w_hour:
        if prev_date_w_hour != -1:
            with open(r'hour_log.csv', mode='a') as csvfile:
                writer = csv.writer(csvfile, delimiter=';', quotechar='|')
                average_list = get_averages()
                average_list.insert(0, prev_date_w_hour)
                current_price = electricity_price.get_price(prev_date_w_hour)
                average_list.insert(1, current_price)
                writer.writerow(remove_dots(average_list))
                clear_average()
        prev_date_w_hour = date_w_hour
    add_to_average(values)


@app.route('/post', methods=["POST"])
def post():
    handle_POST(request.data)
    return ''


@app.route("/dashboard")
def get_dashboard():
    with open('log.csv', mode="r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        list = []
        for row in csvreader:
            list.append(row)
        last = list[-1]
        laststr = last[1] + ";" + last[2] + ";" + last[3]
    return laststr


@app.route('/statistics')
def get_statistics():
    template_data = {}
    with open('log.csv') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        list = []
        for row in csvreader:
            list.append(row)
        last = list[-1]
        try:
            template_data["currtime"] = last[0]
            template_data["currprice"] = last[1]
            template_data["currout"] = last[2]
            template_data["currin"] = last[3]
            template_data["currset"] = last[4]
        except IndexError:
            print("ERROR, FAILURE WHEN PARSING LAST ENTRY IN log.csv")

    with open('hour_log.csv') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        list = []
        for row in csvreader:
            list.append(row)
        dailylist = list[-24:]
        row = 0
        for i in reversed(dailylist):
            try:
                template_data["r" + str(row) + "time"] = i[0]
                template_data["r" + str(row) + "price"] = i[1]
                template_data["r" + str(row) + "out"] = i[2]
                template_data["r" + str(row) + "in"] = i[3]
                template_data["r" + str(row) + "set"] = i[4]
            except IndexError:
                print("ERROR, FAILURE WHEN PARSING hour_log.csv VALUES")
            row += 1
    return render_template('html-file.html', **template_data)


app.run(host='0.0.0.0', port=8090)
