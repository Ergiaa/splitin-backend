from flask import request
from flask_restful import Resource
from flask import g as ctx
from utils.response import response, abort
from utils.error import CustomError
from middleware.auth import authenticate
from services import LedgerService

ledger_service = LedgerService()

class LedgerResource(Resource):
    @authenticate
    def get(self):
        try:
            data = ledger_service.get_all_ledger(ctx.user_id)
            return response("fetched successfully", 200, data=data)
        except CustomError as e:
            return abort(e.message, e.status_code)
        except Exception as e:
            return abort(str(e), 500, error=e)

    def patch(self, ledger_id):
        try:
            data = ledger_service.settle_debt(ledger_id=ledger_id, user_id=ctx.user_id)
            return response("settled successfully", 200, data=data)
        except CustomError as e:
            return abort(e.message, e.status_code)
        except Exception as e:
            return abort(str(e), 500, error=e)