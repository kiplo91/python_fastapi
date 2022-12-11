from typing import Union

from fastapi  import FastAPI,Depends,Response

from pydantic import BaseModel

from database import  CustomerModel,engine
from sqlmodel import Session,select
from models import Customer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:4200",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_session():
    with Session(engine) as session:
        yield session

@app.get('/customers/')
def customers(session:Session = Depends(get_session)):
    stmt = select(CustomerModel)
    result = session.exec(stmt).all()
    return result

@app.post('/customer/register',response_model=Customer,status_code=201)
def register(customer:CustomerModel,session:Session = Depends(get_session)):
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer

@app.get('/customer/{id}')
def view(id:int,response:Response,session:Session = Depends(get_session)):
    customer = session.get(CustomerModel,id)
    if customer is None:
        response.status_code=404
        return "Customer Not Found"
    return customer

@app.put('/customer/{id}',response_model=Union[Customer,str])
def edit( updated_customer: Customer,id:int,response:Response,session:Session=Depends(get_session)):
    customer = session.get(CustomerModel,id)

    #check if trac exist
    if customer is None:
        response.status_code=404
        return "Customer Not Found"

    #update track data
    customer_dict = updated_customer.dict(exclude_unset=True)
    for key,val in customer_dict.items():
        setattr(customer,key,val)
    
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer
    


@app.delete('/customer/{id}')
def delete(id:int, response:Response,session:Session=Depends(get_session)):
    customer = session.get(CustomerModel,id)

    if customer is None:
        response.status_code=404
        return "Customer Not Found"
    
    session.delete(customer)
    session.commit()
    return Response(status_code=200)