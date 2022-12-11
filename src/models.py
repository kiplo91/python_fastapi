from pydantic import BaseModel

class Customer(BaseModel):
    id:int
    name:str
    secret_name:str
    age:int