from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_restful import Api
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import settings

# ===================
# FLASK APP
# ===================
app = Flask(__name__)
CORS(app, origins=settings.CORS_ORIGINS)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['BUNDLE_ERRORS'] = settings.BUNDLE_ERRORS
app.config['UPLOAD_FOLDER'] = settings.STATIC_DIRECTORY

# ===================
# Error Handling
# ===================
from utils.response import abort
@app.errorhandler(Exception)
def handle_error(e):
    return abort("internal server error", 500, e)

# ===================
# Extension & ORM
# ===================
from common.base import Base
db = SQLAlchemy(app, model_class=Base)
api = Api(app)
api.prefix = '/api'

# ===================
# Static Routes
# ===================
@app.route('/static/<path:path>', methods=['GET'])
def send_file(path):
    return send_from_directory('static', path)

# ===================
# API Endpoint Routes
# ===================
from endpoints.ping.resource import PingResource
from endpoints.auth.resource import AuthResource
from endpoints.users.resource import UserResource

api.add_resource(PingResource, '/', '/ping')
api.add_resource(AuthResource, '/auth', '/auth/<string:id>')
api.add_resource(UserResource, '/user')

if __name__ == '__main__':
    app.run()