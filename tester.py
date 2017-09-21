import requests
headers = {"device": "cam", "identifier":"one"}
data = {"state":"4"}
r = requests.get("http://localhost:8000", headers=headers, data=data)
print(r)
