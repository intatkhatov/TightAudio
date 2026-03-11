"""
Конфигурационный файл приложения.
Здесь хранятся пути к папкам и настройки обработки звука.
"""
import os

# Базовые пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "Input")
OUTPUT_DIR = os.path.join(BASE_DIR, "Output")

# Настройки обработки звука
# Минимальная громкость (в dBFS), ниже которой звук считается тишиной
SILENCE_THRESHOLD = -40

# Минимальная длительность тишины (в миллисекундах), которая будет обрезана
SILENCE_DURATION_MS = 500

# Настройки MP3
MP3_BITRATE = "192k"

if __name__ == "__main__":
    print(f"Папка ввода: {INPUT_DIR}")
    print(f"Папка вывода: {OUTPUT_DIR}")
