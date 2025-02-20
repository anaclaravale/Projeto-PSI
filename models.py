from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String, Float, DateTime
from sqlalchemy.orm import relationship
from typing import List
from datetime import datetime
from flask_login import UserMixin  # Importe UserMixin

db = SQLAlchemy()

# Tabela de Gerentes
class Gerente(db.Model):
    __tablename__ = 'tb_gerente'
    ger_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ger_codigo = db.Column(db.Integer)
    ger_nome = db.Column(db.String(255), nullable=False)
    ger_telefone = db.Column(db.String(15), nullable=False)
    ger_email = db.Column(db.String(100), nullable=False)
    ger_senha = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Gerente {self.ger_nome}>'

# Tabela de Clientes
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
        return str(self.cli_id)

# Tabela de Endereços
class Endereco(db.Model):
    __tablename__ = 'tb_endereco'
    end_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    end_cli_id = db.Column(db.Integer, db.ForeignKey('tb_cliente.cli_id'), nullable=False)
    end_estado = db.Column(db.String(2), nullable=False)
    end_cidade = db.Column(db.String(100), nullable=False)
    end_bairro = db.Column(db.String(100), nullable=False)
    end_rua = db.Column(db.String(100), nullable=False)
    end_numero = db.Column(db.String(10), nullable=False)

    cliente = db.relationship('Cliente', back_populates='enderecos')

    def __repr__(self):
        return f'<Endereco {self.end_id}>'

# Tabela de Autores
class Autor(db.Model):
    __tablename__ = 'tb_autor'
    aut_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aut_nome = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f'<Autor {self.aut_nome}>'

# Tabela de Editoras
class Editora(db.Model):
    __tablename__ = 'tb_editora'
    edi_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    edi_nome = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f'<Editora {self.edi_nome}>'

# Tabela de Gêneros
class Genero(db.Model):
    __tablename__ = 'tb_genero'
    gen_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gen_nome = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f'<Genero {self.gen_nome}>'

# Tabela de Livros
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

    def __repr__(self):
        return f'<Livro {self.liv_titulo}>'

# Tabela de Empréstimos
class Emprestimo(db.Model):
    __tablename__ = 'tb_emprestimo'
    emp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    emp_cli_id = db.Column(db.Integer, db.ForeignKey('tb_cliente.cli_id'), nullable=False)
    emp_data_ini = db.Column(db.DateTime, nullable=False)
    emp_dev = db.Column(db.DateTime, nullable=False)
    emp_total = db.Column(db.Float, nullable=False)
    emp_status = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return f'<Emprestimo {self.emp_id}>'

# Tabela de Empréstimos-Livros
class EmprestimoLivro(db.Model):
    __tablename__ = 'tb_emprestimo_livro'
    eml_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    eml_emp_id = db.Column(db.Integer, db.ForeignKey('tb_emprestimo.emp_id'), nullable=False)
    eml_liv_id = db.Column(db.Integer, db.ForeignKey('tb_livro.liv_id'), nullable=False)
    eml_quantidade = db.Column(db.Integer, nullable=False)
    eml_preco = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<EmprestimoLivro {self.eml_id}>'