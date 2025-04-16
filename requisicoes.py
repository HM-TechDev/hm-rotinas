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
        else:
            mensagem_erro = f"Erro na requisição para extrair os pedidos do Bling ({resposta.status_code})"
            logging.error(mensagem_erro)
            print(mensagem_erro)

    except requests.exceptions.RequestException as e:
        print(f"Erro ao extrair os pedidos do Bling: {str(e)}")
        return None


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

    if dados_compras: 
        # Guarda o nº de todos os pedidos de compra correspondente ao status especificado numa lista
        n_pedidos_bling = []

        for pedido in dados_compras:
            n_pedido = pedido['numero_pedido']
            n_pedidos_bling.append(str(n_pedido))

        return n_pedidos_bling
    
    else:
        mensagem_erro = "Erro ao extrair os pedidos por status ({status})"
        logging.error(mensagem_erro)
        print(mensagem_erro)
        raise Exception("Erro ao extrair os pedidos por status")


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

            resposta = requests.post(pipefy_url, json={'query': query}, headers=pipefy_headers)

            if resposta.status_code == 200:
                dados_resposta = resposta.json()
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
                    mensagem_erro1 = "Nenhum card encontrado, ou dados mal formatados {dados_resposta}"
                    logging.error(mensagem_erro1)
                    print(mensagem_erro1)
                    break 
            else:
                mensagem_erro2 = f"Erro na requisição para extrair os cards do Pipefy ({resposta.status_code}, {resposta.text})"
                logging.error(mensagem_erro2)
                print(mensagem_erro2)
                break
            
            #with open('cards_fase.json', 'a') as arquivo:
            #    json.dump(dados_resposta, arquivo, indent=4)

        cards_filtrados = pd.DataFrame(dados_cards)
    
        return cards_filtrados

    except requests.exceptions.RequestException as e:
        mensagem_erro3 = f"Erro ao extrair os cards do pipefy: {str(e)}"
        logging.error(mensagem_erro3)
        print(mensagem_erro3)

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
    resposta = requests.post(pipefy_url, json={"query": query}, headers=pipefy_headers)

    if resposta.status_code == 200:
        
        dados_resposta = resposta.json()

        # Dicionário guarda a relação dos IDs e nomes de cada fase
        fases_dict = {}

        for item in dados_resposta['data']['pipe']['phases']:
            fase = {item['id']: item['name']}
            fases_dict.update(fase)
        
        return fases_dict
        
    else:
        mensagem_erro = f"Erro ao buscar fases do Pipe: {resposta.status_code}, {resposta.json()}"
        logging.error(mensagem_erro)
        print(mensagem_erro)
        return None

def obter_id_fase(pipe, nome_fase):

    # Dicionário contendo a relação dos IDs e nomes de cada fase
    fases_dict = obter_fases_pipefy(pipe)

    if fases_dict:
        # Variável guarda o ID da fase desejada
        id_fase = None

        # Percorre fases_dict para encontrar a chave associada ao nome da fase desejada.
        for chave, valor in fases_dict.items():
            if valor == nome_fase:
                id_fase = chave
                break

        return id_fase

    else:
        raise ValueError(f"Erro: não foi possível obter o ID da fase {nome_fase}")