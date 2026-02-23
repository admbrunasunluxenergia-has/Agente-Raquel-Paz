import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# ==================================================
# CONNECTION POOL (MELHOR PERFORMANCE)
# ==================================================

connection_pool = pool.SimpleConnectionPool(
    1,
    10,
    DATABASE_URL,
    sslmode="require"
)


def conectar():
    try:
        return connection_pool.getconn()
    except Exception as e:
        logger.error(f"❌ Erro ao conectar no banco: {e}")
        raise


def liberar_conexao(conn):
    connection_pool.putconn(conn)


# ==================================================
# CRIAÇÃO DE TABELAS
# ==================================================

def criar_tabelas():

    conn = conectar()
    cursor = conn.cursor()

    try:

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contatos (
            id SERIAL PRIMARY KEY,
            telefone VARCHAR(20) UNIQUE NOT NULL,
            nome VARCHAR(100),
            tipo VARCHAR(50),
            etapa_funil VARCHAR(50) DEFAULT 'novo',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id SERIAL PRIMARY KEY,
            telefone VARCHAR(20) NOT NULL,
            mensagem_id VARCHAR(100) UNIQUE,
            mensagem TEXT,
            resposta TEXT,
            categoria VARCHAR(50),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_mensagens_telefone 
        ON mensagens (telefone);
        """)

        conn.commit()
        logger.info("✅ Tabelas verificadas/criadas")

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        raise

    finally:
        cursor.close()
        liberar_conexao(conn)


# ==================================================
# BUSCAR HISTÓRICO
# ==================================================

def buscar_historico(telefone):

    conn = conectar()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT mensagem, resposta 
            FROM mensagens 
            WHERE telefone = %s 
            ORDER BY criado_em DESC 
            LIMIT 10
        """, (telefone,))

        historico = cursor.fetchall()
        return historico

    except Exception as e:
        logger.error(f"❌ Erro buscar histórico: {e}")
        return []

    finally:
        cursor.close()
        liberar_conexao(conn)


# ==================================================
# BUSCAR CONTATO
# ==================================================

def buscar_contato(telefone):

    conn = conectar()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT nome, tipo, etapa_funil
            FROM contatos 
            WHERE telefone = %s
        """, (telefone,))

        contato = cursor.fetchone()
        return contato

    except Exception as e:
        logger.error(f"❌ Erro buscar contato: {e}")
        return None

    finally:
        cursor.close()
        liberar_conexao(conn)


# ==================================================
# VERIFICAR DUPLICIDADE (ANTI-LOOP)
# ==================================================

def mensagem_existe(mensagem_id):

    if not mensagem_id:
        return False

    conn = conectar()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT 1 FROM mensagens 
            WHERE mensagem_id = %s
        """, (mensagem_id,))

        return cursor.fetchone() is not None

    except Exception as e:
        logger.error(f"❌ Erro verificar duplicidade: {e}")
        return False

    finally:
        cursor.close()
        liberar_conexao(conn)
