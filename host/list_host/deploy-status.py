import requests
import pandas as pd
import json
from datetime import datetime

# Caminhos dos arquivos
CONFIG_PATH = 'D:/dyna/api/token/relatorio/config.json'  # Caminho do arquivo JSON de configuração
EXCEL_PATH = 'D:/dyna/api/host/list_host/excel/deploy-status.xlsx'  # Caminho para salvar o arquivo Excel

# Função para carregar configurações do arquivo JSON
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

# Função para formatar as datas e horas no formato dd/MM/yyyyTHH:mm
def formatar_data(data_str):
    """Formata a data para incluir o 'T' como um literal."""
    return int(datetime.strptime(data_str, "%d/%m/%YT%H:%M").timestamp() * 1000)

# Função para fazer a requisição à API e coletar dados de hosts
def coletar_dados_hosts(api_url, headers, params):
    """Coleta dados dos hosts através da API Dynatrace."""
    all_hosts = []
    next_page_key = None

    while True:
        if next_page_key:
            params['nextPageKey'] = next_page_key
        
        response = requests.get(api_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            hosts = data.get("hosts", [])
            all_hosts.extend(hosts)
            next_page_key = data.get('nextPageKey')

            if not next_page_key:
                break
        else:
            print(f"Falha: {response.status_code}")
            break

    return all_hosts

# Função para processar os dados dos hosts
def processar_dados_hosts(all_hosts):
    """Processa os dados dos hosts e retorna uma lista formatada."""
    formatted_data = []

    for host in all_hosts:
        host_info = host.get("hostInfo", {})

        row = {
            "entityId": host_info.get("entityId"),
            "displayName": host_info.get("displayName"),
            "osType": host_info.get("osType"),
            "cloudType": host_info.get("cloudType"),
            "monitoringMode": host_info.get("monitoringMode"),
            "agentVersion": host_info.get("agentVersion", {}).get("minor"),
            "consumedHostUnits": host_info.get("consumedHostUnits"),
            "softwareTechnologies": ', '.join([tech["type"] for tech in host_info.get("softwareTechnologies", [])])
        }

        first_seen_timestamp = host_info.get("firstSeenTimestamp")
        last_seen_timestamp = host_info.get("lastSeenTimestamp")

        row["Instalação do agente"] = datetime.fromtimestamp(first_seen_timestamp / 1000).strftime('%d/%m/%Y %H:%M') if first_seen_timestamp else "N/A"
        row["Última comunicação"] = datetime.fromtimestamp(last_seen_timestamp / 1000).strftime('%d/%m/%Y %H:%M') if last_seen_timestamp else "N/A"

        current_time = datetime.now().timestamp() * 1000
        status = "Ativo" if last_seen_timestamp and (current_time - last_seen_timestamp < 86400000) else "Inativo"
        row["Status atual"] = status

        formatted_data.append(row)

    return formatted_data

# Função para salvar os dados no Excel
def salvar_dados_excel(formatted_data, file_path):
    """Salva os dados dos hosts em um arquivo Excel."""
    df = pd.DataFrame(formatted_data)
    df.to_excel(file_path, index=False)
    print(f'Dados salvos com sucesso em: {file_path}')

# Função principal
def main():
    print("Iniciando o processo...")

    # Carregar a configuração
    config = load_config(CONFIG_PATH)

    if not config:
        print("Erro ao carregar a configuração.")
        return

    # Extraindo URL e token do JSON
    api_config = config["requests_data"][0]
    url = api_config["url"]
    token = api_config["token"]

    # Construindo a URL completa para a requisição
    api_url = f"{url}/api/v1/oneagents"

    # Definindo cabeçalhos
    headers = {
        'accept': 'application/json; charset=utf-8',
        'Authorization': f'Api-Token {token}',
    }

    # Variáveis de data e hora (inicio e fim) no formato dd/MM/yyyyTHH:mm
    inicio = "01/03/2024T00:00"
    fim = "29/08/2024T23:59"

    # Corrigindo o formato da data e hora para incluir o "T" como um literal
    start_timestamp = formatar_data(inicio)
    end_timestamp = formatar_data(fim)

    # Definindo parâmetros de query
    params = {
        'includeDetails': 'true',
        'availabilityState': 'MONITORED',
        'entitySelector': 'type("HOST")',
        'startTimestamp': start_timestamp,
        'endTimestamp': end_timestamp,
    }

    # Coletar dados dos hosts
    all_hosts = coletar_dados_hosts(api_url, headers, params)

    # Processar os dados dos hosts
    formatted_data = processar_dados_hosts(all_hosts)

    # Salvar os dados no Excel
    salvar_dados_excel(formatted_data, EXCEL_PATH)

    print('------------ Finalizado -------------------')

if __name__ == "__main__":
    main()
