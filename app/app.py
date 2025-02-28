import os
import sys
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from blueprints import register_blueprints
from config import (
    JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRES, APP_SERVER_HOST, APP_SERVER_PORT, 
    SSL_CRT_FILE, SSL_KEY_FILE, BACKEND_ENVIRONMENT, CERT_ABS_PATH1, KEY_ABS_PATH1
)
from hypercorn.asyncio import serve
from hypercorn.config import Config
import asyncio

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWT_ACCESS_TOKEN_EXPIRES

jwt = JWTManager(app)

register_blueprints(app)
app.config['DEBUG'] = BACKEND_ENVIRONMENT != "Production"
