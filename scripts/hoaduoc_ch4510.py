"""Generate the full CH4510 chapter 1–2 bank from the reviewed handoff."""

import json
import random
from pathlib import Path


# Clarify true/false keys and prompts whose original wording assumes a written answer.
REPHRASED = {
    "Q010": ("Hoạt chất đạt định lượng nhưng thiết bị gây nhiễm kim loại và nguyên liệu không rõ nguồn gốc. Có thể coi quy trình đạt yêu cầu không?",
             "Không, vì phải kiểm soát cả nhiễm tạp và nguồn gốc nguyên liệu."),
    "Q013": ("Nhận định “Có thể dùng không khí nén để vận chuyển dung môi hydrocarbon lỏng vì tiện và rẻ” đúng hay sai theo slide?",
             "Sai, vì oxy trong không khí có thể làm tăng nguy cơ cháy nổ."),
    "Q047": ("Nhận định “Thuốc gắn protein huyết tương đồng nghĩa thuốc đã bị phá hủy” đúng hay sai?",
             "Sai, vì gắn protein không đồng nghĩa với phân hủy hóa học."),
    "Q053": ("Phương án nào ghép đúng dạng tiêm, dạng viên, dạng uống lỏng, dạng mềm và dạng xịt với ví dụ tương ứng?",
             "Tiêm: tiêm bắp; viên: viên nén; uống lỏng: siro; dạng mềm: thuốc mỡ; dạng xịt: thuốc xịt."),
    "Q147": ("Điều gì xảy ra với tỉ lệ hai dạng liên hợp của acid yếu hoặc base yếu khi pH = pKa?",
             "Tỉ lệ bằng 1:1 trong mô hình cân bằng đang xét."),
    "Q160": ("Có thể kết luận gì về hoạt tính khi thay một nhóm bằng nhóm đẳng cấu điện tử?",
             "Hoạt tính có thể thay đổi theo hợp chất và phép thay. Không mặc định tăng."),
}


