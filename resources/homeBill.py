from flask import request
from flask_restful import Resource
from flask import g as ctx
from utils.response import response, abort
from utils.error import CustomError
from middleware.auth import authenticate
from services import BillService

bill_service = BillService()

class HomeBillResource(Resource):
    @authenticate
    def get(self):
        try:
            data = bill_service.get_all_bill(ctx.user_id)
            return response("created successfully", 201, data=data)
        except CustomError as e:
            return abort(e.message, e.status_code)
        except Exception as e:
            return abort(str(e), 500, error=e)
