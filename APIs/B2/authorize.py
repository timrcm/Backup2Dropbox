import base64
import json
from urllib.request import urlopen

id_and_key = 'hexAccountId_value:accountKey_value'
basic_auth_string = 'Basic ' + base64.b64encode(id_and_key)
headers = { 'Authorization': basic_auth_string }


response = urlopen('https://api.backblazeb2.com/b2api/v1/b2_authorize_account')
response_data = json.loads(response.read())
response.close()

print('auth token:'), response_data['authorizationToken']
print('api url:'), response_data['apiUrl']
print('download url:'), response_data['downloadUrl']
print('minimum part size:'), response_data['minimumPartSize']
