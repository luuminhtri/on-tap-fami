# Rà soát IT4785E — 10/11/2026

Đã rà soát 260 bản câu hỏi đề cũ (105 nhóm trùng nội dung) và 87 câu Google Unit 1–3. Mỗi câu có giải thích tiếng Việt và liên kết kiến thức chính thức. Bộ Giữa kì 106 câu kế thừa cùng đáp án/lời giải từ hai nguồn này; không có bản đáp án riêng dễ lệch nhau.

## Phân biệt nguồn đáp án

- 87 đáp án Google giữ nguyên fingerprint, tập lựa chọn và bằng chứng Submit đã lưu từ lần kiểm chứng trước. Lần này rà lại kiến thức, viết giải thích chi tiết hơn và bổ sung tài liệu liên quan, không tuyên bố đã submit lại.
- Đề cũ được suy luận/đối chiếu tài liệu Android, Kotlin; không coi dấu khoanh trên ảnh là đáp án chính thức. 221 câu có đủ điều kiện chấm; 39 câu còn thiếu dữ kiện, OCR bị cắt hoặc có nhiều cách hiểu được giữ để ôn nhưng không tính điểm.
- Các phát biểu đơn giản hóa của bài nhập môn được giải thích giới hạn, như Unit của hàm thân khối, vector trong bài adaptive icon và Column so với LazyColumn. Không biến đáp án kỳ vọng của quiz thành quy tắc tuyệt đối.

## Thay đổi tập đáp án so với dữ liệu trước

Các chữ cái ở đây là ID trong đề gốc, không phải vị trí sau khi xáo trộn.

| Mã câu | Trước | Sau | Lý do |
| --- | --- | --- | --- |
| 20231-1-26, 20231-2-7, 20231-4-12 | Không chấm | A, C | Abstract class: phân tích từng phát biểu, không coi lớp abstract luôn có thành viên chưa triển khai. |
| 20231-1-29, 20231-3-15, 20231-4-30 | D | Không chấm | Dialog của chính Activity khác Activity có giao diện dialog; đề thiếu phân biệt. |
| 20231-2-1 | Không chấm | E | Sửa lỗi OCR `Intent ACTION VIEW` thành `Intent.ACTION_VIEW`. |
| 20231-4-34 | A | Không chấm | Nhận định luôn mở chooser cũng sai khi đã có app mặc định; đề chỉ cho chọn một. |
| 20231-4-36 | A, B, C | Không chấm | Lựa chọn D vẫn bị cắt giữa câu trong dữ liệu nguồn. |
| 20231-2-20, 20231-3-34 | Không chấm | A | Lớp cha trực tiếp của RadioGroup là LinearLayout. |
| 20231-2-28 | Không chấm | C | Cách gọi phiên bản công khai bỏ tên món ăn từ Android 10. |
| 20231-3-4 | Không chấm | B, D | onViewCreated: liên kết view và cấu hình view; khác inflate trong onCreateView. |
| 20241-4-3 | Không chấm | B | Ảnh vuông 200×200 trong vùng vuông 100×100: center không scale, ba chế độ còn lại cho 100×100. |

Ngoài ra đã sửa `dpi` thành `xhdpi` trong lựa chọn mật độ icon ở cả bốn bản câu, thay vì chỉ sửa bản Giữa kì.

## Duy trì dữ liệu

- `scripts/it4785e_reviews.json` lưu giải thích, nguồn, các tập đáp án đã rà soát và fingerprint từng câu; JSON/ảnh nguồn không bị sửa.
- `scripts/it4785e_review.py` dừng quá trình tạo web nếu câu thay đổi hoặc có câu mới chưa được rà soát. Tránh âm thầm dùng đáp án cũ cho nội dung mới.
- `scripts/google_quiz_answers.json` giữ bằng chứng kiểm chứng và giải thích Google. Fingerprint kiểm tra nội dung quiz đã tải.
- Giữ nguyên ID câu, lựa chọn và khóa lưu tiến độ để các bài đang làm được giữ lại. Điểm được tính lại theo tập đáp án hiện tại; câu không chấm bị loại khỏi tổng đúng/sai.

## Kiểm tra

Đã chạy quy trình chọn đáp án/xác nhận trên trình duyệt cho 260 câu ngân hàng, 106 câu Giữa kì và 87 câu Google (có xáo trộn). Kiểm tra lời giải ẩn trước xác nhận, hiện sau xác nhận và có liên kết tài liệu; 39 câu không chấm không bị tính sai. Đã kiểm tra 77 URL tài liệu phản hồi thành công.

Chạy `python3 scripts/import_questions.py`, `python3 scripts/test_it4785e_review.py` và `node --check dist/app.js` trước khi cập nhật web.
