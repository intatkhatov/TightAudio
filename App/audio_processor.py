"""
Модуль для обработки аудиофайлов.
Удаление тишины и конвертация WAV в MP3.
"""

from pydub import AudioSegment
from pydub.silence import detect_silence
import config
import os
import sys
import time
import threading

class ProgressBar:
    """Класс для управления прогресс-барами"""
    
    def __init__(self, total=100, prefix='', length=30):
        self.total = total
        self.prefix = prefix
        self.length = length
        self.current = 0
        self.active = True
        
    def update(self, iteration, suffix=''):
        """Обновить прогресс-бар"""
        percent = f"{100 * (iteration / self.total):.1f}"
        filled_length = int(self.length * iteration // self.total)
        bar = '█' * filled_length + '░' * (self.length - filled_length)
        sys.stdout.write(f'\r{self.prefix} |{bar}| {percent}% {suffix}')
        sys.stdout.flush()
        self.current = iteration
        if iteration >= self.total:
            self.complete()
    
    def complete(self):
        """Завершить прогресс-бар"""
        sys.stdout.write('\n')
        self.active = False

def find_speech_chunks_with_progress(audio, min_silence_len, silence_thresh, keep_silence):
    """
    Находит фрагменты речи с прогресс-баром.
    Анализирует аудио по кусочкам и показывает реальный прогресс.
    """
    print("  Поиск фрагментов речи...")
    
    # Размер окна анализа (чем меньше, тем точнее прогресс, но медленнее)
    window_ms = 1000  # Анализируем по 1 секунде
    total_windows = len(audio) // window_ms + 1
    
    progress = ProgressBar(total=total_windows, prefix='  Сканирование тишины')
    
    speech_chunks = []
    current_start = None
    is_speech = False
    
    # Проходим по аудио окнами
    for i in range(total_windows):
        start_ms = i * window_ms
        end_ms = min((i + 1) * window_ms, len(audio))
        
        # Берем кусочек аудио
        chunk = audio[start_ms:end_ms]
        
        # Определяем, есть ли звук в этом кусочке (громче порога тишины)
        if chunk.dBFS > silence_thresh:
            # Это речь
            if not is_speech:
                # Начало нового фрагмента речи
                current_start = start_ms
                is_speech = True
        else:
            # Это тишина
            if is_speech:
                # Конец фрагмента речи
                speech_chunks.append((current_start, start_ms))
                is_speech = False
        
        # Обновляем прогресс-бар
        progress.update(i + 1, f'({i+1}/{total_windows} сек)')
    
    # Если файл закончился речью
    if is_speech:
        speech_chunks.append((current_start, len(audio)))
    
    # Теперь применяем keep_silence (добавляем немного тишины между фрагментами)
    if keep_silence > 0 and speech_chunks:
        result_chunks = []
        for i, (start, end) in enumerate(speech_chunks):
            # Для первого фрагмента начинаем с начала
            if i == 0:
                chunk_start = max(0, start - keep_silence)
            else:
                chunk_start = start - keep_silence
            
            # Для последнего фрагмента заканчиваем в конце
            if i == len(speech_chunks) - 1:
                chunk_end = min(len(audio), end + keep_silence)
            else:
                chunk_end = end + keep_silence
            
            result_chunks.append(audio[chunk_start:chunk_end])
        
        return result_chunks
    else:
        # Без keep_silence просто возвращаем куски аудио
        return [audio[start:end] for start, end in speech_chunks]

def process_wav_to_tight_mp3(input_wav_path, output_mp3_path):
    """
    Берет WAV-файл, удаляет из него тишину и сохраняет как MP3.
    """
    
    print(f"\nОбработка: {os.path.basename(input_wav_path)}")
    
    try:
        # 1. Загружаем WAV-файл с прогрессом
        file_size = os.path.getsize(input_wav_path)
        print(f"  Размер файла: {file_size / 1024 / 1024:.1f} МБ")
        
        # Имитация загрузки
        load_progress = ProgressBar(total=20, prefix='  Загрузка WAV')
        for i in range(20):
            time.sleep(0.02)
            load_progress.update(i+1)
        
        start_time = time.time()
        audio = AudioSegment.from_wav(input_wav_path)
        load_time = time.time() - start_time
        print(f"  Загрузка завершена за {load_time:.1f} сек")
        
        # 2. Показываем исходную длительность
        duration_seconds = len(audio) / 1000
        duration_minutes = duration_seconds / 60
        print(f"  Длительность: {duration_minutes:.1f} минут ({duration_seconds:.1f} сек)")
        
        # 3. Поиск фрагментов речи с реальным прогресс-баром
        chunks = find_speech_chunks_with_progress(
            audio,
            min_silence_len=config.SILENCE_DURATION_MS,
            silence_thresh=config.SILENCE_THRESHOLD,
            keep_silence=300
        )
        
        # 4. Склейка фрагментов с прогресс-баром
        if len(chunks) > 1:
            print("  Склейка фрагментов...")
            tight_audio = chunks[0]
            
            merge_progress = ProgressBar(total=len(chunks)-1, prefix='  Прогресс склейки')
            for i, chunk in enumerate(chunks[1:], 1):
                tight_audio += chunk
                merge_progress.update(i, f'({i}/{len(chunks)-1})')
                time.sleep(0.01)  # Небольшая задержка для плавности
        elif len(chunks) == 1:
            tight_audio = chunks[0]
            print("  Найден один непрерывный фрагмент речи")
        else:
            tight_audio = audio
            print("  Речь не найдена, возвращаем оригинал")
        
        # 5. Показываем результат сжатия
        new_duration_seconds = len(tight_audio) / 1000
        new_duration_minutes = new_duration_seconds / 60
        saved_seconds = duration_seconds - new_duration_seconds
        saved_percent = (saved_seconds / duration_seconds) * 100 if duration_seconds > 0 else 0
        
        print(f"\n  📊 Результат сжатия:")
        print(f"     Было: {duration_minutes:.1f} мин ({duration_seconds:.1f} сек)")
        print(f"     Стало: {new_duration_minutes:.1f} мин ({new_duration_seconds:.1f} сек)")
        print(f"     Сэкономлено: {saved_seconds:.1f} сек ({saved_percent:.1f}%)")
        
        # 6. Экспорт в MP3 с прогресс-баром
        print("  Экспорт в MP3...")
        
        export_progress = ProgressBar(total=100, prefix='  Прогресс экспорта')
        for i in range(100):
            if i == 99:  # На последнем шаге реально экспортируем
                tight_audio.export(
                    output_mp3_path,
                    format="mp3",
                    bitrate=config.MP3_BITRATE
                )
            time.sleep(0.02)  # Плавное обновление (2 секунды на весь экспорт)
            export_progress.update(i+1)
        
        # 7. Показываем размер результата
        result_size = os.path.getsize(output_mp3_path)
        compression_ratio = (1 - result_size / file_size) * 100 if file_size > 0 else 0
        print(f"  💾 Размер MP3: {result_size / 1024 / 1024:.1f} МБ")
        print(f"  📦 Сжатие: {compression_ratio:.1f}% от оригинала")
        print(f"  ✅ Готово: {os.path.basename(output_mp3_path)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ОШИБКА при обработке: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Это модуль обработки аудио. Запустите main.py для работы приложения.")
