from flask_restful import Resource
from utils.response import response, abort
from utils.error import CustomError
from middleware.auth import authenticate
from services import BillService

bill_service = BillService()

class BillResource(Resource):
    @authenticate
    def post(self):
        try:
          data = bill_service.create_bill()
          return response("created successfully", 201, data=data)
        except CustomError as e:
          return abort(e.message, e.status_code)
        except Exception as e:
          return abort(str(e), 500, error=e)

    @authenticate
    def get(self, bill_id):
        try:
          data = bill_service.get_bill(bill_id)
          return response("bill retrieved successfully", 200, data=data)
        except CustomError as e:
          return abort(e.message, e.status_code)
        except Exception as e:
          return abort(str(e), 500, error=e)

    @authenticate
    def patch(self, bill_id, user_id=None):
        try:
          data = bill_service.join_bill(bill_id, user_id)
          return response("joined bill successfully", 200, data=data)
        except CustomError as e:
          return abort(e.message, e.status_code)
        except Exception as e:
          return abort(str(e), 500, error=e)