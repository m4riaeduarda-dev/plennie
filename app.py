
from flask import Flask, jsonify, request, send_from_directory
from database import conectar, criar_tabelas

app = Flask(__name__)

# Prepara a tabela ao iniciar a aplicação.
criar_tabelas()


@app.route("/")
def inicio():
    return send_from_directory(app.root_path, "index.html")


@app.route("/api/despesas", methods=["GET"])
def listar_despesas():
    with conectar() as conexao:
        despesas = conexao.execute(
            "SELECT id, descricao, valor, data, categoria "
            "FROM despesas ORDER BY id DESC"
        ).fetchall()

    return jsonify([dict(despesa) for despesa in despesas])


@app.route("/api/despesas", methods=["POST"])
def cadastrar_despesa():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie os dados em formato JSON."}), 400

    descricao = dados.get("descricao")
    valor = dados.get("valor")
    data = dados.get("data")
    categoria = dados.get("categoria")

    if not all([descricao, data, categoria]) or valor is None:
        return jsonify({"erro": "Preencha todos os campos."}), 400

    if not isinstance(descricao, str) or not descricao.strip():
        return jsonify({"erro": "A descrição é obrigatória."}), 400

    if not isinstance(categoria, str) or not categoria.strip():
        return jsonify({"erro": "A categoria é obrigatória."}), 400

    try:
        valor = float(valor)
    except (ValueError, TypeError):
        return jsonify({"erro": "O valor precisa ser numérico."}), 400

    if not 0 < valor < float("inf"):
        return jsonify({"erro": "O valor precisa ser positivo e válido."}), 400

    try:
        from datetime import date as data_calendario
        data_calendario.fromisoformat(data)
    except (ValueError, TypeError):
        return jsonify({"erro": "Use uma data válida no formato AAAA-MM-DD."}), 400

    with conectar() as conexao:
        cursor = conexao.execute(
            "INSERT INTO despesas (descricao, valor, data, categoria) "
            "VALUES (?, ?, ?, ?)",
            (descricao.strip(), valor, data, categoria.strip())
        )
        novo_id = cursor.lastrowid

    return jsonify({
        "mensagem": "Despesa cadastrada com sucesso!",
        "id": novo_id
    }), 201


if __name__ == "__main__":
    app.run(debug=True)
