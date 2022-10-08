from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_passwd(secret):
    h_passwd = pwd_context.hash(secret=secret)
    return h_passwd

def verify_password(plain_passwd, hashed_passwd):
    return pwd_context.verify(secret=plain_passwd, hash=hashed_passwd)