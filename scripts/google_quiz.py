"""Build local practice pages from the downloaded Google quizzes."""
import json
from pathlib import Path


ATTRIBUTION = """<p class="source-ref">
Portions of this page are reproduced from work created and
<a href="https://developer.android.com/courses/android-basics-compose/course">shared by the Android Open Source Project</a>
and used according to terms described in the
<a href="https://creativecommons.org/licenses/by/2.5/">Creative Commons 2.5 Attribution License</a>.
Code samples follow the <a href="https://developer.android.com/license">Android content license</a>.
</p>"""


def load_google_questions():
    scripts = Path(__file__).resolve().parent
    quizzes = json.loads((scripts / "google_quizzes.json").read_text())
    keys = json.loads((scripts / "google_quiz_answers.json").read_text())
    chapters = []
    verified_count = 0
    for number, quiz in enumerate(quizzes, 1):
        questions = []
        for raw in quiz["questions"]:
            key = keys.get(raw["id"], {})
            valid_key = key.get("fingerprint") == raw["fingerprint"]
            answers = key.get("answers", []) if valid_key else []
            options = [{"id": chr(65 + i), "text": text}
                       for i, text in enumerate(raw["options"])]
            if not set(answers) <= {option["id"] for option in options}:
                raise ValueError(f"Invalid Google quiz key: {raw['id']}")
            verification = key.get("verification", {})
            verified = valid_key and verification.get("score") == verification.get("total") and bool(verification.get("total"))
            verified_count += int(verified)
            questions.append({
                "id": raw["id"], "text": raw["text"], "type": raw["type"],
                "options": options, "answers": answers, "plain": True,
                "note": "" if valid_key else "Nội dung nguồn đã thay đổi. Cần rà lại đáp án trước khi chấm.",
                "explanation": key.get("explanation", "") if valid_key else "",
                "source": {"url": quiz["url"],
                           "title": f"Google · Unit {quiz['unit']} · Pathway {quiz['pathway']}" + (" · Đáp án đã kiểm chứng" if verified else "")},
            })
        chapters.append({
            "number": number,
            "title": f"Unit {quiz['unit']} · Pathway {quiz['pathway']} · {quiz['title']}",
            "questions": questions,
        })
    return chapters, verified_count


def write_google_quiz(target, bank_page, bank_count):
    chapters, verified_count = load_google_questions()
    count = sum(len(chapter["questions"]) for chapter in chapters)
    status = (
        f"{verified_count}/{count} đáp án đã kiểm chứng bằng nút Submit answers trên Google. "
        "Giải thích do người biên soạn viết. Bao gồm Material Design."
    )
    page = (bank_page.replace("Ôn tập IT4785E", "Quizz Google")
            .replace(f"{bank_count} câu", f"{count} câu")
            .replace(f"0/{bank_count}", f"0/{count}")
            .replace("../IT4785E/data.js", "google.js")
            .replace('<a href="scans.html">Xem ảnh nguồn</a>',
                     '<p class="source-ref">Unit 1–3 · 9 pathway. ' + status + '</p>'))
    page = page.replace("</main>", ATTRIBUTION + "</main>")
    (target / "google.html").write_text(page, encoding="utf-8")
    (target / "google.js").write_text(
        'window.COURSE_CODE = "IT4785E";\nwindow.STUDY_MODE = "google";\n'
        + "window.CHAPTERS = " + json.dumps(chapters, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    return count
