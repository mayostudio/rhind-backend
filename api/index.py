import os
import calendar
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import NullPool

# ==================== Database Setup ====================
# The URL is read from the DATABASE_URL environment variable (set it in Vercel).
# Format: postgresql+pg8000://USER:PASSWORD@HOST:6543/postgres
SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=NullPool,          # required for serverless + Supabase pooler
    connect_args={"timeout": 10},  # fail after 10s instead of hanging forever
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ==================== Models ====================
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
    priority = Column(String, default="High")


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
    recurrence = Column(String, default="None")
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


# ==================== FastAPI Setup ====================
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== Schemas ====================
class CreditorCreate(BaseModel):
    name: str
    phone: str = ""


class InstallmentCreate(BaseModel):
    amount: float
    due_date: str


class DebtCreate(BaseModel):
    creditor_id: int
    amount: float
    reason: str = ""
    borrowed_date: str
    payment_method: str = ""
    priority: str = "High"
    installments: List[InstallmentCreate] = []


class DebtUpdate(BaseModel):
    amount: float
    reason: str = ""
    priority: str = "High"


class DailyRecordCreate(BaseModel):
    date: str
    start_time: str = ""
    end_time: str = ""
    expected_income: float = 0.0
    actual_income: float = 0.0
    hours_worked: float = 0.0
    source: str = ""


class DailyRecordUpdate(BaseModel):
    actual_income: float


class RequirementCreate(BaseModel):
    name: str
    is_available: bool
    cost: float


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    allocated_time: str = ""
    deadline: str = ""
    start_time: str = ""
    end_time: str = ""
    project_manager: str = ""
    company: str = ""
    customer: str = ""
    financial_cost: float
    daily_hours_needed: float
    days_to_profit: int
    requirements: List[RequirementCreate] = []


class ProjectUpdate(BaseModel):
    name: str
    description: str = ""
    allocated_time: str = ""
    deadline: str = ""
    start_time: str = ""
    end_time: str = ""
    project_manager: str = ""
    company: str = ""
    customer: str = ""
    financial_cost: float
    daily_hours_needed: float
    days_to_profit: int


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    assignees: str = ""
    customer: str = ""
    deadline: str = ""
    allocated_time: str = ""
    start_time: str = ""
    end_time: str = ""
    recurrence: str = "None"
    project_id: Optional[int] = None
    parent_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: str
    description: str = ""
    assignees: str = ""
    customer: str = ""
    deadline: str = ""
    allocated_time: str = ""
    start_time: str = ""
    end_time: str = ""
    recurrence: str = "None"


class TargetCreate(BaseModel):
    title: str
    target_amount: float


class TargetAddProgress(BaseModel):
    amount: float


class TransactionCreate(BaseModel):
    amount: float
    trans_type: str
    reason: str = ""
    date: str


class TransactionUpdate(BaseModel):
    amount: float
    trans_type: str
    reason: str = ""
    date: str


# ==================== Helpers ====================
NOT_FOUND = {"error": "Not found"}


def _sum(db: Session, column, *filters) -> float:
    """SUM of a column done inside the database (NULL-safe)."""
    q = db.query(func.coalesce(func.sum(column), 0.0))
    for f in filters:
        q = q.filter(f)
    return float(q.scalar() or 0.0)


def calc_vault_balance(db: Session) -> float:
    income = _sum(db, DailyRecord.actual_income) + _sum(
        db, Transaction.amount, Transaction.trans_type == "Income"
    )
    outgoing = _sum(db, Transaction.amount, Transaction.trans_type == "Expense") + _sum(
        db, Installment.amount, Installment.is_paid == True  # noqa: E712
    )
    return income - outgoing


