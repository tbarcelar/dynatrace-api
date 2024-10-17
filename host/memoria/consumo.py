import requests
import json
import pandas as pd

# Caminhos dos arquivos
CONFIG_PATH = 'D:/dyna/api/token/relatorio/config.json'  # Caminho do arquivo JSON de configuração
EXCEL_PATH = 'D:/dyna/api/host/memoria/consumo_memoria.xlsx'  # Caminho para salvar o arquivo Excel

# Carregar configurações do arquivo JSON
def load_config(file_path):
    """Carrega a configuração a partir de um arquivo JSON."""
    try:
        with open(file_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        print(f"Erro: O arquivo {file_path} não foi encontrado.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON em {file_path}.")
        return {}

# Função para consultar a API do Dynatrace
def get_memory_usage(config, start_time, end_time):
    """Consulta a API do Dynatrace para obter o consumo de memória dos hosts."""
    base_url = config["requests_data"][0].get('url')
    token = config["requests_data"][0].get('token')
    headers = {
        'accept': 'application/json',
        'Authorization': f'Api-Token {token}',
    }
    url = (
        f'{base_url}/api/v2/metrics/query?'
        f'metricSelector=(builtin:host.mem.used:splitBy("dt.entity.host"):sort(value(auto,descending)):limit(20)):names'
        f'&from={start_time}'
        f'&to={end_time}'
        f'&resolution=Inf'
    )
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro {response.status_code}: {response.text}")
        return {}

# Função para formatar os valores de bytes para GiB
def bytes_to_gib(value):
    """Converte bytes para GiB e formata o valor."""
    gib_value = value / (1024 ** 3)
    return f"{gib_value:.1f} GiB"

# Função para processar e salvar os dados no Excel
def save_memory_usage_to_excel(data, output_path, start_time, end_time):
    """Salva os dados de uso de memória em um arquivo Excel."""
    results = data.get('result', [])[0].get('data', [])
    records = []
    for item in results:
        records.append({
            'start_time': start_time,
            'end_time': end_time,
            'dt.entity.host.name': item['dimensionMap']['dt.entity.host.name'],
            'dt.entity.host': item['dimensionMap']['dt.entity.host'],
            'values': bytes_to_gib(item['values'][0])
        })

    df = pd.DataFrame(records)
    df.to_excel(output_path, index=False)
    print(f"Dados salvos no Excel: {output_path}")

# Parâmetros de tempo
start_time = '2024-10-16 00:00'
end_time = '2024-10-16 23:59'

# Carregar a configuração
config = load_config(CONFIG_PATH)

# Consultar a API e obter os dados de uso de memória
memory_usage_data = get_memory_usage(config, start_time, end_time)

# Salvar os dados no Excel
if memory_usage_data:
    save_memory_usage_to_excel(memory_usage_data, EXCEL_PATH, start_time, end_time)
    print("Processo concluído com sucesso!")
