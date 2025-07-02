import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from src.api.routers import auth
from src.api.routers import dev_auth
from src.api.routers import matchmaking

app = FastAPI()
app.include_router(auth.router, prefix="/auth")
app.include_router(dev_auth.router, prefix="/dev-auth")
app.include_router(matchmaking.router, prefix="/matchmaking")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)