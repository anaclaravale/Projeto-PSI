from extensoes import db
from flask_login import UserMixin

class Gerente(db.Model, UserMixin):
    __tablename__ = 'tb_gerente'
    ger_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ger_codigo = db.Column(db.Integer)
    ger_nome = db.Column(db.String(255), nullable=False)
    ger_telefone = db.Column(db.String(15), nullable=False)
    ger_email = db.Column(db.String(100), nullable=False)
    ger_senha = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Gerente {self.ger_nome}>'

    # Método get_id para Flask-Login
    def get_id(self):
        return str(self.ger_id)  # Retorna o ger_id como string
    