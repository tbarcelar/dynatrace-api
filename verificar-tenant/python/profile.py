import requests
import json
import pandas as pd

# Caminhos de arquivo
config_file_path = "D:/dyna/api/tenant/config.json"
excel_file_path = "D:/dyna/api/tenant/verificar-tenant/excel/profile.xlsx"

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
            'schemaIds': 'builtin:alerting.profile',
            'scopes': 'environment',
            'fields': 'objectId,value',
            'pageSize': 500
        }
        all_data, next_page_key = [], None
        response = requests.get(api_url, params=params, headers=headers)
        while response.status_code == 200:
            data = response.json()
            all_data.extend(data["items"])
            next_page_key = data.get("nextPageKey")
            if next_page_key:
                params = {'nextPageKey': next_page_key}
                response = requests.get(api_url, params=params, headers=headers)
            else:
                break
        process_data(all_data)
    except Exception as e:
        print(f"Erro ao executar o processo: {e}")

# Função auxiliar para processar os dados da API
def process_data(all_data):
    data_to_save = [
        {
            "objectId": item["objectId"],
            "name": item["value"]["name"]
        } for item in all_data
    ]
    df = pd.DataFrame(data_to_save)
    print(df)
    print("------------------  Profile finalizado --------------------------")
    df.to_excel(excel_file_path, index=False)
    print(f'Arquivo Excel salvo com sucesso em: {excel_file_path}')

if __name__ == "__main__":
    print("Iniciando o processo...")
    main()
    print("Processo concluído.")
