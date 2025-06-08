# resources/__init__.py
from flask_restful import Api

from .ping import PingResource
from .auth import AuthResource
from .bill import BillResource
from .completeBill import CompleteBillResource
from .user import UserResource
from .totalLedger import TotalLedgerResource
from .ledger import LedgerResource

def init_resources(api: Api):
    """
    Initialize the resources for the Flask RESTful API.

    Args:
        api (Api): The Flask RESTful API instance.
    """
    api.add_resource(PingResource, '/', '/ping')
    api.add_resource(AuthResource, '/auth')
    api.add_resource(UserResource, '/user')
    api.add_resource(BillResource, '/bills', '/bills/<string:bill_id>', '/bills/<string:bill_id>/<string:user_id>')
    api.add_resource(CompleteBillResource, '/bills/complete')
    api.add_resource(TotalLedgerResource, '/ledgers/total')
    api.add_resource(LedgerResource,'/ledgers', '/ledgers/<string:ledger_id>')
