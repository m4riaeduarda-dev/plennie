import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

CAMINHO_BANCO = Path(__file__).resolve().parent / "plennie.db"


def caminho_banco():
    # PLENNIE_DB permite usar outro arquivo (ex.: banco temporário nos testes).
    return Path(os.environ.get("PLENNIE_DB", CAMINHO_BANCO))


@contextmanager
def conectar():
    """Conexão com commit no sucesso, rollback no erro e close sempre.

    Sem isso, o `with sqlite3.connect(...)` faz rollback e INSERT/DELETE
    não persistem — era o bug crítico do projeto original.
    """
    conexao = sqlite3.connect(caminho_banco())
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def criar_tabelas():
    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                codigo TEXT NOT NULL UNIQUE,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS despesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL CHECK (valor > 0),
                data DATE NOT NULL,
                categoria TEXT NOT NULL,
                usuario_id INTEGER REFERENCES usuarios(id)
            )
        """)
        colunas = [c["name"] for c in conexao.execute("PRAGMA table_info(despesas)")]
        if "usuario_id" not in colunas:
            conexao.execute(
                "ALTER TABLE despesas ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)"
            )
        conexao.execute(
            "CREATE INDEX IF NOT EXISTS idx_despesas_usuario ON despesas(usuario_id)"
        )


if __name__ == "__main__":
    criar_tabelas()
    print("Banco de dados criado e tabelas preparadas!")
