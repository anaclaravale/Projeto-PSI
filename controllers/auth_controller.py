from flask import Flask, render_template, redirect, request, url_for, flash, session, Blueprint
from flask_bcrypt import check_password_hash
from flask_login import login_user, logout_user
from models.cliente import Cliente
from models.gerente import Gerente
from models.endereco import Endereco
from extensoes import bcrypt
from extensoes import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        session.clear()
        session.permanent = True
        
        gerente = Gerente.query.filter_by(ger_email=email).first()
        cliente = Cliente.query.filter_by(cli_email=email).first()
        
        if gerente and check_password_hash(gerente.ger_senha, senha):
            login_user(gerente)
            session['user_id'] = gerente.ger_id
            session["email"] = gerente.ger_email
            session["gerente_id"] = gerente.ger_id
            session['user_type'] = 'gerente'
            session["logged_in"] = True
            print(f"DEBUG: user_type definido como {session.get('user_type')}")
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('gerente.gerente_dashboard'))
        
        elif cliente and check_password_hash(cliente.cli_senha, senha):
            login_user(cliente)
            session['user_id'] = cliente.cli_id
            session['user_type'] = 'cliente'
            session["logged_in"] = True
            print(f"DEBUG: user_type definido como {session.get('user_type')}")
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('cliente.cliente_dashboard'))
        
        else:
            flash('Email ou senha incorretos.', 'danger')
    return render_template('login.html')

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        telefone = request.form.get('telefone')

        estado = request.form.get('estado')
        cidade = request.form.get('cidade')
        bairro = request.form.get('bairro')
        rua = request.form.get('rua')
        numero = request.form.get('numero')

        if Cliente.query.filter_by(cli_email=email).first():
            flash('Esse e-mail já está em uso. Por favor, escolha outro.', 'warning')
            return redirect(url_for('auth.cadastro'))

        hashed_senha = bcrypt.generate_password_hash(senha).decode('utf-8')
        novo_cliente = Cliente(cli_nome=nome, cli_email=email, cli_senha=hashed_senha, cli_telefone=telefone)

        db.session.add(novo_cliente)
        db.session.commit()  # Confirma para obter o cli_id

        # Salvar o endereço com o ID do cliente recém-criado
        novo_endereco = Endereco(
            end_cli_id=novo_cliente.cli_id,
            end_estado=estado,
            end_cidade=cidade,
            end_bairro=bairro,
            end_rua=rua,
            end_numero=numero
        )

        db.session.add(novo_endereco)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Você pode fazer login agora.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('cadastro.html')

@auth_bp.route('/logout')
def logout():
    logout_user()  # Faz logout do usuário atual
    session.clear()  # Limpa todos os dados da sessão
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('auth.login'))