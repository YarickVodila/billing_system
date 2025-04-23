from typing import Literal
from fastapi import HTTPException
from pydantic import BaseModel, model_validator

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    balance: float = 0.0


class UserJWT(BaseModel):
    username: str
    password: str


class DataForPredict(BaseModel):
    person_age: int
    person_income: int
    person_emp_length: float
    loan_intent: Literal['VENTURE', 'MEDICAL', 'EDUCATION', 'DEBTCONSOLIDATION', 'PERSONAL', 'HOMEIMPROVEMENT']
    loan_grade: Literal['A', 'C', 'B', 'D', 'E', 'F', 'G']
    loan_amnt: int
    loan_int_rate: float
    loan_percent_income: float
    cb_person_default_on_file: Literal['N', 'Y']
    cb_person_cred_hist_length: int

    @model_validator(mode='after')
    def validate_all(self):
        
        loan_intent = self.loan_intent
        loan_grade = self.loan_grade
        cb_person_default_on_file = self.cb_person_default_on_file

        if loan_intent not in ['VENTURE', 'MEDICAL', 'EDUCATION', 'DEBTCONSOLIDATION', 'PERSONAL', 'HOMEIMPROVEMENT']:
            raise HTTPException(status_code=422, detail = f"`{loan_intent}` должен быть одним из этих значений {['VENTURE', 'MEDICAL', 'EDUCATION', 'DEBTCONSOLIDATION', 'PERSONAL', 'HOMEIMPROVEMENT']}")
        
        elif loan_grade not in ['A', 'C', 'B', 'D', 'E', 'F', 'G']:
            raise HTTPException(status_code=422, detail = f"`{loan_intent}` должен быть одним из этих значений {['A', 'C', 'B', 'D', 'E', 'F', 'G']}")
        
        elif cb_person_default_on_file not in ['N', 'Y']:
            raise HTTPException(status_code=422, detail = f"`{cb_person_default_on_file}` должен быть одним из этих значений {['N', 'Y']}")

        return self