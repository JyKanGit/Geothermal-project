from flask import Flask, jsonify, request, render_template
import logging
import data_handler
import subprocess
# import when using ng serve to develop frontend
# from flask_cors import CORS

app = Flask(__name__)

@app.route('/post', methods=["POST"])
def post():
    data_handler.handlePostTemperatures(request.data)
    return ''


@app.route('/consumption', methods=["POST"])
def consumption_post():
    data_handler.handlePostConsumption(request.data)
    return ''


@app.route("/dashboard", methods=["GET"])
def get_dashboard():
    return data_handler.handleGetDashboard()


@app.route('/static/', methods=['GET'])
@app.route('/', methods=['GET'])
def root():
    return render_template('index.html')


@app.route('/api/getElectricity', methods=["GET"])
def getElectricity():
    return jsonify(data_handler.handleGetElectricity())


@app.route('/api/getTemperature', methods=["GET"])
def getTemperatureIn():
    argument: str  = str(request.args.get("id"))
    return jsonify(data_handler.handleGetTemperatureById(argument))


@app.route('/api/getConsumption', methods=["GET"])
def getConsumption():
    return jsonify(data_handler.handleGetConsumption())


@app.route('/api/forceElectricityUpdate', methods=["GET"])
def getForceUpdate():
    return jsonify(data_handler.handleForceElectricityUpdate())


@app.route('/api/updateApplication', methods=["GET"])
def getUpdateApplication():
    logging.debug("Updating application, current commit:")
    result: subprocess.CompletedProcess[bytes] = subprocess.run(['git', 'log', '-n', '1', '--oneline'], stdout=subprocess.PIPE)
    logging.debug(result.stdout.decode('utf-8'))

    logging.debug("Running update script")
    result = subprocess.run(['bash', 'updateFromRepo.sh'], stdout=subprocess.PIPE)
    logging.debug(result.stdout.decode('utf-8'))

    return ""


def initLogging() -> None:
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    logging.basicConfig(filename="logfile.log",
                        encoding='utf-8',
                        level=logging.DEBUG,
                        format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    return


if __name__=="__main__":
    initLogging()
    logging.info("Starting server")
    # For frontend development allow CORS, comment out
    # CORS(app)
    data_handler.addElectricityPricesToDB()
    app.run(host='0.0.0.0', port=8090, debug=False)
    
