from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import engine, SessionLocal
import models
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import calendar

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# ==================== Pydantic Schemas ====================
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

# ==================== Transactions ====================
@app.get("/transactions/")
def get_transactions(db: Session = Depends(get_db)): return db.query(models.Transaction).order_by(models.Transaction.id.desc()).all()
@app.post("/transactions/")
def create_transaction(trans: TransactionCreate, db: Session = Depends(get_db)): db.add(models.Transaction(**trans.dict())); db.commit(); return {"message": "Saved"}
@app.put("/transactions/{trans_id}")
def update_transaction(trans_id: int, t_update: TransactionUpdate, db: Session = Depends(get_db)):
    t = db.query(models.Transaction).filter(models.Transaction.id == trans_id).first()
    if t: t.amount = t_update.amount; t.trans_type = t_update.trans_type; t.reason = t_update.reason; t.date = t_update.date; db.commit(); return {"message": "Updated"}
    return {"error": "Not found"}
@app.delete("/transactions/{trans_id}")
def delete_transaction(trans_id: int, db: Session = Depends(get_db)):
    t = db.query(models.Transaction).filter(models.Transaction.id == trans_id).first()
    if t: db.delete(t); db.commit(); return {"message": "Deleted"}
    return {"error": "Not found"}

# ==================== Tasks ====================
@app.get("/tasks/")
def get_global_tasks(db: Session = Depends(get_db)): return db.query(models.Task).filter(models.Task.project_id == None, models.Task.parent_id == None).all()
@app.get("/tasks/project/{project_id}")
def get_project_tasks(project_id: int, db: Session = Depends(get_db)): return db.query(models.Task).filter(models.Task.project_id == project_id, models.Task.parent_id == None).all()
@app.get("/tasks/subtasks/{parent_id}")
def get_subtasks(parent_id: int, db: Session = Depends(get_db)): return db.query(models.Task).filter(models.Task.parent_id == parent_id).all()

@app.post("/tasks/")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db.add(models.Task(**task.dict())); db.commit(); return {"message": "Added"}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, u: TaskUpdate, db: Session = Depends(get_db)):
    t = db.query(models.Task).filter(models.Task.id == task_id).first()
    if t:
        t.title = u.title; t.description = u.description; t.assignees = u.assignees
        t.customer = u.customer; t.deadline = u.deadline; t.allocated_time = u.allocated_time
        t.start_time = u.start_time; t.end_time = u.end_time; t.recurrence = u.recurrence
        db.commit(); return {"message": "Updated"}
    return {"error": "Not found"}

