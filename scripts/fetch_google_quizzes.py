"""Download the nine public Android Basics with Compose quizzes.

Run from any directory. The output is read by on-tap-web's import script.
Answer keys are reviewed separately and tied to a content hash.
"""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "google_quizzes.json"


def fetch_quiz(pair):
    unit, pathway = pair
    slug = f"android-basics-compose-unit-{unit}-pathway-{pathway}"
    url = f"https://developer.android.com/courses/quizzes/{slug}/{slug}?hl=en"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.select_one("h1")
    questions = []
    for number, item in enumerate(soup.select(".devsite-quiz-question"), 1):
        header = item.select_one(".devsite-quiz-question-header")
        kind = item.get("data-type")
        if not header or kind not in (
            "multiple_choice_single_answer", "multiple_choice_multiple_answer"
        ):
            raise ValueError(f"Unsupported question format: {url}, question {number}")
        text = header.get_text(" ", strip=True)
        code_blocks = [block.get_text() for block in item.select("pre")]
        if code_blocks:
            text += "\n\n" + "\n\n".join(code_blocks)
        if item.select("img"):
            raise ValueError(f"Question contains an image, review before importing: {url} #{number}")
        options = [
            label.get_text(" ", strip=True)
            for label in item.select(".devsite-quiz-answer label")
        ]
        if len(options) < 2:
            raise ValueError(f"Missing options: {url} #{number}")
        body = {"text": text, "type": "multi" if kind.endswith("multiple_answer") else "single",
                "options": options}
        body["id"] = f"google-u{unit}-p{pathway}-q{number}"
        body["fingerprint"] = hashlib.sha256(
            json.dumps(body, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        questions.append(body)
    if not title or not questions:
        raise ValueError(f"Quiz page was not returned: {url}")
    return {"unit": unit, "pathway": pathway, "title": title.get_text(" ", strip=True),
            "url": url, "questions": questions}


def main():
    pairs = [(unit, pathway) for unit in range(1, 4) for pathway in range(1, 4)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        quizzes = list(pool.map(fetch_quiz, pairs))
    temporary = OUTPUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(quizzes, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(OUTPUT)
    for quiz in quizzes:
        print(f"Unit {quiz['unit']} · Pathway {quiz['pathway']}: {len(quiz['questions'])} questions")
    print(f"Saved {sum(len(quiz['questions']) for quiz in quizzes)} questions to {OUTPUT}")


if __name__ == "__main__":
    main()
