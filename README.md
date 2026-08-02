# Test_task_Data_Engineering

Это репозиторий с решением тестового задания для Python-разработчика направления Data Engineering.

## Структура проекта

- task1/ — анализ и модификация XML-аннотаций
- task2/ — обработка COCO-датасета

## Требования

- Python 3.10+
- Стандартная библиотека Python
- Дополнительные зависимости не требуются

## Task 1: XML-аннотации

### Что делает

Папка task1 содержит четыре скрипта:

- script1.py — общая статистика по XML-файлам
- script2.py — статистика по классам
- script3.py — статистика по типам фигур
- script4.py — модификация XML-файлов с сохранением изменённых копий

### Запуск

1. Перейдите в корень проекта:
   ```bash
   cd /path/to/Test_task_Data_Engineering
   ```
2. Запустите нужный скрипт:
   ```bash
   python task1/script1.py
   python task1/script2.py
   python task1/script3.py
   python task1/script4.py
   ```

### Опции

- Для script1.py, script2.py, script3.py можно сохранить результат в txt-файл:
  ```bash
  python task1/script1.py --output task1/statistics.txt
  python task1/script2.py --output task1/class_stats.txt
  python task1/script3.py --output task1/shape_types.txt
  ```

- Для script4.py можно указать папку для сохранения изменённых XML:
  ```bash
  python task1/script4.py --output-dir task1/modified_output
  ```

### Формат выходных файлов

- script1.py / script2.py / script3.py — вывод в консоль и при необходимости txt-файл
- script4.py — создаёт новые XML-файлы с суффиксом _modified в указанной папке

## Task 2: COCO-датасет

### Что делает

Папка task2 содержит три скрипта:

- script1.py — реструктуризация датасета по классам и обновление путей в аннотациях
- script2.py — валидация датасета и формирование отчёта
- script3.py — преобразование COCO-аннотаций в YOLO-формат

### Входные данные

Ожидается, что в папке task2/input_data лежит распакованный датасет с:

- annotations/instances_train.json
- images/train/...

### Запуск

```bash
python task2/script1.py
python task2/script2.py
python task2/script3.py
```

### Опции

- Для script1.py можно указать свои папки ввода/вывода:
  ```bash
  python task2/script1.py --input-dir task2/input_data --output-dir task2/updated_data
  ```

- Для script2.py можно указать путь к аннотациям и выходному отчёту:
  ```bash
  python task2/script2.py --annotation task2/updated_data/updated_annotations.json --data-root task2/updated_data --output task2/updated_data/dataset_report.json
  ```

- Для script3.py можно указать путь к аннотациям и выходной каталог YOLO:
  ```bash
  python task2/script3.py --annotation task2/updated_data/updated_annotations.json --data-root task2/updated_data --output-dir task2/yolo_dataset
  ```

### Формат выходных файлов

- script1.py — создаёт папку task2/updated_data/images/ и файл task2/updated_data/updated_annotations.json
- script2.py — создаёт отчёт task2/updated_data/dataset_report.json
- script3.py — создаёт папку task2/yolo_dataset/ с изображениями и .txt-аннотациями YOLO

## Быстрый старт

1. Создайте и активируйте виртуальное окружение:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Установите зависимости (в данной реализации не требуется!):
   ```bash
   pip install -r requirements.txt
   ```
3. Запустите нужный скрипт из разделов выше.

## Примечание

Все скрипты реализованы без сторонних зависимостей и запускаются стандартным Python 3.10+.
Если входные данные отсутствуют, сначала подготовьте папку task2/input_data и XML-файлы в task1/input_data.
Так же тестовые данные и результаты работы скриптов представлены в репозитории.