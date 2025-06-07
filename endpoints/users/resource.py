from flask_restful import Resource, request
from flask import g as ctx
from uuid import UUID, uuid4
from app import app

from .model import User, Client, Customer, UserType
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
                raise err

            err = validate_phone_number(args['phone_number'])
            if err:
                raise err

            if args['type'] == 'CLIENT':
                if args['ktm'] is None:
                    raise Exception("image `ktm` is required")
                else:
                    ktm = args['ktm']
                    if not allowed_file(ktm.filename):
                        raise Exception("file extension is not allowed")
                if args['bank_account'] is None or args['bank_account'] == "":
                    raise Exception("str `bank_account` is required")
                if args['bank_name'] is None or args['bank_name'] == "":
                    raise Exception("str `bank_name` is required")
                ba = args['bank_account']
                bn = args['bank_name']

                if args['interest'] is None:
                    raise Exception("str `interets` is required")
                else:
                    interest = args['interest']
            
            if args['type'] == 'CUSTOMER':
                if args['interest'] is None:
                    raise Exception("str `interest` is required")
                else:
                    interest = args['interest']
            
            del args['bank_account']
            del args['bank_name']
            del args['interest']
            del args['ktm']
        except Exception as e: 
            return abort("validation failure", 400, e)

        user = User.query.filter_by(email=args['email'], user_type=args['type']).first()
        if user is not None:
            return abort("email already registered", 400, None)

        args['password'] = hash_password(args['password'])
        user = User(**args)
        # db.session.add(user)
        # db.session.commit() # TODO: NOT ATOMIC
        
        resp = user.json()
        userid = resp['id']

        if args['type'] == 'CLIENT':
            path = f"{app.config['UPLOAD_FOLDER'] }/ktm/{ktm.filename}"
            ktm.save(path)
            client = Client(userid, ba, bn, path, interest=interest)
            resp['ktm'] = client.ktm
            # db.session.add(client)
        if args['type'] == 'CUSTOMER':
            customer = Customer(userid, interest)
            # db.session.add(customer)
        # db.session.commit() # TODO: NOT ATOMIC

        return response("created successfully", 201, data=resp)

    @authenticate
    def patch(self):
        current_user = User.query.get(ctx.user_id)
        client_args = {}
        customer_args = {}
        ktm = None

        try:
            args = patch_parser.parse_args()
            
            if (args['email'] is not None or args['email'] != "") and args['email'] != current_user.email:
                err = validate_email(args['email'])
                if err:
                    raise err
                
                user = User.query.filter_by(email=args['email'], user_type=args['type']).first()
                if user is not None:
                    return abort("email already registered", 400, None)
            else:
                del args['email']

            if args['phone_number'] is not None or args['phone_number'] != "":
                err = validate_phone_number(args['phone_number'])
                if err:
                    raise err
            else: 
                del args['phone_number']

            if ctx.role == UserType.CLIENT.value:
                if args['ktm'] is not None:
                    ktm = args['ktm']
                    if not allowed_file(ktm.filename):
                        raise Exception("file extension is not allowed")
                if args['bank_account'] is not None or args['bank_account'] != "":
                    client_args['bank_account'] = args['bank_account']
                if args['bank_name'] is not None or args['bank_name'] != "":
                    client_args['bank_name'] = args['bank_name']
                if args['interest'] is not None:
                    client_args['interest'] = args['interest']
            if ctx.role == UserType.CUSTOMER.value:
                if args['interest'] is not None:
                    customer_args['interest'] = args['interest']
            
            del args['bank_account']
            del args['bank_name']
            del args['interest']
            del args['ktm']
        except Exception as e: 
            return abort("validation failure", 400, e)
        
        # remove blank fields
        args = {k: v for k, v in args.items() if v is not None} 
        User.query.filter_by(id=ctx.user_id).update(args)

        if ctx.role == UserType.CLIENT.value:
            if ktm is not None:
                path = f"{app.config['UPLOAD_FOLDER'] }/ktm/{ctx.user_id}-{ktm.filename}"
                ktm.save(path)
                client_args['ktm'] = path
                client = Client.query.filter_by(user_id=ctx.user_id).update(client_args)
            args.update(client_args)
        elif ctx.role == UserType.CUSTOMER.value:
            customer = Customer.query.filter_by(user_id=ctx.user_id).update(customer_args)
            args.update(customer_args)

        # db.session.commit()
        return response("updated successfully", 201, data=args)