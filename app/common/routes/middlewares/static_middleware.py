from flask import request, jsonify
from ..config.public_routes import ROUTES_PUBLIC
from dotenv import load_dotenv
import os
load_dotenv()


class StaticMiddleware:
    
    SECRET_KEY = os.getenv("SECRET_KEY")
  
    @classmethod
    def check_static_token(self):
        current_route = request.path
        if current_route not in ROUTES_PUBLIC:
            token = request.headers.get('Authorization')
            token = token.replace('Bearer ', '')  if token else ''
            if not token:
                return jsonify({'error': 'Token not provided'}), 401

            try:
                if token != self.SECRET_KEY:
                    raise ValueError("Invalid Token")
            except Exception:
                return jsonify({'error': 'Invalid Token'}), 401