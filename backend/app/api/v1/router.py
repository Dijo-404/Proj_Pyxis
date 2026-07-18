from fastapi import APIRouter

from app.api.v1.routes import cases, customers, transactions


api_router = APIRouter()
api_router.include_router(transactions.router)
api_router.include_router(customers.router)
api_router.include_router(cases.router)

