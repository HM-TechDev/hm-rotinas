import pandas as pd


def obter_token_bling():
    """
    Obtém o token de acesso do Bling a partir do Google Sheet
    """

    # URL para obter o token de acesso
    token_bling_url = 'https://docs.google.com/spreadsheets/d/1ts-h9O8MKb1r16GNSl6ebNQnSknRq_EHrwtttjPpICU/export?format=csv&gid=0'

    try:
        data = pd.read_csv(token_bling_url)
        token_acesso = data.iloc[0, 1]
        return token_acesso
    except Exception as e:
        print("Erro ao acessar o Token na planilha do Google", str(e))
        token_acesso = None

    # Verifica se o token é válido
    if not token_acesso:
        raise Exception("Token de acesso não obtido. Abortando operação.")
    
# Obtém os tokens e define os headers do Bling/Pipefy
bling_token = obter_token_bling()
bling_headers = {"Authorization": f"Bearer {bling_token}", "Content-Type": "application/json"}

pipefy_url = 'https://api.pipefy.com/graphql'
pipefy_token = 'eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJQaXBlZnkiLCJpYXQiOjE3MzkyOTYyOTYsImp0aSI6IjFmMzMyZmIwLTVhYmQtNDBkZi1iODA1LTcxMWQyMmI4ZjZmNiIsInN1YiI6MzAxMzgwNDQ2LCJ1c2VyIjp7ImlkIjozMDEzODA0NDYsImVtYWlsIjoibWlndWVsLnJvZG9scGhvQGdtYWlsLmNvbSJ9fQ.Exo9n9XMDKIAi9pgd1ySQC72rVYO6rLrxFPruVsxvBBl93Bk0qsEDM5A-yhQ7ojaqjDU8yhNoUpjTCSw_qFg6w'

pipefy_headers = {
    "Authorization": f"Bearer {pipefy_token}",
    "Content-Type": "application/json"
}