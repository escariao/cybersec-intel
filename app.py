import requests
import socket
import json
import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Nome do arquivo JSON onde as consultas serão armazenadas
CONSULTAS_FILE = "consultas.json"

# ⚠️ Substitua pela sua chave real da AbuseIPDB
ABUSEIPDB_API_KEY = "SUA_CHAVE_AQUI"

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

def salvar_consulta(ip, data):
    """Salva a consulta no arquivo JSON e garante que data_hora sempre estará presente."""
    try:
        with open(CONSULTAS_FILE, "r") as file:
            consultas = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        consultas = []

    nova_consulta = {
        "ip": ip,
        "resultado": data,
        "data_hora": datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    }

    consultas.insert(0, nova_consulta)  # Adiciona a consulta no topo

    # Mantém apenas as últimas 10 consultas
    consultas = consultas[:10]

    with open(CONSULTAS_FILE, "w") as file:
        json.dump(consultas, file, indent=4)

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
                salvar_consulta(ip, data)
        else:
            error = "Domínio inválido ou IP incorreto. Verifique e tente novamente."

    # Correção: Garantir que consultas seja inicializado corretamente
    try:
        with open(CONSULTAS_FILE, "r") as file:
            consultas = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        consultas = []

    return render_template("index.html", data=data, error=error, consultas=consultas)

@app.route("/api/check_ip/<ip>")
def api_check_ip(ip):
    resolved_ip = resolve_domain(ip) if not ip.replace(".", "").isdigit() else ip

    if not resolved_ip:
        return jsonify({"error": "Domínio inválido ou IP incorreto"}), 400

    data = check_ip(resolved_ip)
    salvar_consulta(resolved_ip, data)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
