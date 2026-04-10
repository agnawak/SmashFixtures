import requests

url = "https://fixture.agnawak.com/generate"
params = {
    "num_teams": 4,
    "min_groups": 10,
}
headers = {
    "X-API-Key": "cfut_iXlztMFczDcT5MGUu4nszyJYZX6VbmQGVpw55RMwd103b927",
}

with open("tier_list.xlsx", "rb") as file_handle:
    response = requests.post(
        url,
        params=params,
        headers=headers,
        files={"file": ("tier_list.xlsx", file_handle, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
         timeout=30,
)
print(response.status_code)
print(response.headers.get("content-type"))

response.raise_for_status()

with open("Fixtures.xlsx", "wb") as output_file:
    print("Saved Fixtures.xlsx")
    output_file.write(response.content)
