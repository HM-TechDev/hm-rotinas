import requests
from requisicoes import *

# Obtém os campos dos cards no pipe
# Campo desejado: {'id': 'nome_do_solicitante', 'label': 'Pedido'}
card = obter_campos_pipefy()

def sincronizar_compras_andamento():

    # Lista contendo os múmeros dos pedidos de compra "Em Andamento"
    pedidos_em_andamento = obter_pedidos_por_status('Em Andamento')

    # Informações (id, nº do pedido e fase atual) sobre os cards que se encontram no pipe 
    df_cards = obter_cards_pipefy()

    # Obtém a ID da fase 'Pagamento'
    fases_pipefy = obter_fases_pipefy()
    id_fase_pagamento = None

    for chave, valor in fases_pipefy.items():
        if valor == 'Pagamento':
            id_fase_pagamento = chave
            break

    # Percorre a lista contendo o número de todos os pedidos de compra para compará-los com o status no Pipefy
    ausentes_pipefy = []

    for n_pedido in pedidos_em_andamento:
        if n_pedido in df_cards['pedido'].values:
            row = df_cards.loc[df_cards['pedido'] == n_pedido]
            print(f"Pedido: {row['pedido'].values[0]} ({row['fase_atual'].values[0]})")

            if row['fase_atual'].values[0] == 'Caseado/Botão' or row['fase_atual'].values[0] == 'Embalagem' :
                print(f"Mover: {row['pedido'].values[0]} ({row['fase_atual'].values[0]})")

                # Query usa o ID do card para movê-lo para a fase de 'Pagamento'
                payload = {
                    "query": f"""
                        mutation {{
                            moveCardToPhase (input: {{
                                card_id: "{row['id'].values[0]}",
                                destination_phase_id: "{id_fase_pagamento}"
                            }}) {{
                                card {{
                                    id
                                    current_phase {{
                                        name
                                    }}
                                }}
                            }}
                        }}
                        """
                }   

                # Requisição POST para mover os cards para 'Pagamento'
                resposta = requests.request("POST", pipefy_url, json=payload, headers=pipefy_headers)
                print(f"{resposta.status_code} : {resposta.text}")
        else:
            ausentes_pipefy.append(n_pedido)
    
    print(f"Pedidos não encontrados no Pipefy {ausentes_pipefy}")


def sincronizar_compras_atendidas():

    # Lista contendo os múmeros dos pedidos de compra "Atendidos"
    pedidos_atendidos = obter_pedidos_por_status('Atendido')

    # Obtém as informações (id, nº do pedido e fase atual) sobre os cards que se encontram no pipe 
    df_cards = obter_cards_pipefy()

    # Obtém a ID da fase 'Finalziado'
    fases_pipefy = obter_fases_pipefy()
    id_fase_alvo = None

    for chave, valor in fases_pipefy.items():
        if valor == 'Finalizado':
            id_fase_alvo = chave
            break

    # Percorre a lista contendo o número de todos os pedidos de compra para compará-los com o status no Pipefy
    ausentes_pipefy = []

    # Envia todos os pedidos "Atendidos" no Bling para o status "Finalizado" no Pipefy
    for n_pedido in pedidos_atendidos:
        if n_pedido in df_cards['pedido'].values:
            row = df_cards.loc[df_cards['pedido'] == n_pedido]
            print(f"Pedido: {row['pedido'].values[0]} ({row['fase_atual'].values[0]})")

            if row['fase_atual'].values[0] == 'Caseado/Botão' or row['fase_atual'].values[0] == 'Embalagem' or row['fase_atual'].values[0] == 'Pagamento':
                print(f"Mover: {row['pedido'].values[0]} ({row['fase_atual'].values[0]})")

                # Query usa o ID do card para movê-lo para a fase de 'Finalizado'
                payload = {
                    "query": f"""
                        mutation {{
                            moveCardToPhase (input: {{
                                card_id: "{row['id'].values[0]}",
                                destination_phase_id: "{id_fase_alvo}"
                            }}) {{
                                card {{
                                    id
                                    current_phase {{
                                        name
                                    }}
                                }}
                            }}
                        }}
                        """
                }   

                # Requisição POST para mover os cards para 'Pagamento'
                resposta = requests.request("POST", pipefy_url, json=payload, headers=pipefy_headers)
                print(f"{resposta.status_code} : {resposta.text}")
        else:
            ausentes_pipefy.append(n_pedido)
    
    print(f"Pedidos não encontrados no Pipefy {ausentes_pipefy}")