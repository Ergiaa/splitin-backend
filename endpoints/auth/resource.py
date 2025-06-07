from flask_restful import Resource, request
from flask import g as ctx
from firebase.config import db

from .validate import login_parser
from endpoints.users.model import User
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

        email = args['email']

        # Fetch user by email
        query = db.collection("users")\
                  .where("email", "==", email)\
                  .limit(1)
        results = query.get()

        if not results:
            return abort("login failed", 401)

        doc = results[0]
        user = doc.to_dict()
        user_id = doc.id  # Firebase document ID

        # Verify password (use dictionary key)
        if not verify_password(args['password'], user.get('password')):
            return abort("login failed", 401)

        token = create_auth_token(user_id)

        return response("login success", 200, data={
            "token": token,
            "user": {
                "id": user_id,
                "email": user.get('email'),
                "username": user.get('username')
            }
        })
    
    @authenticate
    def get(self):
        user_ref = db.collection("users").document(ctx.user_id)
        doc = user_ref.get()

        if not doc.exists:
            return abort("user not found", 404)

        user = doc.to_dict()
        user['id'] = doc.id  # Include document ID

        return response("auth success", 200, data=user)

    def patch(self, id=None):
        if not id:
            return abort("user id required", 400)

        user_ref = db.collection("users").document(id)
        doc = user_ref.get()

        if not doc.exists:
            return abort("user not found", 404)

        user = doc.to_dict()

        # Check verification_status
        if user.get('verification_status') is True:
            return abort("user already verified", 400)

        # Update verification_status
        user_ref.update({'verification_status': True})

        return response("verification success", 200)