# ==================== Root ====================
@app.get("/")
def read_root():
    return {"status": "Rhind ERP Backend is Live!"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Open this in the browser to check the database connection."""
    db.query(func.count(Transaction.id)).scalar()
    return {"status": "ok", "database": "connected"}


# ==================== Transactions ====================
@app.get("/transactions/")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).order_by(Transaction.id.desc()).all()


@app.post("/transactions/")
def create_transaction(trans: TransactionCreate, db: Session = Depends(get_db)):
    db.add(Transaction(**trans.dict()))
    db.commit()
    return {"message": "Saved"}


@app.put("/transactions/{trans_id}")
def update_transaction(trans_id: int, u: TransactionUpdate, db: Session = Depends(get_db)):
    t = db.query(Transaction).filter(Transaction.id == trans_id).first()
    if not t:
        return NOT_FOUND
    t.amount, t.trans_type, t.reason, t.date = u.amount, u.trans_type, u.reason, u.date
    db.commit()
    return {"message": "Updated"}


@app.delete("/transactions/{trans_id}")
def delete_transaction(trans_id: int, db: Session = Depends(get_db)):
    t = db.query(Transaction).filter(Transaction.id == trans_id).first()
    if not t:
        return NOT_FOUND
    db.delete(t)
    db.commit()
    return {"message": "Deleted"}


# ==================== Tasks ====================
@app.get("/tasks/")
def get_global_tasks(db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.project_id == None, Task.parent_id == None).all()  # noqa: E711


@app.get("/tasks/project/{project_id}")
def get_project_tasks(project_id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.project_id == project_id, Task.parent_id == None).all()  # noqa: E711


@app.get("/tasks/subtasks/{parent_id}")
def get_subtasks(parent_id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.parent_id == parent_id).all()


@app.post("/tasks/")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db.add(Task(**task.dict()))
    db.commit()
    return {"message": "Added"}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, u: TaskUpdate, db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        return NOT_FOUND
    t.title = u.title
    t.description = u.description
    t.assignees = u.assignees
    t.customer = u.customer
    t.deadline = u.deadline
    t.allocated_time = u.allocated_time
    t.start_time = u.start_time
    t.end_time = u.end_time
    t.recurrence = u.recurrence
    db.commit()
    return {"message": "Updated"}


@app.put("/tasks/{task_id}/toggle")
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        return NOT_FOUND
    t.is_completed = not t.is_completed
    db.commit()
    return {"message": "Toggled"}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        return NOT_FOUND
    db.query(Task).filter(Task.parent_id == task_id).delete()
    db.delete(t)
    db.commit()
    return {"message": "Deleted"}


# ==================== Targets ====================
EMPTY_TARGETS = {
    "smart_daily_target": 0.0,
    "today_actual_income": 0.0,
    "period_required": 0.0,
    "vault_balance": 0.0,
    "remaining_needed": 0.0,
    "days_left": 0,
    "manual_targets": [],
}


@app.get("/targets/")
def get_targets(
    period: str = "month",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        manual_targets = db.query(Target).all()
        today = datetime.now().date()

        if period == "custom" and start_date and end_date:
            start_d = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_d = datetime.strptime(end_date, "%Y-%m-%d").date()
        elif period == "today":
            start_d = end_d = today
        else:
            start_d = today.replace(day=1)
            end_d = today.replace(day=calendar.monthrange(today.year, today.month)[1])

        start_str, end_str = start_d.strftime("%Y-%m-%d"), end_d.strftime("%Y-%m-%d")

        total_required_period = _sum(
            db,
            Installment.amount,
            Installment.is_paid == False,  # noqa: E712
            Installment.due_date >= start_str,
            Installment.due_date <= end_str,
        )

        vault_balance = calc_vault_balance(db)
        remaining_needed = max(0.0, total_required_period - vault_balance)
        days_left = (end_d - max(today, start_d)).days + 1
        daily_target = remaining_needed if days_left <= 0 else remaining_needed / days_left
        today_income = _sum(db, DailyRecord.actual_income, DailyRecord.date == str(today))

        return {
            "smart_daily_target": round(daily_target, 2),
            "today_actual_income": round(today_income, 2),
            "period_required": round(total_required_period, 2),
            "vault_balance": round(vault_balance, 2),
            "remaining_needed": round(remaining_needed, 2),
            "days_left": days_left if days_left > 0 else 0,
            "manual_targets": manual_targets,
        }
    except Exception as e:
        print("targets error:", repr(e))
        return EMPTY_TARGETS


@app.post("/targets/")
def create_target(target: TargetCreate, db: Session = Depends(get_db)):
    db.add(Target(**target.dict()))
    db.commit()
    return {"message": "Added"}


@app.put("/targets/{t_id}/add")
def add_target_progress(t_id: int, p: TargetAddProgress, db: Session = Depends(get_db)):
    t = db.query(Target).filter(Target.id == t_id).first()
    if not t:
        return NOT_FOUND
    t.current_amount = (t.current_amount or 0.0) + p.amount
    db.commit()
    return {"message": "Updated"}


@app.delete("/targets/{t_id}")
def delete_target(t_id: int, db: Session = Depends(get_db)):
    t = db.query(Target).filter(Target.id == t_id).first()
    if not t:
        return NOT_FOUND
    db.delete(t)
    db.commit()
    return {"message": "Deleted"}


# ==================== Daily records (work shifts) ====================
@app.post("/daily_records/")
def add_daily_record(record: DailyRecordCreate, db: Session = Depends(get_db)):
    db.add(DailyRecord(**record.dict()))
    db.commit()
    return {"message": "Added"}


@app.get("/daily_records/")
def get_daily_records(db: Session = Depends(get_db)):
    return db.query(DailyRecord).order_by(DailyRecord.id.desc()).all()


@app.put("/daily_records/{r_id}")
def update_daily_record(r_id: int, u: DailyRecordUpdate, db: Session = Depends(get_db)):
    r = db.query(DailyRecord).filter(DailyRecord.id == r_id).first()
    if not r:
        return NOT_FOUND
    r.actual_income = u.actual_income
    db.commit()
    return {"message": "Updated"}


@app.delete("/daily_records/{r_id}")
def delete_daily_record(r_id: int, db: Session = Depends(get_db)):
    r = db.query(DailyRecord).filter(DailyRecord.id == r_id).first()
    if not r:
        return NOT_FOUND
    db.delete(r)
    db.commit()
    return {"message": "Deleted"}


# ==================== Projects ====================
@app.post("/projects/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    missing = sum(req.cost for req in project.requirements if not req.is_available)
    status, color = ("Active", "green") if missing == 0 else ("Hold", "orange")
    p_data = project.dict()
    p_data.pop("requirements")
    new_project = Project(**p_data, status=status)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    for r in project.requirements:
        db.add(ProjectRequirement(project_id=new_project.id, category="General", **r.dict()))
    db.commit()
    return {"decision": status, "status_color": color}


@app.put("/projects/{p_id}")
def update_project(p_id: int, u: ProjectUpdate, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == p_id).first()
    if not p:
        return NOT_FOUND
    for r in db.query(DailyRecord).filter(DailyRecord.source == p.name).all():
        r.source = u.name
    p.name = u.name
    p.description = u.description
    p.allocated_time = u.allocated_time
    p.deadline = u.deadline
    p.start_time = u.start_time
    p.end_time = u.end_time
    p.project_manager = u.project_manager
    p.company = u.company
    p.customer = u.customer
    p.financial_cost = u.financial_cost
    p.daily_hours_needed = u.daily_hours_needed
    p.days_to_profit = u.days_to_profit
    db.commit()
    return {"message": "Updated"}


@app.get("/projects/list")
def get_projects(db: Session = Depends(get_db)):
    try:
        # One query for all income/hours totals instead of one query per project
        totals = {
            source: (float(inc or 0.0), float(hrs or 0.0))
            for source, inc, hrs in db.query(
                DailyRecord.source,
                func.sum(DailyRecord.actual_income),
                func.sum(DailyRecord.hours_worked),
            ).group_by(DailyRecord.source)
        }
        result = []
        for p in db.query(Project).all():
            income, hours = totals.get(p.name, (0.0, 0.0))
            result.append({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "allocated_time": p.allocated_time,
                "deadline": p.deadline,
                "start_time": p.start_time,
                "end_time": p.end_time,
                "project_manager": p.project_manager,
                "company": p.company,
                "customer": p.customer,
                "financial_cost": p.financial_cost,
                "daily_hours_needed": p.daily_hours_needed,
                "days_to_profit": p.days_to_profit,
                "status": p.status,
                "total_income": income,
                "total_hours": hours,
            })
        return result
    except Exception as e:
        print("projects error:", repr(e))
        return []


@app.get("/projects/{p_id}/requirements")
def get_project_requirements(p_id: int, db: Session = Depends(get_db)):
    return db.query(ProjectRequirement).filter(ProjectRequirement.project_id == p_id).all()


@app.delete("/projects/{p_id}")
def delete_project(p_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == p_id).first()
    if not p:
        return NOT_FOUND
    db.query(ProjectRequirement).filter(ProjectRequirement.project_id == p.id).delete()
    db.query(DailyRecord).filter(DailyRecord.source == p.name).delete()
    db.delete(p)
    db.commit()
    return {"message": "Deleted"}


# ==================== Dashboard ====================
EMPTY_STATS = {
    "total_projects": 0,
    "total_income": 0.0,
    "total_hours": 0.0,
    "total_debt": 0.0,
    "vault_balance": 0.0,
    "debt_details": [],
}


@app.get("/dashboard/stats")
def get_dashboard_stats(
    period: str = "all",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        vault_balance = calc_vault_balance(db)
        today = datetime.now().date()

        rec_filters = []
        inst_filters = [Installment.is_paid == False]  # noqa: E712

        if period != "all":
            if period == "month":
                start_str = str(today)[:7] + "-01"
                end_str = str(today.replace(day=calendar.monthrange(today.year, today.month)[1]))
            elif period == "custom" and start_date and end_date:
                start_str, end_str = start_date, end_date
            else:
                start_str = end_str = str(today)
            rec_filters += [DailyRecord.date >= start_str, DailyRecord.date <= end_str]
            inst_filters += [Installment.due_date >= start_str, Installment.due_date <= end_str]

        return {
            "total_projects": db.query(func.count(Project.id)).scalar() or 0,
            "total_income": _sum(db, DailyRecord.actual_income, *rec_filters),
            "total_hours": _sum(db, DailyRecord.hours_worked, *rec_filters),
            "total_debt": _sum(db, Installment.amount, *inst_filters),
            "vault_balance": round(vault_balance, 2),
            "debt_details": [],
        }
    except Exception as e:
        print("dashboard error:", repr(e))
        return EMPTY_STATS


# ==================== Creditors & Debts ====================
@app.get("/creditors/list")
def get_creditors(db: Session = Depends(get_db)):
    return db.query(Creditor).all()


@app.post("/creditors/")
def create_creditor(c: CreditorCreate, db: Session = Depends(get_db)):
    db.add(Creditor(**c.dict()))
    db.commit()
    return {"message": "Added"}


@app.delete("/creditors/{c_id}")
def delete_creditor(c_id: int, db: Session = Depends(get_db)):
    c = db.query(Creditor).filter(Creditor.id == c_id).first()
    if not c:
        return NOT_FOUND
    for d in db.query(Debt).filter(Debt.creditor_id == c_id).all():
        db.query(Installment).filter(Installment.debt_id == d.id).delete()
        db.delete(d)
    db.delete(c)
    db.commit()
    return {"message": "Deleted"}


@app.get("/debts/")
def get_debts(db: Session = Depends(get_db)):
    creditors = {c.id: c for c in db.query(Creditor).all()}
    insts_by_debt = {}
    for i in db.query(Installment).order_by(Installment.due_date).all():
        insts_by_debt.setdefault(i.debt_id, []).append(i)

    result = []
    for d in db.query(Debt).order_by(Debt.id.desc()).all():
        c = creditors.get(d.creditor_id)
        insts = insts_by_debt.get(d.id, [])
        paid = sum((i.amount or 0.0) for i in insts if i.is_paid)
        result.append({
            "id": d.id,
            "creditor_id": d.creditor_id,
            "creditor_name": c.name if c else "",
            "creditor_phone": c.phone if c else "",
            "amount": d.amount,
            "reason": d.reason,
            "borrowed_date": d.borrowed_date,
            "payment_method": d.payment_method,
            "priority": d.priority,
            "paid_amount": paid,
            "remaining": (d.amount or 0.0) - paid,
            "installments": [
                {"id": i.id, "amount": i.amount, "due_date": i.due_date, "is_paid": i.is_paid}
                for i in insts
            ],
        })
    return result


@app.post("/debts/")
def create_debt(debt: DebtCreate, db: Session = Depends(get_db)):
    data = debt.dict()
    insts = data.pop("installments")
    new_debt = Debt(**data)
    db.add(new_debt)
    db.commit()
    db.refresh(new_debt)
    for i in insts:
        db.add(Installment(debt_id=new_debt.id, is_paid=False, **i))
    db.commit()
    return {"message": "Added", "id": new_debt.id}


@app.put("/debts/{d_id}")
def update_debt(d_id: int, u: DebtUpdate, db: Session = Depends(get_db)):
    d = db.query(Debt).filter(Debt.id == d_id).first()
    if not d:
        return NOT_FOUND
    d.amount, d.reason, d.priority = u.amount, u.reason, u.priority
    db.commit()
    return {"message": "Updated"}


@app.delete("/debts/{d_id}")
def delete_debt(d_id: int, db: Session = Depends(get_db)):
    d = db.query(Debt).filter(Debt.id == d_id).first()
    if not d:
        return NOT_FOUND
    db.query(Installment).filter(Installment.debt_id == d_id).delete()
    db.delete(d)
    db.commit()
    return {"message": "Deleted"}


@app.put("/installments/{i_id}/pay")
def pay_installment(i_id: int, db: Session = Depends(get_db)):
    i = db.query(Installment).filter(Installment.id == i_id).first()
    if not i:
        return NOT_FOUND
    i.is_paid = True
    db.commit()
    return {"message": "Paid"}


@app.put("/installments/{i_id}/unpay")
def unpay_installment(i_id: int, db: Session = Depends(get_db)):
    i = db.query(Installment).filter(Installment.id == i_id).first()
    if not i:
        return NOT_FOUND
    i.is_paid = False
    db.commit()
    return {"message": "Unpaid"}
