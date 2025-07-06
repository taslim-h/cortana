import base64
import json

with open(r"C:\Users\USER\Downloads\cortana-4cc9a-firebase-adminsdk-fbsvc-2b18bcc557.json") as f:
    json_data = f.read()



# encoded = base64.b64encode(json_data.encode()).decode()

print(json_data)
