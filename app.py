import requests
import socket
import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///consultas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para armazenar consultas
class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100), nullable=False)
    resultado = db.Column(db.Text, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

# ⚠️ Substitua pela sua chave real da AbuseIPDB
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
                # Armazena a consulta no banco de dados
                resultado = str(data)
                nova_consulta = Consulta(ip=ip, resultado=resultado)
                db.session.add(nova_consulta)
                db.session.commit()
        else:
            error = "Domínio inválido ou IP incorreto. Verifique e tente novamente."

    # Recupera as últimas 10 consultas
    consultas = Consulta.query.order_by(Consulta.data_hora.desc()).limit(10).all()
    
    return render_template("index.html", data=data, error=error, consultas=consultas)

@app.route("/api/check_ip/<ip>")
def api_check_ip(ip):
    resolved_ip = resolve_domain(ip) if not ip.replace(".", "").isdigit() else ip
    
    if not resolved_ip:
        return jsonify({"error": "Domínio inválido ou IP incorreto"}), 400
    
    return jsonify(check_ip(resolved_ip))

import os

if __name__ == "__main__":
    with app.app_context():
        db_file = "consultas.db"

        # Deleta o banco se já existir para garantir uma nova criação
        if os.path.exists(db_file):
            os.remove(db_file)
            print("Banco de dados antigo removido.")

        # Cria o banco de dados do zero
        db.create_all()
        print("Novo banco de dados criado com sucesso!")

    app.run(debug=True)
