from flask import Flask, jsonify
import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configuração da base de dados
DB_CONFIG = {
    'host': 'localhost',
    'database': 'escola',
    'user': os.getenv('DB_USER', 'app_user'),
    'password': os.getenv('DB_PASSWORD', 'App_User123!'),
    'port': 5432
}

def get_db_connection():
    """Estabelece ligação com a base de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erro de ligação à BD: {e}")
        return None

@app.route('/')
def home():
    """Página inicial da API"""
    return jsonify({
        'message': 'Bem-vindo à API da Escola!',
        'endpoints': {
            '/users': 'Lista todos os utilizadores',
            '/users/<id>': 'Dados de um utilizador específico',
            '/cursos': 'Lista todos os cursos',
            '/matriculas/<curso_id>': 'Alunos matriculados num curso'
        }
    })

@app.route('/users', methods=['GET'])
def get_users():
    """Lista todos os utilizadores"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro de ligação à BD'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, nome, idade, username, email, created_at 
            FROM users 
            ORDER BY user_id
        """)
        users = cursor.fetchall()
        
        # Converter para lista de dicionários
        users_list = []
        for user in users:
            users_list.append({
                'user_id': user[0],
                'nome': user[1],
                'idade': user[2],
                'username': user[3],
                'email': user[4],
                'created_at': user[5].isoformat() if user[5] else None
            })
        
        return jsonify(users_list)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Dados de um utilizador específico"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro de ligação à BD'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, nome, idade, username, email, created_at 
            FROM users 
            WHERE user_id = %s
        """, (user_id,))
        user = cursor.fetchone()
        
        if user:
            user_data = {
                'user_id': user[0],
                'nome': user[1],
                'idade': user[2],
                'username': user[3],
                'email': user[4],
                'created_at': user[5].isoformat() if user[5] else None
            }
            return jsonify(user_data)
        else:
            return jsonify({'error': 'Utilizador não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/cursos', methods=['GET'])
def get_cursos():
    """Lista todos os cursos"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro de ligação à BD'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT curso_id, nome, descricao, ativo FROM cursos ORDER BY curso_id")
        cursos = cursor.fetchall()
        
        cursos_list = []
        for curso in cursos:
            cursos_list.append({
                'curso_id': curso[0],
                'nome': curso[1],
                'descricao': curso[2],
                'ativo': curso[3]
            })
        
        return jsonify(cursos_list)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/matriculas/<int:curso_id>', methods=['GET'])
def get_matriculas_curso(curso_id):
    """Alunos matriculados num curso específico"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro de ligação à BD'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.user_id, u.nome, u.email, c.nome as curso_nome
            FROM matriculas m
            JOIN users u ON m.user_id = u.user_id
            JOIN cursos c ON m.curso_id = c.curso_id
            WHERE m.curso_id = %s
            ORDER BY u.nome
        """, (curso_id,))
        matriculas = cursor.fetchall()
        
        matriculas_list = []
        for matricula in matriculas:
            matriculas_list.append({
                'user_id': matricula[0],
                'nome': matricula[1],
                'email': matricula[2],
                'curso': matricula[3]
            })
        
        return jsonify({
            'curso_id': curso_id,
            'alunos_matriculados': matriculas_list,
            'total': len(matriculas_list)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
