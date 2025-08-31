# Python 13

```bash
python -m venv health-chatbot
pip install -r requirements.txt
uvicorn main:app 
```
# Config PowerShell
```bash
$token = ""
$id = ""

curl.exe -X POST "http://127.0.0.1:8000/ask" `
   -H "Authorization: Bearer $token" `
   -H "Patient-Id: $id" `
   -F "question=Chiều cao của tôi"
```


# Note
## optimize -> optimize
## note -> fix hoặc rewrite: being process

# Update v1.1
## Add summary record: Tổng hợp lời khuyên: bao gồm {name-value-date}, {lời khuyên} và {} tổng hợp chi tiết: {"metric":"bmi","title":"Chỉ số khối cơ thể (BMI)","value":27.47,"unit":null,"date":"2025-08-23","status":"not_good","label":"Béo phì độ I","advice_top":"Theo dõi năng lượng, tăng vận động >=150 phút/tuần."}
## Optimize error code: Trả về lỗi tường minh hơn:
   - BAD_REQUEST (-): Chưa đăng nhập
   - AUTH_EXPIRED (401,403): Chưa đăng nhập
   - PATIENT_NOT_FOUND (404): Ko tìm thấy dữ liệu khám
   - UPSTREAM_UNAVAILABLE/Exception (500-599): API ko phản hồi | error message
## Fix bug luôn luôn gọi API kết quả xét nghiệm kể cả khi chỉ hỏi hướng dẫn web
## Fix lỗi reponse của phần hướng dẫn web
## Fix retry timeout quá lâu: Dùng hàm Retry và HTTPAdapter để tự kết nối lại retry 1 lần tổng 2. Case test mẫu: 
   - Kẹt ở kết nối (connect timeout) cả 2 lần: (lỗi mạng API)
      Lần 1: 3s (connect timeout) + backoff 0.3s
      Lần 2: 3s (connect timeout)
      TOTAL = ~6.3s
   - Kẹt 503 lần 1: (lỗi mạng/đường truyền chậm)
      Lần 1: get 503 + backoff 0.3s
      Lần 2: trả (200 or 503)
      TOTAL = ~0.3s + (nếu lần 2 chậm có thể tới read timeout 5s ->  = ~5.3s)
   - Kết nối lần đầu timeout, lần 2 kết nối ok nhưng treo đọc (read timeout) (lỗi mạng/đường truyền chậm)
      Lần 1: 3s (connect timeout) + backoff 0.3s
      Lần 2: OK, read timeout 5s
      TOTAL = ~8.3s
   - Trường hợp tốt nhất (Trường hợp bình thường):
      Lần 1: OK (~0.3s) + read (~0.3s)
      TOTAL = ~0.6s
