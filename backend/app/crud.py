from sqlalchemy.orm import Session
from app import models
from app.auth import hash_password

#find user by username
def get_user_by_username(db: Session, username: str):
    return(
        db.query(models.User)
        .filter(models.User.username == username)
        .first()
    )

#find user by email address
def get_user_by_email(db: Session, email: str):
    return(
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )

#find user by id
def get_user_by_id(db: Session, user_id: int):
    return (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

#create user in the database
def create_user(
        db: Session,
        username: str,
        email: str,
        password: str
):
    hashed_password = hash_password(password) #password is converted to a secure hash

    #create user object
    user = models.User(
        username=username,
        email=email,
        password=hashed_password
    )
    #add user to the database, save changes and refresh the object so it contains generated values
    db.add(user)
    db.commit()
    db.refresh(user)

    return user #return the newly created user
