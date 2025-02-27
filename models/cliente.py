from app import db
from flask_login import UserMixin

class Cliente(db.Model, UserMixin):
    __tablename__ = 'tb_cliente'
    cli_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cli_nome = db.Column(db.String(40), nullable=False)
    cli_telefone = db.Column(db.String(15), nullable=False)
    cli_email = db.Column(db.String(100), unique=True, nullable=False)
    cli_senha = db.Column(db.String(100), nullable=False)
    enderecos = db.relationship('Endereco', back_populates='cliente')

    def __repr__(self):
        return f'<Cliente {self.cli_nome}>'

    # Método get_id para Flask-Login
    def get_id(self):
        return str(self.cli_id)  # Retorna o cli_id como string