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

@app.route('/gerenciar_emprestimos')
def gerenciar_emprestimos():
    if not session.get('logged_in') or not session.get('user_id'):
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    emprestimos = Emprestimo.query.filter_by(emp_cli_id=user_id).order_by(Emprestimo.emp_data_ini.asc()).all()

    emprestimos_com_livros = []
    for emprestimo in emprestimos:
        livros = EmprestimoLivro.query.filter_by(eml_emp_id=emprestimo.emp_id).all()
        emprestimos_com_livros.append({'emprestimo': emprestimo, 'livros': livros})

    return render_template('gerenciar_emprestimos.html', emprestimos=emprestimos_com_livros)

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