import os
import requests
import json
import pandas as pd

# Caminhos de arquivo
config_file_path = "D:/dyna/api/tenant/config.json"
output_dir = "D:/dyna/api/tenant/verificar-tenant/excel"
excel_file_path = os.path.join(output_dir, "azure.xlsx")

# Função principal para executar o processo
def main():
    try:
        # Verificar e criar diretório de destino, se necessário
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Carregar dados do arquivo JSON de configuração
        with open(config_file_path, "r") as config_file:
            config_data = json.load(config_file)

        # Inicializar listas vazias para armazenar os dados
        ids, names = [], []

        # Loop através dos requests_data no arquivo JSON
        for request_data in config_data["requests_data"]:
            url = request_data["url"]
            token = request_data["token"]
            # Montar a URL completa para a API
            api_url = f"{url}/api/config/v1/azure/credentials"
            # Definir o header com o token
            headers = {"Authorization": f"Api-Token {token}"}
            # Fazer a requisição GET
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                process_response(response.json(), ids, names)
            else:
                print(f"Falha na requisição para {api_url}. Status code: {response.status_code}")

        # Criar um DataFrame a partir dos dados coletados
        df = pd.DataFrame({"id": ids, "name": names})
        print(df)
        print("------------------  Azure Finalizado --------------------------")
        # Salvar o DataFrame em um arquivo Excel
        df.to_excel(excel_file_path, index=False)
        print(f'Arquivo Excel salvo com sucesso em: {excel_file_path}')

    except Exception as e:
        print(f"Erro ao executar o processo: {e}")

# Função auxiliar para processar a resposta da API
def process_response(response_data, ids, names):
    for value in response_data["values"]:
        id_value = value["id"].replace("AZURE_CREDENTIALS-", "")
        ids.append(id_value)
        names.append(value["name"])

if __name__ == "__main__":
    print("Iniciando o processo...")
    main()
    print("Processo concluído.")
