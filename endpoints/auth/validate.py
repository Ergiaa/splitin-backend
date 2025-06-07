from flask_restful import reqparse

login_parser = reqparse.RequestParser()
login_parser.add_argument('email', type=str, location=['json', 'form'], required=True, help="`email` is required")
login_parser.add_argument('password', type=str, location=['json', 'form'], required=True, help="`password` is required")
