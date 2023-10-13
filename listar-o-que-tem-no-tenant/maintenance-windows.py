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
    'schemaIds': 'builtin:alerting.maintenance-window',
    'scopes': 'environment',
    'fields': 'objectId,value',
}
# Faz a solicitação GET para a API
response = requests.get(api_url, params=params, headers=headers)
# Transforma a resposta JSON em um DataFrame do pandas
data = response.json()["items"]
# Cria uma lista de dicionários com os dados que você quer
data_to_save = []
for item in data:
    data_dict = {
        "objectId": item["objectId"],
        "enabled": item["value"]["enabled"],
        "name": item["value"]["generalProperties"]["name"]
    }
    data_to_save.append(data_dict)
# Cria um DataFrame a partir da lista de dicionários
df = pd.DataFrame(data_to_save)
# Salva o DataFrame em um arquivo Excel
excel_path = "C:/Users/maintenance-windows.xlsx"
df.to_excel(excel_path, index=False)
print(f'Dados salvos em {excel_path}')