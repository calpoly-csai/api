import requests

url = "https://nimbus.api.calpolycsai.com/ask"

payload = "{\n    \"question\": \"What is Dr. Lupo's email?\"\n}"
headers = {
  'Content-Type': 'application/json',
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data = payload)
print(response.text.encode('utf8'))

