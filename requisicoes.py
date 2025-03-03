from funcoes_aux import pipefy_url, pipefy_headers
import requests


def mover_card(row, id_fase):           

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
    print(f"{resposta.status_code} : {resposta.text}")

    return print("Cards movidos com sucesso!")

