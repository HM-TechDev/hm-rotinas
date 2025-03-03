from funcoes_aux import *
from requisicoes import *

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

    # Função avalia o tratamento de cada tipo de pedido ao mover os cards. 
    processar_cards(pedidos_em_andamento, df_cards, id_fase_pagamento, "ANDAMENTO")
    processar_cards(pedidos_atendidos, df_cards, id_fase_finalizado, "ATENDIDOS")

    return "Cards atualizados com sucesso!"

print(sincronizar_compras())