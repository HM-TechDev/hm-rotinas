from requisicoes import *
from funcoes_aux import *
import logging


# Configura o logger
logging.basicConfig(
    filename='logs.txt',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s- %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S'
)

def sincronizar_compras():
    """
    Atualiza os cards do Pipefy de acordo com os status das compras no Bling, movendo-os para as fases apropriadas
    """
 
    pipe_id = "301795013"

    # Lista contendo os múmeros dos pedidos de compra "Em Andamento" e "Atendidos"
    pedidos_em_andamento = obter_pedidos_por_status('Em Andamento')
    pedidos_atendidos = obter_pedidos_por_status('Atendido')
    logging.info(f"Pedidos em Andamento: {pedidos_em_andamento}")
    logging.info(f"Pedidos Atendidos: {pedidos_atendidos}")
    
    # Informações (id, nº do pedido e fase atual) sobre os cards que se encontram no pipe 
    df_cards = obter_cards_fase(pipe_id)
    cards_pipe = df_cards['pedido'].tolist()
    logging.info(f"Cards no Pipe: {cards_pipe}\n")

    # Obtém a ID das fases 'Pagamento' e 'Finalizado'
    id_fase_pagamento = obter_id_fase(pipe_id, 'Pagamento')
    id_fase_finalizado = obter_id_fase(pipe_id, 'Finalizado')

    # Função avalia o tratamento de cada tipo de pedido ao mover os cards. 
    processar_cards(pedidos_em_andamento, df_cards, id_fase_pagamento, "ANDAMENTO")
    processar_cards(pedidos_atendidos, df_cards, id_fase_finalizado, "ATENDIDOS")

    print("Cards atualizados com sucesso!")

sincronizar_compras()
input("")