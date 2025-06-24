# resources/__init__.py
from flask_restful import Api

from .ping import PingResource
from .auth import AuthResource
from .bill import BillResource
from .completeBill import CompleteBillResource
from .user import UserResource
from .totalLedger import TotalLedgerResource
from .ledger import LedgerResource
from .homeBill import HomeBillResource
from .itemBill import ItemBillResource
from .draftBill import DraftBillResource
from .group import GroupResource
from .groupBill import GroupBillResource
from .paymentBill import PaymentBillResource
from .finalizeBill import FinalizeBillResource

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
    api.add_resource(HomeBillResource, '/bills/all')
    api.add_resource(ItemBillResource, '/bills/<string:bill_id>/items')
    api.add_resource(DraftBillResource, '/bills/draft', '/bills/<string:bill_id>/draft')
    api.add_resource(GroupResource, '/groups', '/groups/<string:group_id>', '/groups/<string:group_id>/<string:user_id>')
    api.add_resource(GroupBillResource, '/bills/<string:bill_id>/groups/<string:group_id>')
    api.add_resource(PaymentBillResource, '/bills/<string:bill_id>/payments')
    api.add_resource(FinalizeBillResource, '/bills/<string:bill_id>/finalize')
