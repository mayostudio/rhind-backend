from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# حط الرابط اللي نسخته من Supabase بين علامتين التنصيص تحت
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.oytlfzujnqjhmqglgznw:[RjftfPJHtWeRjulS]@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()