import requests as req

url = "http://localhost:8088/api/helloworld"
response = req.get(url)
print(response.text)