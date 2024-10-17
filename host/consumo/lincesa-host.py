import requests
import json
import pandas as pd

# Caminhos dos arquivos
CONFIG_PATH = 'D:/dyna/api/token/relatorio/config.json'  # Caminho do arquivo JSON de configuração
EXCEL_PATH = 'D:/dyna/api/host/consumo/excel/licensa.xlsx'  # Caminho para salvar o arquivo Excel

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

# Função para fazer a requisição à API com paginação
def fazer_requisicao_api(url, token):
    """Faz a requisição à API com paginação e retorna todas as respostas."""
    headers = {
        'Authorization': f'Api-Token {token}',
        'accept': 'application/json; charset=utf-8',
    }
    params = {
        'includeDetails': 'true',
    }
    responses = []  # Lista para armazenar todas as respostas
    while True:
        response = requests.get(f'{url}/api/v1/entity/infrastructure/hosts', params=params, headers=headers)
        if response.status_code == 200:
            responses.append(response.json())
            next_page_key = response.headers.get('Next-Page-Key')
            if next_page_key:
                params['nextPageKey'] = next_page_key
            else:
                break
        else:
            print(f"Erro para a URL {url}: {response.status_code}")
            return None
    return responses

# Função para extrair todos os valores do campo "monitoringMode" de uma resposta
def extrair_todos_monitoring_mode(respostas):
    """Extrai todos os valores do campo 'monitoringMode' de uma resposta."""
    monitoring_modes = []
    for resposta_lista in respostas:
        for resposta in resposta_lista:
            if resposta and "monitoringMode" in resposta:
                monitoring_modes.append(resposta["monitoringMode"])
    return monitoring_modes

# Função principal
def main():
    print("Iniciando o processo...")

    # Carrega os dados do arquivo config.json
    config_data = load_config(CONFIG_PATH)

    if not config_data:
        print("Erro ao carregar a configuração.")
        return

    # Lista para armazenar todos os DataFrames de cada endpoint
    dfs = []
    endpoints_with_full_stack = set()

    # Itera sobre os endpoints no arquivo config.json
    for endpoint_data in config_data["requests_data"]:
        url = endpoint_data["url"]
        token = endpoint_data["token"]

        # Faz a requisição à API com paginação
        response_data = fazer_requisicao_api(url, token)

        if response_data is not None:
            # Extrai todos os monitoringMode da resposta
            monitoring_modes = extrair_todos_monitoring_mode(response_data)
            if not monitoring_modes:
                monitoring_modes_str = "N/A"
            else:
                monitoring_modes_str = ' / '.join(set(monitoring_modes))
                if "FULL_STACK" in monitoring_modes:
                    endpoints_with_full_stack.add(endpoint_data["name"])

            dfs.append(pd.DataFrame({
                "Name": [endpoint_data["name"]],
                "URL": [url],
                "Monitoring Modes": [monitoring_modes_str]
            }))

    # Concatena todos os DataFrames em um único DataFrame
    final_df = pd.concat(dfs, ignore_index=True)
    
    # Imprime a lista de endpoints com FULL_STACK
    print(f'Endpoints com FULL_STACK: {endpoints_with_full_stack}')
    
    # Imprime o DataFrame final
    print(final_df)

    # Salva os dados em um arquivo Excel
    final_df.to_excel(EXCEL_PATH, index=False)
    print(f'Dados salvos com sucesso em: {EXCEL_PATH}')
    print('------------ Finalizado -------------------')

if __name__ == "__main__":
    main()
