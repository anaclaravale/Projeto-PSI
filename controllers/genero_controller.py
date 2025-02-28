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
from app import app, db

genero_bp = Blueprint('genero', __name__)

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

@genero_bp.route('/cadastrar_genero', methods=['GET', 'POST'])
@admin_required
def cadastrar_genero():
    if request.method == 'POST':
        nome = request.form.get('genero_nome')

        # Verifica se o gênero já existe
        if Genero.query.filter_by(gen_nome=nome).first():
            flash('Gênero já cadastrado.', 'error')
            return redirect(url_for('cadastrar_genero'))

        novo_genero = Genero(gen_nome=nome)

        try:
            db.session.add(novo_genero)
            db.session.commit()
            flash('Gênero cadastrado com sucesso!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Erro ao cadastrar o gênero.', 'error')

        return redirect(url_for('cadastrar_genero'))

    return render_template('cadastrar_genero.html')