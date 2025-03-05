import requests
import socket
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ⚠️ Substitua pela sua chave da AbuseIPDB
ABUSEIPDB_API_KEY = "7652758a92b582f623257d1258cd4512b26ddf7ca4b5d2177bcd9d30578f29fa33fc0737ee25b8a9"

def resolve_domain(domain):
    """Tenta converter um domínio em IP. Retorna None se falhar."""
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None

def check_ip(ip):
    """Consulta IPs na AbuseIPDB e trata erros."""
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Key": ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": "90"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # Se houver erro na resposta, captura e retorna
        if response.status_code != 200:
            return {"error": data.get("errors", [{"detail": "Erro desconhecido"}])[0]["detail"]}
        
        return data
    except Exception as e:
        return {"error": f"Erro ao consultar AbuseIPDB: {str(e)}"}

@app.route("/", methods=["GET", "POST"])
def home():
    data = None
    error = None

    if request.method == "POST":
        user_input = request.form["ip"].strip()
        
        # Verifica se é um domínio e converte para IP
        ip = resolve_domain(user_input) if not user_input.replace(".", "").isdigit() else user_input
        
        if ip:
            data = check_ip(ip)
            if "error" in data:
                error = data["error"]
        else:
            error = "Domínio inválido ou IP incorreto. Verifique e tente novamente."
    
    return render_template("index.html", data=data, error=error)

@app.route("/api/check_ip/<ip>")
def api_check_ip(ip):
    resolved_ip = resolve_domain(ip) if not ip.replace(".", "").isdigit() else ip
    
    if not resolved_ip:
        return jsonify({"error": "Domínio inválido ou IP incorreto"}), 400
    
    return jsonify(check_ip(resolved_ip))

if __name__ == "__main__":
    app.run(debug=True)
