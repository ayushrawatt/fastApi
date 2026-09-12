from random import randrange
from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel


app = FastAPI()

my_posts = [{"title" : "fav food", "content" : "i like jhoi bhaat", "id" : 1},
            {"title" : "fav corn", "content" : "i like closeups", "id" : 2}]

class Post(BaseModel):
    title: str
    content: str
    published: bool  = True
    rating: Optional[int] = None

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_post_index(id):
    for i,p in enumerate(my_posts):
        if p['id'] == id:
            return i

        

@app.get("/")
def read_root():
    return {"message": "heyy this is my 1st server"}


@app.get("/posts")
def get_posts():
    return{"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(2,1000)
    my_posts.append(post_dict)
    return{"data": post_dict}

@app.get("/posts/{id}")
def get_post(id : int):
    pst = find_post(id)
    if not pst:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= f"post with id {id} is not found")

    return{"post_details" : pst}

@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id : int):
    index = find_post_index(id)

    if index == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"post with id {id} not found")
    my_posts.pop(index)
    return Response(status_code = status.HTTP_204_NO_CONTENT)