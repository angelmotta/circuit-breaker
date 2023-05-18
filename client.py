from flask import Flask
from flask import request, jsonify
import urllib.request, json
from werkzeug.exceptions import HTTPException
from circuitBreaker import CircuitBreaker
import time

app = Flask(__name__)

# Create a CircuitBreaker Object
circuit_breaker = CircuitBreaker(maxFaults=5, waitTimeToReset=10)

# Do not remove this method.
@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code

@app.route('/igv')
def igv():
    #tax = get_tax_from_api()
    # Using circuit_breaker object to call the external API
    resultTax = circuit_breaker.callExternalAPI(get_tax_from_api)
    if resultTax is None:
        print("Circuit is opened")
        # We can verify resetTimeout value to close the circuit -> so next clients can try again calling the external API
        if time.time() - circuit_breaker.lastTimeFault > circuit_breaker.waitTimeToReset:
            print("Resetting circuit: circuit is closed")
            circuit_breaker.reset() # next client request can try again calling the external API
        return jsonify(error="Disculpe, servicio externo no disponible"), 503
    else:
        print("Result tax from External API:", resultTax)
        return jsonify(igv=resultTax), 200

def get_tax_from_api():
    url = "http://127.0.0.1:5000/tax"

    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)

    return int(dict["Tax"])

if __name__ == "__main__":
    app.run(debug=True, port=3000)