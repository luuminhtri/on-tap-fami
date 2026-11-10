"""Map the old IT4785E questions to the November 2026 midterm scope."""

from copy import deepcopy
import json

from google_quiz import ATTRIBUTION, load_google_questions, write_google_quiz


# The first ID is the displayed question. Other IDs retain the sources of
# equivalent copies, including copies with options in a different order.
TOPICS = {
    "Kotlin · Cơ bản": [
        "20231-1-22 20231-2-18 20231-3-18 20231-4-35 20241-1-15",
        "20241-1-8 20241-3-16",
        "20241-1-11 20241-2-12 20241-3-10 20241-4-1",
        "20241-2-4 20241-4-17",
        "20241-2-16",
        "20241-4-5",
    ],
    "Kotlin · Hàm": [
        "20231-1-5 20231-2-45 20231-3-6 20231-4-38",
        "20231-1-34 20231-2-43 20231-3-39 20231-4-9",
        "20241-1-9",
        "20241-2-1 20241-3-2",
        "20241-3-4 20241-4-7",
        "20241-3-12",
    ],
    "Kotlin · Lớp và đối tượng": [
        "20231-1-26 20231-2-7 20231-4-12",
        "20231-1-28 20231-2-26 20231-3-33 20231-4-19",
        "20241-1-5",
    ],
    "Android · Introduction và Compose Unit 1": [
        "20231-1-1 20231-2-42 20241-4-19",
        "20231-1-14 20231-2-6 20231-3-30 20231-4-39",
        "20231-1-32 20231-2-44 20231-3-31 20231-4-8",
        "20231-1-33 20231-2-24 20231-3-25 20231-4-6",
        "20231-1-36 20231-2-11 20231-4-16",
        "20231-1-39 20231-2-15 20231-4-41",
        "20241-1-2 20241-2-13",
        "20241-1-4",
        "20241-1-10 20241-4-15",
        "20241-1-14",
        "20241-2-3 20241-4-11",
        "20241-2-15",
        "20241-2-17",
        "20241-3-19 20241-4-6",
    ],
    "Compose Unit 3 · Launcher icons": [
        "20231-1-37 20231-2-12 20231-3-43 20231-4-17",
    ],
}

# Material containers, theming, shape, color, elevation and dark-theme theory.
# Animation, preview, accessibility, Kotlin and core layouts stay in scope.
GOOGLE_EXCLUDED = {
    "google-u1-p2-q8", "google-u1-p2-q10",
    "google-u3-p3-q4", "google-u3-p3-q5", "google-u3-p3-q7",
    "google-u3-p3-q8", "google-u3-p3-q9", "google-u3-p3-q10",
}

# Reviewed semantic duplicates. Keep the existing ID so saved answers survive.
GOOGLE_DUPLICATES = {
    "google-u1-p3-q3": "google-u1-p2-q7",  # @Composable annotation
    "google-u1-p3-q6": "20241-1-4",       # Generated R class
    "google-u3-p2-q8": "google-u2-p2-q6", # Column vertical layout
}

NOTE = (
    "Ôn giữa kì 11/11/2026 từ đề cũ và quiz Google Unit 1–3, "
    "đã gộp câu trùng và bỏ Material Design. "
    "Đáp án câu Google đã được kiểm chứng bằng Submit."
)


def add_google_midterm(midterm):
    google, _ = load_google_questions()
    retained = {q["id"]: q for chapter in midterm for q in chapter["questions"]}
    for chapter in google:
        questions = []
        for original in chapter["questions"]:
            if original["id"] in GOOGLE_EXCLUDED:
                continue
            question = deepcopy(original)
            duplicate = GOOGLE_DUPLICATES.get(question["id"])
            if duplicate:
                retained[duplicate].setdefault("otherSources", []).append(question["source"])
                continue
            retained[question["id"]] = question
            questions.append(question)
        if questions:
            midterm.append({
                "number": len(midterm) + 1,
                "title": "Google · " + chapter["title"],
                "questions": questions,
            })



def write_mobile_pages(target, bank, bank_html):
    by_id = {question["id"]: question for chapter in bank for question in chapter["questions"]}
    midterm = []
    for number, (title, groups) in enumerate(TOPICS.items(), 1):
        questions = []
        for group in groups:
            first, *other_ids = group.split()
            question = deepcopy(by_id[first])
            if other_ids:
                question["otherSources"] = [by_id[item]["source"] for item in other_ids]
            questions.append(question)
        midterm.append({"number": number, "title": title, "questions": questions})

    add_google_midterm(midterm)
    midterm_count = sum(len(chapter["questions"]) for chapter in midterm)
    bank_count = sum(len(chapter["questions"]) for chapter in bank)
    back = 'href="../index.html" class="secondary">← Chọn môn'
    bank_page = bank_html.replace(back, 'href="./" class="secondary">← IT4785E')
    (target / "bank.html").write_text(bank_page.replace("Ôn tập IT4785E", "Ngân hàng câu hỏi"), encoding="utf-8")

    midterm_page = (
        bank_page.replace("Ôn tập IT4785E", "Giữa kì")
        .replace(f"{bank_count} câu", f"{midterm_count} câu")
        .replace(f"0/{bank_count}", f"0/{midterm_count}")
        .replace("../IT4785E/data.js", "midterm.js")
        .replace('<a href="scans.html">Xem ảnh nguồn</a>', f'<p class="source-ref">{NOTE}</p>')
    )
    midterm_page = midterm_page.replace("</main>", ATTRIBUTION + "</main>")
    (target / "midterm.html").write_text(midterm_page, encoding="utf-8")
    (target / "midterm.js").write_text(
        'window.COURSE_CODE = "IT4785E";\nwindow.STUDY_MODE = "midterm";\n'
        + "window.CHAPTERS = " + json.dumps(midterm, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    google_count = write_google_quiz(target, bank_page, bank_count)
    theme = bank_html[bank_html.index("<script>"):bank_html.index("</script>") + len("</script>")]
    (target / "index.html").write_text(f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>IT4785E · Mobile Programming</title>
<link rel="stylesheet" href="../style.css">
{theme}
</head>
<body><main>
<div class="topbar"><a href="../index.html" class="secondary">← Chọn môn</a></div>
<section class="setup panel">
<h1>IT4785E · Mobile Programming</h1>
<a class="secondary course-link" href="midterm.html">Giữa kì<span>{midterm_count} câu</span></a>
<p class="source-ref">{NOTE}</p>
<a class="secondary course-link" href="bank.html">Ngân hàng câu hỏi<span>{bank_count} câu · 8 bộ</span></a>
<a class="secondary course-link" href="google.html">Quizz Google<span>{google_count} câu · 9 pathway</span></a>
</section>
</main></body></html>
""", encoding="utf-8")
