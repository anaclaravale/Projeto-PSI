from extensoes import db

class Genero(db.Model):
    __tablename__ = 'tb_genero'
    gen_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gen_nome = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f'<Genero {self.gen_nome}>'