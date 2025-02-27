from app import db

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