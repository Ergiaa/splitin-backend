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
from endpoints.address.resource import AddressResource
from endpoints.products.resource import ProductResource
from endpoints.jastip.resource import JastipResource, JastipListClientResource, JastipCurrentSessionResource, JastipOrderDetailsResource, JastipHistoryResources
from endpoints.anjem.resource import AnjemResource, AnjemOrderResource
from endpoints.order.resource import OrderResource

api.add_resource(PingResource, '/', '/ping')
api.add_resource(AuthResource, '/auth', '/auth/<string:id>')
api.add_resource(UserResource, '/user')
api.add_resource(AddressResource, '/address')
api.add_resource(ProductResource, '/product', '/product/<string:product_id>')
api.add_resource(JastipResource, '/jastip', '/jastip/<string:jsession_id>')
api.add_resource(JastipListClientResource, '/jastip/clients')
api.add_resource(JastipCurrentSessionResource, '/jastip/session', '/jastip/session/<string:session_id>')
api.add_resource(JastipOrderDetailsResource, '/jastip/details/<string:jheader_id>')
api.add_resource(JastipHistoryResources, '/jastip/history', '/jastip/history/<string:session_id>')
api.add_resource(AnjemResource, '/anjem', '/anjem/<string:id>')
api.add_resource(AnjemOrderResource, '/anjem/history', '/anjem/history/<string:id>')
api.add_resource(OrderResource, '/history')

if __name__ == '__main__':
    app.run()