import requests
import pandas as pd
from requisicoes import *


# Obtém todas as compras 'Em Aberto' no Bling
# compras: lista com dicionários contendo os dados de cada compra (nº pedido, id do pedido e id do fornecedor)
compras = obter_compras_bling()

# Obtém os campos dos cards no pipe
# Campo desejado: {'id': 'nome_do_solicitante', 'label': 'Pedido'}
card = obter_campos_pipefy()
print(card)

# Pipefy: percorrer o pipe buscando os cards referentes aos 'Pedidos em Aberto'
# Para isso, comparar o nº do pedidos de 'compras' com o valor do 'nome_do_solicitante' 
# Se True: verificar se está na fase correta
# Se False: transferir o card para a fase adequada
def sincronizar_compras():
    pass
