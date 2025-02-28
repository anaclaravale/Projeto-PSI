from extensoes import db

class Autor(db.Model):
    __tablename__ = 'tb_autor'
    aut_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aut_nome = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f'<Autor {self.aut_nome}>'