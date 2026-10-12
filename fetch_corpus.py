# -*- coding: utf-8 -*-
"""
Скрипт для скачивания полных текстов страниц из fresh.jsonl и фильтрации вопросов.
"""
import json
import re
from pathlib import Path
import requests

# === НАСТРОЙКИ ПУТЕЙ ===
# Файл с вопросами лежит в data
INPUT_FILE = Path("data/fresh.jsonl")

# Результаты будем сохранять в папку data 
OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

CORPUS_FILE = OUTPUT_DIR / "corpus.jsonl"
FILTERED_QUESTIONS_FILE = OUTPUT_DIR / "fresh_filtered.jsonl"

# === НАСТРОЙКИ API ===
WIKI_API = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "my-rag-project/1.0 (student@university.edu)"
}


def fetch_page_text(title: str):
    """Скачивает полный текст статьи по её названию."""
    try:
        r = requests.get(WIKI_API, timeout=30, headers=HEADERS, params={
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,          # Получаем чистый текст без HTML-разметк
            "titles": title,
            "redirects": 1,            # Автоматически следовать за редиректами
            "format": "json"
        })
        r.raise_for_status()
        data = r.json()
        pages = data["query"]["pages"]
        
        # Берем первую (и единственную) страницу из ответа
        page = next(iter(pages.values()))
        
        # Если страница не найдена, page_id будет отрицательным
        if page.get("missing"):
            return title, ""
            
        real_title = page.get("title", title)
        text = page.get("extract", "")
        return real_title, text
        
    except Exception as e:
        print(f"  [!] Ошибка при загрузке '{title}': {e}")
        return title, ""


def norm(text: str) -> str:
    """Нормализация текста для надежного поиска подстроки (evidence)."""
    # Приводим к нижнему регистру, replacing пунктуацию на пробелы, схлопываем пробелы
    return " ".join(re.sub(r"[^\w\s]", " ", str(text).lower()).split())


def main():
    if not INPUT_FILE.exists():
        print(f"Ошибка: Файл {INPUT_FILE} не найден в корне проекта!")
        return

    # 1. Читаем вопросы и собираем уникальные страницы для скачивания
    tasks = []
    unique_pages = {}  # Словарь: title -> url (для сохранения метаданных)
    
    print("Читаем fresh.jsonl...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            tasks.append(item)
            unique_pages[item["page"]] = item["url"]

    titles = list(unique_pages.keys())
    print(f"Найдено {len(tasks)} вопросов, уникальных страниц: {len(titles)}\n")

    # 2. Скачиваем полные тексты страниц
    corpus = []
    for title in titles:
        print(f"Скачиваем: {title}")
        real_title, text = fetch_page_text(title)
        if text:
            corpus.append({
                "page": real_title,
                "url": unique_pages.get(real_title, unique_pages.get(title, "")),
                "text": text
            })
        else:
            print(f"Текст не найен для '{title}'. Возможно, опечатка в названии страницы.")

    # 3. Сохраняем корпус
    print(f"\nСохраняем корпус в {CORPUS_FILE}...")
    with open(CORPUS_FILE, "w", encoding="utf-8") as f:
        for c in corpus:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"Сохранено {len(corpus)} страниц.")

    # 4. Фильтруем вопросы: оставляем только те, где evidence точно есть в скачанном тексте
    print("\nФильтруем вопросы по наличию evidence в корпусе...")
    # Создаем словарь нормализованных текстов для быстрого поиска
    texts_norm = {c["page"]: norm(c["text"]) for c in corpus}
    
    kept_tasks = []
    for task in tasks:
        page_title = task["page"]
        norm_evidence = norm(task["evidence"])[:120]  # Берем первые 120 символов нормализованной цитаты
        norm_text = texts_norm.get(page_title, "")
        
        if norm_evidence in norm_text:
            kept_tasks.append(task)
        else:
            print(f"Evidence не найден в тексте для вопроса: '{task['question'][:60]}...'")

    # 5. Сохраняем отфильтрованные вопросы
    print(f"\nСохраняем валидные вопросы в {FILTERED_QUESTIONS_FILE}...")
    with open(FILTERED_QUESTIONS_FILE, "w", encoding="utf-8") as f:
        for t in kept_tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
            
    print(f"Готово! Осталось {len(kept_tasks)} вопросов из {len(tasks)}.")
    print("Теперь вы можете использовать data/corpus.jsonl и data/fresh_filtered.jsonl в вашем RAG-пайплайне.")


if __name__ == "__main__":
    main()
