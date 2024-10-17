import json
import requests
import pandas as pd
from datetime import datetime, timedelta

# Caminhos dos arquivos
CONFIG_PATH = "D:/dyna/api/token/relatorio/config.json"  # Caminho do arquivo JSON de configuração
EXCEL_PATH = "D:/dyna/api/host/consumo/excel/list-huL.xlsx"  # Caminho para salvar o arquivo Excel

# Função para carregar configurações do arquivo JSON
def load_config(file_path):
    """Carrega a configuração a partir de um arquivo JSON."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Erro: O arquivo {file_path} não foi encontrado.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON em {file_path}.")
        return {}

# Função para formatar as datas (yyyy-MM-ddTHH:MM)
def format_date_api(date):
    return date.strftime('%Y-%m-%dT%H:%M')

# Função para gerar intervalos semanais
def gerar_intervalos_semanais(data_inicial, data_final):
    intervalos = []
    while data_inicial <= data_final:
        fim_da_semana = min(data_inicial + timedelta(days=6), data_final)  # Até o final da semana ou o último dia
        intervalos.append((data_inicial, fim_da_semana))
        data_inicial = fim_da_semana + timedelta(days=1)  # Próximo dia após o final da semana
    return intervalos

# Função para consultar a API do Dynatrace
def consultar_api(config_data, intervalos_gerais):
    data_list = []
    for intervalo in intervalos_gerais:
        from_date_api = format_date_api(intervalo[0])  # Formato para a API (início da semana)
        to_date_api = format_date_api(intervalo[1])  # Formato para a API (fim da semana)

        # Ajuste para o último intervalo, se for apenas de um dia
        if intervalo[0] == intervalo[1]:
            to_date_api = format_date_api(intervalo[1] + timedelta(days=1))  # Expande até o início do dia seguinte

        for endpoint_data in config_data["requests_data"]:
            # Extrair os dados do endpoint
            url = endpoint_data["url"]
            token = endpoint_data["token"]
            client_name = endpoint_data["name"]

            # Criar o cabeçalho com o token
            headers = {
                'accept': 'application/json',
                'Authorization': f'Api-Token {token}',
            }

            # Parâmetros específicos para a métrica de consumo HU
            params = {
                'metricSelector': '(dsfm:billing.hostunit.connected:splitBy():sort(value(auto,descending)):limit(100)):names:fold(auto)',
                'from': from_date_api,
                'to': to_date_api,
            }

            # Fazer a solicitação com o token no cabeçalho
            response = requests.get(f'{url}/api/v2/metrics/query', params=params, headers=headers)
            print(f"------------------ {client_name} : Coletando informação de {from_date_api} até {to_date_api} --------------------")

            # Verificar se a solicitação foi bem-sucedida
            if response.status_code == 200:
                # Parsear a resposta como JSON
                data = response.json()
                # Verificar se a chave 'result' está presente no JSON retornado
                if 'result' in data and data['result']:
                    # Verificar se há dados e evitar "index out of range"
                    if data['result'][0]['data'] and data['result'][0]['data'][0]['values']:
                        try:
                            # Extrair o valor e arredondar para uma casa decimal
                            value = round(data['result'][0]['data'][0]['values'][0], 1)
                            # Adicionar os dados à lista, incluindo o intervalo de datas
                            data_list.append({
                                'Início': intervalo[0].strftime('%d/%m/%Y'),  # Formato dd/MM/yyyy para o Excel
                                'Fim': intervalo[1].strftime('%d/%m/%Y'),      # Formato dd/MM/yyyy para o Excel
                                'name': client_name,
                                'value': value
                            })
                        except (IndexError, KeyError) as e:
                            print(f"Erro ao acessar dados da resposta para {client_name}: {e}")
                    else:
                        print(f"Sem dados para o intervalo {from_date_api} até {to_date_api} para '{client_name}'.")
                else:
                    print(f"Chave 'result' não encontrada ou vazia para '{client_name}'.")
            else:
                print(f"Falha na solicitação para '{client_name}': {response.status_code}. Resposta: {response.text}")
    return data_list

# Função para salvar os dados no Excel
def salvar_dados_excel(data_list, file_path):
    if data_list:
        result_df = pd.DataFrame(data_list, columns=['Início', 'Fim', 'name', 'value'])
        result_df.to_excel(file_path, index=False)
        print('----------------- Arquivo Excel salvo com sucesso ------------------')
    else:
        print("Nenhum dado foi coletado.")

# Função principal
def main():
    print("Iniciando o processo...")

    # Carregar o conteúdo do arquivo JSON
    config_data = load_config(CONFIG_PATH)

    # Definir as datas de início e fim
    data_inicial = datetime(2024, 10, 1)
    data_final = datetime(2024, 10, 5)

    # Gerar intervalos semanais dentro do período especificado
    intervalos_gerais = gerar_intervalos_semanais(data_inicial, data_final)

    # Consultar a API e obter os dados
    data_list = consultar_api(config_data, intervalos_gerais)

    # Salvar os dados no Excel
    salvar_dados_excel(data_list, EXCEL_PATH)

    print('------------ Finalizado -------------------')

if __name__ == "__main__":
    main()
