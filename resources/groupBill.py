from flask import request
from flask_restful import Resource
from flask import g as ctx
from utils.response import response, abort
from utils.error import CustomError
from middleware.auth import authenticate
from services import BillService

bill_service = BillService()

class GroupBillResource(Resource):
    @authenticate
    def patch(self, bill_id, group_id):
        try:
            data = bill_service.assign_group(bill_id, group_id)
            return response("updated successfully", 200, data=data)
        except CustomError as e:
            return abort(e.message, e.status_code)
        except Exception as e:
            return abort(str(e), 500, error=e)
