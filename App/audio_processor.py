"""
Модуль для обработки аудиофайлов.
Удаление тишины и конвертация WAV в MP3.
"""

from pydub import AudioSegment
from pydub.silence import split_on_silence
import config
import os

def process_wav_to_tight_mp3(input_wav_path, output_mp3_path):
    """
    Берет WAV-файл, удаляет длинные паузы, но оставляет микропаузы для естественности.
    """
    
    print(f"Обработка: {os.path.basename(input_wav_path)}")
    
    try:
        # 1. Загружаем WAV-файл
        print("  Загрузка аудио...")
        audio = AudioSegment.from_wav(input_wav_path)
        
        # 2. Показываем исходную длительность
        duration_seconds = len(audio) / 1000
        print(f"  Исходная длительность: {duration_seconds:.1f} сек")
        
        # 3. Удаляем длинные паузы, но оставляем микропаузы
        print(f"  Удаление длинных пауз...")
        
        # Разбиваем на чанки по тишине
        chunks = split_on_silence(
            audio,
            min_silence_len=config.SILENCE_DURATION_MS,  # 500 мс - паузы длиннее этого считаются "лишними"
            silence_thresh=config.SILENCE_THRESHOLD,     # -40 dB - порог тишины
            keep_silence=300                              # Оставляем 300 мс тишины между чанками (короткая пауза)
        )
        
        # Склеиваем все чанки обратно
        if chunks:
            tight_audio = chunks[0]
            for chunk in chunks[1:]:
                tight_audio += chunk
        else:
            # Если тишина не найдена, оставляем как есть
            tight_audio = audio
        
        # 4. Показываем новую длительность
        new_duration_seconds = len(tight_audio) / 1000
        saved_seconds = duration_seconds - new_duration_seconds
        print(f"  Длительность после сжатия: {new_duration_seconds:.1f} сек")
        print(f"  Сэкономлено: {saved_seconds:.1f} сек")
        
        # 5. Сохраняем как MP3
        print(f"  Экспорт в MP3...")
        tight_audio.export(
            output_mp3_path,
            format="mp3",
            bitrate=config.MP3_BITRATE
        )
        
        print(f"  ✅ Готово: {os.path.basename(output_mp3_path)}")
        return True
        
    except Exception as e:
        print(f"  ❌ ОШИБКА при обработке {input_wav_path}: {e}")
        return False

if __name__ == "__main__":
    print("Это модуль обработки аудио. Запустите main.py для работы приложения.")
