"""
from typing import Optional
Business Logic for Site Account Management
Handles daily balance tracking and expense deductions
"""

from decimal import Decimal
from sqlalchemy.orm import Session


class SiteAccountService:
    """
    Manages site daily accounts:
    - Add amount to site account (supervisor)
    - Deduct expenses from available balance
    - Prevent over-expense (optional rule)
    """
    
    @staticmethod
    def add_daily_balance(
        db: Session,
        site_id: int,
        amount: Decimal,
        date: str,
        added_by: int,
        notes: Optional[str] = None
    ) -> dict:
        """
        Supervisor adds amount to site account for daily expenses
        """
        pass
    
    @staticmethod
    def deduct_expense(
        db: Session,
        site_id: int,
        amount: Decimal,
        expense_type: str,
        description: str
    ) -> dict:
        """
        Deduct expense from site account
        - Check available balance
        - Record expense
        - Update running balance
        
        TODO: Implement after SiteAccount model is ready
        """
        pass
    
    @staticmethod
    def get_available_balance(
        db: Session,
        site_id: int,
        date: str
    ) -> Decimal:
        """
        Get available balance for site on specific date
        """
        pass
