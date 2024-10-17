import requests
import json
import pandas as pd
from datetime import datetime, timedelta

# Caminhos dos arquivos
CONFIG_PATH = 'D:/dyna/api/token/relatorio/config.json'  # Caminho do arquivo JSON de configuração
EXCEL_PATH = 'D:/dyna/api/host/consumo/excel/list-hu_licensa.xlsx'  # Caminho para salvar o arquivo Excel

# Função para carregar configurações do arquivo JSON
def load_config(file_path):
    """Carrega a configuração a partir de um arquivo JSON."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: O arquivo {file_path} não foi encontrado.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON em {file_path}.")
        return {}

# Função para fazer a requisição à API e coletar dados de hosts
def coletar_dados_hosts(request_data, start_date, end_date):
    """Coleta dados dos hosts através da API Dynatrace."""
    token = request_data['token']
    endpoint = request_data['url']
    cliente = request_data['name']
    headers = {
        'accept': 'application/json',
        'Authorization': f'Api-Token {token}',
    }
    current_date = start_date
    host_data = []
    while current_date <= end_date:
        # Converter a data para timestamps
        start_timestamp = int(current_date.timestamp()) * 1000
        end_timestamp = int((current_date + timedelta(days=1)).timestamp()) * 1000
        params = {
            'includeDetails': 'false',
            'startTimestamp': start_timestamp,
            'endTimestamp': end_timestamp,
        }
        # Realizar a solicitação HTTP
        print(f"{cliente}, data: {current_date.strftime('%Y-%m-%d')}")
        response = requests.get(f"{endpoint}/api/v1/oneagents", headers=headers, params=params)
        print(f"------------------ {cliente} : Coletando informação --------------------")
        try:
            response_json = response.json()
            # Verificar se a resposta contém a chave 'hosts'
            if 'hosts' in response_json:
                for host_info in response_json['hosts']:
                    entity_id = host_info.get('hostInfo', {}).get('entityId')
                    display_name = host_info.get('hostInfo', {}).get('displayName')
                    consumed_host_units = host_info.get('hostInfo', {}).get('consumedHostUnits')
                    monitoring_mode = host_info.get('configuredMonitoringMode')
                    if entity_id and display_name:
                        # Adicionar os dados do host à lista
                        host_data.append({
                            'Início': start_date.strftime('%d/%m/%Y'),
                            'Fim': end_date.strftime('%d/%m/%Y'),
                            'Endpoint': cliente,
                            'EntityId': entity_id,
                            'DisplayName': display_name,
                            'ConsumedHostUnits': consumed_host_units,
                            'MonitoringMode': monitoring_mode
                        })
        except json.JSONDecodeError:
            print("--------- Erro ----------")
        current_date += timedelta(days=1)  # Avançar para o próximo dia
    return host_data

# Função para salvar os dados no Excel
def salvar_dados_excel(host_data, file_path):
    """Salva os dados dos hosts em um arquivo Excel."""
    df_host_data = pd.DataFrame(host_data)
    df_host_data.drop_duplicates(subset=['DisplayName'], inplace=True)
    df_host_data.to_excel(file_path, index=False)
    print(f'Dados salvos com sucesso em: {file_path}')
    print('----------------- Finalizado ------------------')

# Função principal
def main():
    print("Iniciando o processo...")

    # Carregar o conteúdo do arquivo JSON
    config_data = load_config(CONFIG_PATH)
    if not config_data:
        print("Erro ao carregar a configuração.")
        return

    # Definir as datas de início e fim
    start_date = datetime(2024, 10, 16, 0, 0)
    end_date = datetime(2024, 10, 16, 23, 59)

    # Lista para armazenar os dados dos hosts
    host_data = []

    # Iterar sobre as configurações de solicitação Dynatrace
    for request_data in config_data['requests_data']:
        dados_host = coletar_dados_hosts(request_data, start_date, end_date)
        host_data.extend(dados_host)

    # Salvar os dados no Excel
    salvar_dados_excel(host_data, EXCEL_PATH)

    print('------------ Finalizado -------------------')

if __name__ == "__main__":
    main()
