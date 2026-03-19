from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from config import Config

serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

def generate_token(email):
    return serializer.dumps(email, salt="password-reset")

def verify_token(token, expiration=180):  # 3 minutes
    try:
        email = serializer.loads(
            token,
            salt="password-reset",
            max_age=expiration
        )
        return email
    
    except SignatureExpired:
        return "expired"
    except BadSignature:
        return None
