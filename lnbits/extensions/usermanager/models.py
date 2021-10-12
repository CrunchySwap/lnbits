from pydantic import BaseModel
from fastapi.param_functions import Query
from sqlite3 import Row

class CreateUserData(BaseModel):
    user_name: str = Query(...)
    wallet_name: str = Query(...)
    admin_id: str = Query(...)
    email: str = Query("")
    password: str = Query("")


class Users(BaseModel):
    id: str
    name: str
    admin: str
    email: str
    password: str


class Wallets(BaseModel):
    id: str
    admin: str
    name: str
    user: str
    adminkey: str
    inkey: str

    @classmethod
    def from_row(cls, row: Row) -> "Wallets":
        return cls(**dict(row))
