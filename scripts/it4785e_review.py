"""Apply the per-question IT4785E review without changing original source scans."""
import hashlib
import json
from pathlib import Path


def fingerprint(question):
    content = {key: question[key] for key in ("text", "type", "options", "fields") if key in question}
    return hashlib.sha256(json.dumps(content, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def review_bank(chapters):
    review = json.loads(Path(__file__).with_name("it4785e_reviews.json").read_text())
    questions = {q["id"]: q for chapter in chapters for q in chapter["questions"]}
    reviewed = set()
    for group in review["groups"]:
        for question_id, result in group["questions"].items():
            if question_id in reviewed:
                raise ValueError(f"Duplicate IT4785E review: {question_id}")
            reviewed.add(question_id)
            question = questions[question_id]
            if fingerprint(question) != result["fingerprint"]:
                raise ValueError(f"IT4785E {question_id}: nội dung đã thay đổi, cần rà lại đáp án/lời giải")
            if "options" in result:
                question["options"] = result["options"]
            question["answers"] = result["answers"]
            if not set(question["answers"]) <= {o["id"] for o in question["options"]}:
                raise ValueError(f"Invalid reviewed answer: {question_id}")
            question.update(
                explanation=group["explanation"],
                references=group["references"],
                reviewedOn=review["reviewedOn"],
                plain=True,
                note="" if question["answers"] or question.get("fields") else
                    "Câu chưa đủ điều kiện để chấm điểm. Xác nhận để xem phân tích.",
            )
    if reviewed != questions.keys():
        raise ValueError(f"IT4785E còn câu chưa rà soát: {questions.keys() - reviewed}")
