from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import mysql.connector
from typing import List
import os
from dotenv import load_dotenv
load_dotenv()
def get_db_connection():
    print(os.getenv("MYSQL_HOST"))
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )
    return connection

app = FastAPI()
class CreateNoteSchema(BaseModel):
    username:str
    note: str
def get_user_id(username: str, db_connection):
    """Get the user ID for a given username; create the user if they don't exist."""
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()


    if not user:
        cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
        db_connection.commit()
        user_id = cursor.lastrowid
    else:
        user_id = user["id"]

    cursor.close()
    return user_id

@app.post("/notes")
def add_note(data: CreateNoteSchema):
    db_connection = get_db_connection()
    user_id = get_user_id(data.username, db_connection)

    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO notes (user_id, note) VALUES (%s, %s)", (user_id, data.note))
    db_connection.commit()

    cursor.close()
    db_connection.close()
    return {"message": "Note added successfully"}

@app.get("/notes/{username}")
def get_notes(username: str):
    db_connection = get_db_connection()
    user_id = get_user_id(username, db_connection)

    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT id, note FROM notes WHERE user_id = %s", (user_id,))
    notes = cursor.fetchall()

    cursor.close()
    db_connection.close()

    return {"notes": [{"id": note["id"], "note": note["note"]} for note in notes]}

@app.delete("/notes/{username}/{note_id}")
def delete_note(username: str, note_id: int):
    db_connection = get_db_connection()
    user_id = get_user_id(username, db_connection)

    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s AND user_id = %s", (note_id, user_id))
    db_connection.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Note not found")

    cursor.close()
    db_connection.close()
    return {"message": "Note deleted successfully"}
if __name__ == '__main__':
    import uvicorn
    print(os.getenv("MYSQL_HOST"))
    uvicorn.run(app,host='0.0.0.0',port=8080)
