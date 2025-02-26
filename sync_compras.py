import requests
from requisicoes import *


# Obtém todas as compras 'Em Aberto' no Bling
# compras: lista com dicionários contendo os dados de cada compra (nº pedido, id do pedido e id do fornecedor)
compras = obter_compras_bling()

# Obtém os campos dos cards no pipe
# Campo desejado: {'id': 'nome_do_solicitante', 'label': 'Pedido'}
card = obter_campos_pipefy()

# Pipefy: percorrer o pipe buscando os cards referentes aos 'Pedidos em Aberto'
# Para isso, comparar o nº do pedidos de 'compras' com o valor do 'nome_do_solicitante' 
# Se True: verificar se está na fase correta
# Se False: transferir o card para a fase adequada
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
    else:
        print(f"Erro na requisição: {response.status_code}, {response.text}")
