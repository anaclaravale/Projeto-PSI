from flask import Flask, render_template, redirect, request, url_for, flash, session, Blueprint
from sqlalchemy.exc import IntegrityError
from functools import wraps
from models.editora import Editora
from models.gerente import Gerente
from app import db

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