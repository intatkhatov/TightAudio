"""
Главный модуль приложения.
Координирует работу всех остальных модулей.
Запустите этот файл, чтобы обработать все WAV из папки Input.
"""

import os
import sys
from datetime import datetime

# Добавляем путь к папке App, чтобы Python мог найти наши модули
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import file_handler
import audio_processor

def main():
    """Главная функция приложения"""
    
    print("=" * 60)
    print("TightAudio - Удаление тишины из аудиозаписей")
    print("=" * 60)
    
    # 1. Проверяем, существует ли папка Input
    if not os.path.exists(config.INPUT_DIR):
        print(f"\n❌ Ошибка: Папка с исходными файлами не найдена:")
        print(f"   {config.INPUT_DIR}")
        print("\nСоздайте эту папку и положите в неё WAV-файлы.")
        return
    
    # 2. Получаем список WAV-файлов
    print(f"\n🔍 Поиск WAV-файлов в папке Input...")
    wav_files = file_handler.get_wav_files()
    
    if not wav_files:
        print(f"\n❌ В папке {config.INPUT_DIR} нет WAV-файлов.")
        print("Положите WAV-файлы в папку Input и запустите снова.")
        return
    
    print(f"   Найдено файлов: {len(wav_files)}")
    
    # 3. Определяем номер запуска и создаем выходную папку
    print(f"\n📁 Подготовка папки для результатов...")
    run_number = file_handler.get_next_run_number()
    output_folder = file_handler.create_output_folder(run_number)
    
    # 4. Обрабатываем каждый файл
    print(f"\n🎯 Начинаем обработку {len(wav_files)} файлов...")
    print("-" * 60)
    
    successful = 0
    failed = 0
    
    for i, wav_file in enumerate(wav_files, 1):
        print(f"\n[{i}/{len(wav_files)}] ", end="")
        
        # Создаем имя для выходного MP3
        output_mp3 = file_handler.get_output_filename(wav_file, output_folder)
        
        # Обрабатываем
        success = audio_processor.process_wav_to_tight_mp3(wav_file, output_mp3)
        
        if success:
            successful += 1
        else:
            failed += 1
    
    # 5. Итоги
    print("-" * 60)
    print("\n✅ Обработка завершена!")
    print(f"   Успешно: {successful} файлов")
    if failed > 0:
        print(f"   С ошибками: {failed} файлов")
    print(f"   Результаты сохранены в: {output_folder}")
    print("=" * 60)

if __name__ == "__main__":
    main()
