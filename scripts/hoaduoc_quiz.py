"""Generate the slide-based chemistry practice bank and its study guide."""
import json
import random
from pathlib import Path


def write_hoaduoc(dist, template):
    project = Path(__file__).resolve().parents[1]
    chapters = []
    for line in (project / "scripts/hoaduoc_questions.txt").read_text().splitlines():
        if line.startswith("# "):
            number, title = line[2:].split("|")
            chapters.append({"number": int(number), "title": title, "questions": []})
            continue
        page, text, correct, *rest = line.split("|")
        wrong, explanation = rest[:3], rest[3]
        index = sum(len(c["questions"]) for c in chapters) + 1
        options = [correct, *wrong]
        random.Random(index).shuffle(options)
        chapters[-1]["questions"].append({
            "id": f"hd-{index:03}", "text": text, "type": "single",
            "options": [{"id": str(i), "text": t} for i, t in enumerate(options)],
            "answers": [str(options.index(correct))], "explanation": explanation,
            "source": {"term": "slide", "pages": [int(page)], "number": index},
        })
    multi = [
        (1, 13, "Chọn các chất được liệt kê trong nhóm nguyên liệu vô cơ ở trang 13.",
         [r"$\mathrm{BaSO_4}$", r"$\mathrm{MnO_2}$", "Morphine", "Insulin"], ["0", "1"],
         "Barite và pyrolusite là ví dụ khoáng sản. Morphine và insulin thuộc các ví dụ nguồn khác."),
        (2, 50, "Chọn các vấn đề được tối ưu ở giai đoạn pilot.",
         ["Phương thức nạp nguyên liệu", "Thu hồi dung môi", "Khả năng tinh chế", "Chỉ chọn tên thương mại"], ["0", "1", "2"],
         "Pilot cần tối ưu thao tác, dung môi, tinh chế, thiết bị, an toàn và các yếu tố vận hành."),
        (5, 84, "Chọn các tính chất được liệt kê trong mục 2.2.",
         ["Độ hòa tan", "Hằng số phân ly", "Thế oxi hóa khử", "Giá niêm yết"], ["0", "1", "2"],
         "Các mục này xét quan hệ giữa tính chất vật lý và hoạt tính sinh học.")
    ]
    for group, page, text, options, answers, explanation in multi:
        chapters[group - 1]["questions"].append({
            "id": f"hd-m{group}", "text": text, "type": "multi",
            "options": [{"id": str(i), "text": t} for i, t in enumerate(options)],
            "answers": answers, "explanation": explanation,
            "source": {"term": "slide", "pages": [page], "number": group},
        })
    target = dist / "HOADUOC"
    target.mkdir(exist_ok=True)
    count = sum(len(c["questions"]) for c in chapters)
    (target / "questions.json").write_text(json.dumps(chapters, ensure_ascii=False, indent=2))
    (target / "data.js").write_text('window.COURSE_CODE = "HOADUOC";\nwindow.CHAPTERS = ' + json.dumps(chapters, ensure_ascii=False) + ';\n')
    guide = """<details class="study-guide" open><summary>Cách ôn từ mất gốc</summary>
    <p>Học lần lượt 6 cụm dưới đây. Mỗi lượt khoảng 10–15 câu. Đọc câu, tự giải thích rồi mới chọn và xác nhận. Sau khi xem giải thích, bấm số trang nguồn để đối chiếu slide.</p>
    <ol><li>Lượt đầu chọn từng cụm, giữ thứ tự câu để xây nền tảng.</li>
    <li>Làm lại câu sai, tự nói lý do loại từng phương án. Câu đoán đúng cũng nên xem lại.</li>
    <li>Ngày hôm sau và sau 3 ngày, làm lại cụm đã học. Khi đã quen, chọn nhiều cụm và bật xáo trộn để luyện trắc nghiệm.</li></ol>
    <p>Phản ứng hóa học cần nhớ chất đầu → tác nhân → nhóm chức sản phẩm. Với pH–pKa, xác định acid/base và dạng ion hóa trước khi tính.</p>
    <p>Bộ câu hỏi tự soạn từ chương 1–2, trang PDF 1–107, có giải thích sau xác nhận. Đây là bộ luyện kiến thức, chưa có căn cứ để dự đoán tỉ lệ câu trong đề thi.</p>
    <p>Lưu ý đối chiếu với cô về các trang 28, 40 (thuật ngữ tiền lâm sàng), 39 (chỉ số điều trị), 81, 83 (ví dụ đồng phân), 98 (đơn vị bước sóng). Các mệnh đề dễ sai ở những chỗ này được tránh trong đáp án chấm điểm. Các nhận xét khái quát về nhóm chức được ghi rõ là theo slide.</p></details>"""
    page = template.replace("__COURSE__", "HOADUOC").replace("__TOTAL__", str(count)).replace("__SOURCE_LINK__", guide)
    page = page.replace("Ôn tập HOADUOC", "Hóa dược · Ôn giữa kì")
    page = page.replace('<link rel="stylesheet" href="../style.css">', '<link rel="stylesheet" href="../style.css"><link rel="stylesheet" href="chemistry.css">')
    (target / "index.html").write_text(page)
    (target / "chemistry.css").write_text("""
.study-guide {margin:1.2rem 0;line-height:1.7}
.study-guide summary {cursor:pointer;font-weight:700}
.study-guide p,.study-guide li {max-width:75ch}
body:has(.study-guide) .katex {font-size:1.12em}
.katex-display {overflow-x:auto;overflow-y:hidden;padding:.6rem 0}
.content {min-width:0;overflow-wrap:anywhere}
.content .katex {white-space:nowrap}
.question-text {line-height:1.8}
.result {line-height:1.7}
""")
    return f'<a class="secondary course-link" href="./HOADUOC/">Hóa dược · Giữa kì<span>{count} câu · Chương 1–2</span></a>'
