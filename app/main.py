from random import randrange
from sys import exception
from turtle import pos
from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
import psycopg2
import time
from psycopg2.extras import RealDictCursor

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool  = True

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastAPI', user='postgres', password='2554650', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("database connection OK")
        break
    except Exception as error:
        print("database connection failed")
        print("Error: ", error)
        time.sleep(2)

@app.get("/")
def read_root():
    return {"message": "heyy this is my 1st server"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts """)
    posts = cursor.fetchall()
    return{"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()

    conn.commit()
    return{"data": new_post} 

@app.get("/posts/{id}")
def get_post(id : int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (id,))
    post = cursor.fetchone()
    
    if post is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"post with id {id} is not found")

    return{"post_details" : post}

@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id : int):

    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""",(id,) )
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"post with id {id} not found")
    
    return Response(status_code = status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id : int, post : Post):

    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",(post.title, post.content, post.published, id,))
    updated_post = cursor.fetchone()
    conn.commit()
    
    if updated_post == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"post with id {id} not found")

    return{"data" : updated_post}
