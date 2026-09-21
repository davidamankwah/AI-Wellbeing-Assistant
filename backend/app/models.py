from sqlalchemy import Column, Integer, String 
from app.database import Base

# user database model
class User(Base):
    __tablename__ = "users" # name of the table that will be created in the database

    id = Column(Integer, primary_key=True, index=True) # ID for each user
    username = Column(String, unique=True, index=True, nullable=False) # unique username and cannot be empty
    email = Column(String, unique=True, index=True, nullable=False) #unique email and cannot be empty
    password = Column(String, nullable=False) # stores the HASHED password, not the actual password