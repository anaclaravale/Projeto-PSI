from flask import Flask, render_template, redirect, request, url_for, flash, session, Blueprint
from functools import wraps
from models.autor import Autor
from models.gerente import Gerente
from extensoes import db

autor_bp = Blueprint('autor', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Por favor, realize o login como gerente.", "error")
            return redirect(url_for('auth.login'))

        gerente = Gerente.query.filter_by(ger_email=session.get('email')).first()
        if not gerente or gerente.ger_email != 'gerente@biblioteca.com':
            flash("Permissões negadas", "error")
            return redirect(url_for('gerente.gerente_dashboard'))

        return f(*args, **kwargs)
    return decorated_function

@autor_bp.route('/cadastrar_autor', methods=['GET', 'POST'])
@admin_required
def cadastrar_autor():
    if request.method == 'POST':
        nome = request.form.get('autor_nome')  # Captura o valor do campo 'autor_nome'

        if not nome:
            flash('O nome do autor é obrigatório.', 'error')
            return redirect(url_for('autor.cadastrar_autor'))

        # Verifica se o autor já existe
        autor_existente = Autor.query.filter_by(aut_nome=nome).first()
        if autor_existente:
            flash('Autor já cadastrado.', 'error')
            return redirect(url_for('cadastrar_autor'))

        # Cria um novo autor
        novo_autor = Autor(aut_nome=nome)

        try:
            db.session.add(novo_autor)
            db.session.commit()
            flash('Autor cadastrado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar o autor: {str(e)}', 'error')

        return redirect(url_for('autor.cadastrar_autor'))

    return render_template('cadastrar_autor.html')
