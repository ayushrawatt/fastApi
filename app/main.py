from ast import mod
from pyexpat import model
from random import randrange
from sys import exception
from turtle import pos, title
from webbrowser import get
from fastapi import FastAPI, HTTPException, Response, status, Depends
from pydantic import BaseModel
import psycopg2
import time
from sqlalchemy.orm import Session
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from .database import engine, get_db, Base
from . import models
load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool  = True

while True:
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            cursor_factory=RealDictCursor
        )
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


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return{"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    #cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()

    # conn.commit()
    new_post = models.Post(**post.dict()) #title=post.title, content=post.content, published=post.published 
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return{"data": new_post} 


@app.get("/posts/{id}")
def get_post(id : int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (id,))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"post with id {id} is not found")

    return{"post_details" : post}


@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id : int, db: Session = Depends(get_db)):

    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""",(id,) )
    # deleted_post = cursor.fetchone()
    # conn.commit()

    deleted_post = db.query(models.Post).filter(models.Post.id == id).first()
    db.delete(deleted_post)
    db.commit()

    if deleted_post == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"post with id {id} not found")
    
    return Response(status_code = status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id : int, updated_post : Post, db: Session = Depends(get_db)):

    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",(post.title, post.content, post.published, id,))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"post with id {id} not found")

    post_query.update(updated_post.dict())
    db.commit()

    return{"data" : post_query.first()}
