from requisicoes import pipefy_url, pipefy_headers
import requests

def mover_card(row, id_fase):           
    """
    Mova um card para uma determinada fase do Pipefy
    """

    # Query usa o ID do card para movê-lo para a fase desejada
    payload = {
        "query": f"""
            mutation {{
                moveCardToPhase (input: {{
                    card_id: "{row['id'].values[0]}",
                    destination_phase_id: "{id_fase}"
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

    # Requisição POST para mover os cards no Pipefy
    resposta = requests.request("POST", pipefy_url, json=payload, headers=pipefy_headers)

    return print(f"{resposta.status_code} : {resposta.text}")


def processar_cards(pedidos, df_cards, id_fase, tipo):
    """
    Avalia a fase atual dos cards para então movê-los para a fase de destino.
    - Pedidos Em Andamento: podem ser transferidos das fases 'Caseado/Botão' e 'Embalagem' para a fase 'Pagamento'
    - Pedidos Atendidos: podem ser transferidos das fases 'Caseado/Botão' , 'Embalagem' e 'Pagamento' para a fase 'Finalizado'
    """

    # Guarda os pedidos de compra não encontrados no Pipefy
    ausentes_pipefy = []

    # Define as fases atuais válidas a partir das quais os cards podem ser movidos para a fase de destino
    if tipo == "ANDAMENTO":
        fases_atuais_validas = ['Caseado/Botão', 'Embalagem']
        id_fase_destino = id_fase
    elif tipo == "ATENDIDOS":
        fases_atuais_validas = ['Caseado/Botão', 'Embalagem', 'Pagamento']
        id_fase_destino = id_fase

    # Percorre a lista contendo todos os pedidos de compra para verificar se os mesmos se encontram no Pipefy
    for n_pedido in pedidos:
        
        if n_pedido in df_cards['pedido'].values:
            
            # Verifica se o card está em uma das fases válidas para o status para então movê-lo
            row = df_cards.loc[df_cards['pedido'] == n_pedido]
            if row['fase_atual'].values[0] in fases_atuais_validas:
                mover_card(row, id_fase_destino)
        else:
            ausentes_pipefy.append(n_pedido)
    
    # Terminal exibe a lista dos pedidos de compra nao encontrados
    print(f"Pedidos não encontrados no Pipefy (status = {tipo}): {ausentes_pipefy}")