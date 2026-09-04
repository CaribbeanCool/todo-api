import logging
import os

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from todo_api.database import Base, engine, get_db
from todo_api.models import TodoDB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("todo_api")

app = FastAPI()

APP_ENV = os.getenv("APP_ENV", "development")

DB_DEPENDS = Depends(get_db)  # Dependency for database session


# Create tables on startup if they don't exist yet
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# --- Pydantic schemas (API shape, separate from DB model) ---
class TodoCreate(BaseModel):
    title: str
    done: bool = False


class Todo(BaseModel):
    id: int
    title: str
    done: bool

    class Config:
        from_attributes = True  # allows converting from a SQLAlchemy object


@app.get("/")
def read_root():
    return {"status": "ok", "message": "To-Do API is running", "environment": APP_ENV}


@app.get("/health")
def health_check(db: Session = DB_DEPENDS):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except OperationalError:
        db_status = "unreachable"

    healthy = db_status == "ok"
    return {
        "status": "ok" if healthy else "degraded",
        "database": db_status,
    }


@app.get("/todos", response_model=list[Todo])
def list_todos(db: Session = DB_DEPENDS):
    return db.query(TodoDB).all()


@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, db: Session = DB_DEPENDS):
    new_todo = TodoDB(title=todo.title, done=todo.done)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    logger.info(f"Created todo id={new_todo.id} title={new_todo.title!r}")
    return new_todo


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int, db: Session = DB_DEPENDS):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, updated: TodoCreate, db: Session = DB_DEPENDS):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.title = updated.title
    todo.done = updated.done
    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = DB_DEPENDS):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        logger.warning(f"Attempted delete of nonexistent todo id={todo_id}")
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    logger.info(f"Deleted todo id={todo_id}")
