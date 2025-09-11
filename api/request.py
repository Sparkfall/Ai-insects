import requests as req

# listfile
url = "http://localhost:8088/api/listfile"
Params = {
    'cameraID':'camera1',
    'date':'25-9-8'
}
response = req.post(url,json=Params)
response.raise_for_status()
print(response.json)
# print(response['message'])

#getfile
url = "http://localhost:8088/api/getfile"
Params = {
    'cameraID':'camera1',
    'date':'25-9-8',
    'filename':'20250908000000.jpg'
}
response = req.post(url,json=Params)
response.raise_for_status()
print(response.json)
# print(response)

url = "http://localhost:8088/api/putfile"
Params = {
            'cameraID':'camera1',
            'date':'25-9-8',
            'filename':'1.jpg'
        }
def upload_jpg_file(file_path, upload_url):
    with open(file_path, 'rb') as file:
        files = {'file': (file_path.split('/')[-1], file, 'image/jpeg')}
        response = req.post(upload_url,params=Params,files=files)
        response.raise_for_status()
        print(response.json())
upload_jpg_file("1.jpg", url)