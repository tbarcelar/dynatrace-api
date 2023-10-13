import json
import requests
import openpyxl

# Carrega o arquivo config.json
with open("C:/Users/config.json", "r") as config_file:
    config_data = json.load(config_file)

# Obtém a URL e o token do JSON
url = config_data["requests_data"][0]["url"]
token = config_data["requests_data"][0]["token"]

# Define a URL da API Dynatrace
api_url = f"{url}/api/config/v1/notifications"

# Define os cabeçalhos com o token
headers = {
    'Accept': 'application/json; charset=utf-8',
    'Content-Type': 'application/json; charset=utf-8',
    "Authorization": f"Api-Token {token}",
}

params = {
    'schemaIds': 'builtin:problem.notifications',
    'scopes': 'environment',
    'fields': 'id,name',
}

# Faz a solicitação GET para a API
response = requests.get(api_url, params=params, headers=headers)

# Verifica se a solicitação foi bem-sucedida
if response.status_code == 200:
    # Obtenha o conteúdo JSON da resposta
    data = response.json()["values"]

    # Crie um novo arquivo Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Escreva os cabeçalhos na planilha
    sheet.append(["id", "name"])

    # Escreva os dados na planilha
    for item in data:
        sheet.append([item["id"], item["name"]])

    # Salve o arquivo Excel
    workbook.save("C:/Users/notificacion-problem.xlsx")
    print("Dados salvos no arquivo Excel 'output.xlsx'")

else:
    print(f"A solicitação falhou com o código de status {response.status_code}")
