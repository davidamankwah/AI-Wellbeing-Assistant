from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, get_db
from app import models, schemas, crud
from app.auth import verify_password, create_access_token, verify_access_token

# create the FastAPI application
app = FastAPI(
    title="AI Wellbeing Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer() # HTTPBearer useed for authorization header

# create the database tables
# SQLAlchemy checks the models and creates the tables 
# if they do not already exist.
Base.metadata.create_all(bind=engine) 



# home endpoint
@app.get("/")
def home():
    return{"message":"Welcome to the AI Wellbeing Assistant API!"}

#user registration endpoint
@app.post("/register", response_model=schemas.UserResponse)
def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    existing_username = crud.get_user_by_username( # check whether the username already exists
        db,
        user.username
    )
    # if a user with this username already exists, stop the registration process.
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exist!"
        )
    existing_email = crud.get_user_by_email( # check whether the email already exists
        db,
        user.email
    )
    # if another user already uses this email, stop the registration process.
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )
    # create the new user
    new_user = crud.create_user(
        db=db,
        username=user.username,
        email=user.email,
        password=user.password
    )
    # Return the newly created user, password is not returned.
    return new_user

#user login endpoint
#check user's login details and create access token.
@app.post("/login", response_model=schemas.Token)
def login(
    user: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = crud.get_user_by_username(  #look for user with the provided username
        db,
        user.username
    )

    if not existing_user:  #if username doesn't exist return error
        raise HTTPException(
            status_code=401,
            details="Invalid username or password"
        )
    
    password_correct = verify_password( #look for user with the provided password
        user.password,
        existing_user.password
    )

    if not password_correct:  #if password doesn't exist return error
        raise HTTPException(
            status_code=401,
            details="Invalid username or password"
        )

    access_token = create_access_token( # a successful login creates JWT access token 
        data={
            "sub": str(existing_user.id),
            "username": existing_user.username
        }
    )

    return{  #returns the access token to the frontend.
        "access_token": access_token,
        "token_type": "bearer"
    }

# get the currently authenticated user with a valid JWT access token.
@app.get("/users/me", response_model=schemas.UserResponse)
def get_current_user(
    # FastAPI extracts authorization header and provides credentials to this function.
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db) # get a database session
):
    token = credentials.credentials # extract JWT token from the authorization header.
    user_id = verify_access_token(token) # verify jwt token

    # prevent user from accessing the endpoint when token is expired
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # find user in the database using the ID and extract jwt token
    user = crud.get_user_by_id(
        db,
        int(user_id)
    )

    # if token has a user ID that is not in the database, return an error.
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user # return the authenticated user's information.