def write_ch4510(dist, template):
    source = json.loads(Path(__file__).with_name("hoaduoc_ch4510.json").read_text(encoding="utf-8"))
    choices_file = Path(__file__).with_name("hoaduoc_ch4510_choices.txt")
    distractors = {}
    for line in choices_file.read_text(encoding="utf-8").splitlines():
        number, *options = (field.strip() for field in line.split("|"))
        question_id = f"Q{number}"
        if question_id in distractors or len(options) != 3 or not all(options):
            raise ValueError(f"CH4510: phương án nhiễu không hợp lệ ở {question_id}")
        distractors[question_id] = options
    former_open = {item["id"] for item in source["questions"] if not item["options"]}
    if distractors.keys() != former_open:
        raise ValueError("CH4510: cần đúng một bộ phương án nhiễu cho mỗi câu chuyển thể")
    target = dist / "HOADUOC"
    chapters = [
        {"number": 1, "title": "Chương 1 · Đại cương, nghiên cứu và sản xuất", "questions": []},
        {"number": 2, "title": "Chương 2 · Cấu trúc và hoạt tính sinh học", "questions": []},
    ]
    ids = set()
    for item in source["questions"]:
        chapter = item["chapter"]
        pages = item["pages"]
        if chapter not in (1, 2) or not pages or any(not 1 <= page <= 107 for page in pages):
            raise ValueError(f"CH4510: nguồn ngoài phạm vi ở {item['id']}")
        if item["id"] in ids:
            raise ValueError(f"CH4510: trùng mã {item['id']}")
        ids.add(item["id"])
        question_id = item["id"]
        prompt, answer = REPHRASED.get(question_id, (item["q"], item["a"]))
        choices = item["options"]
        converted = not choices
        if converted:
            if question_id not in REPHRASED:
                prompt = f"Chọn phương án đúng cho yêu cầu sau. {prompt}"
            choices = [answer, *distractors[question_id]]
            random.Random(question_id).shuffle(choices)
        if len(set(choices)) != 4 or len(choices) != 4 or answer not in choices:
            raise ValueError(f"CH4510: đáp án trắc nghiệm không hợp lệ ở {question_id}")
        chapters[chapter - 1]["questions"].append({
            "id": question_id,
            "text": prompt,
            "type": "single",
            "options": [{"id": str(i), "text": text} for i, text in enumerate(choices)],
            "answers": [str(choices.index(answer))],
            "modelAnswer": answer,
            "convertedToQuiz": converted,
            "explanation": item["e"],
            "origin": item["origin"],
            "topic": item["topic"],
            "kind": item["kind"],
            "flag": item["flag"],
            "slidePages": pages,
            "plain": True,
        })

    coverage = source["coverage"]
    if [item["page"] for item in coverage] != list(range(1, 108)):
        raise ValueError("CH4510: bản đồ trang PDF không đầy đủ")
    if any(not (target / "chuong-1-2-slides" / f"{page:03}.jpg").is_file() for page in range(1, 108)):
        raise ValueError("CH4510: thiếu ảnh slide gốc")

    count = sum(len(chapter["questions"]) for chapter in chapters)
    (target / "chuong-1-2.js").write_text(
        'window.COURSE_CODE = "HOADUOC";\nwindow.STUDY_MODE = "ch4510";\nwindow.CHAPTERS = '
        + json.dumps(chapters, ensure_ascii=False, indent=2) + ';\n', encoding="utf-8",
    )

    guide = f"""<p class="source-ref">{count} câu trắc nghiệm một đáp án · Chấm tự động</p>
<details class="study-guide"><summary>Phạm vi và hướng ôn</summary>
<p>Chương 1 từ trang PDF 1–75. Chương 2 từ trang 76–107. Bộ câu hỏi tổng hợp từ slide cô Mỵ, Câu hỏi Hóa Dược 1 và bộ câu hỏi CH4510. Mỗi lời giải ghi nguồn hình thành câu và có ảnh slide để đối chiếu. Ký hiệu P là vị trí đoạn trong bộ Word.</p>
<p><strong>Hướng ôn dự đoán từ bài giảng:</strong> luyện đọc chuỗi tổng hợp và vai trò tác nhân, bảng nguồn–hoạt chất–tác dụng, R–D–P và các bước nghiên cứu. Với chương 2, ưu tiên cấu trúc–hoạt tính, đẳng cấu, pH–pKa, độ tan và đọc đồ thị. Đây là gợi ý ôn tập, chưa có ma trận thi chính thức.</p>
<p><strong>Các trang cần đối chiếu:</strong> 13 (công thức quặng), 28 và 40–41 (tiền lâm sàng), 39 (chỉ số điều trị), 53 (NADPH/DOPA), 74 (hydrazide), 76–80 (khái quát nhóm chức), 81 và 83 (ví dụ đối quang), 86–87 (hệ số phân bố và khí thực), 90–92 (mô hình khoảng cách), 98 (đơn vị bước sóng), 106 (ester/ether).</p>
<p>Các câu thực hành hoặc câu thuộc chương sau được đối chiếu để chọn phần liên quan đến chương 1–2. Câu chuyển thể hoặc mở rộng có ghi nguồn riêng trong lời giải.</p>
</details>"""
    page = (template.replace("__COURSE__", "HOADUOC")
            .replace("Ôn tập HOADUOC", "CH4510 · Hóa dược đại cương")
            .replace("__TOTAL__", str(count))
            .replace("__SOURCE_LINK__", guide)
            .replace("../HOADUOC/data.js", "chuong-1-2.js")
            .replace('<link rel="stylesheet" href="../style.css">',
                     '<link rel="stylesheet" href="../style.css"><link rel="stylesheet" href="chemistry.css">'))
    (target / "chuong-1-2.html").write_text(page, encoding="utf-8")
    return f'<a class="secondary course-link" href="./HOADUOC/chuong-1-2.html">CH4510 · Hóa dược đại cương<span>{count} câu · Chương 1–2</span></a>'
