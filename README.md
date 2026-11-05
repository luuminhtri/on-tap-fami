# Góc ôn tập xác suất thống kê

Web tĩnh với 60 câu từ chap1–chap4. Mở `dist/index.html` trực tiếp hoặc chạy:

```sh
python3 -m http.server 4173 --directory dist
```

Chọn chương hoặc tất cả chương. Mỗi bộ có tiến độ và đồng hồ riêng, lưu trong localStorage của trình duyệt. Đồng hồ dừng khi đóng trang, tạm dừng hoặc hoàn thành bộ. Chỉ câu đã xác nhận được tính là đã làm. Câu nhiều đáp án phải chọn đủ và không chọn thừa mới được tính đúng. Đáp án lấy nguyên từ JSON, chưa thẩm định nội dung học thuật.

KaTeX được đóng gói cục bộ nên không cần CDN để hiển thị công thức. JSON gốc không bị sửa; data.js chỉ chứa nội dung câu hỏi và đáp án, không chứa thông tin người tạo/phản biện.
