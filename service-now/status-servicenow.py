import requests
import json
import pandas as pd
from datetime import datetime

# Caminhos dos arquivos
CONFIG_PATH = 'D:/dyna/api/token/relatorio/config.json'  # Caminho do arquivo JSON de configuração
EXCEL_PATH = 'D:/dyna/api/service-now/excel/token-service-now.xlsx'  # Caminho do arquivo Excel de entrada
RESULT_EXCEL_PATH = 'D:/dyna/api/service-now/excel/status_servicenow.xlsx'  # Caminho para salvar o arquivo Excel de saída

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

# Carregar dados do Excel
def load_excel(file_path):
    """Carrega dados do arquivo Excel."""
    try:
        return pd.read_excel(file_path)
    except FileNotFoundError:
        print(f"Erro: O arquivo {file_path} não foi encontrado.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Erro ao carregar o arquivo Excel: {e}")
        return pd.DataFrame()

# Função para verificar o uso dos tokens
def check_token_usage(config, df):
    """Verifica a última vez que os tokens foram usados."""
    requests_data = config.get('requests_data', [])
    excel_data = []
    for request_data in requests_data:
        tenant_url = request_data.get('url', '')
        token = request_data.get('token', '')
        
        matching_rows = df[df['tenant'] == tenant_url]
        if matching_rows.empty:
            print(f"Tenant not found in Excel: {tenant_url}")
            excel_data.append({
                'Nome Cliente': request_data.get('name', 'N/A'),
                'tenant': tenant_url,
                'Status': 'Token not found',
                'Data de Verificação': 'N/A'
            })
            continue
        
        id_value = matching_rows.iloc[0]['id']
        url = f"{tenant_url}/api/v2/apiTokens/{id_value}"
        headers = {
            'accept': 'application/json; charset=utf-8',
            'Authorization': f'Api-Token {token}',
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_response = response.json()
            status = 'OK' if json_response.get('lastUsedDate') else 'NOK'
            excel_data.append({
                'Data de Verificação': (datetime.fromisoformat(json_response.get('lastUsedDate')).strftime('%d/%m/%Y') if json_response.get('lastUsedDate') else 'N/A'),
                'Nome Cliente': request_data.get('name', 'N/A'),
                'tenant': tenant_url,
                'Status': status,
            })
            print(f"Nome Cliente: {request_data.get('name', 'N/A')}")
            print(f"Data de Verificação: {excel_data[-1]['Data de Verificação']}")
            print(f"Tenant: {tenant_url}")
            print(f"Status: {status}")
            print()
        elif response.status_code == 404:
            print(f"Token not found for Tenant: {tenant_url}")
            excel_data.append({
                'Nome Cliente': request_data.get('name', 'N/A'),
                'tenant': tenant_url,
                'Status': 'Token not found',
                'Data de Verificação': 'N/A'
            })
        else:
            print(f'Erro na solicitação para {request_data["name"]}: {response.status_code}')
    
    return pd.DataFrame(excel_data)

# Função para salvar os resultados no Excel
def save_results_to_excel(df, file_path):
    """Salva os resultados no arquivo Excel."""
    df.to_excel(file_path, index=False)
    print(f"Dados salvos no Excel: {file_path}")

# Função principal
def main():
    print("Iniciando o processo...")

    # Carregar a configuração
    config = load_config(CONFIG_PATH)
    if not config:
        print("Erro ao carregar a configuração.")
        return

    # Carregar os dados do Excel
    df = load_excel(EXCEL_PATH)
    if df.empty:
        print("Erro ao carregar os dados do Excel.")
        return

    # Verificar o uso dos tokens
    result_df = check_token_usage(config, df)
    if result_df.empty:
        print("Nenhum dado a ser salvo.")
    else:
        # Reorganizar as colunas
        result_df = result_df[['Data de Verificação', 'Nome Cliente', 'tenant', 'Status']]
        save_results_to_excel(result_df, RESULT_EXCEL_PATH)
    print('------------ Finalizado -------------------')

if __name__ == "__main__":
    main()
