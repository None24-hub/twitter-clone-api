from pathlib import Path

from aiofiles import open
from fastapi import UploadFile

from .settings import MEDIA_PATH


async def check_or_get_filename(path: Path) -> Path:
    """
    Проверяет, существует ли файл с указанным путём.
    Если файл уже есть, то к имени добавляется числовой суффикс,
    и проверка повторяется до тех пор, пока не будет найдено свободное имя.
    Возвращает путь с уникальным именем файла.
    """
    original_path = path
    counter = 0

    while path.exists():
        counter += 1
        filename = f"{original_path.stem} ({counter}){original_path.suffix}"
        path = original_path.with_name(filename)
    return path


async def save_uploaded_file(uploaded_file: UploadFile) -> str:
    """
    Принимает загруженный файл (UploadFile) и сохраняет его на диск.
    Если файл с таким именем уже существует — имя автоматически изменяется так,
    чтобы избежать перезаписи.

    Возвращает строку — относительный путь к сохранённому файлу,
    который затем используется в проекте и сохраняется в базе данных.
    """

    MEDIA_PATH.mkdir(parents=True, exist_ok=True)

    file_path: Path = MEDIA_PATH
    if uploaded_file.filename is not None:
        file_path = MEDIA_PATH / uploaded_file.filename
    filename = await check_or_get_filename(path=file_path)
    img_path = f"{filename.stem}{filename.suffix}"
    content = uploaded_file.file.read()
    async with open(filename, "wb") as file:
        await file.write(content)
    return img_path
