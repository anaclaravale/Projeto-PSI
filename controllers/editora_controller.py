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

editora_bp = Blueprint('editora', __name__)

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

@editora_bp.route('/cadastrar_editora', methods=['GET', 'POST'])
@admin_required
def cadastrar_editora():
    if request.method == 'POST':
        nome = request.form.get('editora_nome')

        # Verifica se a editora já existe
        if Editora.query.filter_by(edi_nome=nome).first():
            flash('Editora já cadastrada.', 'error')
            return redirect(url_for('cadastrar_editora'))

        nova_editora = Editora(edi_nome=nome)

        try:
            db.session.add(nova_editora)
            db.session.commit()
            flash('Editora cadastrada com sucesso!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Erro ao cadastrar a editora.', 'error')

        return redirect(url_for('cadastrar_editora'))

    return render_template('cadastrar_editora.html')