def response(message: str, status_code: int, data: dict = None, meta: dict = None, error: Exception = None) -> tuple[dict, int]:
    response = {
        'status': True,
        'message': message
    }
    
    if status_code >= 400:
        response['status'] = False
        if error and hasattr(error, 'data') and 'message' in error.data:
            response['error'] = error.data['message']
        elif error:
            response['error'] = str(error)

    if data:
        response['data'] = data
    else:
        response['data'] = None
    
    if meta:
        response['meta'] = meta

    return (response, status_code)

def abort(message: str, status_code: int, error: Exception = None) -> tuple[dict, int]:
    response = {
        'status': False,
        'message': message
    }

    if error and hasattr(error, 'data') and 'message' in error.data:
        response['error'] = error.data['message']
    elif error: 
        response['error'] = str(error)

    return (response, status_code)