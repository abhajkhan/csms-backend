"""Initial schema migration based on CSMS_SPEC.md §6

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('driver_type', sa.String(length=20), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('acc_balance', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('phone')
    )

    # 2. sites
    op.create_table(
        'sites',
        sa.Column('site_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('site_name', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('site_id')
    )

    # 3. site_supervisors
    op.create_table(
        'site_supervisors',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.Column('supervisor_id', sa.Integer(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['site_id'], ['sites.site_id'], ),
        sa.ForeignKeyConstraint(['supervisor_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('site_id', 'supervisor_id', name='uq_site_supervisor')
    )
    op.create_index('ix_site_supervisor_active', 'site_supervisors', ['site_id', 'supervisor_id', 'is_active'], unique=False)

    # 4. workers
    op.create_table(
        'workers',
        sa.Column('worker_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('daily_wage', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('worker_id')
    )

    # 5. attendances (Note: no verification columns per CSMS_SPEC.md §6.5 & §8.2)
    op.create_table(
        'attendances',
        sa.Column('attendance_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('labour_type', sa.String(length=10), nullable=False),
        sa.Column('labour_id', sa.Integer(), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=10), server_default='present', nullable=False),
        sa.ForeignKeyConstraint(['site_id'], ['sites.site_id'], ),
        sa.PrimaryKeyConstraint('attendance_id'),
        sa.UniqueConstraint('labour_type', 'labour_id', 'site_id', 'date', name='uq_attendance_unique')
    )
    op.create_index('ix_attendance_date', 'attendances', ['date'], unique=False)
    op.create_index('ix_attendance_labour', 'attendances', ['labour_type', 'labour_id'], unique=False)

    # 6. supervisor_balance_logs
    op.create_table(
        'supervisor_balance_logs',
        sa.Column('log_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('supervisor_id', sa.Integer(), nullable=False),
        sa.Column('txn_type', sa.String(length=10), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('note', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['supervisor_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index('ix_balance_log_supervisor', 'supervisor_balance_logs', ['supervisor_id'], unique=False)

    # 7. worker_payments
    op.create_table(
        'worker_payments',
        sa.Column('payment_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('worker_id', sa.Integer(), nullable=False),
        sa.Column('paid_by', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('payment_type', sa.String(length=15), nullable=False),
        sa.Column('paid_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('note', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['paid_by'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['worker_id'], ['workers.worker_id'], ),
        sa.PrimaryKeyConstraint('payment_id')
    )
    op.create_index('ix_worker_payment_paid_at', 'worker_payments', ['paid_at'], unique=False)
    op.create_index('ix_worker_payment_worker', 'worker_payments', ['worker_id'], unique=False)

    # 8. expenses
    op.create_table(
        'expenses',
        sa.Column('expense_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.Column('recorded_by', sa.Integer(), nullable=False),
        sa.Column('expense_type', sa.String(length=25), nullable=False),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('reference_type', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['recorded_by'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['site_id'], ['sites.site_id'], ),
        sa.PrimaryKeyConstraint('expense_id')
    )
    op.create_index('ix_expense_recorded_by', 'expenses', ['recorded_by'], unique=False)
    op.create_index('ix_expense_site_date', 'expenses', ['site_id', 'date'], unique=False)
    op.create_index('ix_expense_type', 'expenses', ['expense_type'], unique=False)

    # 9. ajax_driver_logs
    op.create_table(
        'ajax_driver_logs',
        sa.Column('log_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('driver_id', sa.Integer(), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('num_mixes', sa.Integer(), nullable=False),
        sa.Column('rate_per_mix', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('expense_id', sa.Integer(), nullable=True),
        sa.Column('note', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['driver_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['expense_id'], ['expenses.expense_id'], ),
        sa.ForeignKeyConstraint(['site_id'], ['sites.site_id'], ),
        sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index('ix_ajax_log_driver_date', 'ajax_driver_logs', ['driver_id', 'date'], unique=False)

    # 10. hitachi_driver_logs
    op.create_table(
        'hitachi_driver_logs',
        sa.Column('log_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('driver_id', sa.Integer(), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('hours_worked', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('hourly_rate', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('expense_id', sa.Integer(), nullable=True),
        sa.Column('note', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['driver_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['expense_id'], ['expenses.expense_id'], ),
        sa.ForeignKeyConstraint(['site_id'], ['sites.site_id'], ),
        sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index('ix_hitachi_log_driver_date', 'hitachi_driver_logs', ['driver_id', 'date'], unique=False)

    # 11. warehouses
    op.create_table(
        'warehouses',
        sa.Column('warehouse_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('warehouse_id')
    )

    # 12. warehouse_items
    op.create_table(
        'warehouse_items',
        sa.Column('item_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=20), nullable=False, comment='ItemCategory enum value'),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('last_unit_price', sa.Numeric(precision=12, scale=2), nullable=True, comment='Updated on each purchase IN'),
        sa.PrimaryKeyConstraint('item_id')
    )

    # 13. warehouse_stocks
    op.create_table(
        'warehouse_stocks',
        sa.Column('stock_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['warehouse_items.item_id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.warehouse_id'], ),
        sa.PrimaryKeyConstraint('stock_id'),
        sa.UniqueConstraint('warehouse_id', 'item_id', name='uq_warehouse_stock_item')
    )
    op.create_index('ix_warehouse_stock_wh_item', 'warehouse_stocks', ['warehouse_id', 'item_id'], unique=False)

    # 14. stock_movements
    op.create_table(
        'stock_movements',
        sa.Column('movement_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('movement_type', sa.String(length=5), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('movement_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=True),
        sa.Column('reference', sa.String(length=255), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['item_id'], ['warehouse_items.item_id'], ),
        sa.ForeignKeyConstraint(['site_id'], ['sites.site_id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.warehouse_id'], ),
        sa.PrimaryKeyConstraint('movement_id')
    )
    op.create_index('ix_stock_movement_date', 'stock_movements', ['movement_date'], unique=False)
    op.create_index('ix_stock_movement_warehouse', 'stock_movements', ['warehouse_id'], unique=False)

    # 15. purchases
    op.create_table(
        'purchases',
        sa.Column('purchase_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('purchased_by', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=True, comment="NULL when destination_type='warehouse'"),
        sa.Column('warehouse_id', sa.Integer(), nullable=True, comment="NULL when destination_type='site'"),
        sa.Column('destination_type', sa.String(length=15), nullable=False, comment='DestinationType enum: site | warehouse'),
        sa.Column('quantity', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('purchased_from', sa.String(length=255), nullable=True),
        sa.Column('vehicle_type', sa.String(length=10), nullable=False, comment='VehicleType enum: own | outer | none'),
        sa.Column('vehicle_rent', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('purchase_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['warehouse_items.item_id'], ),
        sa.ForeignKeyConstraint(['purchased_by'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['site_id'], ['sites.site_id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.warehouse_id'], ),
        sa.PrimaryKeyConstraint('purchase_id')
    )
    op.create_index('ix_purchase_date', 'purchases', ['purchase_date'], unique=False)
    op.create_index('ix_purchase_driver', 'purchases', ['purchased_by'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_purchase_driver', table_name='purchases')
    op.drop_index('ix_purchase_date', table_name='purchases')
    op.drop_table('purchases')
    op.drop_index('ix_stock_movement_warehouse', table_name='stock_movements')
    op.drop_index('ix_stock_movement_date', table_name='stock_movements')
    op.drop_table('stock_movements')
    op.drop_index('ix_warehouse_stock_wh_item', table_name='warehouse_stocks')
    op.drop_table('warehouse_stocks')
    op.drop_table('warehouse_items')
    op.drop_table('warehouses')
    op.drop_index('ix_hitachi_log_driver_date', table_name='hitachi_driver_logs')
    op.drop_table('hitachi_driver_logs')
    op.drop_index('ix_ajax_log_driver_date', table_name='ajax_driver_logs')
    op.drop_table('ajax_driver_logs')
    op.drop_index('ix_expense_type', table_name='expenses')
    op.drop_index('ix_expense_site_date', table_name='expenses')
    op.drop_index('ix_expense_recorded_by', table_name='expenses')
    op.drop_table('expenses')
    op.drop_index('ix_worker_payment_worker', table_name='worker_payments')
    op.drop_index('ix_worker_payment_paid_at', table_name='worker_payments')
    op.drop_table('worker_payments')
    op.drop_index('ix_balance_log_supervisor', table_name='supervisor_balance_logs')
    op.drop_table('supervisor_balance_logs')
    op.drop_index('ix_attendance_labour', table_name='attendances')
    op.drop_index('ix_attendance_date', table_name='attendances')
    op.drop_table('attendances')
    op.drop_table('workers')
    op.drop_index('ix_site_supervisor_active', table_name='site_supervisors')
    op.drop_table('site_supervisors')
    op.drop_table('sites')
    op.drop_table('users')
