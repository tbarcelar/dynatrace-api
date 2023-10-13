import requests
import json
import pandas as pd
import os

# Inicialize um DataFrame vazio para armazenar todos os dados
final_df = pd.DataFrame()

# Função para fazer a solicitação com base nos dados do JSON
def make_request(config_data):
    headers = {
        'accept': 'application/json',
        'Authorization': f'Api-Token {config_data["token"]}',
    }

    url = f'{config_data["url"]}/api/v2/metrics/query'
    params = {
        'metricSelector': 'builtin:billing.ddu.metrics.total:splitBy():sort(value(auto,descending)):limit(100):names',
        'from': '2023-09-20T00:00:00Z',
        'to': '2023-09-27T23:59:00Z',
        'resolution': 'Inf',
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()  # Converter a resposta JSON em um dicionário
        process_data(config_data['name'], data)
        print(f'Solicitação para {config_data["name"]} foi bem-sucedida.')
    else:
        print(f'Erro na solicitação para {config_data["name"]}. Código de status: {response.status_code}')

def process_data(request_name, data):
    # Verifique se 'result' está presente no JSON
    if 'result' in data and data['result']:
        # Verifique se 'data' está presente na primeira entrada de 'result'
        if 'data' in data['result'][0] and data['result'][0]['data']:
            timestamps = data['result'][0]['data'][0]['timestamps']
            values = data['result'][0]['data'][0]['values']

            # Formatar timestamps para o formato desejado
            formatted_timestamps = [pd.to_datetime(timestamp, unit='ms').strftime('%d/%m/%Y') for timestamp in timestamps]

            # Converter os valores para números (caso estejam como texto)
            formatted_values = [pd.to_numeric(value) for value in values]

            # Criar um DataFrame com os dados formatados
            df = pd.DataFrame({'Tenant': [request_name] * len(timestamps),
                               'Timestamp': formatted_timestamps,
                               'Value': formatted_values})

            global final_df
            final_df = pd.concat([final_df, df], ignore_index=True)
        else:
            print(f'Dados ausentes na resposta para {request_name}.')
    else:
        print(f'Resposta vazia ou sem "result" para {request_name}.')

# Carregue os dados de configuração do JSON
with open('C:/Users/config.json', 'r') as json_file:
    config_data = json.load(json_file)

# Itere sobre os itens da lista e faça solicitações para cada um
for request_data in config_data['requests_data']:
    make_request(request_data)

# Arredonde os valores da coluna 'Value' para o número inteiro mais próximo
final_df['Value'] = final_df['Value'].round()

# Caminho do arquivo de saída
excel_file_name = 'C:/Users/metric.xlsx'

# Verifique se o arquivo de saída já existe
if os.path.exists(excel_file_name):
    # Ler o arquivo Excel existente
    existing_data = pd.read_excel(excel_file_name)
    
    # Concatenar os DataFrames existentes com o novo DataFrame
    final_df = pd.concat([existing_data, final_df], ignore_index=True)

# Salvar o DataFrame final em um único arquivo Excel
final_df.to_excel(excel_file_name, index=False)

print('Todas as solicitações foram concluídas e os dados foram salvos com sucesso.')
