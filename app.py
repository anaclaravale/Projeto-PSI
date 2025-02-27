from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_bcrypt import Bcrypt
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


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.secret_key = 'muitodificil'
db = SQLAlchemy()

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_cliente'

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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Por favor, realize o login como gerente.", "error")
            return redirect(url_for('login_gerente'))

        gerente = Gerente.query.filter_by(ger_email=session.get('email')).first()
        if not gerente or gerente.ger_email != 'gerente@biblioteca.com':
            flash("Permissões negadas", "error")
            return redirect(url_for('gerente_dashboard'))

        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
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
            return redirect(url_for('cadastro'))

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
        return redirect(url_for('login_cliente'))

    return render_template('cadastro.html')

@app.route('/login_cliente', methods=['GET', 'POST'])
def login_cliente():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not email or not senha:
            flash('Por favor, preencha todos os campos.', 'error')
            return redirect(url_for('login_cliente'))

        cliente = Cliente.query.filter_by(cli_email=email).first()

        if cliente and bcrypt.check_password_hash(cliente.cli_senha, senha):
            login_user(cliente)
            session['logged_in'] = True
            session['user_id'] = cliente.cli_id  # Define o user_id na sessão
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('cliente_dashboard'))  # Redireciona para o painel do cliente
        else:
            flash('E-mail ou senha inválidos.', 'error')

    return render_template('login_cliente.html')


@app.route('/login_gerente', methods=['GET', 'POST'])
def login_gerente():
    session.clear()
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        gerente = Gerente.query.filter_by(ger_email=email).first()
        if gerente and bcrypt.check_password_hash(gerente.ger_senha, senha):
            login_user(gerente)  # Autentica o gerente
            session['gerente_id'] = gerente.ger_id
            session['nome'] = gerente.ger_nome
            session['email'] = gerente.ger_email

            return redirect(url_for('gerente_dashboard'))

        flash('Credenciais inválidas para gerente.', 'error')

    return render_template('login_gerente.html')

@app.route('/cliente_dashboard')
@login_required
def cliente_dashboard():
    if not isinstance(current_user, Cliente):
        flash('Acesso negado.', 'error')
        return redirect(url_for('index'))
    cliente = Cliente.query.get(current_user.cli_id)
    return render_template('cliente_dashboard.html', cliente=cliente)

@app.route('/gerente_dashboard')
@admin_required
def gerente_dashboard():
    if not isinstance(current_user, Gerente):
        flash('Acesso negado.', 'error')
        return redirect(url_for('index'))

    gerente = Gerente.query.get(current_user.ger_id)
    return render_template('gerente_dashboard.html', gerente=gerente)

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



@app.route('/adicionar_gerente', methods=['GET', 'POST'])
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

@app.route('/cadastrar_autor', methods=['GET', 'POST'])
@admin_required
def cadastrar_autor():
    if request.method == 'POST':
        nome = request.form.get('autor_nome')  # Captura o valor do campo 'autor_nome'

        if not nome:
            flash('O nome do autor é obrigatório.', 'error')
            return redirect(url_for('cadastrar_autor'))

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

        return redirect(url_for('cadastrar_autor'))

    return render_template('cadastrar_autor.html')

@app.route('/cadastrar_editora', methods=['GET', 'POST'])
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

@app.route('/cadastrar_genero', methods=['GET', 'POST'])
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

@app.route('/cadastrar_livro', methods=['GET', 'POST'])
@admin_required
def cadastrar_livro():
    if request.method == 'POST':
        # Captura os dados do formulário
        titulo = request.form.get('titulo')
        isbn = request.form.get('isbn')
        ano = request.form.get('ano')
        autor_id = request.form.get('autor')
        editora_id = request.form.get('editora')
        genero_id = request.form.get('genero')
        pais_origem = request.form.get('pais_origem')
        estoque = request.form.get('estoque')
        preco = request.form.get('preco')
        gerente_id = session.get('gerente_id')  # ID do gerente logado

        # Validações básicas
        if not all([titulo, isbn, ano, autor_id, editora_id, genero_id, pais_origem, estoque, preco]):
            flash('Todos os campos são obrigatórios.', 'error')
            return redirect(url_for('cadastrar_livro'))

        try:
            # Converte os valores para os tipos corretos
            ano = int(ano)
            estoque = int(estoque)
            preco = float(preco)
            autor_id = int(autor_id)
            editora_id = int(editora_id)
            genero_id = int(genero_id)
        except ValueError:
            flash('Dados inválidos. Verifique os campos numéricos.', 'error')
            return redirect(url_for('cadastrar_livro'))

        # Cria um novo livro
        novo_livro = Livro(
            liv_titulo=titulo,
            liv_isbn=isbn,
            liv_ano=ano,
            liv_aut_id=autor_id,
            liv_edi_id=editora_id,
            liv_gen_id=genero_id,
            liv_pais_origem=pais_origem,
            liv_estoque=estoque,
            liv_preco=preco,
            liv_ger_id=gerente_id
        )

        try:
            db.session.add(novo_livro)
            db.session.commit()
            flash('Livro cadastrado com sucesso!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Erro ao cadastrar o livro: ISBN ou título já existem.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar o livro: {str(e)}', 'error')

        return redirect(url_for('cadastrar_livro'))

    # Busca autores, editoras e gêneros para exibir no formulário
    autores = db.session.query(Autor.aut_id, Autor.aut_nome).all()
    editoras = db.session.query(Editora.edi_id, Editora.edi_nome).all()
    generos = db.session.query(Genero.gen_id, Genero.gen_nome).all()

    return render_template('cadastro_livro.html', autores=autores, editoras=editoras, generos=generos)

