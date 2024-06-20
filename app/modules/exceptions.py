from fastapi import status, HTTPException

exception_active = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="User is not active",
    headers={"WWW-Authenticate": "Bearer"},
)

exception_license = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="The license is invalid",
    headers={"WWW-Authenticate": "Bearer"},
)

exception_file = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="The file is invalid",
    headers={"WWW-Authenticate": "Bearer"},
)

exception_file_count = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You can upload only three files for one report",
    headers={"WWW-Authenticate": "Bearer"},
)

exception_file_size = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Max file size is 10MB",
    headers={"WWW-Authenticate": "Bearer"},
)

exception_limit = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Year limit reached",
    headers={"WWW-Authenticate": "Bearer"},
)

exception_right = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Don't have the right to do this",
    headers={"WWW-Authenticate": "Bearer"},
)

exception_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Not found",
)

exception_token = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token is wrong or missing",
    headers={"WWW-Authenticate": "Bearer"},
)

exception_user_form = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Incorrect username or password',
    headers={'WWW-Authenticate': 'Bearer'},
)

exception_registration_data = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="This name or mail or phone is already exist",
    headers={"WWW-Authenticate": "Bearer"},
)

exception_not_found_file = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="This key doesn't exist",
)