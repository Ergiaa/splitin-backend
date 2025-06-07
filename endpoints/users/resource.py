from flask_restful import Resource, request
from flask import g as ctx
from uuid import UUID, uuid4
from app import app

from firebase.config import db
from .model import User
from .validate import post_parser, patch_parser
from utils.validate import *
from utils.response import response, abort
from utils.password import hash_password
from middleware.auth import authenticate

class UserResource(Resource):
    def post(self):
        try:
            args = post_parser.parse_args()
            
            err = validate_email(args['email'])
            if err:
                raise Exception(err)
        
        except Exception as e:
            return abort("validation failure", 400, e)
        
        email = args.get('email')
        username = args.get('username')

        # Check email
        email_query = db.collection("users")\
                        .where("email", "==", email)\
                        .limit(1)
        email_results = email_query.get()
        for doc in email_results:
            if doc.id != ctx.user_id:
                return abort("email already registered", 400, None)

        # Check username
        username_query = db.collection("users")\
                        .where("username", "==", username)\
                        .limit(1)
        username_results = username_query.get()
        if username_results:
            return abort("username already registered", 400, None)

        args['password'] = hash_password(args['password'])
        user = User.create_user(args)

        return response("created successfully", 201, data=user)

    @authenticate
    def patch(self):
        current_user = User(ctx.user_id).get()

        try:
            args = patch_parser.parse_args()
            
            # Assume current_user_data is a dict of current user info

            email = args.get('email')
            username = args.get('username')

            # Check email
            if email and email != current_user.get('email'):
                err = validate_email(email)
                if err:
                    raise Exception(err)

                email_query = db.collection("users")\
                                .where("email", "==", email)\
                                .limit(1)
                email_results = email_query.get()
                for doc in email_results:
                    if doc.id != ctx.user_id:
                        return abort("email already registered", 400, None)
            else:
                args.pop('email', None)  # remove 'email' from args if no change

            # Check username
            if username and username != current_user.get('username'):
                username_query = db.collection("users")\
                                .where("username", "==", username)\
                                .limit(1)
                username_results = username_query.get()
                for doc in username_results:
                    # If a document exists and it's not the current user, abort
                    if doc.id != ctx.user_id:
                        return abort("username already registered", 400, None)
            else:
                args.pop('username', None)  # remove 'username' from args if no change


            if args.get('phone_number') and args['phone_number'] != current_user.get('phone_number'):
                err = validate_phone_number(args['phone_number'])
                if err:
                    raise Exception(err)
            else:
                args.pop('phone_number', None)

        except Exception as e:
            return abort("validation failure", 400, e)
        
        # remove blank fields
        args = {k: v for k, v in args.items() if v is not None} 
        User(ctx.user_id).update(args)
        user = User(ctx.user_id).get()

        return response("updated successfully", 201, data=user)