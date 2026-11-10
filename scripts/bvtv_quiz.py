"""Build the CH4486 practice set from reviewed questions for chapters 1–3."""

import json
import random
from pathlib import Path


REFERENCES = {
    "definition": ("US EPA · Định nghĩa pesticide", "https://www.epa.gov/minimum-risk-pesticides/what-pesticide"),
    "ddt": ("US EPA · Lịch sử DDT", "https://www.epa.gov/ingredients-used-pesticide-products/ddt-brief-history-and-status"),
    "biopesticide": ("US EPA · Thuốc BVTV sinh học", "https://www.epa.gov/ingredients-used-pesticide-products/what-are-biopesticides"),
    "epa": ("US EPA · Tài liệu đào tạo về thuốc BVTV", "https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P1017DIK.TXT"),
    "who": ("WHO · Phân loại theo mức nguy hại", "https://www.who.int/publications/i/item/9789240005662"),
    "irac": ("IRAC · Quản lý kháng thuốc", "https://irac-online.org/mode-of%20action/classification-online/"),
    "formulation": ("FAO/WHO · Dạng chế phẩm", "https://www.fao.org/agriculture/crops/thematic-sitemap/theme/pests/jmps/manual/en/"),
    "fate": ("US EPA · Đường đi trong môi trường", "https://www.epa.gov/pesticide-science-and-assessing-pesticide-risks/technical-overview-ecological-risk-assessment-1"),
    "dt": ("US EPA · DT₅₀ và động học phân hủy", "https://www.epa.gov/pesticide-science-and-assessing-pesticide-risks/guidance-calculate-representative-half-life-values"),
    "tlv": ("ACGIH · Giới hạn phơi nhiễm nghề nghiệp", "https://www.acgih.org/science/tlv-bei-guidelines/tlv-chemical-substances-introduction/"),
    "codex": ("Codex · Thuật ngữ dư lượng", "https://codex.fao.org/codex-texts/codex-online-databases/pesticides-residues/glossary"),
    "jmpr": ("FAO/WHO · Đánh giá dư lượng", "https://www.fao.org/agriculture/crops/thematic-sitemap/theme/pests/jmpr/am/"),
    "aid": ("US EPA · Sơ cứu khi phơi nhiễm", "https://www.epa.gov/pesticide-incidents/first-aid-case-pesticide-exposure"),
}


def load_questions():
    chapters = []
    seen_ids = set()
    bank = Path(__file__).with_name("bvtv_questions.txt")
    for line in bank.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            number, title = line[2:].split("|")
            chapters.append({"number": int(number), "title": title, "questions": []})
            continue
        number, pages, reference, prompt, *choices, explanation = line.split("|")
        chapter = chapters[-1]
        question_id = f"bvtv-{chapter['number']}-{number}"
        options = [
            {"id": str(i), "text": choice.removeprefix("+")}
            for i, choice in enumerate(choices)
        ]
        answers = [str(i) for i, choice in enumerate(choices) if choice.startswith("+")]
        if (question_id in seen_ids or len(options) != 4 or not 1 <= len(answers) < len(options)
                or len({o["text"] for o in options}) != 4 or not all((pages, prompt, explanation))):
            raise ValueError(f"Invalid CH4486 question: {question_id}")
        seen_ids.add(question_id)
        random.Random(question_id).shuffle(options)
        question = {
            "id": question_id,
            "text": prompt,
            "type": "multi" if len(answers) > 1 else "single",
            "options": options,
            "answers": answers,
            "explanation": explanation,
            "source": {"pdfPages": pages},
        }
        if reference:
            title, url = REFERENCES[reference]
            question["references"] = [{"title": title, "url": url}]
        chapter["questions"].append(question)
    if [chapter["number"] for chapter in chapters] != [1, 2, 3] or not all(c["questions"] for c in chapters):
        raise ValueError("CH4486 must include questions for chapters 1–3")
    return chapters


def write_bvtv(dist, template):
    chapters = load_questions()
    count = sum(len(chapter["questions"]) for chapter in chapters)
    target = dist / "CH4486"
    target.mkdir(exist_ok=True)
    (target / "data.js").write_text(
        'window.COURSE_CODE = "CH4486";\nwindow.CHAPTERS = '
        + json.dumps(chapters, ensure_ascii=False, indent=2) + ';\n', encoding="utf-8",
    )
    page = (template.replace("__COURSE__", "CH4486")
            .replace("Ôn tập CH4486", "Hóa học Bảo vệ thực vật · CH4486")
            .replace("__TOTAL__", str(count))
            .replace("__SOURCE_LINK__", '<p class="source-ref">Chương 1–3 · Giải thích sau khi xác nhận</p>'))
    (target / "index.html").write_text(page, encoding="utf-8")
    return f'<a class="secondary course-link" href="./CH4486/">CH4486 · Hóa học Bảo vệ thực vật<span>{count} câu · Chương 1–3</span></a>'
