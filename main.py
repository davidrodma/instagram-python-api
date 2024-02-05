# app/main.py
from flask import Flask
from app.common.routes.routes import Routes

app = Flask(__name__)

Routes(app)

if __name__ == '__main__':
    app.run(debug=True)
