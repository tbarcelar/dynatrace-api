import requests
import json
import pandas as pd

# Carregar o arquivo JSON com as configurações
config_file_path = "C:/Users/config.json"
with open(config_file_path, "r") as config_file:
    config_data = json.load(config_file)["requests_data"]

# Listas para armazenar os resultados
dashboard_results = []

# Loop através das configurações no arquivo JSON
for request_data in config_data:
    dynatrace_url = request_data["url"]
    token = request_data["token"] #scope WriteConfig
    
    # Montar a URL completa para a API
    api_url = f"{dynatrace_url}/api/config/v1/dashboards"

    # Definir o header com o token
    headers = {
        "Authorization": f"Api-Token {token}"
    }

    # Fazer a requisição GET
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        dashboard_data = response.json()["dashboards"]
        
        for dashboard in dashboard_data:
            dashboard_id = dashboard["id"]
            dashboard_name = dashboard["name"]
            dashboard_results.append({
                "Environment": request_data["name"],
                "id": dashboard_id,
                "Dashboard Name": dashboard_name
            })
    else:
        print(f"Erro ao listar dashboards em {request_data['name']}: {response.status_code} - {response.text}")

# Criar um DataFrame do pandas
df = pd.DataFrame(dashboard_results)

# Salvar o DataFrame no Excel
excel_file_path = "C:/Users/dashboard.xlsx"
df.to_excel(excel_file_path, index=False)

print("Dados salvos no arquivo Excel.")
