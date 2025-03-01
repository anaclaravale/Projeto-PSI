from flask import Flask, render_template, redirect, request, url_for, flash, session, Blueprint
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, desc
from functools import wraps
from datetime import datetime, timedelta
from models.cliente import Cliente
from models.emprestimo import Emprestimo
from models.emprestimo_livro import EmprestimoLivro
from models.gerente import Gerente
from models.livro import Livro
from models.autor import Autor
from models.editora import Editora
from models.genero import Genero
from extensoes import bcrypt
from extensoes import db

gerente_bp = Blueprint('gerente', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Por favor, realize o login como gerente.", "error")
            return redirect(url_for('auth.login'))

        gerente = Gerente.query.filter_by(ger_email=session.get('email')).first()
        if not gerente or gerente.ger_email != 'gerente@biblioteca.com':
            flash("Permissões negadas", "error")
            return redirect(url_for('gerente_dashboard'))

        return f(*args, **kwargs)
    return decorated_function

@gerente_bp.route('/gerente_dashboard')
@login_required
def gerente_dashboard():
    session['user_type'] = session.get('user_type', 'desconhecido')
    print(f"DEBUG: user_type na rota = {session.get('user_type')}")

    # Calcula os totais
    total_livros = Livro.query.count()  # Total de livros
    total_autores = Autor.query.count()  # Total de autores
    total_editoras = Editora.query.count()  # Total de editoras
    total_generos = db.session.query(func.count(func.distinct(Genero.gen_id))).scalar()
    
    if session.get('user_type') != 'gerente':
        flash('Acesso negado!', 'error')
        return redirect(url_for('auth.login'))

    # Passa as variáveis para o template
    return render_template('gerente_dashboard.html', 
                            total_livros=total_livros,
                            total_autores=total_autores,
                            total_editoras=total_editoras,
                            total_generos=total_generos)

@gerente_bp.route('/listar_clientes')
@admin_required
def listar_clientes():
    clientes = Cliente.query.all()  # Busca todos os clientes
    return render_template('listar_clientes.html', clientes=clientes)

@gerente_bp.route('/listar_livros')
@admin_required
def listar_livros():
    livros = Livro.query.all()  # Busca todos os livros
    return render_template('listar_livros.html', livros=livros)

@gerente_bp.route('/listar_emprestimos')
@admin_required
def listar_emprestimos():
    emprestimos = Emprestimo.query.all()  # Busca todos os empréstimos
    return render_template('listar_emprestimos.html', emprestimos=emprestimos)

@gerente_bp.route('/relatorio_emprestimos_cliente', methods=['GET', 'POST'])
@admin_required
def relatorio_emprestimos_cliente():
    relatorio = None
    if request.method == 'POST':
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')

        relatorio = db.session.query(
            Cliente.cli_nome,
            func.count(Emprestimo.emp_id).label('total_emprestimos'),
            func.round(func.sum(Emprestimo.emp_total), 2).label('total_valor')
        ).outerjoin(Emprestimo).filter(
            Emprestimo.emp_data_ini.between(data_inicio, data_fim)
        ).group_by(Cliente.cli_id).order_by(desc('total_emprestimos')).all()

    return render_template('relatorio_emprestimos_cliente.html', relatorio=relatorio)

@gerente_bp.route('/top_livros', methods=['GET'])
@admin_required
def top_livros():
    dias = request.args.get('dias', 30)
    top_livros = db.session.query(
        Livro.liv_id,
        Livro.liv_titulo,
        func.count(EmprestimoLivro.eml_id).label('total_emprestimos')
    ).join(EmprestimoLivro).join(Emprestimo).filter(
        Emprestimo.emp_data_ini >= datetime.now() - timedelta(days=int(dias))
    ).group_by(Livro.liv_id).order_by(desc('total_emprestimos')).limit(10).all()

    return render_template('top_livros.html', top_livros=top_livros, dias=dias)

@gerente_bp.route('/livros_nao_emprestados', methods=['GET'])
@admin_required
def livros_nao_emprestados():
    livros_nao_emprestados = Livro.query.filter(Livro.liv_estoque > 0).all()
    return render_template('livros_nao_emprestados.html', livros=livros_nao_emprestados)