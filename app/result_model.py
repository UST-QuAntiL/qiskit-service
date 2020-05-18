from app import db

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.String(120))

    def __repr__(self):
        return 'Result {}'.format(self.result)