@app.route('/emprestimo', methods=['GET', 'POST'])
def emprestimo():
    if not session.get('logged_in'):
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('login_cliente'))

    if request.method == 'POST':
        duracao_dias = int(request.form.get('duracao', 0))
        livros_ids = request.form.getlist('livros')
        quantidades = request.form.getlist('quantidades')

        if not livros_ids or not quantidades:
            flash('Nenhum livro foi selecionado para o empréstimo.', 'error')
            return redirect('/emprestimo')

        emprestimo_livros = []
        total = 0

        for livro_id, quantidade in zip(livros_ids, quantidades):
            livro = Livro.query.get(livro_id)
            if not livro:
                flash(f'O livro com ID "{livro_id}" não foi encontrado.', 'danger')
                return redirect('/emprestimo')

            if livro.liv_estoque < int(quantidade):
                flash(f'O livro {livro_id} não tem estoque suficiente. Estoque atual: {livro.liv_estoque}.', 'error')
                return redirect('/emprestimo')

            total += livro.liv_preco * int(quantidade)
            emprestimo_livros.append({'livro': livro, 'quantidade': int(quantidade)})

        novo_emprestimo = Emprestimo(
            emp_cli_id=current_user.cli_id,  # Usa current_user.cli_id
            emp_data_ini=datetime.now(),
            emp_status='Ativo',
            emp_total=total,
            emp_dev=datetime.now() + timedelta(days=duracao_dias)
        )

        db.session.add(novo_emprestimo)
        db.session.flush()

        for item in emprestimo_livros:
            db.session.add(EmprestimoLivro(
                eml_emp_id=novo_emprestimo.emp_id,
                eml_liv_id=item['livro'].liv_id,
                eml_quantidade=item['quantidade'],
                eml_preco=item['quantidade'] * item['livro'].liv_preco
            ))

            item['livro'].liv_estoque -= item['quantidade']
            db.session.add(item['livro'])

        db.session.commit()
        flash('Empréstimo realizado com sucesso!', 'success')
        return redirect('/gerenciar_emprestimos')

    livros = Livro.query.join(Genero).join(Autor).all()
    return render_template('emprestimo.html', livros=livros)

@app.route('/listar_livros')
@admin_required
def listar_livros():
    livros = Livro.query.all()  # Busca todos os livros
    return render_template('listar_livros.html', livros=livros)

@app.route('/listar_clientes')
@admin_required
def listar_clientes():
    clientes = Cliente.query.all()  # Busca todos os clientes
    return render_template('listar_clientes.html', clientes=clientes)

@app.route('/listar_emprestimos')
@admin_required
def listar_emprestimos():
    emprestimos = Emprestimo.query.all()  # Busca todos os empréstimos
    return render_template('listar_emprestimos.html', emprestimos=emprestimos)

@app.route('/relatorio_emprestimos_cliente', methods=['GET', 'POST'])
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

@app.route('/clientes_acima_cem', methods=['GET', 'POST'])
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

@app.route('/top_livros', methods=['GET'])
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

@app.route('/livros_nao_emprestados', methods=['GET'])
@admin_required
def livros_nao_emprestados():
    livros_nao_emprestados = Livro.query.filter(Livro.liv_estoque > 0).all()
    return render_template('livros_nao_emprestados.html', livros=livros_nao_emprestados)

@app.route("/devolver/<int:emp_id>", methods=["POST"])
def devolver(emp_id):
    emprestimo = Emprestimo.query.filter_by(emp_id=emp_id, emp_cli_id=session['user_id']).first()

    if not emprestimo or emprestimo.emp_status == 'Finalizado':
        return redirect(url_for("gerenciar_emprestimos"))

    livros = EmprestimoLivro.query.filter_by(eml_emp_id=emp_id).all()

    for livro in livros:
        livro_atual = Livro.query.get(livro.eml_liv_id)
        livro_atual.liv_estoque += livro.eml_quantidade

    emprestimo.emp_status = 'Finalizado'
    
    db.session.commit()
    flash("Empréstimo devolvido com sucesso!", "success")

    return redirect(url_for("gerenciar_emprestimos"))

@app.route('/gerenciar_emprestimos')
def gerenciar_emprestimos():
    if not session.get('logged_in') or not session.get('user_id'):
        return redirect(url_for('login_cliente'))
    
    user_id = session['user_id']
    emprestimos = Emprestimo.query.filter_by(emp_cli_id=user_id).order_by(Emprestimo.emp_data_ini.asc()).all()

    emprestimos_com_livros = []
    for emprestimo in emprestimos:
        livros = EmprestimoLivro.query.filter_by(eml_emp_id=emprestimo.emp_id).all()
        emprestimos_com_livros.append({'emprestimo': emprestimo, 'livros': livros})

    return render_template('gerenciar_emprestimos.html', emprestimos=emprestimos_com_livros)

@app.route('/logout')
def logout():
    logout_user()  # Faz logout do usuário atual
    session.clear()  # Limpa a sessão
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('login_cliente'))