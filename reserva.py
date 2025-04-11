import requests
import pandas as pd
import re
import json
import time


"""
Contém as funções não utilizadas no momento
"""


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
    pagina = True

    # Variável para armazenar dicionários contendo a relação dos IDs/Fases
    data = []
    dados_json = []

    while pagina == True:
        
        # Define quais informações serão extraídas dos cards do pipe 
        query = """
            {
                allCards(pipeId: %s, first: 50, after: "%s") {
                pageInfo {
                    hasNextPage
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
            
            # Atualiza o endCursor para a próxima página
            endCursor = dados_resposta['data']['allCards']['pageInfo']['endCursor']

            # Interrompe o processo se não houver mais páginas com dados disponíveis
            pagina = dados_resposta['data']['allCards']['pageInfo']['hasNextPage']
            if pagina == False:
                break

            time.sleep(0.5)

        else:
            print(f"Erro na requisição: {response.status_code}, {response.text}")
        
        with open('cards.json', 'a') as arquivo:
            json.dump(dados_json, arquivo, indent=4)
    
    # Cria um dataframe com os dados dos cards
    df_cards = pd.DataFrame(data)
    df_cards.to_excel('cards.xlsx', index=False)

    return df_cards

print(obter_cards_pipefy())