import requests
import json
import pandas as pd

# Caminhos de arquivo
config_file_path = "D:/dyna/api/tenant/config.json"
excel_file_path = "D:/dyna/api/tenant/verificar-tenant/excel/tag.xlsx"

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
            'schemaIds': 'builtin:tags.auto-tagging',
            'scopes': 'environment',
            'fields': 'objectId,value'
        }
        response = requests.get(api_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json().get('items', [])
            process_data(data)
        else:
            print(f"Erro na solicitação. Código de status: {response.status_code}")
    except Exception as e:
        print(f"Erro ao executar o processo: {e}")

# Função auxiliar para processar os dados da API
def process_data(items):
    df = pd.DataFrame(items)
    print(df)
    print("------------------  Tag finalizado --------------------------")
    df.to_excel(excel_file_path, index=False)
    print(f"Arquivo Excel salvo com sucesso em: {excel_file_path}")

if __name__ == "__main__":
    print("Iniciando o processo...")
    main()
    print("Processo concluído.")
