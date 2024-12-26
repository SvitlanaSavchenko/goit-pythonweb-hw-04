import asyncio
import os
import random
import string
from pathlib import Path
import argparse
import logging
from aiofiles import open as aio_open
from shutil import copyfile

# Налаштування логування
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def generate_random_files(source_folder: Path, count: int = 20):
    """Генерує випадкові файли у вказаній папці."""
    logger.info(f"Генерація {count} випадкових файлів у {source_folder}")
    source_folder.mkdir(parents=True, exist_ok=True)
    extensions = ['txt', 'jpg', 'png', 'pdf', 'csv']
    for _ in range(count):
        extension = random.choice(extensions)
        filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + f".{extension}"
        file_path = source_folder / filename
        async with aio_open(file_path, 'w') as f:
            await f.write(''.join(random.choices(string.ascii_letters + string.digits, k=100)))
    logger.info("Генерація файлів завершена.")

async def copy_file(file: Path, output_folder: Path):
    """Копіює файл у відповідну підпапку на основі його розширення."""
    ext = file.suffix.lstrip('.').lower()
    target_folder = output_folder / ext
    target_folder.mkdir(parents=True, exist_ok=True)
    target_file = target_folder / file.name

    try:
        copyfile(file, target_file)
        logger.info(f"Копіювання файлу: {file} -> {target_file}")
    except Exception as e:
        logger.error(f"Помилка копіювання файлу {file}: {e}")

async def read_folder(source_folder: Path, output_folder: Path):
    """Читає всі файли у вихідній папці та копіює їх до цільової."""
    logger.info(f"Читання файлів з {source_folder}")
    tasks = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            file_path = Path(root) / file
            tasks.append(copy_file(file_path, output_folder))

    if tasks:
        await asyncio.gather(*tasks)
    logger.info("Сортування файлів завершено.")

async def main():
    parser = argparse.ArgumentParser(description="Сортування файлів за розширенням.")
    parser.add_argument("source", type=str, help="Вихідна папка.")
    parser.add_argument("output", type=str, help="Цільова папка.")
    parser.add_argument("--generate", action="store_true", help="Генерувати випадкові файли.")
    parser.add_argument("--count", type=int, default=20, help="Кількість файлів для генерації (за замовчуванням: 20).")

    args = parser.parse_args()
    source_folder = Path(args.source)
    output_folder = Path(args.output)

    if args.generate:
        await generate_random_files(source_folder, args.count)

    await read_folder(source_folder, output_folder)

if __name__ == "__main__":
    asyncio.run(main())
