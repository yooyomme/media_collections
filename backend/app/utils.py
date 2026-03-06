import os, io, uuid, aiofiles, anyio
from PIL import Image
from fastapi import UploadFile, HTTPException

from app.loggers import debug_logger

UPLOAD_DIR = "../static/uploads"
os.makedirs(f"{UPLOAD_DIR}/avatars", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/covers", exist_ok=True)

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]

async def process_and_save_image(file: UploadFile, folder: str, size=(400, 400)) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Формат файла {file.content_type} не поддерживается")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Размер файла больше 2MB")

    try:
        image = Image.open(io.BytesIO(content))
        image = image.convert("RGB")

        image.thumbnail(size)

        file_name = f"{uuid.uuid4()}.webp"

        relative_path = f"uploads/{folder}/{file_name}"
        full_save_path = os.path.join("static", relative_path)

        buffer = io.BytesIO()
        image.save(buffer, format="WEBP", quality=80)

        async with aiofiles.open(full_save_path, mode="wb") as out_file:
            await out_file.write(buffer.getvalue())

        return f"/static/{relative_path}"
    except Exception as e:
        debug_logger.warning(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="Ошибка обработки изображения")


async def delete_image(avatar_path: str) -> bool:
    if not avatar_path:
        return False
    file_path = avatar_path.lstrip("/")
    try:
        if os.path.exists(file_path):
            await anyio.to_thread.run_sync(os.remove, file_path)
            return True
        else:
            return False
    except Exception as e:
        debug_logger.warning(f"Error while deleting image: {e}")
        return False