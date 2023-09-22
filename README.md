# Install

```
pip install -r requirements.txt
```

# Run

```
python app.py
```

# Test

```
curl -X POST -F "file=@test.txt" http://127.0.0.1:5000/upload
curl http://127.0.0.1:5000/retrieve/test.txt
curl -X DELETE http://127.0.0.1:5000/delete/test.txt
```
