# app/main.py
from app import app,blueprint
from app.common.routes.config.routes import Routes
from app.common.routes.middlewares.static_middleware import StaticMiddleware
import sys

@app.before_request
def middleware():
    return StaticMiddleware.check_static_token()

Routes(blueprint)
app.register_blueprint(blueprint)

if __name__ == '__main__':
    port = 5011
    if len(sys.argv) > 1 and (sys.argv[1]=='5011' or sys.argv[1]=='5012' or sys.argv[1]=='5013'):
        port = int(sys.argv[1])
    app.run(debug=True, port=port)