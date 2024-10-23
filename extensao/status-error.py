import json
import requests
import pandas as pd

# Caminhos de arquivos
config_path = 'D:/dyna/api/analise/extensao/config-oracle.json'
output_path = 'D:/dyna/api/analise/extensao/excel/status-oracle-error.xlsx'

# Parâmetros da solicitação
params = {
    'from': '2024-10-20T11:00:00-03:00',
    'to': '2024-10-22T23:59:00-03:00',
    'limit': '1000',
    'query': 'event.type="sfm" AND loglevel="error" AND dt.extension.name="com.dynatrace.extension.sql-oracle"',
    'sort': '-timestamp',
}

def load_config(config_path):
    try:
        with open(config_path, 'r') as file:
            config_data = json.load(file)
    except Exception as e:
        print(f'Erro ao carregar o arquivo de configuração: {e}')
        config_data = None
    return config_data

def fetch_logs(url, token, params):
    headers = {
        'accept': 'application/json; charset=utf-8',
        'Authorization': f'Api-Token {token}',
    }
    response = requests.get(f'{url}/api/v2/logs/search', params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Falha na solicitação: {response.status_code}")
        return None

def process_logs(data, name):
    records = []
    unique_combinations = set()
    for result in data['results']:
        content = result['content']
        config_id = result['additionalColumns']['dt.extension.config.id'][0]
        combination = (config_id, content)
        if combination not in unique_combinations:
            unique_combinations.add(combination)
            records.append({'Cliente': name, 'ID': config_id, 'Status': content})
    return records

def save_to_excel(records, output_path):
    df = pd.DataFrame(records)
    df.to_excel(output_path, index=False)
    print(f'Relatório salvo em: {output_path}')

def main():
    print("-------------- Iniciando --------------")
    config_data = load_config(config_path)
    if config_data:
        client_info = config_data['requests_data'][0]
        data = fetch_logs(client_info['url'], client_info['token'], params)
        if data:
            records = process_logs(data, client_info['name'])
            save_to_excel(records, output_path)
    print("-------------- Finalizado --------------")

if __name__ == "__main__":
    main()
