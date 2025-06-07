from flask_restful import Resource, request
from flask import g as ctx
# from app import db

from .validate import login_parser
from endpoints.users.model import User, Client, Customer, UserType    
from utils.response import response, abort
from utils.password import verify_password
from utils.jwt import create_auth_token
from middleware.auth import authenticate

class AuthResource(Resource):
    def post(self):
        try:
            args = login_parser.parse_args(strict=True) 
        except Exception as e:
            return abort("validation failure", 400, e)

        user = User.query.filter_by(email=args['email'], user_type=args['type']).first()
        if not user:
            return abort("login failed", 401)
        if user.user_type == UserType.CLIENT:
            client = Client.query.filter_by(user_id=user.id).first()
            if client.verification_status == False:
                return abort("user not verified", 404)
        
        if not verify_password(args['password'], user.password):
            return abort("login failed", 401)
        
        token = create_auth_token(str(user.id), str(user.user_type.value))
        return response("login success", 200, data={
            "token": token,
        })
    
    @authenticate
    def get(self):
        user = User.query.get(ctx.user_id)
        if not user:
            return abort("user not found", 404)
        
        if ctx.role == UserType.CUSTOMER.value:
            resp = user.json(deep=UserType.CUSTOMER)
        else:
            resp = user.json(deep=UserType.CLIENT)
            
        return response("auth success", 200, data=resp)
    
    def patch(self, id=None):
        if id is None:
            return abort("user id required", 400)
        user = Client.query.filter_by(user_id = id).first()
        if not user:
            return abort("user not found", 404)
        if user.verification_status == True:
            return abort("user already verified", 400)
        
        Client.query.filter_by(user_id=id).update({'verification_status':True})
        db.session.commit()

        return response("verification success", 200)