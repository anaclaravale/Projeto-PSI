from flask import Flask, render_template, redirect, request, url_for, flash, session, Blueprint
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from functools import wraps
from datetime import datetime, timedelta
from models.autor import Autor
from models.editora import Editora
from models.emprestimo import Emprestimo
from models.emprestimo_livro import EmprestimoLivro
from models.genero import Genero
from models.gerente import Gerente
from models.livro import Livro
from app import db

livro_bp = Blueprint('livro', __name__)

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

@livro_bp.route('/cadastrar_livro', methods=['GET', 'POST'])
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

@livro_bp.route('/emprestimo', methods=['GET', 'POST'])
def emprestimo():
    if not session.get('logged_in'):
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('login'))

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


