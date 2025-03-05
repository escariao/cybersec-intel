import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ⚠️ Substitua pela sua chave da AbuseIPDB
ABUSEIPDB_API_KEY = "SUA_CHAVE_AQUI"

def check_ip(ip):
    """ Consulta IPs na AbuseIPDB """
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Key": ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": "90"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

@app.route("/", methods=["GET", "POST"])
def home():
    data = None
    if request.method == "POST":
        ip = request.form["ip"]
        data = check_ip(ip)
    return render_template("index.html", data=data)

@app.route("/api/check_ip/<ip>")
def api_check_ip(ip):
    return jsonify(check_ip(ip))

if __name__ == "__main__":
    app.run(debug=True)
