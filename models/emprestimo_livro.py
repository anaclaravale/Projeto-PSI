from app import db

class EmprestimoLivro(db.Model):
    __tablename__ = 'tb_emprestimo_livro'
    eml_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    eml_emp_id = db.Column(db.Integer, db.ForeignKey('tb_emprestimo.emp_id'), nullable=False)
    eml_liv_id = db.Column(db.Integer, db.ForeignKey('tb_livro.liv_id'), nullable=False)
    eml_quantidade = db.Column(db.Integer, nullable=False)
    eml_preco = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<EmprestimoLivro {self.eml_id}>'