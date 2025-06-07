from flask_restful import Resource
from datetime import datetime

class PingResource(Resource):
    def get(self):
        return {
            'ping': 'pong',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }