from flask import Flask, render_template, redirect, request, url_for, flash, session
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

@app.route('/cliente_dashboard')
@login_required
def cliente_dashboard():
    if session.get('user_type') != 'cliente':  # Verifica se o usuário é um cliente
        flash('Acesso negado.', 'error')
        return redirect(url_for('index'))

    cliente = Cliente.query.get(current_user.cli_id)
    return render_template('cliente_dashboard.html', cliente=cliente)

@app.route('/editar', methods=['GET', 'POST'])
@login_required
def editar():
    cliente = Cliente.query.get(current_user.cli_id)
    endereco = Endereco.query.filter_by(end_cli_id=current_user.cli_id).first()

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')

        if email != cliente.cli_email and is_email_taken(email):
            flash('Este e-mail já está em uso.', 'warning')
            return redirect(url_for('editar'))

        cliente.cli_nome = nome
        cliente.cli_email = email
        cliente.cli_telefone = telefone

        if endereco:
            endereco.end_estado = request.form.get('estado')
            endereco.end_cidade = request.form.get('cidade')
            endereco.end_bairro = request.form.get('bairro')
            endereco.end_rua = request.form.get('rua')
            endereco.end_numero = request.form.get('numero')
        else:
            endereco = Endereco(
                end_cli_id=cliente.cli_id,
                end_estado=request.form.get('estado'),
                end_cidade=request.form.get('cidade'),
                end_bairro=request.form.get('bairro'),
                end_rua=request.form.get('rua'),
                end_numero=request.form.get('numero')
            )
            db.session.add(endereco)

        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('cliente_dashboard'))

    return render_template('editar.html', cliente=cliente, endereco=endereco)

@app.route('/excluir', methods=['POST'])
@login_required
def excluir():
    cliente = Cliente.query.get(current_user.cli_id)

    if not cliente:
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('cliente_dashboard'))

    logout_user()
    db.session.delete(cliente)
    db.session.commit()
    session.clear()

    flash('Conta excluída com sucesso.', 'success')
    return redirect(url_for('index'))