# app/main.py
from flask import Flask
from app.controllers.item_controller import ItemController

app = Flask(__name__)

# Rotas
app.add_url_rule('/items', 'get_all', ItemController.get_all, methods=['GET'])
app.add_url_rule('/items/<string:id>', 'get', ItemController.get, methods=['GET'])
app.add_url_rule('/items', 'add', ItemController.add, methods=['POST'])
app.add_url_rule('/items/<string:id>', 'update', ItemController.update, methods=['PUT'])
app.add_url_rule('/items/<string:id>', 'delete', ItemController.delete, methods=['DELETE'])

if __name__ == '__main__':
    app.run(debug=True)
