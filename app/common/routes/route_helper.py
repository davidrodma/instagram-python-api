# app/main.py
from flask import Flask, request, jsonify
from app.common.controllers.controller import Controller
import jwt

# Chave secreta para assinar o token JWT
SECRET_KEY = 'sua_chave_secreta'

# Lista de rotas públicas
ROTAS_PUBLICAS = ['/login', '/rota_publica']

class RouteHelper:
    def create_default_routes(self,app:Flask,module,controller:Controller):
        app.add_url_rule('/'+module, 'paginate', controller.paginate, methods=['GET'])
        app.add_url_rule('/'+module+'/<string:id>', 'find_by_id', controller.find_by_id, methods=['GET'])
        app.add_url_rule('/'+module+'', 'create', controller.create, methods=['POST'])
        app.add_url_rule('/'+module+'/<string:id>', 'update_by_id', controller.update_by_id, methods=['PUT'])
        app.add_url_rule('/'+module+'', 'delete_many_by_ids', controller.delete_many_by_ids, methods=['DELETE'])
        app.add_url_rule('/'+module+'/status', 'status', controller.status, methods=['PATCH'])


    def verificar_token():
        rota_atual = request.path
        if rota_atual not in ROTAS_PUBLICAS:
            token = request.headers.get('Authorization')
            token = token.replace('Bearer ', '')  if token else ''
            if not token:
                return jsonify({'error': 'Token não fornecido'}), 401

            try:
                # Verificar e decodificar o token JWT
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token expirado'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Token inválido'}), 401

            # Adicione o payload do token à variável de contexto para uso posterior na rota
            request.context = {'user_id': payload['user_id']}