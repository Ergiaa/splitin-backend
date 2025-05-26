ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def validate_email(email: str) -> Exception:
    if '@' not in email:
        return Exception('email must contain `@`')

    part = email.split('@')
    if len(part) <= 1:
        return Exception('email must contain domain')
    
    if '.' not in part[1]:
        return Exception('email domain must contain `.`')

    return None

def validate_phone_number(phone_number: str) -> Exception:
    # https://id.wikipedia.org/wiki/Nomor_telepon_di_Indonesia
    if len(phone_number) < 10 or len(phone_number) > 13:
        return Exception('phone number must be between 10 and 13 characters')
    
    for c in phone_number:
        if c == '+':
            return Exception('phone number format must be: 08xxxxxxxxxx')
        if '0' < c > '9':
            return Exception('phone number must be numeric')

    return None

def allowed_file(filename) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS