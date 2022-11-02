from fastapi import APIRouter
from api.reports import router as report_router
from api.users import router as users_router

router = APIRouter()
router.include_router(report_router)
router.include_router(users_router)