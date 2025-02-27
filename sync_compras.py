import requests
from requisicoes import *


# Obtém todas as compras 'Em Aberto' no Bling
# compras: lista com dicionários contendo os dados de cada compra (nº pedido, id do pedido e id do fornecedor)
compras = obter_compras_bling()

# Guarda o nº de todos os pedidos de compra 'Em Aberto' numa lista
n_pedidos_bling = []

for pedido in compras:
    n_pedido = pedido['numero_pedido']
    n_pedidos_bling.append(n_pedido)

# Obtém os campos dos cards no pipe
# Campo desejado: {'id': 'nome_do_solicitante', 'label': 'Pedido'}
card = obter_campos_pipefy()

def sincronizar_compras():

    cards_pipefy = obter_cards_pipefy()

    # Obtém a ID da fase 'Pagamento'
    fases_pipefy = obter_fases_pipefy()
    id_fase_pagamento = None

    for chave, valor in fases_pipefy.items():
        if valor == 'Pagamento':
            id_fase_pagamento = chave
            break
    
    pedido_fase = {}
    for cards in cards_pipefy.values():
        pedido_fase.update(cards)

   # Percorre a lista contendo o número de todos os pedidos de compra para compará-los com o status no Pipefy
    for n_pedido in n_pedidos_bling:
        if n_pedido in pedido_fase and pedido_fase[n_pedido] == 'Pagamento':
            print(f"Pedido nº {n_pedido} está atualizado!")
        elif n_pedido in pedido_fase and pedido_fase[n_pedido] != 'Pagamento':
            print(f"Pedido nº {n_pedido} foi enviado para a fase de 'Pagamento'.")
        else:
            print(f"Pedido nº {n_pedido} não encontrado no Pipefy")





print(sincronizar_compras())
