# Python 13 - Health Chatbot

## Cài đặt môi trường
```bash
python -m venv health-chatbot
pip install -r requirements.txt
uvicorn main:app
```

---

## Config PowerShell
```powershell
$token = ""
$id = ""

curl.exe -X POST "http://127.0.0.1:8000/ask" `
   -H "Authorization: Bearer $token" `
   -H "Patient-Id: $id" `
   -F "question=Chiều cao của tôi"
```

---

## Ghi chú
- `optimize` → **optimize**
- `note` → **fix** hoặc **rewrite: being process**

---

## Update v1.1

### Thêm tính năng
- **Summary record**: Tổng hợp lời khuyên bao gồm:
  - `{name-value-date}`
  - `{lời khuyên}`
  - Chi tiết JSON:
    ```json
    {
      "metric": "bmi",
      "title": "Chỉ số khối cơ thể (BMI)",
      "value": 27.47,
      "unit": null,
      "date": "2025-08-23",
      "status": "not_good",
      "label": "Béo phì độ I",
      "advice_top": "Theo dõi năng lượng, tăng vận động >=150 phút/tuần."
    }
    ```

### Tối ưu mã lỗi
- `BAD_REQUEST (-)` → Chưa đăng nhập  
- `AUTH_EXPIRED (401,403)` → Chưa đăng nhập  
- `PATIENT_NOT_FOUND (404)` → Không tìm thấy dữ liệu khám  
- `UPSTREAM_UNAVAILABLE / Exception (500-599)` → API không phản hồi | error message  

### Fix bugs
- Luôn gọi API kết quả xét nghiệm ngay cả khi chỉ hỏi hướng dẫn web → **đã fix**  
- Lỗi response của phần hướng dẫn web → **đã fix**  
- Retry timeout quá lâu → **đã tối ưu** bằng `Retry` + `HTTPAdapter`  
  - **Case test mẫu**:  

    1. **Connect timeout cả 2 lần (lỗi mạng API)**  
       - Lần 1: 3s + backoff 0.3s  
       - Lần 2: 3s  
       - **TOTAL ≈ 6.3s**

    2. **503 lần 1 (lỗi mạng/đường truyền chậm)**  
       - Lần 1: 503 + backoff 0.3s  
       - Lần 2: 200 hoặc 503  
       - **TOTAL ≈ 0.3s → 5.3s**

    3. **Timeout lần đầu, lần 2 OK nhưng treo read timeout (lỗi mạng/đường truyền chậm)**  
       - Lần 1: 3s + backoff 0.3s  
       - Lần 2: OK, read timeout 5s  
       - **TOTAL ≈ 8.3s**

    4. **Trường hợp tốt nhất (bình thường)**  
       - Lần 1: OK (~0.3s) + read (~0.3s)  
       - **TOTAL ≈ 0.6s**
