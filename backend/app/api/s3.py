from fastapi import APIRouter, Depends, Response, status, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
import re

from services.depends import get_s3_service
from services.s3 import S3Service
from config import configs

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

    return RedirectResponse(url=f"{configs.endpoint_url}/{configs.bucket}/{key}")

    '''
    try:
        # Получаем файл из S3
        file = await s3_service.get(key)
        body = file.get("Body")

        # Проверяем, что body существует
        if body is None:
            print("File body is None for key: %s", key)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File body is empty",
            )
        content_type = file.get("ContentType", "application/octet-stream")

    except Exception as e:
        print("Failed to get file from S3 for key: %s", key)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get file from S3",
        )

    async def stream_file():
        total_size = 0
        try:
            # Читаем файл по частям
            async for chunk in body.iter_chunks(chunk_size=8192):
                total_size += len(chunk)
                yield chunk
        except RuntimeError as e:
            print("RuntimeError during streaming: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Connection to S3 was closed unexpectedly.",
            )
        except Exception as e:
            print("Unexpected error during streaming: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed during file streaming",
            )
        finally:
            # Закрытие body
            if body is not None:
                try:
                    await body.close()
                except Exception as close_error:
                    print("Failed to close S3 body: %s", str(close_error))
        print("File streaming completed. Total size: %d bytes", total_size)

    # Возвращаем поток данных в StreamingResponse
    return StreamingResponse(stream_file(), media_type=content_type)
    '''
