
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class Customer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    LIMIT_BAL: int = Field(gt=0)
    SEX: Literal[1, 2]
    EDUCATION: Literal[0, 1, 2, 3, 4, 5, 6]
    MARRIAGE: Literal[0, 1, 2, 3]
    AGE: int = Field(ge=18, le=100)

    PAY_0: int = Field(ge=-2, le=8)
    PAY_2: int = Field(ge=-2, le=8)
    PAY_3: int = Field(ge=-2, le=8)
    PAY_4: int = Field(ge=-2, le=8)
    PAY_5: int = Field(ge=-2, le=8)
    PAY_6: int = Field(ge=-2, le=8)

    BILL_AMT1: int
    BILL_AMT2: int
    BILL_AMT3: int
    BILL_AMT4: int
    BILL_AMT5: int
    BILL_AMT6: int

    PAY_AMT1: int = Field(ge=0)
    PAY_AMT2: int = Field(ge=0)
    PAY_AMT3: int = Field(ge=0)
    PAY_AMT4: int = Field(ge=0)
    PAY_AMT5: int = Field(ge=0)
    PAY_AMT6: int = Field(ge=0)
