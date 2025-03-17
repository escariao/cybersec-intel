# 🛡️ CyberSec Intel

![GitHub repo size](https://img.shields.io/github/repo-size/escariao/cybersec-intel)
![GitHub issues](https://img.shields.io/github/issues/escariao/cybersec-intel)
![GitHub license](https://img.shields.io/github/license/escariao/cybersec-intel)
![GitHub last commit](https://img.shields.io/github/last-commit/escariao/cybersec-intel)

**CyberSec Intel** é uma plataforma voltada para **inteligência de ameaças cibernéticas**, aplicação web desenvolvida em Python com o framework Flask, que permite a verificação de IPs ou domínios contra o histórico de abusos reportado na AbuseIPDB. A aplicação também mantém um histórico local das últimas 10 consultas realizadas.

## 🚀 **Principais Funcionalidades**
✔️ **Verificação de IPs/Domínios:** Insira um IP ou domínio para análise.  
✔️ **Resolução de Domínios:** Converte domínios em IPs válidos.  
✔️ **Consulta à AbuseIPDB:** Realiza chamadas à API para verificar o histórico de abuso.  
✔️ **Histórico de Consultas:** Armazena as últimas 10 consultas em um arquivo JSON.  
✔️ **API RESTful:** Endpoint `/api/check_ip/<ip>` para consultas programáticas.  


## 🛠 **Tecnologias Utilizadas**
| Tecnologia | Descrição |
|------------|------------|
| **🐍 Python** | Linguagem principal do projeto |
| **Flask** | Framework web para interface |
| **Requests** | Captura de informações de APIs |
| **Render** | Hospedagem do serviço |

## 📌 **Como Usar**

1️⃣ Clone o repositório:
```bash
git clone https://github.com/escariao/cybersec-intel.git
```

2️⃣ Instale as dependências:
```bash
cd cybersec-intel
pip install -r requirements.txt
```

3️⃣ Inicie o servidor:
```bash
python app.py
```

Acesse **http://localhost:5000/** no navegador para utilizar a interface.

## 🌍 **Versão Online**
A plataforma pode ser acessada sem instalação:
🔗 [CyberSec Intel Online](https://cybersec-intel.onrender.com/)

---
Desenvolvido por **Andrey M. E.** 🛡️
