import requests
import json
import pandas as pd

# Caminhos dos arquivos
CONFIG_PATH = 'D:/dyna/api/token/relatorio/config.json'  # Caminho do arquivo JSON de configuração
EXCEL_PATH = 'D:/dyna/api/service-now/excel/token-service-now.xlsx'  # Caminho para salvar o arquivo Excel

# Carregar configurações do arquivo JSON
def load_config(file_path):
    """Carrega a configuração a partir de um arquivo JSON."""
    try:
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print(f"Erro: O arquivo {file_path} não foi encontrado.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON em {file_path}.")
        return {}

# Fazer a requisição à API do Dynatrace
def make_api_request(endpoint_url, token):
    """Faz a requisição à API do Dynatrace e retorna a resposta JSON."""
    headers = {
        'accept': 'application/json; charset=utf-8',
        'Authorization': f'Api-Token {token}',
    }
    params = {'sort': '-creationDate'}
    response = requests.get(f'{endpoint_url}/api/v2/apiTokens', params=params, headers=headers)
    return response

# Processar a resposta JSON da API
def process_response(response, name, endpoint_url):
    """Processa a resposta JSON da API e retorna um DataFrame com os tokens filtrados."""
    try:
        json_response = response.json()
        api_tokens = json_response.get('apiTokens', [])
        filtered_tokens = [token for token in api_tokens if 'ServiceNow'.lower() in token.get('name', '').lower() and token.get('name', '').lower() != 'api-status-servicenow']
        
        if not filtered_tokens:
            result_df = pd.DataFrame([{
                'Cliente': name,
                'tenant': endpoint_url,
                'id': None,
                'name': None,
                'enabled': None,
            }])
        else:
            result_df = pd.DataFrame(columns=['Cliente', 'tenant', 'id', 'name', 'enabled'])
            for token in filtered_tokens:
                result_df = pd.concat([result_df, pd.DataFrame([{
                    'Cliente': name,
                    'tenant': endpoint_url,
                    'id': token.get('id', ''),
                    'name': token.get('name', ''),
                    'enabled': token.get('enabled', ''),
                }])], ignore_index=True)
                print(f"Cliente: {name}")
                print(f"Tenant: {endpoint_url}")
                print(f"Token ID: {token.get('id', '')}")
                print(f"Token Name: {token.get('name', '')}")
                print(f"Token Enabled: {token.get('enabled', '')}")
                print("\n")
        return result_df
    except json.decoder.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON para {name}: {e}")
        return pd.DataFrame(columns=['Cliente', 'tenant', 'id', 'name', 'enabled'])

# Função principal para listar os tokens
def list_tokens(config):
    """Lista os tokens do Dynatrace e salva os resultados em um arquivo Excel."""
    requests_data = config.get('requests_data', [])
    if requests_data:
        combined_result_df = pd.DataFrame(columns=['Cliente', 'tenant', 'id', 'name', 'enabled'])
        for request_data in requests_data:
            endpoint_url = request_data.get('url', '')
            token = request_data.get('token', '')
            name = request_data.get('name', '')
            
            if endpoint_url and token:
                print(f'Verificando: {name}')
                response = make_api_request(endpoint_url, token)
                result_df = process_response(response, name, endpoint_url)
                combined_result_df = pd.concat([combined_result_df, result_df], ignore_index=True)
            else:
                print(f"Erro: {name}.")
        
        combined_result_df.to_excel(EXCEL_PATH, index=False)
        print(f"Finalizado: {EXCEL_PATH}")
    else:
        print("Erro: Nenhum dado de solicitação encontrado no JSON.")

# Carregar a configuração e listar tokens
config = load_config(CONFIG_PATH)
list_tokens(config)
print('------------ Finalizado -------------------')
