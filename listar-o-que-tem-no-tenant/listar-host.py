import json
import tkinter as tk
from tkinter import simpledialog, messagebox
import requests
import pandas as pd
from datetime import datetime, timedelta
from openpyxl import load_workbook, Workbook

# Função para abrir o pop-up e obter o nome da request
def obter_nome_request():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal

    nome_da_request = simpledialog.askstring("Nome da Request", "Digite o nome da request:")

    root.destroy()  # Fecha a janela pop-up

    return nome_da_request

# Função para comparar strings ignorando maiúsculas e minúsculas
def comparar_strings_ignore_case(str1, str2):
    return str1.lower() == str2.lower()

# Função para obter o número de dias da janela pop-up
def obter_numero_de_dias():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal

    numero_de_dias = simpledialog.askinteger("Número de Dias", "Quantos dias deseja:")

    root.destroy()  # Fecha a janela pop-up

    return numero_de_dias

# Loop principal
nome_da_request = None  # Inicializa a variável fora do loop

while True:
    # Obter o nome da request usando a função
    nome_da_request = obter_nome_request()
    
    if not nome_da_request:
        # Se nenhum nome for fornecido, sair do loop
        break

    # Caminho para o JSON original
    caminho_json_original = "C:/Users/config.json"

    # Carrega o JSON original
    with open(caminho_json_original, 'r') as json_file:
        data = json.load(json_file)

    # Procura a request pelo nome (ignorando maiúsculas e minúsculas)
    request_encontrada = None
    for request in data['requests_data']:
        if comparar_strings_ignore_case(request['name'], nome_da_request):
            request_encontrada = request
            break

    # Verifica se a request foi encontrada
    if request_encontrada:
        # Caminho para o JSON que você deseja atualizar (com o caminho correto)
        caminho_json_atualizar = "C:/Users/config.json"

        # Carrega o JSON para atualizar
        with open(caminho_json_atualizar, 'r') as json_atualizar_file:
            json_atualizar = json.load(json_atualizar_file)

        # Substitui o conteúdo existente pela nova request
        json_atualizar['requests_data'] = [request_encontrada]

        # Salva o JSON atualizado
        with open(caminho_json_atualizar, 'w') as json_atualizar_file:
            json.dump(json_atualizar, json_atualizar_file, indent=4)

        # Obter o número de dias usando a função
        numero_de_dias = obter_numero_de_dias()

        if numero_de_dias:
            # Lendo o arquivo json com os dados da url e do token
            json_path = caminho_json_atualizar
            with open(json_path) as f:
                data = json.load(f)

            # Iterando sobre os dados do json
            for item in data["requests_data"]:
                url = item["url"]
                name = item["name"]
                token = item["token"]
                headers = {
                    'accept': 'application/json; charset=utf-8',
                    'Authorization': f'Api-Token {token}',
                }
                url = f"{url}/api/v1/entity/infrastructure/hosts"

                # Calculate the date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=numero_de_dias)  # Alterado para coletar dados dos últimos xx dias

                # Create an empty DataFrame to hold the data
                final_df = pd.DataFrame(columns=['displayName', 'osType', 'monitoringMode', 'agentVersion', 'entityId', 'cloudType'])

                # Convert dates to ISO 8601 format (expected by the API)
                start_date_iso = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                end_date_iso = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

                params = {
                    'fromTs': start_date_iso,
                    'toTs': end_date_iso,
                }

                response = requests.get(url, params=params, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    df = pd.DataFrame(data)

                    # Remove duplicatas com base na coluna 'entityId'
                    df = df.drop_duplicates(subset='entityId', keep='first')

                    if 'agentVersion' in df.columns:
                        df['agentVersion'] = df['agentVersion'].apply(lambda x: x['minor'] if isinstance(x, dict) else None)

                    # Filtra os registros onde monitoringMode é FULL_STACK ou INFRASTRUCTURE
                    df = df[df['monitoringMode'].isin(['FULL_STACK', 'INFRASTRUCTURE'])]

                    # Seleciona as colunas necessárias
                    selected_columns = ['displayName', 'osType', 'monitoringMode', 'agentVersion', 'entityId', 'cloudType']
                    df = df[selected_columns]

                    # Append the data to the final DataFrame
                    final_df = pd.concat([final_df, df], ignore_index=True)
                else:
                    print(f"Erro ao obter os dados da API no tenant {name}: {response.text}")

            # Remove duplicatas novamente com base na coluna 'entityId'
            final_df = final_df.drop_duplicates(subset='entityId', keep='first')

            # Save the final DataFrame to an excel file
            final_df.to_excel("C:/Users/tbarc/Dedalus Prime/Monitoração & Continuidade - Dynatrace/Api/host/list-host-de-1-tenant/list-host.xlsx", index=False)

            # Exibe uma mensagem de "Finalizado" e fecha o pop-up
            messagebox.showinfo("Finalizado", "O processo foi concluído.")

        # Após a conclusão do segundo código, encerrar o loop
        break
    else:
        # Se o nome da request não for encontrado, exibir uma mensagem de erro
        messagebox.showerror("Erro", f"Request '{nome_da_request}' não encontrada. Digite novamente.")
