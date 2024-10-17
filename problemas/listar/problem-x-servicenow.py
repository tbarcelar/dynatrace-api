import requests
import json
import pandas as pd
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Caminhos dos arquivos
CONFIG_PATH = 'D:/dyna/api/token/relatorio/config.json'  # Caminho do arquivo JSON de configuração
OUTPUT_PATH = 'D:/dyna/api/problemas/excel/problem-x-servicenow.xlsx'  # Caminho para salvar o arquivo Excel

# Intervalo de tempo desejado
START_TIME_STR = '2024-10-10T00:00:00-03:00'
END_TIME_STR = '2024-10-10T12:59:00-03:00'

# Inicializar listas para armazenar os dados
data_summary = []
data_details = []

def load_config(file_path):
    """Carrega a configuração a partir de um arquivo JSON."""
    try:
        with open(file_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error(f"Erro: O arquivo {file_path} não foi encontrado.")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Erro ao decodificar JSON em {file_path}.")
        return {}

def collect_problems(request_data):
    """Coleta problemas a partir da configuração fornecida."""
    url = request_data.get('url')
    token = request_data.get('token')
    cliente = request_data.get('name')
    headers = {
        'accept': 'application/json; charset=utf-8',
        'Authorization': f'Api-Token {token}',
    }

    # Sem problemSelector
    params_no_filter = {
        'from': START_TIME_STR,
        'to': END_TIME_STR,
        'pageSize': 50,
    }
    logging.info(f"------------------ {cliente} :  Coletando informação  --------------------")

    try:
        response_no_filter = requests.get(f'{url}/api/v2/problems', params=params_no_filter, headers=headers)
        response_no_filter.raise_for_status()  # Lança um erro para códigos de status HTTP não 200
    except requests.RequestException as e:
        logging.error(f"Erro na solicitação (sem filtro) para {cliente}: {e}")
        return []
    
    raw_data = []  # Para armazenar dados brutos
    try:
        data_no_filter = response_no_filter.json()
        problems_no_filter = data_no_filter.get('problems', [])
        for problem in problems_no_filter:
            title = problem.get('title')
            display_id = problem.get('displayId')
            problem_filters = problem.get('problemFilters', [])

            # Adicionar dados brutos
            raw_data.append({
                'Display ID': display_id,
                'Title': title,
                'Problem Filters': [pf.get('name') for pf in problem_filters]  # Armazena os nomes dos filtros
            })

            # Adicionar ao detalhe apenas problemas com o filtro "Service Now"
            if any("service now" in pf.get('name', '').lower() for pf in problem_filters):
                data_details.append({
                    'Cliente': cliente,
                    'Title': title,
                    'Problem ID': problem.get('problemId'),
                })
    except json.JSONDecodeError:
        logging.error("Erro ao decodificar JSON para problemas sem filtro. Conteúdo da resposta:")
        logging.error(response_no_filter.text)
    
    return raw_data

def save_to_excel(summary_data, details_data, output_path):
    """Salva os dados de resumo e detalhes em um arquivo Excel com duas abas."""
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        summary_data.to_excel(writer, sheet_name='Resumo', index=False)
        details_data.to_excel(writer, sheet_name='Detalhes', index=False)

# Carregar a configuração
config_data = load_config(CONFIG_PATH)

# Validação da configuração
if not config_data.get('requests_data'):
    logging.error("A configuração carregada não contém 'requests_data'. Verifique o arquivo de configuração.")
else:
    # Iterar sobre as solicitações no JSON de configuração
    for request_data in config_data.get('requests_data', []):
        raw_data = collect_problems(request_data)

        # Criar um DataFrame a partir dos dados brutos
        df_raw = pd.DataFrame(raw_data)

        # Contar problemas sem filtro (total de displayId)
        total_problems_without_filter = df_raw['Display ID'].nunique()

        # Contar problemas com filtro (com "service now" no nome dos filtros)
        total_problems_with_filter = df_raw[
            df_raw['Problem Filters'].apply(lambda filters: any("service now" in filter_name.lower() for filter_name in filters))
        ]['Display ID'].nunique()

        # Adicionar os dados resumidos à lista
        data_summary.append({
            'Cliente': request_data.get('name'),
            'Total de problemas com filtro': total_problems_with_filter,
            'Total de problemas sem filtro': total_problems_without_filter
        })

    # Criar DataFrames a partir dos dados
    df_summary = pd.DataFrame(data_summary)
    df_details = pd.DataFrame(data_details)

    # Agregar dados de detalhes por cliente e title, contando apenas os problemas com filtro
    df_details_aggregated = df_details.groupby(['Cliente', 'Title']).size().reset_index(name='Total')

    # Salvar DataFrames em um arquivo Excel
    save_to_excel(df_summary, df_details_aggregated, OUTPUT_PATH)

    logging.info(f"Finalizado: {OUTPUT_PATH}")

    # Imprimir os endpoints que falharam
    if not data_details:
        logging.info("Nenhum problema com o filtro 'Service Now' foi encontrado.")
