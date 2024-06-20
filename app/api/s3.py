from fastapi import APIRouter, Depends, Response, status, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import re

from services.depends import get_s3_service
from services.s3 import S3Service

router = APIRouter(
    prefix="/s3",
    tags=['s3'])

file_key_pattern = r'georeport/files/[a-f0-9]{40}-.*'

@router.get("/")
async def get(
        key: str,
        s3_service: S3Service = Depends(get_s3_service)
):
    '''Получение файлов'''
    if re.fullmatch(file_key_pattern, key) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key have a wrong format"
        )
    file =  await s3_service.get(key)
    #['ResponseMetadata', 'AcceptRanges', 'LastModified', 'ContentLength', 'ETag', 'CacheControl', 'ContentType',
    # 'Expires', 'Metadata', 'Body']
    return StreamingResponse(file["Body"], media_type=file['ContentType'])
