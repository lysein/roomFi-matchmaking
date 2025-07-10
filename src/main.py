import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import auth
from src.api.routers import dev_auth
from src.api.routers import matchmaking
from src.api.routers import users
from src.api.routers import landlords
from src.api.routers import properties
from src.api.routers import juno


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⬅️ TEMPORARY: lets any origin connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matchmaking.router, prefix="/matchmaking", tags=["matchmaking"])
app.include_router(users.router, prefix="/db",tags=["user_profiles"])
app.include_router(landlords.router, prefix="/db", tags=["landlord_profiles"])
app.include_router(properties.router, prefix="/db", tags=["properties"])
app.include_router(juno.router, prefix="/juno", tags=["juno"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)