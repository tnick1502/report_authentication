from fastapi import APIRouter
from api.reports import router as report_router
from api.users import router as users_router
from api.files import router as files_router
from api.test_type_files import router as test_type_files_router
from api.s3 import router as s3_router
from api.stat import router as stat_router

router = APIRouter()
router.include_router(report_router)
router.include_router(users_router)
router.include_router(files_router)
router.include_router(test_type_files_router)
router.include_router(s3_router)
router.include_router(stat_router)