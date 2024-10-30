import requests
import json
import pandas as pd

# Caminhos de arquivo
config_file_path = "D:/dyna/api/tenant/config.json"
excel_file_path = "D:/dyna/api/tenant/verificar-tenant/excel/dashboard.xlsx"

# Função principal para executar o processo
def main():
    try:
        # Carregar dados do arquivo JSON de configuração
        with open(config_file_path, "r") as config_file:
            config_data = json.load(config_file)["requests_data"]

        # Inicializar lista para armazenar os resultados
        dashboard_results = []

        # Loop através das configurações no arquivo JSON
        for request_data in config_data:
            dynatrace_url = request_data["url"]
            token = request_data["token"]
            # Montar a URL completa para a API
            api_url = f"{dynatrace_url}/api/config/v1/dashboards"
            # Definir o header com o token
            headers = {"Authorization": f"Api-Token {token}"}
            # Fazer a requisição GET
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                process_response(response.json(), dashboard_results, request_data["name"])
            else:
                print(f"Erro ao listar dashboards em {request_data['name']}: {response.status_code} - {response.text}")

        # Criar um DataFrame a partir dos dados coletados
        df = pd.DataFrame(dashboard_results)
        print(df)
        print("------------------  Dashboard finalizado --------------------------")
        # Salvar o DataFrame em um arquivo Excel
        df.to_excel(excel_file_path, index=False)
        print(f'Arquivo Excel salvo com sucesso em: {excel_file_path}')

    except Exception as e:
        print(f"Erro ao executar o processo: {e}")

# Função auxiliar para processar a resposta da API
def process_response(dashboard_data, dashboard_results, environment_name):
    for dashboard in dashboard_data["dashboards"]:
        dashboard_id = dashboard["id"]
        dashboard_name = dashboard["name"]
        dashboard_results.append({
            "Environment": environment_name,
            "id": dashboard_id,
            "Dashboard Name": dashboard_name
        })

if __name__ == "__main__":
    print("Iniciando o processo...")
    main()
    print("Processo concluído.")
