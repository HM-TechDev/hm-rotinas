from requisicoes import *
from funcoes_aux import *
import logging


# Configura o logger
logging.basicConfig(
    filename='logs.txt',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s- %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def sincronizar_compras():
    """
    Atualiza os cards do Pipefy de acordo com os status das compras no Bling, movendo-os para as fases apropriadas
    """
 
    pipe_id = "306043381"

    # Lista contendo os múmeros dos pedidos de compra "Em Andamento" e "Atendidos"
    pedidos_em_andamento = obter_pedidos_por_status('Em Andamento')
    pedidos_atendidos = obter_pedidos_por_status('Atendido')
    
    # Informações (id, nº do pedido e fase atual) sobre os cards que se encontram no pipe 
    df_cards = obter_cards_fase(pipe_id)

    # Obtém a ID das fases 'Pagamento' e 'Finalizado'
    id_fase_pagamento = obter_id_fase(pipe_id, 'Pagamento')
    id_fase_finalizado = obter_id_fase(pipe_id, 'Finalizado')

    # Função avalia o tratamento de cada tipo de pedido ao mover os cards. 
    processar_cards(pedidos_em_andamento, df_cards, id_fase_pagamento, "ANDAMENTO")
    processar_cards(pedidos_atendidos, df_cards, id_fase_finalizado, "ATENDIDOS")

    mensagem = "Cards atualizados com sucesso!"
    return mensagem

print(sincronizar_compras())
input("Press any key to exit...")