import os
import re
import secrets
import sqlite3
import time
from datetime import date as data_calendario, timedelta
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

from database import conectar, criar_tabelas

app = Flask(__name__)
CORS(app, supports_credentials=True)  # sessão via cookie + acesso do Android


def carregar_chave_secreta():
    """Chave que assina o cookie de sessão. Prefira definir PLENNIE_SECRET_KEY."""
    chave = os.environ.get("PLENNIE_SECRET_KEY")
    if chave:
        return chave
    arquivo = Path(app.root_path) / ".secret_key"
    if arquivo.exists():
        return arquivo.read_text().strip()
    chave = secrets.token_hex(32)
    arquivo.write_text(chave)
    try:
        arquivo.chmod(0o600)
    except OSError:
        pass
    return chave


app.config.update(
    SECRET_KEY=carregar_chave_secreta(),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Em produção (HTTPS) rode com PLENNIE_HTTPS=1.
    SESSION_COOKIE_SECURE=os.environ.get("PLENNIE_HTTPS") == "1",
    PERMANENT_SESSION_LIFETIME=timedelta(days=14),
)

# Prepara as tabelas ao iniciar a aplicação.
criar_tabelas()

CAMPOS = "id, descricao, valor, data, categoria"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
FALHAS = {}            # tentativas de login erradas: chave -> [timestamps]
JANELA, MAX_FALHAS = 300, 5
HASH_FALSO = generate_password_hash("senha-falsa")


@app.after_request
def sem_cache_na_api(resposta):
    if request.path.startswith("/api/"):
        resposta.headers["Cache-Control"] = "no-store"
    return resposta


@app.errorhandler(Exception)
def tratar_erro(e):
    if isinstance(e, HTTPException):
        return e
    app.logger.exception("Erro não tratado")
    return jsonify({"erro": "Erro interno no servidor."}), 500


@app.route("/")
def inicio():
    return send_from_directory(app.root_path, "index.html")


# ---------------------------------------------------------------- autenticação
def gerar_codigo():
    alfabeto = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "PLN" + "".join(secrets.choice(alfabeto) for _ in range(6))


def validar_credenciais(dados):
    if not isinstance(dados, dict):
        return None, None, "Envie os dados em formato JSON."
    email = dados.get("email")
    senha = dados.get("senha")
    if not isinstance(email, str) or not EMAIL_RE.match(email.strip()) or len(email) > 254:
        return None, None, "Informe um e-mail válido."
    if not isinstance(senha, str) or len(senha) < 8:
        return None, None, "A senha precisa ter pelo menos 8 caracteres."
    if len(senha) > 128:
        return None, None, "A senha pode ter no máximo 128 caracteres."
    return email.strip().lower(), senha, None


def muitas_falhas(chave):
    agora = time.time()
    FALHAS[chave] = [t for t in FALHAS.get(chave, []) if agora - t < JANELA]
    return len(FALHAS[chave]) >= MAX_FALHAS


