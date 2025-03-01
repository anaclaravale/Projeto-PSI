from extensoes import db

class Emprestimo(db.Model):
    __tablename__ = 'tb_emprestimo'
    emp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    emp_cli_id = db.Column(db.Integer, db.ForeignKey('tb_cliente.cli_id'), nullable=False)
    emp_data_ini = db.Column(db.DateTime, nullable=False)
    emp_dev = db.Column(db.DateTime, nullable=False)
    emp_total = db.Column(db.Float, nullable=False)
    emp_status = db.Column(db.String(15), nullable=False)

    cliente = db.relationship('Cliente', backref='emprestimos')

    def __repr__(self):
        return f'<Emprestimo {self.emp_id}>'