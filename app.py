import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Set production key FLASK_SECRET_KEY="my-secret-key"
# Set APP_SETTINGS=config.ProductionConfig in production phase

env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)
db = SQLAlchemy(app)


@app.route("/")
def index():
    secret_key = app.config.get("SECRET_KEY")
    return f"The configured secret key is {secret_key}."


if __name__ == '__main__':
    app.run()