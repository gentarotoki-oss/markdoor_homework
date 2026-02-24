from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# データ保存用のJSONファイル
DATA_FILE = "todos.json"

class Todo(BaseModel):
    id: int
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    completed: bool
    created_at: str

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# JSONファイルの読み書き
def load_todos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(DATA_FILE, "w") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)

# 全タスク取得
@app.get("/todos")
def get_todos():
    return load_todos()

# タスク作成
@app.post("/todos")
def create_todo(todo: TodoCreate):
    todos = load_todos()
    new_todo = {
        "id": len(todos) + 1,
        "title": todo.title,
        "description": todo.description,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    todos.append(new_todo)
    save_todos(todos)
    return new_todo

# タスク更新
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate):
    todos = load_todos()
    for t in todos:
        if t["id"] == todo_id:
            if todo.title is not None:
                t["title"] = todo.title
            if todo.description is not None:
                t["description"] = todo.description
            if todo.completed is not None:
                t["completed"] = todo.completed
            save_todos(todos)
            return t
    raise HTTPException(status_code=404, detail="Task not found")

# タスク削除
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    todos = load_todos()
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            deleted = todos.pop(i)
            save_todos(todos)
            return {"message": "Task deleted", "task": deleted}
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")