def usuario_logado():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return None
    with conectar() as conexao:
        return conexao.execute(
            "SELECT id, email, codigo FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()


def login_obrigatorio(funcao):
    @wraps(funcao)
    def embrulho(*args, **kwargs):
        usuario = usuario_logado()
        if usuario is None:
            session.clear()
            return jsonify({"erro": "Faça login para continuar."}), 401
        return funcao(usuario["id"], *args, **kwargs)
    return embrulho


@app.route("/api/registrar", methods=["POST"])
def registrar():
    email, senha, erro = validar_credenciais(request.get_json(silent=True))
    if erro:
        return jsonify({"erro": erro}), 400

    senha_hash = generate_password_hash(senha)
    with conectar() as conexao:
        novo_id = codigo = None
        for _ in range(5):
            codigo = gerar_codigo()
            try:
                cursor = conexao.execute(
                    "INSERT INTO usuarios (email, senha_hash, codigo) VALUES (?, ?, ?)",
                    (email, senha_hash, codigo),
                )
                novo_id = cursor.lastrowid
                break
            except sqlite3.IntegrityError as e:
                if "email" in str(e).lower():
                    return jsonify({"erro": "Este e-mail já está cadastrado."}), 409
                # colisão de código: tenta outro
        if novo_id is None:
            return jsonify({"erro": "Não foi possível criar a conta."}), 500

        # O primeiro usuário herda as despesas antigas, de antes do login existir.
        total = conexao.execute("SELECT COUNT(*) AS n FROM usuarios").fetchone()["n"]
        if total == 1:
            conexao.execute(
                "UPDATE despesas SET usuario_id = ? WHERE usuario_id IS NULL", (novo_id,)
            )

    session.clear()
    session["usuario_id"] = novo_id
    session.permanent = True
    return jsonify({"id": novo_id, "email": email, "codigo": codigo}), 201


@app.route("/api/login", methods=["POST"])
def login():
    email, senha, erro = validar_credenciais(request.get_json(silent=True))
    if erro:
        return jsonify({"erro": erro}), 400

    chave = f"{email}|{request.remote_addr}"
    if muitas_falhas(chave):
        return jsonify({"erro": "Muitas tentativas. Aguarde alguns minutos."}), 429

    with conectar() as conexao:
        usuario = conexao.execute(
            "SELECT id, email, codigo, senha_hash FROM usuarios WHERE email = ?", (email,)
        ).fetchone()

    senha_ok = check_password_hash(usuario["senha_hash"] if usuario else HASH_FALSO, senha)
    if usuario is None or not senha_ok:
        FALHAS.setdefault(chave, []).append(time.time())
        return jsonify({"erro": "E-mail ou senha incorretos."}), 401

    FALHAS.pop(chave, None)
    session.clear()
    session["usuario_id"] = usuario["id"]
    session.permanent = True
    return jsonify({"id": usuario["id"], "email": usuario["email"], "codigo": usuario["codigo"]})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensagem": "Sessão encerrada."})


@app.route("/api/eu", methods=["GET"])
def quem_sou_eu():
    usuario = usuario_logado()
    if usuario is None:
        session.clear()
        return jsonify({"erro": "Faça login para continuar."}), 401
    return jsonify(dict(usuario))


# -------------------------------------------------------------------- despesas
def validar_despesa(dados):
    """Retorna (despesa_limpa, None) ou (None, mensagem_de_erro)."""
    if not isinstance(dados, dict):
        return None, "Envie os dados em formato JSON."

    descricao = dados.get("descricao")
    valor = dados.get("valor")
    data = dados.get("data")
    categoria = dados.get("categoria")

    if not all([descricao, data, categoria]) or valor is None:
        return None, "Preencha todos os campos."
    if not isinstance(descricao, str) or not descricao.strip():
        return None, "A descrição é obrigatória."
    if len(descricao.strip()) > 200:
        return None, "A descrição pode ter no máximo 200 caracteres."
    if not isinstance(categoria, str) or not categoria.strip():
        return None, "A categoria é obrigatória."
    try:
        valor = float(valor)
    except (ValueError, TypeError):
        return None, "O valor precisa ser numérico."
    if not 0 < valor < float("inf"):
        return None, "O valor precisa ser positivo e válido."
    try:
        data_calendario.fromisoformat(data)
    except (ValueError, TypeError):
        return None, "Use uma data válida no formato AAAA-MM-DD."

    return {
        "descricao": descricao.strip(),
        "valor": valor,
        "data": data,
        "categoria": categoria.strip(),
    }, None


@app.route("/api/despesas", methods=["GET"])
@login_obrigatorio
def listar_despesas(usuario_id):
    with conectar() as conexao:
        despesas = conexao.execute(
            f"SELECT {CAMPOS} FROM despesas WHERE usuario_id = ? ORDER BY id DESC",
            (usuario_id,),
        ).fetchall()
    return jsonify([dict(d) for d in despesas])


@app.route("/api/despesas/<int:despesa_id>", methods=["GET"])
@login_obrigatorio
def buscar_despesa(usuario_id, despesa_id):
    with conectar() as conexao:
        despesa = conexao.execute(
            f"SELECT {CAMPOS} FROM despesas WHERE id = ? AND usuario_id = ?",
            (despesa_id, usuario_id),
        ).fetchone()
    if despesa is None:
        return jsonify({"erro": "Despesa não encontrada."}), 404
    return jsonify(dict(despesa))


@app.route("/api/despesas", methods=["POST"])
@login_obrigatorio
def cadastrar_despesa(usuario_id):
    despesa, erro = validar_despesa(request.get_json(silent=True))
    if erro:
        return jsonify({"erro": erro}), 400

    with conectar() as conexao:
        cursor = conexao.execute(
            "INSERT INTO despesas (descricao, valor, data, categoria, usuario_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (despesa["descricao"], despesa["valor"], despesa["data"],
             despesa["categoria"], usuario_id),
        )
        novo_id = cursor.lastrowid

    return jsonify({"mensagem": "Despesa cadastrada com sucesso!", "id": novo_id}), 201


@app.route("/api/despesas/<int:despesa_id>", methods=["PUT"])
@login_obrigatorio
def atualizar_despesa(usuario_id, despesa_id):
    despesa, erro = validar_despesa(request.get_json(silent=True))
    if erro:
        return jsonify({"erro": erro}), 400

    with conectar() as conexao:
        cursor = conexao.execute(
            "UPDATE despesas SET descricao = ?, valor = ?, data = ?, categoria = ? "
            "WHERE id = ? AND usuario_id = ?",
            (despesa["descricao"], despesa["valor"], despesa["data"],
             despesa["categoria"], despesa_id, usuario_id),
        )
    if cursor.rowcount == 0:
        return jsonify({"erro": "Despesa não encontrada."}), 404
    return jsonify({"mensagem": "Despesa atualizada com sucesso!"})


@app.route("/api/despesas/<int:despesa_id>", methods=["DELETE"])
@login_obrigatorio
def remover_despesa(usuario_id, despesa_id):
    with conectar() as conexao:
        cursor = conexao.execute(
            "DELETE FROM despesas WHERE id = ? AND usuario_id = ?",
            (despesa_id, usuario_id),
        )
    if cursor.rowcount == 0:
        return jsonify({"erro": "Despesa não encontrada."}), 404
    return jsonify({"mensagem": "Despesa removida com sucesso!"})


@app.route("/api/despesas", methods=["DELETE"])
@login_obrigatorio
def remover_todas_despesas(usuario_id):
    with conectar() as conexao:
        conexao.execute("DELETE FROM despesas WHERE usuario_id = ?", (usuario_id,))
    return jsonify({"mensagem": "Despesas removidas."})


if __name__ == "__main__":
    # O modo debug só liga se você pedir: FLASK_DEBUG=1 python app.py
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
