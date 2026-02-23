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
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mensagens (
        id SERIAL PRIMARY KEY,
        telefone VARCHAR(20),
        mensagem TEXT,
        resposta TEXT,
        categoria VARCHAR(50),
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()
