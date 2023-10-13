import requests
import pandas as pd
import openpyxl
import json

# coloque o token gerado pelo oauth
headers = {
    'Authorization': 'Bearer xxxxxxxxxxxxxxxxxxxx',
}

response = requests.get(
    'https://api.dynatrace.com/iam/v1/accounts/UUID da conta principal /users',

    headers=headers,
).text

#converter em dataframe para salvar como excel a lista
obj = json.loads(response)
df = pd.json_normalize(obj['items'])

# salvar como excel, se api estiver fora da pasta colocar o caminho de onde salvar
df.to_excel('C:/Users/user.xlsx')




