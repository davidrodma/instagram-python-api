# app/main.py
from flask import Flask
from app.modules.item import ItemController
from app.common.routes.route_helper import RouteHelper

class Routes:
    helper = RouteHelper()
    
    def __init__(self,app:Flask):
        self.helper.create_default_routes(app,'items',ItemController)