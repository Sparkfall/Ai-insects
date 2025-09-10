import requests as req
import json

# listfile
# url = "http://localhost:8088/api/listfile"
# Params = {
#     'cameraID':'camera1',
#     'date':'25-9-8'
# }
# response = json.loads(req.post(url,json=Params).text)
# print(response['message'])

#getfile
url = "http://localhost:8088/api/getfile"
Params = {
    'cameraID':'camera1',
    'date':'25-9-8',
    'filename':'20250908000000.jpg'
}
response = req.post(url,json=Params).text
print(response)