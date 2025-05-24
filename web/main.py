from fastapi import FastAPI
from web.routes import user  # Import the user route

app = FastAPI()

# Register route(s)
app.include_router(user.router)

# Optional root route
@app.get("/")
async def root():
    return {"message": "Welcome to Gringo AI Ops"}