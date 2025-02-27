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

    cards_pipefy = obter_cards_pipefy()

    # Obtém a ID da fase 'Pagamento'
    fases_pipefy = obter_fases_pipefy()
    id_fase_pagamento = None

    for chave, valor in fases_pipefy.items():
        if valor == 'Pagamento':
            id_fase_pagamento = chave
            break

   # Percorre a lista contendo o número de todos os pedidos de compra para compará-los com o status no Pipefy
    for n_pedido in n_pedidos_compras:
        
        if n_pedido in cards_pipefy and cards_pipefy[n_pedido] == 'Pagamento':
            print("Tudo certo!")
        elif n_pedido in cards_pipefy and cards_pipefy[n_pedido] != 'Pagamento':
            print("Necessário atualizar o card!")
        else: 
            print(f"Erro: O pedido {n_pedido} não foi encontrado no Pipefy.")




print(sincronizar_compras())
