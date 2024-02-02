# app/main.py
from flask import Flask
from app.controllers.item_controller import ItemController

app = Flask(__name__)

# Rotas
app.add_url_rule('/items', 'find_many', ItemController.find_many, methods=['GET'])
app.add_url_rule('/items/<string:id>', 'find_by_id', ItemController.find_by_id, methods=['GET'])
app.add_url_rule('/items', 'create', ItemController.create, methods=['POST'])
app.add_url_rule('/items/<string:id>', 'update_by_id', ItemController.update_by_id, methods=['PUT'])
app.add_url_rule('/items/<string:id>', 'delete_by_id', ItemController.delete_by_id, methods=['DELETE'])

if __name__ == '__main__':
    app.run(debug=True)
