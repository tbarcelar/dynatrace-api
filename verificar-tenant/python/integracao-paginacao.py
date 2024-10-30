import requests
import json
import pandas as pd

# Caminhos de arquivo
config_file_path = "D:/dyna/api/tenant/config.json"
excel_file_path = "D:/dyna/api/tenant/verificar-tenant/excel/integracacao.xlsx"

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
            'schemaIds': 'builtin:problem.notifications',
            'scopes': '',
            'fields': 'objectId,value',
            'pageSize': 500
        }
        all_items, next_page_key = [], None
        while True:
            if next_page_key:
                params['nextPageKey'] = next_page_key
            response = requests.get(api_url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                all_items.extend(items)
                next_page_key = data.get('nextPageKey')
                if not next_page_key:
                    break
            else:
                print(f"Erro : {response.status_code}")
                break
        process_data(all_items)
    except Exception as e:
        print(f"Erro ao executar o processo: {e}")

# Função auxiliar para processar os dados da API
def process_data(all_items):
    df = pd.DataFrame(all_items)
    print(df)
    print("------------------  Integração finalizado --------------------------")
    df.to_excel(excel_file_path, index=False)
    print(f'Arquivo Excel salvo com sucesso em: {excel_file_path}')

if __name__ == "__main__":
    print("Iniciando o processo...")
    main()
    print("Processo concluído.")
