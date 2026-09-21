import os
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt, JWTError

load_dotenv() # read the environment variables stored inside the .env file.

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

# create a password hashing configuration and bcrypt to securely hash password
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# hash a user's password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# check whether a password matches a stored hash
def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password) #returns True or false if the password is correct or incorrect

# create a JWT access token
def create_access_token(data: dict):
    to_encode = data.copy() #copy of the data so that the original is not lost

    # calculate when the time when token should expire.
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # add the expiration time to the token data.
    to_encode.update({
        "exp":expire
    })

    # encode and sign the token using the secret key and selected algorithm. relsuted string returned to frontend
    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

#verify a JWT access token
def verify_access_token(token: str):
    try: 
        payload = jwt.decode(  # decode JWT token using the secret key
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub") # get the user's ID from the "sub" (subject) field

        # if the token does not contain a user ID, token as invalid.
        if user_id is None:
            return None

        return user_id # return the user ID

    # JWTError catches problems
    # return none to show invalid token.
    except JWTError:
        return None
   