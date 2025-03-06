import requests
import socket
import json
import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Nome do arquivo JSON para armazenar consultas
CONSULTAS_FILE = "consultas.json"

# ⚠️ Substitua pela sua chave real da AbuseIPDB
ABUSEIPDB_API_KEY = "7652758a92b582f623257d1258cd4512b26ddf7ca4b5d2177bcd9d30578f29fa33fc0737ee25b8a9"

def resolve_domain(domain):
    """Tenta resolver um domínio para IP. Retorna None se falhar."""
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None  # Agora o erro será tratado corretamente

def check_ip(ip):
    """Consulta IPs na AbuseIPDB e trata respostas inesperadas."""
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
            return {"error": data.get("errors", [{"detail": "Erro desconhecido na API"}])[0]["detail"]}

        return data
    except Exception as e:
        return {"error": f"Erro ao consultar AbuseIPDB: {str(e)}"}

def salvar_consulta(ip, data):
    """Salva a consulta no JSON garantindo que data_hora sempre estará presente."""
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

    consultas.insert(0, nova_consulta)  # Adiciona no topo da lista
    consultas = consultas[:10]  # Mantém apenas as últimas 10 consultas

    with open(CONSULTAS_FILE, "w") as file:
        json.dump(consultas, file, indent=4)

@app.route("/", methods=["GET", "POST"])
def home():
    data = None
    error = None

    if request.method == "POST":
        user_input = request.form["ip"].strip()

        # Se for um domínio, tenta resolver para IP
        if not user_input.replace(".", "").isdigit():
            ip = resolve_domain(user_input)
            if not ip:
                error = f"Domínio '{user_input}' não pode ser resolvido para um IP válido. Verifique se ele é acessível."
        else:
            ip = user_input  # Já é um IP, segue adiante

        if ip:
            data = check_ip(ip)
            if "error" in data:
                error = data["error"]
            else:
                salvar_consulta(ip, data)
        else:
            error = "O IP inserido não é válido. Por favor, insira um IP no formato correto."

    # Garantir que consultas seja inicializado corretamente
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
    if "error" in data:
        return jsonify(data), 400

    salvar_consulta(resolved_ip, data)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
