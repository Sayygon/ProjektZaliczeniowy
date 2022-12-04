from typing import Union
from fastapi import FastAPI, File, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import cv2
import numpy as np
from starlette.responses import StreamingResponse
import io
import secrets
from datetime import datetime
import os

app = FastAPI()
security = HTTPBasic()

@app.get("/prime/{number}")
async def read_item(number: Union[str, None] = None):
    try:
        number = int(number)
        if number >= 1:
            if number%1 == 0:
                flag = 0
                for k in range(2, int(number ** 1/2) + 1):
                    if (number % k == 0):
                        flag = 1
                    break
                if (flag == 0):
                    return f"{number} to jest liczba pierwsza"
                else:
                    return f"{number} to nie jest liczba pierwsza"
            else:
                return f"{number} to nie jest liczba całkowita"
        else:
            return f"liczba {number} nie może być mniejsza lub równa zero"
    except:
        return f"{number} to nie jest liczba"

@app.post("/picture/invert")
async def UploadImage(file: bytes = File(...)):
    print(type(file))
    ready_file = np.fromstring(file, np.uint8)
    image = cv2.imdecode(ready_file, cv2.IMREAD_COLOR)
    inverted = cv2.bitwise_not(image)
    _, encoded_image = cv2.imencode('.PNG', inverted)

    return StreamingResponse(io.BytesIO(encoded_image.tobytes()), media_type="image/png")

@app.get("/auth")
def read_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = bytes(os.environ.get("USER"), 'utf-8')
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = bytes(os.environ.get("PASSWORD"), 'utf-8')
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return datetime.now()
