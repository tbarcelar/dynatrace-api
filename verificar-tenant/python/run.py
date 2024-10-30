import requests
import json
import pandas as pd
import os

# Caminhos de arquivo
config_file_path = "D:/dyna/api/tenant/config.json"
excel_file_path = "D:/dyna/api/tenant/verificar-tenant/excel/list-run.xlsx"

# Função para obter a URL e o token do JSON
def obter_configuracao():
    try:
        with open(config_file_path, "r") as config_file:
            config_data = json.load(config_file)
        url = config_data["requests_data"][0]["url"]
        token = config_data["requests_data"][0]["token"]
        return url, token
    except Exception as e:
        print(f"Erro ao carregar a configuração: {e}")
        raise

# Função principal para executar o processo
def main():
    try:
        url, token = obter_configuracao()
        api_url = f"{url}/api/v2/settings/objects"
        headers = {
            'Accept': 'application/json; charset=utf-8',
            'Content-Type': 'application/json; charset=utf-8',
            "Authorization": f"Api-Token {token}"
        }
        params = {
            'schemaIds': 'builtin:rum.web.enablement',
            'fields': 'objectId,value'
        }
        response = requests.get(api_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json().get('items', [])
            process_data(data)
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro ao executar o processo: {e}")

# Função auxiliar para processar os dados da API
def process_data(settings_objects):
    extracted_data = [
        {'objectId': item['objectId'], 'value': item['value']}
        for item in settings_objects
    ]
    df = pd.DataFrame(extracted_data)
    print(df)
    try:
        df.to_excel(excel_file_path, index=False)
        print(f"Dados salvos com sucesso em {excel_file_path}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")
    print("---------------- Finalizado Run ---------------------")

if __name__ == "__main__":
    print("Iniciando o processo...")
    main()
    print("Processo concluído.")