@app.put("/tasks/{task_id}/toggle")
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(models.Task).filter(models.Task.id == task_id).first()
    if t: t.is_completed = not t.is_completed; db.commit(); return {"message": "Toggled"}
    return {"error": "Not found"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(models.Task).filter(models.Task.id == task_id).first()
    if t: db.query(models.Task).filter(models.Task.parent_id == task_id).delete(); db.delete(t); db.commit(); return {"message": "Deleted"}
    return {"error": "Not found"}

# ==================== Targets ====================
@app.get("/targets/")
def get_targets(period: str = "month", start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    manual_targets = db.query(models.Target).all()
    today = datetime.now().date()
    if period == "custom" and start_date and end_date: start_d, end_d = datetime.strptime(start_date, "%Y-%m-%d").date(), datetime.strptime(end_date, "%Y-%m-%d").date()
    elif period == "today": start_d = end_d = today
    else: start_d, end_d = today.replace(day=1), today.replace(day=calendar.monthrange(today.year, today.month)[1])
    start_str, end_str = start_d.strftime("%Y-%m-%d"), end_d.strftime("%Y-%m-%d")
    unpaid_insts = db.query(models.Installment).filter(models.Installment.is_paid == False).all()
    period_debts = [i for i in unpaid_insts if start_str <= i.due_date <= end_str]
    total_required_period = sum(i.amount for i in period_debts)
    all_records, all_trans, paid_insts = db.query(models.DailyRecord).all(), db.query(models.Transaction).all(), db.query(models.Installment).filter(models.Installment.is_paid == True).all()
    total_in = sum(r.actual_income for r in all_records) + sum(t.amount for t in all_trans if t.trans_type == 'Income')
    total_out = sum(t.amount for t in all_trans if t.trans_type == 'Expense') + sum(i.amount for i in paid_insts)
    vault_balance = total_in - total_out
    remaining_needed = max(0.0, total_required_period - vault_balance)
    days_left = (end_d - max(today, start_d)).days + 1
    daily_survival_target = remaining_needed if days_left <= 0 else remaining_needed / days_left
    today_actual_income = sum(r.actual_income for r in all_records if r.date == str(today))
    return {"smart_daily_target": round(daily_survival_target, 2), "today_actual_income": round(today_actual_income, 2), "period_required": round(total_required_period, 2), "vault_balance": round(vault_balance, 2), "remaining_needed": round(remaining_needed, 2), "days_left": days_left if days_left > 0 else 0, "manual_targets": manual_targets}

@app.post("/targets/")
def create_target(target: TargetCreate, db: Session = Depends(get_db)): db.add(models.Target(**target.dict())); db.commit(); return {"message": "Added"}
@app.put("/targets/{t_id}/add")
def add_target_progress(t_id: int, p: TargetAddProgress, db: Session = Depends(get_db)): t = db.query(models.Target).filter(models.Target.id == t_id).first(); t.current_amount += p.amount; db.commit(); return {"message": "Updated"}
@app.delete("/targets/{t_id}")
def delete_target(t_id: int, db: Session = Depends(get_db)): t = db.query(models.Target).filter(models.Target.id == t_id).first(); db.delete(t); db.commit(); return {"message": "Deleted"}

# ==================== Projects & Records ====================
@app.post("/daily_records/")
def add_daily_record(record: DailyRecordCreate, db: Session = Depends(get_db)): db.add(models.DailyRecord(**record.dict())); db.commit(); return {"message": "Added"}

@app.post("/projects/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    missing = sum(req.cost for req in project.requirements if not req.is_available)
    status, color = ("Active", "green") if missing == 0 else ("Hold", "orange")
    p_data = project.dict(); p_data.pop('requirements')
    np = models.Project(**p_data, status=status)
    db.add(np); db.commit(); db.refresh(np)
    for r in project.requirements: db.add(models.ProjectRequirement(project_id=np.id, **r.dict(), category="General"))
    db.commit(); return {"decision": status, "status_color": color}

@app.put("/projects/{p_id}")
def update_project(p_id: int, u: ProjectUpdate, db: Session = Depends(get_db)):
    p = db.query(models.Project).filter(models.Project.id == p_id).first()
    if p:
        for r in db.query(models.DailyRecord).filter(models.DailyRecord.source == p.name).all(): r.source = u.name
        p.name = u.name; p.description = u.description; p.allocated_time = u.allocated_time; p.deadline = u.deadline
        p.start_time = u.start_time; p.end_time = u.end_time; p.project_manager = u.project_manager; p.company = u.company
        p.customer = u.customer; p.financial_cost = u.financial_cost; p.daily_hours_needed = u.daily_hours_needed; p.days_to_profit = u.days_to_profit
        db.commit(); return {"message": "Updated"}
    return {"error": "Not found"}

@app.get("/projects/list")
def get_projects(db: Session = Depends(get_db)):
    res = []
    for p in db.query(models.Project).all():
        recs = db.query(models.DailyRecord).filter(models.DailyRecord.source == p.name).all()
        res.append({**p.__dict__, "total_income": sum(r.actual_income for r in recs), "total_hours": sum(r.hours_worked for r in recs)})
    return res

@app.delete("/projects/{p_id}")
def delete_project(p_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Project).filter(models.Project.id == p_id).first()
    db.query(models.ProjectRequirement).filter(models.ProjectRequirement.project_id == p.id).delete()
    db.query(models.DailyRecord).filter(models.DailyRecord.source == p.name).delete()
    db.delete(p); db.commit(); return {"message": "Deleted"}

@app.get("/dashboard/stats")
def get_dashboard_stats(period: str = "all", start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    records, all_trans, paid_insts = db.query(models.DailyRecord).all(), db.query(models.Transaction).all(), db.query(models.Installment).filter(models.Installment.is_paid == True).all()
    vault_balance = (sum(r.actual_income for r in records) + sum(t.amount for t in all_trans if t.trans_type == 'Income')) - (sum(t.amount for t in all_trans if t.trans_type == 'Expense') + sum(i.amount for i in paid_insts))
    today = datetime.now().date()
    start_str = end_str = str(today)
    if period == "month": start_str, end_str = str(today)[:7]+"-01", str(today.replace(day=calendar.monthrange(today.year, today.month)[1]))
    elif period == "custom": start_str, end_str = start_date, end_date
    f_recs = [r for r in records if start_str <= r.date <= end_str] if period != "all" else records
    f_insts = [i for i in db.query(models.Installment).filter(models.Installment.is_paid == False).all() if start_str <= i.due_date <= end_str] if period != "all" else db.query(models.Installment).filter(models.Installment.is_paid == False).all()
    return {"total_projects": db.query(models.Project).count(), "total_income": sum(r.actual_income for r in f_recs), "total_hours": sum(r.hours_worked for r in f_recs), "total_debt": sum(i.amount for i in f_insts), "vault_balance": round(vault_balance, 2), "debt_details": []}