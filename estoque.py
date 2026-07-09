from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = 'meu_banco.db'

def criar_tabelas():
    """Garante a estrutura profissional com duas tabelas relacionadas (1:N)"""
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    
    # 1. Tabela de Cadastro Único do Produto/Ativo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CADASTRO_PRODUTOS (
            ETIQUETA TEXT PRIMARY KEY
            ,NOME_PRODUTO TEXT NOT NULL
            ,MARCA TEXT NOT NULL
            ,MODELO TEXT NOT NULL
            ,CATEGORIA TEXT NOT NULL
            ,NUMERO_SERIE TEXT
        );
    ''')
    
    # 2. Tabela de Histórico de Movimentações (Entradas e Saídas)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS HISTORICO_MOVIMENTACOES (
            ID INTEGER PRIMARY KEY AUTOINCREMENT
            ,ETIQUETA_PRODUTO TEXT NOT NULL
            ,QUANT INTEGER NOT NULL
            ,TIPO_MOVIMENTACAO TEXT NOT NULL
            ,STATUS_MOV TEXT
            ,DESTINATARIO TEXT
            ,OBSERVACOES TEXT
            ,DATA_REGISTRO DATETIME DEFAULT CURRENT_TIMESTAMP
            ,FOREIGN KEY(ETIQUETA_PRODUTO) REFERENCES CADASTRO_PRODUTOS(ETIQUETA)
        );
    ''')
    conexao.commit()
    conexao.close()

criar_tabelas()

@app.route('/', methods=['GET'])
def index():
    buscar = request.args.get('busca', '').strip()
    mostrar_tudo = request.args.get('todos', '')
    
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    
    movimentacoes = []
    saldos = []
    
    # Query mestre: Traz os produtos e calcula o saldo líquido real via LEFT JOIN
    query_saldo_base = """
        SELECT 
            p.ETIQUETA
            , p.NOME_PRODUTO
            , p.MARCA
            , p.MODELO
            , p.CATEGORIA
            , COALESCE(SUM(CASE WHEN m.TIPO_MOVIMENTACAO = 'ENTRADA' THEN m.QUANT ELSE -m.QUANT END), 0) AS SALDO_ATUAL
        FROM CADASTRO_PRODUTOS p
        LEFT JOIN HISTORICO_MOVIMENTACOES m ON p.ETIQUETA = m.ETIQUETA_PRODUTO
    """
    
    if buscar:
        # 1. Histórico de logs daquela etiqueta específica
        query_busca = """
            SELECT m.ID, p.ETIQUETA, p.NOME_PRODUTO, p.MARCA, p.MODELO, p.CATEGORIA, 
                   m.QUANT, m.TIPO_MOVIMENTACAO, m.STATUS_MOV, m.DESTINATARIO, p.NUMERO_SERIE, m.OBSERVACOES, m.DATA_REGISTRO
            FROM HISTORICO_MOVIMENTACOES m
            JOIN CADASTRO_PRODUTOS p ON p.ETIQUETA = m.ETIQUETA_PRODUTO
            WHERE p.ETIQUETA = ?
            ORDER BY m.DATA_REGISTRO DESC
        """
        cursor.execute(query_busca, (buscar,))
        movimentacoes = cursor.fetchall()
        
        # 2. Saldo atual do produto buscado
        cursor.execute(query_saldo_base + " WHERE p.ETIQUETA = ? GROUP BY p.ETIQUETA", (buscar,))
        saldos = cursor.fetchall()
        
    elif mostrar_tudo == 'true':
        # 1. Histórico completo de movimentações de todo mundo
        query_tudo = """
            SELECT m.ID, p.ETIQUETA, p.NOME_PRODUTO, p.MARCA, p.MODELO, p.CATEGORIA, 
                   m.QUANT, m.TIPO_MOVIMENTACAO, m.STATUS_MOV, m.DESTINATARIO, p.NUMERO_SERIE, m.OBSERVACOES, m.DATA_REGISTRO
            FROM HISTORICO_MOVIMENTACOES m
            JOIN CADASTRO_PRODUTOS p ON p.ETIQUETA = m.ETIQUETA_PRODUTO
            ORDER BY m.DATA_REGISTRO DESC
        """
        cursor.execute(query_tudo)
        movimentacoes = cursor.fetchall()
        
        # 2. Saldo atual de todos os produtos cadastrados no sistema
        cursor.execute(query_saldo_base + " GROUP BY p.ETIQUETA")
        saldos = cursor.fetchall()
        
    conexao.close()
    return render_template(
        'index.html', 
        movimentacoes=movimentacoes, 
        saldos=saldos, 
        buscar=buscar, 
        listando_todos=(mostrar_tudo == 'true')
    )

@app.route('/inserir', methods=['POST'])
def inserir():
    etiqueta = request.form.get('etiqueta').strip()
    nome_produto = request.form.get('nome_produto')
    marca = request.form.get('marca')
    modelo = request.form.get('modelo')
    categoria = request.form.get('categoria')
    quant = int(request.form.get('quant'))
    tipo = request.form.get('tipo_movimentacao')
    status_mov = request.form.get('status_mov')
    destinatario = request.form.get('destinatario') if tipo == 'SAIDA' else ''
    numero_serie = request.form.get('numero_serie')
    observacoes = request.form.get('observacoes')

    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    
    # PASSO 1: Insere ou atualiza as características do Produto (Garante que ele exista)
    query_produto = """
        INSERT INTO CADASTRO_PRODUTOS (ETIQUETA, NOME_PRODUTO, MARCA, MODELO, CATEGORIA, NUMERO_SERIE)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(ETIQUETA) DO UPDATE SET
            NOME_PRODUTO=excluded.NOME_PRODUTO,
            MARCA=excluded.MARCA,
            MODELO=excluded.MODELO,
            CATEGORIA=excluded.CATEGORIA,
            NUMERO_SERIE=coalesce(nullif(excluded.NUMERO_SERIE, ''), NUMERO_SERIE)
    """
    cursor.execute(query_produto, (etiqueta, nome_produto, marca, modelo, categoria, numero_serie))
    
    # PASSO 2: Registra a movimentação no histórico
    query_mov = """
        INSERT INTO HISTORICO_MOVIMENTACOES (ETIQUETA_PRODUTO, QUANT, TIPO_MOVIMENTACAO, STATUS_MOV, DESTINATARIO, OBSERVACOES)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query_mov, (etiqueta, quant, tipo, status_mov, destinatario, observacoes))
    
    conexao.commit()
    conexao.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)