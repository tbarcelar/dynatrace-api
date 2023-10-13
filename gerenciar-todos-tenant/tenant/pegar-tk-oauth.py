import requests
url = "https://sso.dynatrace.com/sso/oauth2/token"
payload = {
    "grant_type": "client_credentials",
    "client_id": "dtxxxxxxxxxxx",
    "client_secret": "xxxxxxxx", # token gerado na conta principal
    "scope": "account-env-read",
    "resource": "urn:dxxxxxxx"
}
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "AWSALB=BErwkNSKIUrJjaUrZqGX6/9v43NfUtADIcoQhs2x6/tKJFc0GQsjtB7hwalv2x+qbm+YTsP3kZHDhxC/j+8djrQNU0dS1x9B0twbLwiLkQxArdPAAU/FGahXFKPr; AWSALBCORS=BErwkNSKIUrJjaUrZqGX6/9v43NfUtADIcoQhs2x6/tKJFc0GQsjtB7hwalv2x+qbm+YTsP3kZHDhxC/j+8djrQNU0dS1x9B0twbLwiLkQxArdPAAU/FGahXFKPr"
}
response = requests.post(url, headers=headers, data=payload)
if response.status_code == 200:
    data = response.json()
    access_token = data.get("access_token")
    print("Access Token:", access_token)
else:
    print("Error:", response.text)