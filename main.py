from fastapi import FastAPI
from database import init_db
from routes import auth, admin, user

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(user.router)


@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI Library Management System"}
