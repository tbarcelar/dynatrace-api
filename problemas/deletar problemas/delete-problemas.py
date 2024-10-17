import json
import pandas as pd
import requests

# Caminhos dos arquivos
CONFIG_PATH = 'D:/dyna/api/problemas/deletar-problemas/config.json'  # Caminho do arquivo JSON de configuração
EXCEL_PATH = 'D:/dyna/api/problemas/excel/problemasid.xlsx'  # Caminho para carregar o arquivo Excel

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

def get_base_url_and_token(config_data):
    """Extrai URL base e token da configuração."""
    base_url = config_data["requests_data"][0].get('url')
    token = config_data["requests_data"][0].get('token')
    if not base_url or not token:
        raise ValueError("URL base ou token não encontrados no JSON de configuração.")
    return base_url, token

def delete_problem(base_url, token, problem_id):
    """Envia solicitação para deletar o problema específico."""
    close_url = f'{base_url}/api/v2/problems/{problem_id}/close'
    headers = {
        'accept': 'application/json; charset=utf-8',
        'Authorization': f'Api-Token {token}',  # Utilizar o token do JSON de configuração
        'Content-Type': 'application/json; charset=utf-8',
    }
    json_data = {'message': 'string'}  # Mensagem pode ser qualquer coisa, não é relevante para o fechamento do problema
    response = requests.post(close_url, headers=headers, json=json_data)
    return response.status_code

# Carregar a configuração
config_data = load_config(CONFIG_PATH)
base_url, token = get_base_url_and_token(config_data)

# Carregar o arquivo Excel
df = pd.read_excel(EXCEL_PATH)

# Iterar sobre as linhas do DataFrame e deletar problemas
for index, row in df.iterrows():
    problem_id = row['problemId']
    status_code = delete_problem(base_url, token, problem_id)
    if status_code in [200, 204]:
        print(f'Sucesso: Problema {problem_id} fechado com sucesso.')
    else:
        print(f'Erro {status_code}: Problema {problem_id}.')

print("Processo de deleção de problemas finalizado.")
