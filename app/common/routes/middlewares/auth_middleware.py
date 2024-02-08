from flask import request, jsonify
import jwt
from datetime import datetime, timedelta
from ..config.public_routes import ROUTES_PUBLIC
from dotenv import load_dotenv
import os
load_dotenv()


class AuthMiddleware:
    
    SECRET_KEY = os.getenv("SECRET_KEY")
  

    @classmethod
    def token_generator(self,user_id):
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        token = jwt.encode(payload, self.SECRET_KEY, algorithm='HS256')
        return token

    @classmethod
    def check_token(self):
        current_route = request.path
        if current_route not in ROUTES_PUBLIC:
            token = request.headers.get('Authorization')
            token = token.replace('Bearer ', '')  if token else ''
            if not token:
                return jsonify({'error': 'Token not provided'}), 401

            try:
                payload = jwt.decode(token, self.SECRET_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Expired Token'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid Token'}), 401
            
            request.context = {'user_id': payload['user_id']}

    @classmethod
    def login_token_test(self):
        data = request.get_json()
        if not data.get('username') or not data.get('password'):
               return jsonify({'error': 'Username and Password Required'}), 401
        if data['username'] == 'user_test' and data['password'] == 'password_test':
            user_id = 1  # ID user_example
            token = self.token_generator(user_id)
            return jsonify({'token': token})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401