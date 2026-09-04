from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


# --- Data model ---
class Todo(BaseModel):
    id: int
    title: str
    done: bool = False


class TodoCreate(BaseModel):
    title: str
    done: bool = False


# --- In-memory "database" ---
todos: dict[int, Todo] = {}
next_id = 1


@app.get("/")
def read_root():
    return {"status": "ok", "message": "To-Do API v2 is running"}


@app.get("/todos", response_model=list[Todo])
def list_todos():
    return list(todos.values())


@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    global next_id
    new_todo = Todo(id=next_id, title=todo.title, done=todo.done)
    todos[next_id] = new_todo
    next_id += 1
    return new_todo


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todos[todo_id]


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, updated: TodoCreate):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo = Todo(id=todo_id, title=updated.title, done=updated.done)
    todos[todo_id] = todo
    return todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    del todos[todo_id]
