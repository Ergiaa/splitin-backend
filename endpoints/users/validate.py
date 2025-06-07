from flask_restful import reqparse
from werkzeug.datastructures import FileStorage 

post_parser = reqparse.RequestParser()
post_parser.add_argument('username', type=str, location=['form'], required=True, help="str `name` is required")
post_parser.add_argument('email', type=str, location=['form'], required=True, help="str `email` is required")
post_parser.add_argument('password', type=str, location=['form'], required=True, help="str `password` is required")

patch_parser = reqparse.RequestParser()
patch_parser.add_argument('name', type=str, location=['form'], required=False, help="str `name` is required")
patch_parser.add_argument('email', type=str, location=['form'], required=False, help="str `email` is required")
patch_parser.add_argument('student_id', type=str, location=['form'], required=False, help="str `student_id` is required")
patch_parser.add_argument('phone_number', type=str, location=['form'], required=False, help="str `phone_number` is required")