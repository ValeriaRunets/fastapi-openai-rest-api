from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
from typing import Annotated
import time

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlmodel import Field, Session, SQLModel, create_engine, select


# Define the SQLModel for the Item
class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(default=None, index=True)
    description: str | None = Field(default=None, index=True)
    year: int | None = Field(default=None, index=True)
    price: float = Field(index=True)

# Database setup
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_tables_in_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# FastAPI app setup with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables_in_db()
    yield

app = FastAPI(lifespan=lifespan)

# Middleware to measure processing time
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Common parameters for pagination
async def common_parameters(offset: int = 0, limit: int = 100):
    return {"offset": offset, "limit": limit}

CommonsDepPagination = Annotated[dict, Depends(common_parameters)]

# FastAPI endpoints for CRUD operations on Item
@app.post("/items/")
def create_item(item: Item, session: SessionDep) -> Item:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@app.get("/items/")
def read_items(
    session: SessionDep,
    Commons: dict = CommonsDepPagination
) -> list[Item]:
    items = session.exec(select(Item).offset(Commons["offset"]).limit(Commons["limit"])).all()
    return items

@app.get("/items/{item_id}")
def read_item(item_id: int, session: SessionDep) -> Item:
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found!")
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found!")
    session.delete(item)
    session.commit()
    return {"status": "Done!"}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, session: SessionDep) -> Item:
    db_item = session.get (Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item in db not found!")
    session.merge(item)
    session.commit()
    session.refresh(item)
    return item