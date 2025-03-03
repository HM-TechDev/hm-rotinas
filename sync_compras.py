import requests
from funcoes_aux import *
from requisicoes import mover_card

def sincronizar_compras_andamento(pedidos_em_andamento, df_cards, id_fase_pagamento):

    # Percorre a lista contendo o número de todos os pedidos de compra para compará-los com o status no Pipefy
    ausentes_pipefy = []

    for n_pedido in pedidos_em_andamento:
        if n_pedido in df_cards['pedido'].values:
            
            row = df_cards.loc[df_cards['pedido'] == n_pedido]
            print(f"Pedido: {row['pedido'].values[0]} ({row['fase_atual'].values[0]})")

            if row['fase_atual'].values[0] == 'Caseado/Botão' or row['fase_atual'].values[0] == 'Embalagem' :
                print(f"Mover: {row['pedido'].values[0]} ({row['fase_atual'].values[0]})")
                resultado = mover_card(row, id_fase_pagamento)
        
        else:
            ausentes_pipefy.append(n_pedido)
    
    print(f"Pedidos não encontrados no Pipefy {ausentes_pipefy}")


def sincronizar_compras_atendidas(pedidos_atendidos, df_cards, id_fase_finalizado):

    # Percorre a lista contendo o número de todos os pedidos de compra para compará-los com o status no Pipefy
    ausentes_pipefy = []

    # Envia todos os pedidos "Atendidos" no Bling para o status "Finalizado" no Pipefy
    for n_pedido in pedidos_atendidos:
        if n_pedido in df_cards['pedido'].values:
            
            row = df_cards.loc[df_cards['pedido'] == n_pedido]
            print(f"Pedido: {row['pedido'].values[0]} ({row['fase_atual'].values[0]})")

            if row['fase_atual'].values[0] == 'Caseado/Botão' or row['fase_atual'].values[0] == 'Embalagem' or row['fase_atual'].values[0] == 'Pagamento':
                print(f"Mover: {row['pedido'].values[0]} ({row['fase_atual'].values[0]})")
                resultado = mover_card(row, id_fase_finalizado)

        else:
            ausentes_pipefy.append(n_pedido)
    
    print(f"Pedidos não encontrados no Pipefy {ausentes_pipefy}")


def sincronizar_compras():

    # Lista contendo os múmeros dos pedidos de compra "Em Andamento" e "Atendidos"
    pedidos_em_andamento = obter_pedidos_por_status('Em Andamento')
    pedidos_atendidos = obter_pedidos_por_status('Atendido')

    # Informações (id, nº do pedido e fase atual) sobre os cards que se encontram no pipe 
    df_cards = obter_cards_pipefy()

    # TESTE - SUBSTITUIR PELO PIPE DESEJADO POSTERIORMENTE 
    pipe_id = "305715568"

    # Obtém a ID das fases 'Pagamento' e 'Finalizado'
    id_fase_pagamento = obter_id_fase(pipe_id, 'Pagamento')
    id_fase_finalizado = obter_id_fase(pipe_id, 'Finalizado')

    sincronizar_compras_andamento(pedidos_em_andamento, df_cards, id_fase_pagamento)
    sincronizar_compras_atendidas(pedidos_atendidos, df_cards, id_fase_finalizado)

sincronizar_compras()