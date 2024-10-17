import json
import requests
import pandas as pd
from datetime import datetime

# Caminhos dos arquivos
CONFIG_PATH = 'D:/dyna/api/token/relatorio/config.json'  # Caminho do arquivo JSON de configuração
OUTPUT_PATH = 'D:/dyna/api/problemas/excel/relatorio-problem.xlsx'  # Caminho para salvar o arquivo Excel

# Intervalo de tempo desejado
START_TIME_STR = '2024-10-10T00:00:00-03:00'
END_TIME_STR = '2024-10-10T23:59:00-03:00'

# Inicializar lista para armazenar os dados extraídos
extracted_data = []

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

def fetch_problems(url, token, cliente_name):
    """Busca problemas da API e extrai dados específicos."""
    headers = {
        'accept': 'application/json; charset=utf-8',
        'Authorization': f'Api-Token {token}',
    }
    params = {
        'pageSize': '499',
        'from': START_TIME_STR,
        'to': END_TIME_STR,
    }
    full_url = f'{url}/api/v2/problems'

    try:
        response = requests.get(full_url, params=params, headers=headers)
        response.raise_for_status()  # Lança um erro para códigos de status HTTP não 200
        print(f'----------- Verificando: {cliente_name}')
    except requests.RequestException as e:
        print(f"Erro na solicitação para {cliente_name}: {e}")
        return []

    try:
        json_data = json.loads(response.text)
        return json_data.get('problems', [])
    except json.JSONDecodeError:
        print("Erro ao decodificar JSON. Conteúdo da resposta:")
        print(response.text)
        return []

def extract_problem_data(problems):
    """Extrai dados específicos de cada problema."""
    data = []
    for problem in problems:
        display_id = problem.get('displayId', '')
        title = problem.get('title', '')
        impact_level = problem.get('impactLevel', '')
        severity_level = problem.get('severityLevel', '')
        start_time = problem.get('startTime', 0)
        end_time = problem.get('endTime', 0)

        # Obter o nome do host das entidades afetadas
        host_name = ''
        for entity in problem.get('affectedEntities', []):
            host_name = entity.get('name', '')
            break
        if not host_name:
            for entity in problem.get('impactedEntities', []):
                host_name = entity.get('name', '')
                break

        # Formatar os tempos de início e fim
        start_time_formatted = datetime.utcfromtimestamp(start_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
        end_time_formatted = datetime.utcfromtimestamp(end_time / 1000).strftime('%Y-%m-%d %H:%M:%S')

        data.append({
            'Host': host_name,
            'Display ID': display_id,
            'Title': title,
            'Impact Level': impact_level,
            'Severity Level': severity_level,
            'Start Time': start_time_formatted,
            'End Time': end_time_formatted
        })
    return data

# Carregar a configuração
config_data = load_config(CONFIG_PATH)

# Iterar sobre as solicitações no JSON de configuração
for request_data in config_data.get('requests_data', []):
    url = request_data.get('url')
    token = request_data.get('token')
    cliente_name = request_data.get('name')

    if url and token and cliente_name:
        problems = fetch_problems(url, token, cliente_name)
        extracted_data.extend(extract_problem_data(problems))

# Criar DataFrame a partir dos dados extraídos
df = pd.DataFrame(extracted_data)

# Salvar DataFrame em um arquivo Excel
df.to_excel(OUTPUT_PATH, index=False)

print(f'Salvo no excel: {OUTPUT_PATH}')
