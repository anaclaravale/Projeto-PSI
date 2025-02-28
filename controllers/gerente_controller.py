from flask import Flask, render_template, redirect, request, url_for, flash, session, Blueprint
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, desc
from functools import wraps
from datetime import datetime, timedelta
from models.cliente import Cliente
from models.autor import Autor
from models.editora import Editora
from models.emprestimo import Emprestimo
from models.emprestimo_livro import EmprestimoLivro
from models.endereco import Endereco
from models.genero import Genero
from models.gerente import Gerente
from models.livro import Livro
from app import app, db, bcrypt

gerente_bp = Blueprint('gerente', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Por favor, realize o login como gerente.", "error")
            return redirect(url_for('login'))

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
    
    if session.get('user_type') != 'gerente':
        flash('Acesso negado!', 'error')
        return redirect(url_for('login'))
    
    return render_template('gerente_dashboard.html')

@gerente_bp.route('/adicionar_gerente', methods=['GET', 'POST'])
@admin_required
def adicionar_gerente():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        senha = request.form.get('senha')

        if Gerente.query.filter_by(ger_email=email).first():
            flash('E-mail já cadastrado para outro gerente.', 'error')
            return redirect(url_for('adicionar_gerente'))

        hashed_senha = bcrypt.generate_password_hash(senha).decode('utf-8')
        novo_gerente = Gerente(ger_codigo=codigo, ger_nome=nome, ger_telefone=telefone, ger_email=email, ger_senha=hashed_senha)

        try:
            db.session.add(novo_gerente)
            db.session.commit()
            flash('Gerente adicionado com sucesso!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Erro ao adicionar gerente: e-mail já existe.', 'error')

        return redirect(url_for('adicionar_gerente'))

    return render_template('admin_dashboard.html')

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

@gerente_bp.route('/clientes_acima_cem', methods=['GET', 'POST'])
@admin_required
def clientes_acima_cem():
    clientes = None
    if request.method == 'POST':
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')

        clientes = db.session.query(
            Cliente.cli_nome,
            func.sum(Emprestimo.emp_total).label('total')
        ).join(Emprestimo).filter(
            Emprestimo.emp_data_ini.between(data_inicio, data_fim)
        ).group_by(Cliente.cli_id).having(func.sum(Emprestimo.emp_total) > 100).all()

    return render_template('clientes_acima_cem.html', clientes=clientes)

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