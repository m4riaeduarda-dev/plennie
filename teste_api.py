
import json
from urllib.request import Request, urlopen

dados = {
    "descricao": "Teste de cadastro",
    "valor": 25.50,
    "data": "2026-10-21",
    "categoria": "Alimentação"
}

requisicao = Request(
    "http://127.0.0.1:5000/api/despesas",
    data=json.dumps(dados).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urlopen(requisicao) as resposta:
    print("Status:", resposta.status)
    print("Resposta:", resposta.read().decode("utf-8"))
