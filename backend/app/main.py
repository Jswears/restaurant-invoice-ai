from fastapi import FastAPI
from app.routes.invoice_routes import router as invoice_router

app = FastAPI(title="Restaurant Invoice AI - Stage 2")


@app.get("/health")
def health():
    return {"ok": True}


app.include_router(invoice_router)
