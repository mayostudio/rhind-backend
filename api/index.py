from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import calendar

# ==================== Database Setup ====================
# لاحظ التعديل هنا: ضفنا pg8000 للرابط عشان Vercel يقبله
SQLALCHEMY_DATABASE_URL = "postgresql+pg8000://postgres.oytlfzujnqjhmqglgznw:RjftfPJHtWeRjulS@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
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
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class CreditorCreate(BaseModel): name: str; phone: str
class InstallmentCreate(BaseModel): amount: float; due_date: str
class DebtCreate(BaseModel): creditor_id: int; amount: float; reason: str; borrowed_date: str; payment_method: str; priority: str = "High"; installments: List[InstallmentCreate] = []
class DebtUpdate(BaseModel): amount: float; reason: str; priority: str
class DailyRecordCreate(BaseModel): date: str; start_time: str; end_time: str; expected_income: float; actual_income: float; hours_worked: float; source: str
class DailyRecordUpdate(BaseModel): actual_income: float
class RequirementCreate(BaseModel): name: str; is_available: bool; cost: float
class ProjectCreate(BaseModel):
    name: str; description: str = ""; allocated_time: str = ""; deadline: str = ""; start_time: str = ""; end_time: str = ""; project_manager: str = ""; company: str = ""; customer: str = ""; financial_cost: float; daily_hours_needed: float; days_to_profit: int; requirements: List[RequirementCreate] = []
class ProjectUpdate(BaseModel):
    name: str; description: str = ""; allocated_time: str = ""; deadline: str = ""; start_time: str = ""; end_time: str = ""; project_manager: str = ""; company: str = ""; customer: str = ""; financial_cost: float; daily_hours_needed: float; days_to_profit: int
class TaskCreate(BaseModel):
    title: str; description: str = ""; assignees: str = ""; customer: str = ""; deadline: str = ""; allocated_time: str = ""; start_time: str = ""; end_time: str = ""; recurrence: str = "None"; project_id: Optional[int] = None; parent_id: Optional[int] = None
class TaskUpdate(BaseModel):
    title: str; description: str = ""; assignees: str = ""; customer: str = ""; deadline: str = ""; allocated_time: str = ""; start_time: str = ""; end_time: str = ""; recurrence: str = "None"
class TargetCreate(BaseModel): title: str; target_amount: float
class TargetAddProgress(BaseModel): amount: float
class TransactionCreate(BaseModel): amount: float; trans_type: str; reason: str; date: str
class TransactionUpdate(BaseModel): amount: float; trans_type: str; reason: str; date: str

# ==================== Endpoints ====================
@app.get("/")
def read_root(): return {"status": "Rhind ERP Backend is Live!"}

@app.get("/transactions/")
def get_transactions(db: Session = Depends(get_db)): return db.query(Transaction).order_by(Transaction.id.desc()).all()
@app.post("/transactions/")
def create_transaction(trans: TransactionCreate, db: Session = Depends(get_db)): db.add(Transaction(**trans.dict())); db.commit(); return {"message": "Saved"}
@app.put("/transactions/{trans_id}")
def update_transaction(trans_id: int, t_update: TransactionUpdate, db: Session = Depends(get_db)):
    t = db.query(Transaction).filter(Transaction.id == trans_id).first()
    if t: t.amount = t_update.amount; t.trans_type = t_update.trans_type; t.reason = t_update.reason; t.date = t_update.date; db.commit(); return {"message": "Updated"}
    return {"error": "Not found"}
@app.delete("/transactions/{trans_id}")
def delete_transaction(trans_id: int, db: Session = Depends(get_db)):
    t = db.query(Transaction).filter(Transaction.id == trans_id).first()
    if t: db.delete(t); db.commit(); return {"message": "Deleted"}
    return {"error": "Not found"}

@app.get("/tasks/")
def get_global_tasks(db: Session = Depends(get_db)): return db.query(Task).filter(Task.project_id == None, Task.parent_id == None).all()
@app.get("/tasks/project/{project_id}")
def get_project_tasks(project_id: int, db: Session = Depends(get_db)): return db.query(Task).filter(Task.project_id == project_id, Task.parent_id == None).all()
@app.get("/tasks/subtasks/{parent_id}")
def get_subtasks(parent_id: int, db: Session = Depends(get_db)): return db.query(Task).filter(Task.parent_id == parent_id).all()

