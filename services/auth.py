from firebase.config import db
from validators import auth_post_parser
from utils.password import verify_password
from utils.jwt import create_auth_token
from utils.error import CustomError

class AuthService:
    def login(self):
        args = auth_post_parser.parse_args(strict=True)
        email = args['email']

        query = db.collection("users")\
                  .where("email", "==", email)\
                  .limit(1)
        results = query.get()

        if not results:
            raise CustomError(message="user not found", status_code=404)

        doc = results[0]
        user = doc.to_dict()
        user_id = doc.id

        if not verify_password(args['password'], user.get('password')):
            raise CustomError(message="password is incorrect", status_code=401)

        token = create_auth_token(user_id)

        return {
            "token": token,
            "user": {
                "id": user_id,
                "email": user.get('email'),
                "username": user.get('username')
            }
        }

    def me(self, user_id):
        user_ref = db.collection("users").document(user_id)
        doc = user_ref.get()

        if not doc.exists:
            raise CustomError(message="user not found", status_code=404)

        user = doc.to_dict()
        user['id'] = doc.id
        user.pop("password", None)

        return user
