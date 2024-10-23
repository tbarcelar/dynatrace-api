import json
import requests
from collections import defaultdict
import pandas as pd
from datetime import datetime

# Caminhos de arquivos
config_path = 'D:/dyna/api/token/relatorio/config.json'
output_path = 'D:/dyna/api/analise/extensao/excel/relatorio_extensoes.xlsx'

# Parâmetros de tempo (pode ser dinamicamente ajustado conforme necessário)
from_time = '2024-10-20T12:45:00-03:00'
to_time = '2024-10-22T13:16:00-03:00'

def load_config(config_path):
    try:
        with open(config_path, 'r') as file:
            config_data = json.load(file)
    except Exception as e:
        print(f'Erro ao carregar o arquivo de configuração: {e}')
        config_data = None
    return config_data

def fetch_data(client_info, from_time, to_time):
    url = client_info['url']
    cliente = client_info['name']
    token = client_info['token']
    client_data = defaultdict(set)
    headers = {
        'accept': 'application/json; charset=utf-8',
        'Authorization': f'Api-Token {token}',
    }
    api_url = (f'{url}/api/v2/metrics/query?metricSelector=(dsfm:extension.config.status:'
               f'splitBy("dt.extension.name","dt.extension.config.id","dt.extension.status"):'
               f'sort(value(auto,descending)):limit(20)):names&from={from_time}&to={to_time}&resolution=Inf')
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"------------------ {cliente} : Coletando informação --------------------")
        for entry in data['result'][0]['data']:
            extension_name = entry['dimensionMap']['dt.extension.name']
            extension_status_value = entry['dimensionMap']['dt.extension.status']
            if extension_status_value != 'OK':
                extension_status_value = 'NOK'
            client_data[extension_name].add(extension_status_value)
    else:
        print(f"Falha na solicitação para {cliente}: {response.status_code}")
        client_data = None
    return cliente, client_data

def process_data(config_data, from_time, to_time):
    today_date = datetime.today().strftime('%d/%m/%Y')
    report_data = []

    for client_info in config_data['requests_data']:
        cliente, client_data = fetch_data(client_info, from_time, to_time)
        if client_data is None:
            report_data.append({
                'Cliente': cliente,
                'Extensão': None,
                'status': f'Falha na solicitação',
                'Data de verificação': today_date
            })
            continue

        for ext_name, statuses in client_data.items():
            if 'OK' in statuses and 'NOK' in statuses:
                report_data.append({
                    'Cliente': cliente,
                    'Extensão': ext_name,
                    'status': 'OK',
                    'Data de verificação': today_date
                })
                report_data.append({
                    'Cliente': cliente,
                    'Extensão': ext_name,
                    'status': 'NOK',
                    'Data de verificação': today_date
                })
            elif 'OK' in statuses:
                report_data.append({
                    'Cliente': cliente,
                    'Extensão': ext_name,
                    'status': 'OK',
                    'Data de verificação': today_date
                })
            elif 'NOK' in statuses:
                report_data.append({
                    'Cliente': cliente,
                    'Extensão': ext_name,
                    'status': 'NOK',
                    'Data de verificação': today_date
                })
        if not client_data:
            report_data.append({
                'Cliente': cliente,
                'Extensão': None,
                'status': 'Nenhuma informação disponível',
                'Data de verificação': today_date
            })
    return report_data

def save_report(report_data, output_path):
    df = pd.DataFrame(report_data)
    df.to_excel(output_path, index=False)
    print(f'Relatório salvo em: {output_path}')

def main():
    print("Iniciando a execução do script.")
    config_data = load_config(config_path)
    if config_data:
        report_data = process_data(config_data, from_time, to_time)
        save_report(report_data, output_path)
    print("Finalizando a execução do script.")

if __name__ == "__main__":
    main()