@app.post("/tasks/")
def create_task(task: TaskCreate, db: Session = Depends(get_db)): db.add(Task(**task.dict())); db.commit(); return {"message": "Added"}
@app.put("/tasks/{task_id}")
def update_task(task_id: int, u: TaskUpdate, db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if t:
        t.title = u.title; t.description = u.description; t.assignees = u.assignees
        t.customer = u.customer; t.deadline = u.deadline; t.allocated_time = u.allocated_time
        t.start_time = u.start_time; t.end_time = u.end_time; t.recurrence = u.recurrence
        db.commit(); return {"message": "Updated"}
    return {"error": "Not found"}
@app.put("/tasks/{task_id}/toggle")
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if t: t.is_completed = not t.is_completed; db.commit(); return {"message": "Toggled"}
    return {"error": "Not found"}
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if t: db.query(Task).filter(Task.parent_id == task_id).delete(); db.delete(t); db.commit(); return {"message": "Deleted"}
    return {"error": "Not found"}

@app.get("/targets/")
def get_targets(period: str = "month", start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    manual_targets = db.query(Target).all()
    today = datetime.now().date()
    if period == "custom" and start_date and end_date: start_d, end_d = datetime.strptime(start_date, "%Y-%m-%d").date(), datetime.strptime(end_date, "%Y-%m-%d").date()
    elif period == "today": start_d = end_d = today
    else: start_d, end_d = today.replace(day=1), today.replace(day=calendar.monthrange(today.year, today.month)[1])
    start_str, end_str = start_d.strftime("%Y-%m-%d"), end_d.strftime("%Y-%m-%d")
    unpaid_insts = db.query(Installment).filter(Installment.is_paid == False).all()
    period_debts = [i for i in unpaid_insts if start_str <= i.due_date <= end_str]
    total_required_period = sum(i.amount for i in period_debts)
    all_records, all_trans, paid_insts = db.query(DailyRecord).all(), db.query(Transaction).all(), db.query(Installment).filter(Installment.is_paid == True).all()
    total_in = sum(r.actual_income for r in all_records) + sum(t.amount for t in all_trans if t.trans_type == 'Income')
    total_out = sum(t.amount for t in all_trans if t.trans_type == 'Expense') + sum(i.amount for i in paid_insts)
    vault_balance = total_in - total_out
    remaining_needed = max(0.0, total_required_period - vault_balance)
    days_left = (end_d - max(today, start_d)).days + 1
    daily_survival_target = remaining_needed if days_left <= 0 else remaining_needed / days_left
    today_actual_income = sum(r.actual_income for r in all_records if r.date == str(today))
    return {"smart_daily_target": round(daily_survival_target, 2), "today_actual_income": round(today_actual_income, 2), "period_required": round(total_required_period, 2), "vault_balance": round(vault_balance, 2), "remaining_needed": round(remaining_needed, 2), "days_left": days_left if days_left > 0 else 0, "manual_targets": manual_targets}

@app.post("/targets/")
def create_target(target: TargetCreate, db: Session = Depends(get_db)): db.add(Target(**target.dict())); db.commit(); return {"message": "Added"}
@app.put("/targets/{t_id}/add")
def add_target_progress(t_id: int, p: TargetAddProgress, db: Session = Depends(get_db)): t = db.query(Target).filter(Target.id == t_id).first(); t.current_amount += p.amount; db.commit(); return {"message": "Updated"}
@app.delete("/targets/{t_id}")
def delete_target(t_id: int, db: Session = Depends(get_db)): t = db.query(Target).filter(Target.id == t_id).first(); db.delete(t); db.commit(); return {"message": "Deleted"}

@app.post("/daily_records/")
def add_daily_record(record: DailyRecordCreate, db: Session = Depends(get_db)): db.add(DailyRecord(**record.dict())); db.commit(); return {"message": "Added"}

@app.post("/projects/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    missing = sum(req.cost for req in project.requirements if not req.is_available)
    status, color = ("Active", "green") if missing == 0 else ("Hold", "orange")
    p_data = project.dict(); p_data.pop('requirements')
    np = Project(**p_data, status=status)
    db.add(np); db.commit(); db.refresh(np)
    for r in project.requirements: db.add(ProjectRequirement(project_id=np.id, **r.dict(), category="General"))
    db.commit(); return {"decision": status, "status_color": color}

@app.put("/projects/{p_id}")
def update_project(p_id: int, u: ProjectUpdate, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == p_id).first()
    if p:
        for r in db.query(DailyRecord).filter(DailyRecord.source == p.name).all(): r.source = u.name
        p.name = u.name; p.description = u.description; p.allocated_time = u.allocated_time; p.deadline = u.deadline
        p.start_time = u.start_time; p.end_time = u.end_time; p.project_manager = u.project_manager; p.company = u.company
        p.customer = u.customer; p.financial_cost = u.financial_cost; p.daily_hours_needed = u.daily_hours_needed; p.days_to_profit = u.days_to_profit
        db.commit(); return {"message": "Updated"}
    return {"error": "Not found"}

@app.get("/projects/list")
def get_projects(db: Session = Depends(get_db)):
    res = []
    for p in db.query(Project).all():
        recs = db.query(DailyRecord).filter(DailyRecord.source == p.name).all()
        res.append({**p.__dict__, "total_income": sum(r.actual_income for r in recs), "total_hours": sum(r.hours_worked for r in recs)})
    return res

@app.delete("/projects/{p_id}")
def delete_project(p_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == p_id).first()
    db.query(ProjectRequirement).filter(ProjectRequirement.project_id == p.id).delete()
    db.query(DailyRecord).filter(DailyRecord.source == p.name).delete()
    db.delete(p); db.commit(); return {"message": "Deleted"}

@app.get("/creditors/list")
def get_creditors(db: Session = Depends(get_db)): return db.query(Creditor).all()