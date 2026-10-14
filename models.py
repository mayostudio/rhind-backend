from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from database import Base

class Creditor(Base):
    __tablename__ = "creditors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)

class Debt(Base):
    __tablename__ = "debts"
    id = Column(Integer, primary_key=True, index=True)
    creditor_id = Column(Integer)
    amount = Column(Float)
    reason = Column(String)
    borrowed_date = Column(String)
    payment_method = Column(String)
    priority = Column(String, default="حرجة")

class Installment(Base):
    __tablename__ = "installments"
    id = Column(Integer, primary_key=True, index=True)
    debt_id = Column(Integer)
    amount = Column(Float)
    due_date = Column(String)
    is_paid = Column(Boolean, default=False)

class DailyRecord(Base):
    __tablename__ = "daily_records"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    expected_income = Column(Float)
    actual_income = Column(Float)
    hours_worked = Column(Float)
    source = Column(String)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, default="")
    allocated_time = Column(String, default="")
    deadline = Column(String, default="")
    start_time = Column(String, default="")
    end_time = Column(String, default="")
    project_manager = Column(String, default="")
    company = Column(String, default="")
    customer = Column(String, default="")
    financial_cost = Column(Float)
    daily_hours_needed = Column(Float)
    days_to_profit = Column(Integer)
    status = Column(String)

class ProjectRequirement(Base):
    __tablename__ = "project_requirements"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer)
    name = Column(String)
    category = Column(String)
    is_available = Column(Boolean)
    cost = Column(Float)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, default="")
    assignees = Column(String, default="")
    customer = Column(String, default="")
    deadline = Column(String, default="")
    allocated_time = Column(String, default="")
    start_time = Column(String, default="")
    end_time = Column(String, default="")
    recurrence = Column(String, default="لا يوجد")
    is_completed = Column(Boolean, default=False)
    project_id = Column(Integer, nullable=True)
    parent_id = Column(Integer, nullable=True)

class Target(Base):
    __tablename__ = "targets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    target_amount = Column(Float)
    current_amount = Column(Float, default=0.0)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    trans_type = Column(String)
    reason = Column(String)
    date = Column(String)