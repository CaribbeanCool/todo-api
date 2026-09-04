import os

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from todo_api.database import Base, engine, get_db
from todo_api.models import TodoDB

app = FastAPI()

APP_ENV = os.getenv("APP_ENV", "development")

DB_DEPENDS = Depends(get_db)  # Dependency for database session
# Create tables on startup if they don't exist yet
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


@app.get("/todos", response_model=list[Todo])
def list_todos(db: Session = DB_DEPENDS):
    return db.query(TodoDB).all()


@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, db: Session = DB_DEPENDS):
    new_todo = TodoDB(title=todo.title, done=todo.done)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
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
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
