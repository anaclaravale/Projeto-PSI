from flask import Flask, render_template, redirect, url_for, flash, session, Blueprint
from models.emprestimo import Emprestimo
from models.emprestimo_livro import EmprestimoLivro
from models.livro import Livro
from extensoes import db

emprestimo_bp = Blueprint('emprestimo', __name__)

@emprestimo_bp.route('/gerenciar_emprestimos')
def gerenciar_emprestimos():
    if not session.get('logged_in') or not session.get('user_id'):
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    emprestimos = Emprestimo.query.filter_by(emp_cli_id=user_id).order_by(Emprestimo.emp_data_ini.asc()).all()

    emprestimos_com_livros = []
    for emprestimo in emprestimos:
        # Recuperando os livros associados ao empréstimo
        livros = EmprestimoLivro.query.filter_by(eml_emp_id=emprestimo.emp_id).all()
        emprestimos_com_livros.append({'emprestimo': emprestimo, 'livros': livros})

    return render_template('gerenciar_emprestimos.html', emprestimos=emprestimos_com_livros)

@emprestimo_bp.route("/devolver/<int:emp_id>", methods=["POST"])
def devolver(emp_id):
    emprestimo = Emprestimo.query.filter_by(emp_id=emp_id, emp_cli_id=session['user_id']).first()

    if not emprestimo or emprestimo.emp_status == 'Finalizado':
        return redirect(url_for("emprestimo.gerenciar_emprestimos"))

    livros = EmprestimoLivro.query.filter_by(eml_emp_id=emp_id).all()

    for livro in livros:
        livro_atual = Livro.query.get(livro.eml_liv_id)
        livro_atual.liv_estoque += livro.eml_quantidade

    emprestimo.emp_status = 'Finalizado'
    
    db.session.commit()
    flash("Empréstimo devolvido com sucesso!", "success")

    return redirect(url_for("emprestimo.gerenciar_emprestimos"))