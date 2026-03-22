from fastapi import Request
import sqlite3


def get_db(request: Request) -> sqlite3.Connection:
    return request.app.state.db
