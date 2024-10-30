import requests
import pandas as pd
import json

# Caminhos de arquivo
config_path = 'D:/dyna/api/tenant/config.json'
output_path = 'D:/dyna/api/tenant/verificar-tenant/excel/disable-host.xlsx'

# Função para obter a URL e o token do JSON
def obter_configuracao():
    try:
        with open(config_path, 'r') as file:
            config_data = json.load(file)
        url = config_data['requests_data'][0]['url']
        token = config_data['requests_data'][0]['token']
        return url, token
    except Exception as e:
        print(f"Erro ao carregar a configuração: {e}")
        raise

# Função principal para executar o processo
def main():
    try:
        url, token = obter_configuracao()
        headers = {
            'accept': 'application/json; charset=utf-8',
            'Authorization': f'Api-Token {token}'
        }
        params = {
            'entitySelector': 'type("HOST")',
            'from': 'now-2h'
        }
        all_entities, next_page_key = [], None

        while True:
            if next_page_key:
                params = {'nextPageKey': next_page_key}
            else:
                params = {'entitySelector': 'type("HOST")'}

            response = requests.get(f'{url}/api/v2/entities', params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                all_entities.extend(data['entities'])
                next_page_key = data.get('nextPageKey')
                if not next_page_key:
                    break
            else:
                print(f'Erro {response.status_code}')
                print(f'Erro: {response.text}')
                break

        process_data(all_entities)
    except Exception as e:
        print(f"Erro ao executar o processo: {e}")

# Função auxiliar para processar os dados da API
def process_data(all_entities):
    df = pd.json_normalize(all_entities)
    print(df)
    print("------------------  Host finalizado --------------------------")
    if 'type' in df.columns:
        df.drop(columns=['type'], inplace=True)
    df.to_excel(output_path, index=False)
    print(f'Arquivo Excel salvo com sucesso em: {output_path}')

if __name__ == "__main__":
    print("Iniciando o processo...")
    main()
    print("Processo concluído.")
