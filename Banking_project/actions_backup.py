from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes import user, transaction, transfer, admin

app = FastAPI(
    title="SecureBank API",
    description="A complete banking backend with user auth, transactions, transfers, and admin panel.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        
    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(user.router)           
app.include_router(transaction.router)    
app.include_router(transfer.router)       
app.include_router(admin.router)          

@app.on_event("startup")
def startup():
    """Creates all database tables when the server starts."""
    init_db()
    print("[App] SecureBank API started successfully.")
    print("[App] Docs available at: http://127.0.0.1:8000/docs")




@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "app": "SecureBank API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
