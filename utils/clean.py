from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp  # if you're using Firestore

def clean_datetime(obj):
    if isinstance(obj, datetime):
        return obj.replace(microsecond=0).isoformat() + "Z"
    elif isinstance(obj, list):
        return [clean_datetime(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: clean_datetime(v) for k, v in obj.items()}
    else:
        return obj
