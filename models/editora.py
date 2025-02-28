from extensoes import db

class Editora(db.Model):
    __tablename__ = 'tb_editora'
    edi_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    edi_nome = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f'<Editora {self.edi_nome}>'
