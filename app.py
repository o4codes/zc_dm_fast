from fastapi import FastAPI, status, HTTPException

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}