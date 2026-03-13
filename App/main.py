"""
Главный модуль приложения.
Координирует работу всех остальных модулей.
Запустите этот файл, чтобы обработать WAV из папки Input.
"""

import os
import sys

# Добавляем путь к папке App, чтобы Python мог найти наши модули
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import file_handler
import audio_processor

def choose_files(files):
    """
    Позволяет пользователю выбрать, какие файлы обработать.
    Возвращает список выбранных файлов.
    """
    print("\n📋 Найдены следующие WAV-файлы:")
    for i, file in enumerate(files, 1):
        # Показываем только имя файла, без полного пути
        print(f"  {i}. {os.path.basename(file)}")
    
    print("\n  a - обработать все файлы")
    print("  q - выйти")
    print("  (можно выбрать несколько: 1,3,5-7)")
    
    while True:
        choice = input("\n👉 Ваш выбор: ").strip().lower()
        
        if choice == 'q':
            return []
        elif choice == 'a':
            return files
        
        try:
            selected_indices = set()
            # Разбираем ввод: "1,3,5-7"
            parts = choice.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    # Диапазон: "5-7"
                    start, end = map(int, part.split('-'))
                    for num in range(start, end + 1):
                        if 1 <= num <= len(files):
                            selected_indices.add(num)
                else:
                    # Одиночное число
                    if part.isdigit():
                        num = int(part)
                        if 1 <= num <= len(files):
                            selected_indices.add(num)
            
            if selected_indices:
                # Преобразуем номера в пути к файлам
                selected_files = [files[i-1] for i in sorted(selected_indices)]
                print(f"  Выбрано файлов: {len(selected_files)}")
                return selected_files
            else:
                print("  ❌ Некорректный ввод. Попробуйте снова.")
        except:
            print("  ❌ Некорректный ввод. Попробуйте снова.")

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
    
    # 3. Даем пользователю выбрать файлы
    selected_files = choose_files(wav_files)
    
    if not selected_files:
        print("\n👋 Выход по запросу пользователя.")
        return
    
    # 4. Определяем номер запуска и создаем выходную папку
    print(f"\n📁 Подготовка папки для результатов...")
    run_number = file_handler.get_next_run_number()
    output_folder = file_handler.create_output_folder(run_number)
    
    # 5. Обрабатываем выбранные файлы
    print(f"\n🎯 Начинаем обработку {len(selected_files)} файлов...")
    print("-" * 60)
    
    successful = 0
    failed = 0
    
    for i, wav_file in enumerate(selected_files, 1):
        print(f"\n[{i}/{len(selected_files)}] ", end="")
        
        # Создаем имя для выходного MP3
        output_mp3 = file_handler.get_output_filename(wav_file, output_folder)
        
        # Обрабатываем
        success = audio_processor.process_wav_to_tight_mp3(wav_file, output_mp3)
        
        if success:
            successful += 1
        else:
            failed += 1
    
    # 6. Итоги
    print("-" * 60)
    print("\n✅ Обработка завершена!")
    print(f"   Успешно: {successful} файлов")
    if failed > 0:
        print(f"   С ошибками: {failed} файлов")
    print(f"   Результаты сохранены в: {output_folder}")
    print("=" * 60)

if __name__ == "__main__":
    main()
