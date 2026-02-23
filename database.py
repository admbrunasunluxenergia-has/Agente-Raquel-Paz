import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")


def conectar():
    return psycopg2.connect(DATABASE_URL)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contatos (
        id SERIAL PRIMARY KEY,
        telefone VARCHAR(20) UNIQUE,
        nome VARCHAR(100),
        tipo VARCHAR(50),
        etapa_funil VARCHAR(50) DEFAULT 'novo',
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mensagens (
        id SERIAL PRIMARY KEY,
        telefone VARCHAR(20),
        mensagem_id VARCHAR(100),
        mensagem TEXT,
        resposta TEXT,
        categoria VARCHAR(50),
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()


def buscar_historico(telefone):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mensagem, resposta
        FROM mensagens
        WHERE telefone = %s
        ORDER BY criado_em DESC
        LIMIT 10
    """, (telefone,))

    historico = cursor.fetchall()

    cursor.close()
    conn.close()

    return historico


def buscar_contato(telefone):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome, tipo, etapa_funil
        FROM contatos
        WHERE telefone = %s
    """, (telefone,))

    contato = cursor.fetchone()

    cursor.close()
    conn.close()

    return contato


def mensagem_existe(mensagem_id):

    if not mensagem_id:
        return False

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM mensagens WHERE mensagem_id = %s
    """, (mensagem_id,))

    existe = cursor.fetchone() is not None

    cursor.close()
    conn.close()

    return existe
