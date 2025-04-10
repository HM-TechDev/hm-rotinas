from datetime import datetime, timedelta
import requests
import pandas as pd
import re
import json


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

def obter_compras_bling(status):
    """
    Obtém os dados dos pedidos de compras nos últimos 30 dias de acordo com o status
    """

    data_final = datetime.today().date()
    data_inicial = data_final - timedelta(days=30)

    compras = []
    url_compras = f"https://bling.com.br/Api/v3/pedidos/compras?pagina=1&valorSituacao={status}&dataInicial={data_inicial}&dataFinal={data_final}"
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


def obter_pedidos_por_status(status):
    """
    Retorna a lista dos pedidos do Bling associados a um determinado status
    """
    
    pedidos_compras_status = {"Em Aberto" : 0,
                             "Atendido" : 1,
                             "Cancelado" : 2,
                             "Em Andamento" : 3}
    
    cod_status = pedidos_compras_status.get(status)

    # Obtém todas as compras correspondente ao status especificado no Bling
    # compras: lista de dicionários contendo os dados de cada compra (nº pedido, id do pedido e id do fornecedor)
    dados_compras = obter_compras_bling(cod_status)

    # Guarda o nº de todos os pedidos de compra correspondente ao status especificado numa lista
    n_pedidos_bling = []

    for pedido in dados_compras:
        n_pedido = pedido['numero_pedido']
        n_pedidos_bling.append(n_pedido)

    return n_pedidos_bling


def obter_campos_pipefy():
    """
    Obtém informações referentes aos campos usados nos cards de um determinado pipe
    """

    pipe_id = "301795013"

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

def obter_cursor_pipefy():
    """
    Obtém o endCursor necessário pára realizar a paginação no Pipefy
    """

    pipe_id = "301795013"

    # Define quais informações serão extraídas dos cards do pipe 
    query = """
        {
        allCards(pipeId: %s) {
        pageInfo {
            endCursor
            hasNextPage
            hasPreviousPage
            startCursor
        }
            edges {
                node {
                    id
                    }
                }
            }
        }
    """ % (pipe_id)

    # Requisição POST para obter os dados dos cards
    response = requests.post(pipefy_url, json={'query': query}, headers=pipefy_headers)

    if response.status_code == 200:
        dados_resposta = response.json()
        #with open('cursor.json', 'w') as arquivo:
        #    json.dump(dados_resposta, arquivo, indent=4)
        
        return dados_resposta["data"]["allCards"]["pageInfo"]["endCursor"]


def obter_cards_pipefy():
    """
    Obtém os dados guardados em cada card de determinado pipe e retorna estas informações num dataframe
    """

    # Informações necessárias para executar a query para o Pipefy
    pipe_id = "301795013"
    endCursor = obter_cursor_pipefy()
    
    # Variável para armazenar dicionários contendo a relação dos IDs/Fases
    data = []
    dados_json = []

    while True:
        
        # Define quais informações serão extraídas dos cards do pipe 
        query = """
            {
                allCards(pipeId: %s, first: 50, after: "%s") {
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                    startCursor
                    endCursor
                }
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
                        cursor
                    }
                }
            }
        """ % (pipe_id, endCursor if endCursor else "")

        # Requisição POST para obter os dados dos cards
        response = requests.post(pipefy_url, json={'query': query}, headers=pipefy_headers)

        if response.status_code == 200:
            dados_resposta = response.json()
            dados_json.append(dados_resposta)

            # Percorre os cards guardando as informações mais relevantes de cada um num dicionário
            for edge in dados_resposta['data']['allCards']['edges']:
                node = edge['node']
                id = node['id']
                fase_atual = node['current_phase']['name']
                
                for field in node['fields']:
                    if field['name'] == 'Pedido':
                        pedido = field['value']
                        break

                # Remove caracteres não-numéricos do pedido e obtém os 4 primeiros dígitos
                if pedido.isdigit() == False:
                    pedido = re.sub(r'\D', '', pedido)[:4]
                pedido = int(pedido)

                # Insere o dicionário na lista
                data.append({'id': id, 'pedido': pedido, 'fase_atual': fase_atual})
            
            # Interrompe o processo se não houver mais páginas com dados disponíveis
            if not dados_resposta['data']['allCards']['pageInfo']['hasNextPage']:
                break

            # Atualiza o endCursor para a próxima página
            endCursor = dados_resposta['data']['allCards']['pageInfo']['endCursor']

        else:
            print(f"Erro na requisição: {response.status_code}, {response.text}")
        
        with open('cards.json', 'w') as arquivo:
            json.dump(dados_json, arquivo, indent=4)
    
    # Cria um dataframe com os dados dos cards
    df_cards = pd.DataFrame(data)
    df_cards.to_excel('cards.xlsx', index=False)

    return df_cards

print(obter_cards_pipefy())

def obter_fases_pipefy(pipe):
    """
    Obtém o ID e nome de cada fase presente em um pipe, retornando estas informações num dicionário
    """

    id_pipe = pipe

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
    ''' % id_pipe

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

def obter_id_fase(pipe, nome_fase):

    # Dicionário contendo a relação dos IDs e nomes de cada fase
    fases_dict = obter_fases_pipefy(pipe)

    # Variável guarda o ID da fase desejada
    id_fase = None

    # Percorre fases_dict para encontrar a chave associada ao nome da fase desejada.
    for chave, valor in fases_dict.items():
        if valor == nome_fase:
            id_fase = chave
            break

    return id_fase
