import requests


def upload(file_path, window):
    with open(file_path, "rb") as f:
        contents = f.read()
        heroesprofile_upload(contents)
        # upload to hotslogs' API?


def heroesprofile_upload(contents):
    res = requests.post(
        url="https://api.heroesprofile.com/api/upload/alt",
        data=contents,
        headers={"Content-Type": "application/octet-stream"},
    )
    print(res)
