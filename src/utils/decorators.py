from functools import wraps
from flask import session, redirect
from flask import abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "role" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def employer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "employer":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


