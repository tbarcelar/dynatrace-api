import requests
import pandas as pd
import json
import os  # Importe o módulo 'os' para lidar com caminhos de diretórios

# Nome do arquivo JSON onde estão a URL e o token
json_file = "C:/Users/config.json"

# Nome do arquivo Excel onde você quer salvar os resultados
excel_file = "C:/Users/list-token.xlsx"

# Certifique-se de que o diretório onde o arquivo Excel será salvo existe
excel_directory = os.path.dirname(excel_file)
if not os.path.exists(excel_directory):
    os.makedirs(excel_directory)

# Abre o arquivo JSON e carrega os dados
with open(json_file) as f:
    data = json.load(f)

# Extrai a URL, nome e token do primeiro item da lista requests_data
url = data["requests_data"][0]["url"]
name = data["requests_data"][0]["name"]
token = data["requests_data"][0]["token"]

# Cabeçalhos da requisição
headers = {
    "Authorization": f"Api-Token {token}"  # scope apiTokens.read
}

# Faz a requisição à API do Dynatrace
response = requests.get(url + "/api/v2/apiTokens", headers=headers)

# Verifica se a requisição foi bem sucedida
if response.status_code == 200:
    # Converte os dados JSON em um DataFrame do pandas
    api_tokens = response.json()["apiTokens"]
    
    # Cria um DataFrame com os dados desejados
    df = pd.DataFrame({
        'Dynatrace': [url] * len(api_tokens),
        'Token': [token_data['id'] for token_data in api_tokens],
        'name': [token_data['name'] for token_data in api_tokens],
        'enabled': [token_data['enabled'] for token_data in api_tokens],
        'owner': [token_data['owner'] for token_data in api_tokens],
        'creationDate': [token_data['creationDate'] for token_data in api_tokens]
    })
    
    # Salva o DataFrame em um arquivo Excel
    df.to_excel(excel_file, index=False)
    print(f"Arquivo {excel_file} salvo com sucesso!")
else:
    print(f"Erro ao fazer a requisição: {response.status_code}")
