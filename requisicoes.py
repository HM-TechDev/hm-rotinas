from datetime import datetime, timedelta
import requests
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

def obter_compras_bling():
    """
    Obtém os dados dos pedidos de compras nos últimos 30 dias de acordo com o status
    
    Bling - Status
    0: "Em Aberto"
    1: "Atendido"
    2: "Cancelado"
    3: "Em Andamento"

    """

    data_final = datetime.today().date()
    data_inicial = data_final - timedelta(days=30)

    compras = []
    url_compras = f"https://bling.com.br/Api/v3/pedidos/compras?pagina=1&valorSituacao=3&dataInicial={data_inicial}&dataFinal={data_final}"
    resposta = requests.get(url_compras, headers=bling_headers, timeout=15)

    try:      
        # Verifica a resposta e converte o JSON para pyton
        if resposta.status_code == 200:
            dados_resposta = resposta.json()

            for item in dados_resposta["data"]:
            
                numero_pedido = item["numero"]
                id_compras = item["id"]
                id_fornecedor = item["fornecedor"]["id"]

                # Adicionando um dicionário com id_produto e quantidade à lista "Produtos"
                compras.append({"numero_pedido": numero_pedido,"id_compras": id_compras, "id_fornecedor": id_fornecedor})
            return compras

    except requests.exceptions.RequestException as e:
        print(f"Erro durante a requisição para o pedido {numero_pedido}: {str(e)}")



def obter_campos_pipefy():
    """
    Obtém informações referentes aos campos usados nos cards de um determinado pipe
    """

    pipe_id = "305715568"

    # Define quais campos serão extraídos dos cards
    query = '''
    {
    pipe(id: %s){
        start_form_fields{
            id
            label
            type
            options
            description
            is_multiple
        }
        phases{
            id
            name
        fields{
            id
            label
        }
        }
    }
    }
    ''' % pipe_id

    # Requisição POST para obter os dos campos incluídos nos cards
    response = requests.post(pipefy_url, json={"query": query}, headers=pipefy_headers)
    
    if response.status_code == 200:
        return(response.json())
    else:
        print("Erro ao buscar campos do Pipe:", response.status_code, response.json())

def obter_cards_pipefy():
    """
    Obtém os dados guardados em cada card de determinado pipe e retorna estas informações num dataframe
    """

    pipe_id = "305715568"

    # Define quais informações serão extraídas dos cards do pipe 
    query = """
        {
            cards(pipe_id: %s) {
                edges {
                    node {
                        id
                        current_phase {
                            name
                        }
                        done
                        fields {
                            name
                            value
                        }
                    }
                }
            }
        }
    """ % pipe_id

    # Requisição POST para obter os dados dos cards
    response = requests.post(pipefy_url, json={'query': query}, headers=pipefy_headers)

    if response.status_code == 200:
        dados_resposta = response.json()

        data = []

        # Percorre os cards guardando as informações mais relevantes de cada um num dicionário
        for edge in dados_resposta['data']['cards']['edges']:
            node = edge['node']
            id = node['id']
            fase_atual = node['current_phase']['name']
            
            for field in node['fields']:
                if field['name'] == 'Pedido':
                    pedido = field['value']
                    break
            
            pedido = int(pedido)

            data.append({'id': id, 'pedido': pedido, 'fase_atual': fase_atual})
        
        df = pd.DataFrame(data)
    
    else:
        print(f"Erro na requisição: {response.status_code}, {response.text}")

    return df


def obter_fases_pipefy():
    """
    Obtém o ID e nome de cada fase presente em um pipe, retornando estas informações num dicionário
    """

    pipe_id = "305715568"

    # Extrai o nome e o ID de cada fase do pipe
    query = '''
        {
            pipe(id: %s) {
                id
                phases {
                id
                name
            }
        }
    }
    ''' % pipe_id

    # Requisição POST para obter os dados dos pipes
    response = requests.post(pipefy_url, json={"query": query}, headers=pipefy_headers)
    
    if response.status_code == 200:
        
        dados_resposta = response.json()

        # Dicionário guarda a relação dos IDs e nomes de cada fase
        fases_dict = {}

        for item in dados_resposta['data']['pipe']['phases']:
            fase = {item['id']: item['name']}
            fases_dict.update(fase)
        
        return fases_dict
        
    else:
        print("Erro ao buscar campos do Pipe:", response.status_code, response.json())
