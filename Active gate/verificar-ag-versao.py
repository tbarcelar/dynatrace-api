import json
import requests
import pandas as pd

# Caminho para o arquivo JSON de configuração
json_file_path = 'xxxxx/config.json'

# Leitura do arquivo JSON
with open(json_file_path, 'r') as file:
    config = json.load(file)

# Lista para armazenar os resultados
results = []

# Processar cada entrada do JSON
for request_data in config.get('requests_data', []):
    url = f"{request_data['url']}/api/v2/activeGates"
    token = f"Api-Token {request_data['token']}"
    name = request_data['name']
    
    headers = {
        'accept': 'application/json; charset=utf-8',
        'Authorization': token,
    }

    params = {
        'versionCompareType': 'EQUAL',
    }

    # Solicitação GET para a API
    response = requests.get(url, params=params, headers=headers)
    response_data = response.json()

    # Extrair a versão
    if 'activeGates' in response_data and len(response_data['activeGates']) > 0:
        version = response_data['activeGates'][0].get('version', 'N/A').split('-')[0]  # Pega a versão e remove o sufixo
    else:
        version = 'N/A'

    # Adiciona os resultados à lista
    results.append({
        'name': name,
        'url': url,
        'version': version
    })

# Convertendo os resultados para um DataFrame
df = pd.DataFrame(results)

# Caminho para salvar o arquivo Excel
excel_file_path = 'xxxx/excel/activegate.xlsx'

# Salvando o DataFrame em um arquivo Excel
df.to_excel(excel_file_path, index=False)

print(f"Dados salvos em {excel_file_path}")
