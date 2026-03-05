from fastapi import FastAPI

app = FastAPI(title="Org API")

@app.get("/health")
def health():
    return {"status": "ok"}