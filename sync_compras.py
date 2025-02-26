import requests
from requisicoes import *


# Obtém todas as compras 'Em Aberto' no Bling
# compras: lista com dicionários contendo os dados de cada compra (nº pedido, id do pedido e id do fornecedor)
compras = obter_compras_bling()

# Guarda o nº de todos os pedidos de compra 'Em Aberto' numa lista
n_pedidos_compras = []

for pedido in compras:
    n_pedido = pedido['numero_pedido']
    n_pedidos_compras.append(n_pedido)


# Obtém os campos dos cards no pipe
# Campo desejado: {'id': 'nome_do_solicitante', 'label': 'Pedido'}
card = obter_campos_pipefy()

def sincronizar_compras():

    pipe_id = "305715568"

    # Extrai as informações guardadas no cards do pipe 
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
        print(dados_resposta)

        # Guarda os pares "Nº Pedido : Fase" de cada card
        dados_cards = {}
        
        # Percorre os cards extraindo o nº do pedido e a fase em que cada card se encontra
        for edge in dados_resposta['data']['cards']['edges']:
            node = edge['node']
            
            for campo in node['fields']:
                if campo['name'] == 'Pedido':
                    pedido = campo['value']
            
            fase_atual = node['current_phase']['name']
            
            dados_cards[pedido] = fase_atual

    else:
        print(f"Erro na requisição: {response.status_code}, {response.text}")
