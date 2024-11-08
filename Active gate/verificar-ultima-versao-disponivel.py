from playwright.sync_api import sync_playwright

def get_latest_version():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://docs.dynatrace.com/docs/whats-new/release-notes/activegate')

        # Esperar até que o conteúdo relevante esteja carregado
        page.wait_for_selector('xpath=//*[@id="img-provider"]/div[1]/div/div/div/div[2]/div/div[1]/div[1]/div/div/a')

        # Encontrar o seletor XPath e obter a versão
        latest_version_element = page.query_selector('xpath=//*[@id="img-provider"]/div[1]/div/div/div/div[2]/div/div[1]/div[1]/div/div/a')
        latest_version = latest_version_element.text_content().strip() if latest_version_element else 'Versão não encontrada'
        
        browser.close()
        return latest_version

print(get_latest_version())
