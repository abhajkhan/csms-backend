"""
Business Logic: R001-R002
Auto-calculate site expense when stock moves from Warehouse to Site
"""

from decimal import Decimal
from sqlalchemy.orm import Session
from typing import Optional


class ExpenseCalculator:
    """
    R001: When stock moves Warehouse→Site, auto-calculate expense
    R002: Expense = Item Qty × (Purchase Price / Purchase Qty at that time)
    """
    
    @staticmethod
    def calculate_material_expense(
        quantity: Decimal,
        purchase_total_amount: Decimal,
        purchase_quantity: Decimal
    ) -> Decimal:
        """
        Calculate expense based on purchase unit price at time of stock entry
        
        Args:
            quantity: Amount being moved to site
            purchase_total_amount: Total amount paid for original purchase
            purchase_quantity: Total quantity in original purchase
            
        Returns:
            Calculated expense amount
        """
        if purchase_quantity == 0:
            raise ValueError("Purchase quantity cannot be zero")
        
        unit_price = purchase_total_amount / purchase_quantity
        expense_amount = quantity * unit_price
        
        return expense_amount.quantize(Decimal("0.01"))
    
    @staticmethod
    def create_expense_from_stock_movement(
        db: Session,
        stock_movement_id: int,
        site_id: int
    ) -> Optional[dict]:
        """
        TODO: Implement after models are ready
        - Fetch stock movement
        - Get linked purchase details
        - Calculate expense
        - Create expense record for site
        - Update site account balance
        """
        # Placeholder for implementation
        pass


# R003-R006 will be implemented in respective service files
