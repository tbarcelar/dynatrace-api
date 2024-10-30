import requests
import pandas as pd
import json
import os

# Caminhos de arquivo
json_file = "D:/dyna/api/tenant/config.json"
excel_file = "D:/dyna/api/tenant/verificar-tenant/excel/list-token.xlsx"

# Função para verificar e criar diretório
def verificar_criar_diretorio(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Função para obter a URL e o token do JSON
def obter_configuracao():
    try:
        with open(json_file) as f:
            data = json.load(f)
        url = data["requests_data"][0]["url"]
        name = data["requests_data"][0]["name"]
        token = data["requests_data"][0]["token"]
        return url, name, token
    except Exception as e:
        print(f"Erro ao carregar a configuração: {e}")
        raise

# Função principal para executar o processo
def main():
    try:
        verificar_criar_diretorio(os.path.dirname(excel_file))
        url, name, token = obter_configuracao()
        headers = {"Authorization": f"Api-Token {token}"}
        response = requests.get(url + "/api/v2/apiTokens", headers=headers)
        if response.status_code == 200:
            data = response.json()["apiTokens"]
            process_data(data, url)
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro ao executar o processo: {e}")

# Função auxiliar para processar os dados da API
def process_data(api_tokens, url):
    df = pd.DataFrame({
        'Dynatrace': [url] * len(api_tokens),
        'Token': [token_data['id'] for token_data in api_tokens],
        'name': [token_data['name'] for token_data in api_tokens],
        'enabled': [token_data['enabled'] for token_data in api_tokens],
        'owner': [token_data['owner'] for token_data in api_tokens],
        'creationDate': [token_data['creationDate'] for token_data in api_tokens]
    })
    print(df)
    print("------------------  token finalizado --------------------------")
    df.to_excel(excel_file, index=False)
    print(f"Arquivo {excel_file} salvo com sucesso!")

if __name__ == "__main__":
    print("Iniciando o processo...")
    main()
    print("Processo concluído.")
