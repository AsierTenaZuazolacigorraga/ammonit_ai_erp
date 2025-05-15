import pandas as pd
import requests

# Service Layer base URL

base_url = "https://xxxxxxxxxxxxxxxxxxxxxx:50000/b1s/v1"

# Login credentials

payload = {
    "CompanyDB": "xxxxxxxxx",
    "UserName": "xxxxxxxxxxx",
    "Password": "xxxxxxxxxxxx",
}

# Log in to get session cookies
session = requests.Session()
response = session.post(f"{base_url}/Login", json=payload)

# Construct query URL
query_url = f"{base_url}/SQLQueries('sql05')/List"

# Disable pagination
headers = {"Prefer": "odata.maxpagesize=0"}

# Send query request
response = session.get(query_url, headers=headers)

# Log out to end session
session.post(f"{base_url}/Logout")

# Convert response to Pandas DataFrame
# df = pd.DataFrame(response.json())
data = response.json()["value"]

# Convert to Pandas DataFrame
df = pd.DataFrame(data)

# Print results
print(df)


import requests

# Set the API endpoint and headers
endpoint = "https://your-sap-service-layer-url/b1s/v1/Items"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Basic Your_Base64_Encoded_Credentials",
}

# Make a GET request to the API
response = requests.get(endpoint, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON data from the response
    items = response.json()
    for item in items["value"]:
        print(f"Item Code: {item['ItemCode']}, Item Name: {item['ItemName']}")
else:
    print(
        f"Failed to retrieve items. Status Code: {response.status_code}, Error: {response.text}"
    )
