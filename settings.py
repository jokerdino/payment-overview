DEBUG = True
PORT = 8080
SECRET_KEY = "secret"
WTF_CSRF_ENABLED = True

PASSWORDS = {
        "admin": "$pbkdf2-sha256$29000$Sam1dm6N0dr7P4fQWouRsg$TZAyEXnS.EouKV36lF1GaXfb.0pZ3J.F4NLAa.fzP54",
        "notadmin": "$pbkdf2-sha256$29000$Sam1dm6N0dr7P4fQWouRsg$TZAyEXnS.EouKV36lF1GaXfb.0pZ3J.F4NLAa.fzP54",
        "super": "$pbkdf2-sha256$29000$Sam1dm6N0dr7P4fQWouRsg$TZAyEXnS.EouKV36lF1GaXfb.0pZ3J.F4NLAa.fzP54"}

ADMIN_USERS = ["admin"]
SUPERADMIN = ["super"]
