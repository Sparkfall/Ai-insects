import requests as req

url = "http://122.112.224.186:5228/api/helloworld"
response = req.get(url)
print(response.text)