import requests
import json
import pandas as pd
import os

with open('C:/Users/xxxxxxxxxxx/config.json') as config_file:
    config_data = json.load(config_file)

api_metrics = {
    'metrics': 'builtin:billing.ddu.metrics.total:splitBy():sort(value(auto,descending)):limit(100):names',
    'log': 'builtin:billing.ddu.log.total:splitBy():sort(value(auto,descending)):limit(100):names',
    'events': 'builtin:billing.ddu.events.total:splitBy():sort(value(auto,descending)):limit(100):names'
}

# Inicializar um DataFrame vazio para armazenar todos os dados
final_df = pd.DataFrame(columns=['Timestamp', 'Tenant', 'Metrics', 'Log', 'Events'])

# Iterar sobre as solicitações no arquivo de configuração JSON
for request_data in config_data['requests_data']:
    request_name = request_data['name']
    url = request_data['url']
    token = request_data['token']

    # Inicializar listas vazias para cada métrica
    metrics_values = []
    log_values = []
    events_values = []
    timestamps = []

    # Itere sobre as APIs e faça solicitações para cada uma delas
    for api_name, metric_selector in api_metrics.items():
        # Construir o cabeçalho com o token
        headers = {
            'accept': 'application/json',
            'Authorization': f'Api-Token {token}',
        }

        response = requests.get(
            f'{url}/api/v2/metrics/query?metricSelector={metric_selector}&from=2023-05-01 00:00&to=2023-05-30 23:59&resolution=Inf',
            headers=headers,
        )

        if response.status_code == 200:
            print(f'Solicitação para {api_name} da API {api_name} bem-sucedida')
            # Analisar a resposta JSON
            data = response.json()

            # Extrair as timestamps (datas) da resposta e converter para o formato desejado
            timestamps = [pd.to_datetime(item['data'][0]['timestamps'][0], unit='ms').strftime('%d/%m/%Y') if 'data' in item and item['data'] and 'timestamps' in item['data'][0] and item['data'][0]['timestamps'] else None for item in data['result']]
            
            # Extrair os valores das métricas correspondentes
            values = [item['data'][0]['values'][0] if 'data' in item and item['data'] and 'values' in item['data'][0] and item['data'][0]['values'] else None for item in data['result']]
            
            if api_name == 'metrics':
                metrics_values = values
            elif api_name == 'log':
                log_values = values
            elif api_name == 'events':
                events_values = values
        else:
            print(f'A solicitação para {api_name} da API {api_name} falhou com código de status {response.status_code}')

    # Adicionar os dados desta solicitação ao DataFrame final
    api_dataframe = pd.DataFrame({
        'Timestamp': timestamps,
        'Tenant': [request_name] * len(timestamps),
        'Metrics': metrics_values,
        'Log': log_values,
        'Events': events_values
    })

    # Preencher valores ausentes com zero
    api_dataframe = api_dataframe.fillna(0)

    # Formate as colunas Metrics, Log e Events
    api_dataframe['Metrics'] = api_dataframe['Metrics'].apply(lambda x: f'{x:.2f}')
    api_dataframe['Log'] = api_dataframe['Log'].apply(lambda x: f'{x:.2f}')
    api_dataframe['Events'] = api_dataframe['Events'].apply(lambda x: f'{x:.2f}')

    final_df = pd.concat([final_df, api_dataframe], ignore_index=True)

# Caminho do arquivo de saída em Excel
excel_file_path = 'C:/Users/ddu.xlsx'

# Verificar se o arquivo Excel existe
if os.path.isfile(excel_file_path):
    # O arquivo Excel existe, portanto, carregue os dados existentes primeiro
    existing_data = pd.read_excel(excel_file_path)
    
    # Concatene os novos dados com os dados existentes
    final_df = pd.concat([existing_data, final_df], ignore_index=True)
else:
    # O arquivo Excel não existe, portanto, use o DataFrame final diretamente
    pass

# Salvar o DataFrame final em um arquivo Excel
final_df.to_excel(excel_file_path, index=False)

print(f'Dados salvos com sucesso em "{excel_file_path}"')
