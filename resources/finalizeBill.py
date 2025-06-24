from flask import request
from flask_restful import Resource
from flask import g as ctx
from utils.response import response, abort
from utils.error import CustomError
from middleware.auth import authenticate
from services import BillService

bill_service = BillService()

class FinalizeBillResource(Resource):
    @authenticate
    def patch(self, bill_id):
        try:
            args = request.get_json()

            data = bill_service.finalize_bill(bill_id, args)
            return response("finalized successfully", 200, data=data)
        except CustomError as e:
            return abort(e.message, e.status_code)
        except Exception as e:
            return abort(str(e), 500, error=e)
