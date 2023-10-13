import os
import requests
import json
import pandas as pd

# Caminho para o arquivo JSON de configuração
config_file_path = "C:/Users/config.json"

# Caminho para o diretório de destino do arquivo Excel
output_dir = "C:/Users/excel"

# Verifique se o diretório de destino existe e crie-o se não existir
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Caminho completo para o arquivo Excel de saída
excel_file_path = os.path.join(output_dir, "aws.xlsx")

with open(config_file_path, "r") as config_file:
    config_data = json.load(config_file)


# Inicializar listas vazias para armazenar os dados
ids = []
names = []

# Loop através dos requests_data no arquivo JSON
for request_data in config_data["requests_data"]:
    url = request_data["url"]
    token = request_data["token"]

    # Montar a URL completa para a API
    api_url = f"{url}/api/config/v1/aws/credentials"

    # Definir o header com o token
    headers = {
        "Authorization": f"Api-Token {token}"
    }

    # Fazer a requisição GET
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        # Iterar pelos dicionários na lista
        for item in response.json():
            # Extrair o valor após "AWS_CREDENTIALS-"
            id_value = item["id"].split("-")[1]
            ids.append(id_value)
            names.append(item["name"])
    else:
        print(f"Falha na requisição para {api_url}. Status code: {response.status_code}")

# Criar um DataFrame a partir dos dados coletados
df = pd.DataFrame({"id": ids, "name": names})

# Salvar o DataFrame em um arquivo Excel
df.to_excel(excel_file_path, index=False)

print(f'Dados salvos em {excel_file_path}')