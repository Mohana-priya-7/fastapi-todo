from fastapi import FastAPI ,Depends,HTTPException
from schemas import Todo as TodoSchema,TodoCreate  
from sqlalchemy.orm import Session 
from database import SessionLocal ,Base,engine
from models import Todo as TodoModel
Base.metadata.create_all(bind=engine)
app=FastAPI()
#Dependency to get the database session
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.post("/todos/", response_model=TodoSchema)  
def create_todo(todo: TodoCreate,db:Session=Depends(get_db)):
    db_todo=TodoModel(**todo.dict())
    db.add(db_todo)
    db.commit() 
    db.refresh(db_todo)
    return db_todo 
@app.get("/todos/",response_model=list[TodoSchema])
def read_todos(db:Session=Depends(get_db)):
    return db.query(TodoModel).all()
#GET /todos/{id} single todo by id
@app.get("/todos/{id}",response_model=TodoSchema)
def read_todo(todo_id:int,db:Session=Depends(get_db)):
    r=db.query(TodoModel).filter(TodoModel.id==todo_id).first()
    if not r:
        raise HTTPException(status_code=404,detail="Todo not found")
    return r
@app.put("/todos/{todos_id}",response_model=TodoSchema)
def update_todo(todo_id:int,updated_todo:TodoCreate,db:Session=Depends(get_db)):
    r=db.query(TodoModel).filter(TodoModel.id==todo_id).first()
    if not r:
        raise HTTPException(status_code=404,detail="Todo not found")
    for key,value in updated_todo.dict().items():
        setattr(r,key,value)
    db.commit()
    db.refresh(r)
    return r
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id:int,db:Session=Depends(get_db)):
    r=db.query(TodoModel).filter(TodoModel.id==todo_id).first()
    if not r:
        raise HTTPException(status_code=404,detail="Todo not found")
    db.delete(r)
    db.commit()
    return {"message":"Todo deleted successfully"}