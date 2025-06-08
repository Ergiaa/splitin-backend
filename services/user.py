from firebase.config import db
from flask import g as ctx
from models import User
from validators import user_post_parser, user_patch_parser
from utils.validate import validate_email, validate_phone_number
from utils.password import hash_password
from utils.error import CustomError

class UserService:
    def create_user(self):
        args = user_post_parser.parse_args()

        err = validate_email(args['email'])
        if err:
            raise CustomError(err, 400)

        email = args.get('email')
        username = args.get('username')

        # Check for existing email
        if db.collection("users").where("email", "==", email).limit(1).get():
            raise CustomError("email already registered", 400)

        # Check for existing username
        if db.collection("users").where("username", "==", username).limit(1).get():
            raise CustomError("username already registered", 400)

        args['password'] = hash_password(args['password']).decode("utf-8")
        user = User.create_user(args)
        user.pop("password", None)

        return user

    def update_user(self):
        current_user = User(ctx.user_id).get()
        if not current_user:
            raise CustomError("user not found", 404)

        args = user_patch_parser.parse_args()

        email = args.get('email')
        username = args.get('username')

        # Email validation and uniqueness check
        if email and email != current_user.get('email'):
            err = validate_email(email)
            if err:
                raise CustomError(err, 400)

            email_results = db.collection("users").where("email", "==", email).limit(1).get()
            for doc in email_results:
                if doc.id != ctx.user_id:
                    raise CustomError("email already registered", 400)
        else:
            args.pop('email', None)

        # Username validation and uniqueness check
        if username and username != current_user.get('username'):
            username_results = db.collection("users").where("username", "==", username).limit(1).get()
            for doc in username_results:
                if doc.id != ctx.user_id:
                    raise CustomError("username already registered", 400)
        else:
            args.pop('username', None)

        # Phone number validation
        phone_number = args.get('phone_number')
        if phone_number and phone_number != current_user.get('phone_number'):
            err = validate_phone_number(phone_number)
            if err:
                raise CustomError(err, 400)
        
        # Update user data
        user = User(ctx.user_id)
        user.update(args)

        updated_user = user.get()
        updated_user.pop("password", None)  # Remove password from response

        return updated_user
