"""
Модуль для работы с файловой системой.
Создание папок, поиск WAV-файлов, получение следующего номера запуска.
"""

import os
import glob
from pathlib import Path
import config

def get_next_run_number():
    """
    Определяет следующий номер папки Run_N в папке Output.
    Смотрит на существующие папки Run_1, Run_2 и т.д. и возвращает следующий номер.
    """
    # Убеждаемся, что папка Output существует
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    # Ищем все папки, начинающиеся с "Run_" в папке Output
    run_folders = glob.glob(os.path.join(config.OUTPUT_DIR, "Run_*"))
    
    if not run_folders:
        return 1
    
    # Извлекаем номера из названий папок
    numbers = []
    for folder in run_folders:
        folder_name = os.path.basename(folder)
        try:
            # Ожидаем формат "Run_ЧИСЛО"
            number = int(folder_name.split("_")[1])
            numbers.append(number)
        except (IndexError, ValueError):
            # Если папка называется не по шаблону, просто игнорируем её
            continue
    
    if not numbers:
        return 1
    
    return max(numbers) + 1

def create_output_folder(run_number):
    """
    Создает папку для конкретного запуска.
    Например: /Users/intatkhatov/Documents/TightAudio/Output/Run_3
    """
    folder_name = f"Run_{run_number}"
    folder_path = os.path.join(config.OUTPUT_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    print(f"Создана папка для результатов: {folder_path}")
    return folder_path

def get_wav_files():
    """
    Находит все WAV-файлы в папке Input.
    Возвращает список путей к файлам.
    """
    # Убеждаемся, что папка Input существует
    if not os.path.exists(config.INPUT_DIR):
        print(f"ОШИБКА: Папка {config.INPUT_DIR} не существует!")
        return []
    
    # Ищем все .wav файлы (регистр букв не важен)
    wav_files = glob.glob(os.path.join(config.INPUT_DIR, "*.wav"))
    wav_files += glob.glob(os.path.join(config.INPUT_DIR, "*.WAV"))
    
    return wav_files

def get_output_filename(input_file_path, output_folder):
    """
    Создает имя для выходного MP3-файла на основе имени входного WAV-файла.
    """
    # Получаем имя файла без пути
    base_name = os.path.basename(input_file_path)
    # Меняем расширение на .mp3 (в любом регистре)
    base_name_without_ext = os.path.splitext(base_name)[0]
    output_filename = f"{base_name_without_ext}.mp3"
    return os.path.join(output_folder, output_filename)

# Тестирование модуля (если запустить этот файл напрямую)
if __name__ == "__main__":
    print("Тестирование file_handler.py")
    print(f"Следующий номер запуска: {get_next_run_number()}")
    wavs = get_wav_files()
    print(f"Найдено WAV-файлов: {len(wavs)}")
    for wav in wavs:
        print(f"  - {wav}")
