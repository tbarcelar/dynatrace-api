import requests
import json
import pandas as pd

url = "https://api.dynatrace.com/env/v1/accounts/ID DA CONTA PRINCIPAL/environments"
headers = {
    'Authorization': 'Bearer xxxxxxxxx' # coloque o token gerado pelo oauth
}

response = requests.get(url, headers=headers)
data = response.json()  # Carrega a resposta JSON

# Verifique a estrutura do JSON e substitua 'chave_correta' pela chave real que contém os dados das assinaturas
df = pd.json_normalize(data['tenantResources'])

# Salvar em um arquivo Excel, altere o nome do usuário
df.to_excel('C:/Users/environments.xlsx', index=False)  

