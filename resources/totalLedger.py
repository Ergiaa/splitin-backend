from flask import request
from flask_restful import Resource
from flask import g as ctx
from utils.response import response, abort
from utils.error import CustomError
from middleware.auth import authenticate
from services import LedgerService

ledger_service = LedgerService()

class TotalLedgerResource(Resource):
    @authenticate
    def get(self):
        try:
            data = ledger_service.get_total_ledger(ctx.user_id)
            return response("fetched successfully", 200, data=data)
        except CustomError as e:
            return abort(e.message, e.status_code)
        except Exception as e:
            return abort(str(e), 500, error=e)
