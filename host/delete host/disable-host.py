import requests
import pandas as pd
import json

# Caminhos dos arquivos
CONFIG_PATH = 'D:/dyna/api/host/delete host/config.json'  # Caminho do arquivo JSON de configuração
EXCEL_PATH = 'D:/dyna/api/host/delete host/disable-host.xlsx'  # Caminho para o arquivo Excel

# Função para carregar configurações do arquivo JSON
def load_config(file_path):
    """Carrega a configuração a partir de um arquivo JSON."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Erro: O arquivo {file_path} não foi encontrado.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON em {file_path}.")
        return {}

# Função para desabilitar os hosts
def desabilitar_host(url, token, host_id):
    """Desabilita o host especificado."""
    headers = {
        'accept': 'application/json; charset=utf-8',
        'Authorization': f'Api-Token {token}',
    }
    json_data = [
        {
            'schemaId': 'builtin:host.monitoring',
            'schemaVersion': '1.4',
            'scope': f'{host_id}',
            'value': {
                'enabled': False,
            },
        },
    ]
    response = requests.post(f'{url}/api/v2/settings/objects', headers=headers, json=json_data)
    return response

# Função para carregar os dados do Excel
def load_excel(file_path):
    """Carrega os dados do arquivo Excel."""
    try:
        return pd.read_excel(file_path)
    except FileNotFoundError:
        print(f"Erro: O arquivo {file_path} não foi encontrado.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Erro ao carregar o arquivo Excel: {e}")
        return pd.DataFrame()

# Função principal
def main():
    print("Iniciando o processo...")

    # Carregar a configuração
    config_data = load_config(CONFIG_PATH)
    if not config_data:
        print("Erro ao carregar a configuração.")
        return

    # Extrair URL e token do JSON
    url = config_data['requests_data'][0]['url']
    token = config_data['requests_data'][0]['token']

    # Carregar o arquivo Excel
    df = load_excel(EXCEL_PATH)
    if df.empty:
        print("Erro ao carregar os dados do Excel.")
        return

    # Iterar sobre as linhas do DataFrame
    for index, row in df.iterrows():
        # Obter o ID do host da coluna 'entityId'
        host_id = row['entityId']
        
        # Desabilitar o host
        response = desabilitar_host(url, token, host_id)
        
        # Verificar a resposta
        if response.status_code == 200:
            # Verificar se o host já está desabilitado
            if 'Host já está desabilitado' in response.text:
                print(f'Host {host_id} já está desabilitado!')
            else:
                print(f'Host {host_id} desabilitado com sucesso!')
        else:
            print(f'Falha ao desabilitar o host {host_id}. Código de status: {response.status_code}')
            print(f'Resposta do servidor: {response.text}')

    print('------------ Finalizado -------------------')

if __name__ == "__main__":
    main()
