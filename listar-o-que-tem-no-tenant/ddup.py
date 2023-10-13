import json
import requests
import pandas as pd

# Carrega o arquivo config.json
with open("C:/Users/config.json", "r") as config_file:
    config_data = json.load(config_file)

# Obtém a URL e o token do JSON
url = config_data["requests_data"][0]["url"]
token = config_data["requests_data"][0]["token"]

# Define a URL da API Dynatrace
api_url = f"{url}/api/v2/settings/objects"

# Define os cabeçalhos com o token
headers = {
    'Accept': 'application/json; charset=utf-8',
    'Content-Type': 'application/json; charset=utf-8',
    "Authorization": f"Api-Token {token}",
}

params = {
    'schemaIds': 'builtin:accounting.ddu.limit',
    'scopes': 'environment',
    'fields': 'objectId,value',
}

# Faz a solicitação GET para a API
response = requests.get(api_url, params=params, headers=headers)

# Transforma a resposta JSON em um DataFrame do pandas
data = response.json()["items"]

# Crie um DataFrame vazio para armazenar os dados reestruturados
df = pd.DataFrame(columns=["objectId", "Nome", "limitEnabled", "limitValue"])

# Defina as linhas correspondentes
linhas = ["metrics", "logMonitoring", "serverless", "traces"]

# Itera sobre as linhas e reestrutura os dados
for linha in linhas:
    for item in data:
        objectId = item["objectId"]
        value = item["value"].get(linha, {})
        limitEnabled = value.get("limitEnabled", False)
        limitValue = value.get("limitValue", 0)

        # Adiciona uma nova linha ao DataFrame
        df = df._append({"objectId": objectId, "Nome": linha, "limitEnabled": limitEnabled, "limitValue": limitValue}, ignore_index=True)

# Salva os dados em um arquivo Excel
excel_path = "C:/Users/ddup.xlsx"
df.to_excel(excel_path, index=False)

print(f'Dados salvos em {excel_path}')
