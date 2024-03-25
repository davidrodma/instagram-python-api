# app/main.py
from app import app
from app.common.routes.config.routes import Routes
from app.common.routes.middlewares.static_middleware import StaticMiddleware

@app.before_request
def middleware():
    return StaticMiddleware.check_static_token()

Routes(app)

if __name__ == '__main__':
    app.run(debug=True, port=5011)