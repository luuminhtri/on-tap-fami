import hashlib
import json
import re
from pathlib import Path

from mobile_midterm import write_mobile_pages
from it4785e_review import review_bank
from hoaduoc_quiz import write_hoaduoc

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
        has_source = "source" in raw
        if (not answers and not has_source) or not set(answers) <= {option["id"] for option in options}:
            raise ValueError(f"{path}: đáp án không hợp lệ ở câu {question_id}")
        questions.append({
            "id": question_id,
            "text": normalize(raw["noi_dung"]),
            "type": raw["loai"],
            "options": options,
            "answers": answers,
            **{key: raw[key] for key in ("source", "note", "fields", "plain") if key in raw},
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
    page = template.replace("__COURSE__", code).replace("__TOTAL__", str(count)).replace(
        "__SOURCE_LINK__",
        '<a href="scans.html">Xem ảnh nguồn</a>' if code == "IT4785E" else "",
    )
    if code == "IT4785E":
        review_bank(chapters)
        write_mobile_pages(target, chapters, page)
    else:
        (target / "index.html").write_text(page, encoding="utf-8")
    (target / "data.js").write_text(
        f"window.COURSE_CODE = {json.dumps(code)};\n"
        + "window.CHAPTERS = " + json.dumps(chapters, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    label = 'IT4785E · Mobile Programming' if code == 'IT4785E' else code
    links.append(f'<a class="secondary course-link" href="./{code}/">{label}<span>{count} câu</span></a>')
    print(f"/{code} · {len(chapters)} chương · {count} câu")

links.append(write_hoaduoc(dist, template))

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


# Change asset URLs with their contents so cached scripts cannot break newer HTML.
for page_path in dist.rglob("*.html"):
    def version_asset(match):
        attribute, url = match.groups()
        asset_path = page_path.parent / url
        if not asset_path.is_file():
            return match.group(0)
        version = hashlib.sha256(asset_path.read_bytes()).hexdigest()[:12]
        return f'{attribute}="{url}?v={version}"'

    markup = re.sub(
        r'(src|href)="([^"?:]+\.(?:js|css))(?:\?[^" ]*)?"',
        version_asset,
        page_path.read_text(encoding="utf-8"),
    )
    page_path.write_text(markup, encoding="utf-8")
