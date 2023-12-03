from flask import Flask
from models import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root@localhost/dbms"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.app = app
db.init_app(app)

with app.app_context():
    db.create_all()

from views import bp
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True, port=8000)