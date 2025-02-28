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

    # Obtém as informações (id, nº do pedido e fase atual) sobre os cards que se encontram no pipe 
    df_cards = obter_cards_pipefy()

    # Obtém a ID da fase 'Pagamento'
    fases_pipefy = obter_fases_pipefy()
    id_fase_pagamento = None

    for chave, valor in fases_pipefy.items():
        if valor == 'Pagamento':
            id_fase_pagamento = chave
            break

   # Percorre a lista contendo o número de todos os pedidos de compra para compará-los com o status no Pipefy
    for n_pedido in n_pedidos_bling:
        if n_pedido in df_cards['pedido'].values:
            row = df_cards.loc[df_cards['pedido'] == n_pedido]
            if row['fase_atual'].values[0] == 'Pagamento':
                print(f"Atualizado: {row['pedido'].values[0]} - {row['fase_atual'].values[0]}")
            else:
                print(f"Mover: {row['pedido'].values[0]} ({row['fase_atual'].values[0]}) - ID:{row['id'].values[0]}")
        else:
            print(f"Pedido nº{n_pedido} não encontrado no Pipefy")

print(sincronizar_compras())