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