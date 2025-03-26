import hashlib

from tables import *
from sql import *

def hash_password(password: str, salt: int = None):
    password = f"{password}{salt}"
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_email(email: str, session) -> MainUser | None:
    return session.query(MainUser).filter(MainUser.email == email).first()

def validate_password(password: str, hash: str, salt: int) -> bool:
    hashed_pass = hash_password(password, salt)
    if hash == hashed_pass:
        return True

    return False

def add_user_to_email_list(email: EmailTable, session: SessionDep):
    db_user = EmailList.model_validate(email)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user