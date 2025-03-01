from extensoes import db

class Livro(db.Model):
    __tablename__ = 'tb_livro'
    liv_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    liv_titulo = db.Column(db.String(100), nullable=False)
    liv_isbn = db.Column(db.String(30))
    liv_ano = db.Column(db.Integer, nullable=False)
    liv_aut_id = db.Column(db.Integer, db.ForeignKey('tb_autor.aut_id'), nullable=False)
    liv_edi_id = db.Column(db.Integer, db.ForeignKey('tb_editora.edi_id'), nullable=False)
    liv_gen_id = db.Column(db.Integer, db.ForeignKey('tb_genero.gen_id'), nullable=False)
    liv_pais_origem = db.Column(db.String(100), nullable=False)
    liv_estoque = db.Column(db.Integer, nullable=False)
    liv_preco = db.Column(db.Float, nullable=False)
    liv_ger_id = db.Column(db.Integer, db.ForeignKey('tb_gerente.ger_id'), nullable=False)

    autor = db.relationship("Autor", backref="livros")
    editora = db.relationship("Editora", backref="livros")
    genero = db.relationship("Genero", backref="livros")

    def __repr__(self):
        return f'<Livro {self.liv_titulo}>'