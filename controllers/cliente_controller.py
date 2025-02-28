from flask import Flask, render_template, redirect, request, url_for, flash, session, Blueprint
from flask_login import logout_user, login_required, current_user
from models.cliente import Cliente
from models.endereco import Endereco
from extensoes import db

cliente_bp = Blueprint('cliente', __name__)

def is_email_taken(email):
    return Cliente.query.filter_by(cli_email=email).first() is not None

@cliente_bp.route('/cliente_dashboard')
@login_required
def cliente_dashboard():
    if session.get('user_type') != 'cliente':  # Verifica se o usuário é um cliente
        flash('Acesso negado.', 'error')
        return redirect(url_for('index'))

    cliente = Cliente.query.get(current_user.cli_id)
    return render_template('cliente_dashboard.html', cliente=cliente)

@cliente_bp.route('/editar', methods=['GET', 'POST'])
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
            return redirect(url_for('cliente.editar'))

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
        return redirect(url_for('cliente.cliente_dashboard'))

    return render_template('editar.html', cliente=cliente, endereco=endereco)

@cliente_bp.route('/excluir', methods=['POST'])
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