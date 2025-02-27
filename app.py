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
from controllers import auth_controller, autor_controller, cliente_controller, editora_controller, emprestimo_controller, genero_controller, gerente_controller, livro_controller



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.secret_key = 'muitodificil'
db = SQLAlchemy()

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.permanent_session_lifetime = timedelta(minutes=30)  # Sessão expira após 30 minutos

# Inicializa o banco de dados
db.init_app(app)

with app.app_context():
    db.create_all()

    # Verificar se o gerente já existe
    gerente_existe = Gerente.query.filter_by(ger_codigo=9966).first()

    if gerente_existe is None:
        # Criando uma nova instância de Gerente
        novo_gerente = Gerente(
            ger_codigo=9966,
            ger_nome="Marcos",
            ger_telefone="3444427777",
            ger_email="gerente@biblioteca.com",
            ger_senha="$2b$12$QyfS1b2byE1HwzzSLIdH1uW6XogT9Z1WWK5S9iNqkTIgL04IVQ9u2"
        )

        # Adicionando à sessão e commitando
        db.session.add(novo_gerente)
        db.session.commit()
    else:
        print("Gerente já existe.")

@login_manager.user_loader
def load_user(user_id):
    # Tenta carregar um Cliente
    cliente = Cliente.query.get(int(user_id))
    if cliente:
        return cliente

    # Tenta carregar um Gerente
    gerente = Gerente.query.get(int(user_id))
    if gerente:
        return gerente

    return None  # Retorna None se nenhum usuário for encontrado

def is_email_taken(email):
    return Cliente.query.filter_by(cli_email=email).first() is not None



@app.route('/')
def index():
    return render_template('index.html')