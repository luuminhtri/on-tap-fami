import json
import re
from pathlib import Path

project = Path(__file__).resolve().parents[1]
dist = project / "dist"


def normalize(text):
    def table(match):
        rows = [
            row.strip().replace("$", "")
            for row in match.group(1).split(r"\hline")
            if row.strip()
        ]
        columns = max(row.count("&") + 1 for row in rows)
        return (
            r"$\begin{array}{|" + "c|" * columns + r"}\hline "
            + r" \\\hline ".join(rows) + r"\\\hline\end{array}$"
        )

    return re.sub(r"\$\\begin\{tabular\}(.*?)\\end\{tabular\}\$", table, text, flags=re.S)


def read_chapter(path, number, used_ids):
    rows = json.loads(path.read_text(encoding="utf-8"))["list"]
    if not rows:
        raise ValueError(f"{path}: chương không có câu hỏi")
    questions = []
    for row in rows:
        raw = row["cau_hoi"]
        question_id = str(raw["id"])
        if question_id in used_ids:
            raise ValueError(f"{path}: trùng mã câu hỏi {question_id} trong cùng môn")
        used_ids.add(question_id)
        options = [
            {"id": option["id"], "text": normalize(option["content"])}
            for option in raw["lua_chon"]
        ]
        answers = raw["dap_an"]
        if not answers or not set(answers) <= {option["id"] for option in options}:
            raise ValueError(f"{path}: đáp án không hợp lệ ở câu {question_id}")
        questions.append({
            "id": question_id,
            "text": normalize(raw["noi_dung"]),
            "type": raw["loai"],
            "options": options,
            "answers": answers,
        })
    return {"number": number, "title": rows[0]["chuong"]["ten"], "questions": questions}


courses = {}
for folder in sorted(project.parent.iterdir()):
    if not folder.is_dir() or not re.fullmatch(r"[A-Z][A-Z0-9_-]*", folder.name):
        continue
    files = []
    for path in folder.glob("chap*.json"):
        match = re.fullmatch(r"chap([1-9][0-9]*)\.json", path.name)
        if match:
            files.append((int(match[1]), path))
    if files:
        used_ids = set()
        courses[folder.name] = [
            read_chapter(path, number, used_ids) for number, path in sorted(files)
        ]

if not courses:
    raise SystemExit("Không tìm thấy bộ câu hỏi. Hãy thêm thư mục mã môn cạnh on-tap-web.")

template = (project / "scripts/course.html").read_text(encoding="utf-8")
links = []
for code, chapters in courses.items():
    count = sum(len(chapter["questions"]) for chapter in chapters)
    target = dist / code
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text(
        template.replace("__COURSE__", code).replace("__TOTAL__", str(count)), encoding="utf-8"
    )
    (target / "data.js").write_text(
        f"window.COURSE_CODE = {json.dumps(code)};\n"
        + "window.CHAPTERS = " + json.dumps(chapters, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    links.append(f'<a class="secondary course-link" href="./{code}/">{code}<span>{count} câu</span></a>')
    print(f"/{code} · {len(chapters)} chương · {count} câu")

home = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chọn môn ôn tập</title>
<link rel="stylesheet" href="style.css">
<script>try{document.documentElement.dataset.theme=localStorage.getItem('xstk-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')}catch{}</script>
</head>
<body><main><section class="setup panel">
<h1>Chọn môn ôn tập</h1>
__LINKS__
</section></main></body></html>
"""
(dist / "index.html").write_text(home.replace("__LINKS__", "\n".join(links)), encoding="utf-8")
