from app import app
from flask_sqlalchemy import SQLAlchemy
from decouple import config

PASS = config('POSTGRESPASS')
KEY = config('KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{PASS}@localhost/atb'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = KEY

db = SQLAlchemy(app)