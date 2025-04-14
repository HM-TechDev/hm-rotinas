from datetime import datetime, timedelta
from tokens import *
import pandas as pd
import requests
import logging
import json
import time

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
        n_pedidos_bling.append(str(n_pedido))

    return n_pedidos_bling


def obter_cards_fase(pipe):
    """
    Obtém os cards de todas as fases do pipe exceto os que se encontram na fase "Pagamento"
    """

    endCursor = None
    pagina = True

    # Listas para armazenar as informações dos cards
    dados_json = []
    dados_cards = []

    try: 
        while pagina:

            query = """
                {
                    allCards(pipeId: %s, after: %s) {
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                        edges {
                            node {
                                id
                                current_phase {
                                    id
                                    name
                                }
                                fields {
                                    name
                                    value
                                }
                            }
                        }
                    }
                }
            """ % (pipe, 'null' if endCursor is None else '"' + endCursor + '"')

            response = requests.post(pipefy_url, json={'query': query}, headers=pipefy_headers)

            if response.status_code == 200:
                dados_resposta = response.json()
                dados_json.append(dados_resposta)
                
                if 'data' in dados_resposta and dados_resposta['data']['allCards'] is not None:

                    for edge in dados_resposta['data']['allCards']['edges']:
                        card = edge['node']
                        card_id = card['id']
                        card_fase = card['current_phase']['name']

                        for field in card['fields']:
                            if field['name'] == 'Pedido':
                                card_pedido = field['value']
                                break

                        if card['current_phase']['name'] != "Finalizado":
                            dados_cards.append({'id': card_id, 'pedido': card_pedido, 'fase_atual': card_fase})
                    
                    # Atualiza o cursor para a próxima página
                    endCursor = dados_resposta['data']['allCards']['pageInfo']['endCursor']
                    pagina = dados_resposta['data']['allCards']['pageInfo']['hasNextPage']

                    time.sleep(0.5)
                else:
                    print("Nenhum card encontrado ou dados mal formatados:", dados_resposta)
                    break 
            else:
                print(f"Erro na requisição: {response.status_code}, {response.text}")
                break
            
            with open('cards_fase.json', 'a') as arquivo:
                json.dump(dados_resposta, arquivo, indent=4)

        cards_filtrados = pd.DataFrame(dados_cards)
        cards_filtrados.to_excel('cards_fase.xlsx', index=False)
    
        return cards_filtrados

    except requests.exceptions.RequestException as e:
        mensagem_erro = f"Erro durante a requisição: {str(e)}"
        logging.error(mensagem_erro)
        print(mensagem_erro)

def obter_fases_pipefy(pipe):
    """
    Obtém o ID e nome de cada fase presente em um pipe, retornando estas informações num dicionário
    """

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
    ''' % pipe

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
