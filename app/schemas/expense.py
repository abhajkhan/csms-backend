"""Expense Pydantic schemas."""

from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    pass


class ExpenseResponse(BaseModel):
    pass
