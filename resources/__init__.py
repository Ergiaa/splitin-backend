# resources/__init__.py
from flask_restful import Api

from .ping import PingResource
from .auth import AuthResource
from .bill import BillResource

def init_resources(api: Api):
    """
    Initialize the resources for the Flask RESTful API.

    Args:
        api (Api): The Flask RESTful API instance.
    """
    api.add_resource(PingResource, '/', '/ping')
    api.add_resource(AuthResource, '/auth')
    api.add_resource(BillResource, '/bills', '/bills/<string:bill_id>', '/bills/<string:bill_id>/<string:user_id>')
