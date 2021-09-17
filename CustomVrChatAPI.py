#from _typeshed import Self
import requests, json, aiohttp, asyncio
import base64
from os.path import exists

class VRCAPI:
    base = "https://vrchat.com/api/1"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def __init__(self, apiKey=None, username = None, password = None):
        self.api_key = apiKey
        self.username = username
        self.password = password
        self.auth = ""

        validation = False
        hasAuth = self.load_auth()  # Load auth key from local file
        if hasAuth:
            print("Successfully loaded locally stored auth key!")
            validation = self.validate_auth()

        if not validation:
            self.do_auth()
        
        if not self.api_key:
            r = requests.get(url = VRCAPI.base + "/config", headers = VRCAPI.headers)
            self.api_key = r.json()["apiKey"]

    
    # This method validates the current auth key
    # If the auth key is invalid, then a new one will be generated.
    def validate_auth(self):
        cookies = dict(auth=self.auth)
        r = requests.get(url = VRCAPI.base + "/auth", headers = VRCAPI.headers, cookies=cookies)

        if r.status_code == 401:
            print("Auth key is invalid...")
            return False

        return r.json()["ok"]

    # This method retrieves a new auth key and saves it into a local file.
    def do_auth(self):
        r = requests.get(url = VRCAPI.base + "/auth/user", auth = requests.auth.HTTPBasicAuth(self.username, self.password), headers = VRCAPI.headers)
        r.raise_for_status()
        print("Login return code: " + str(r.status_code))
        
        # Successful
        if r.status_code == 200:
            self.auth = r.cookies["auth"]
            self.api_key = r.cookies["apiKey"]
            self.save_auth()
            print("Successfully logged in!")
        
        # Failed
        elif r.status_code == 401:
            data = r.json()
            print("Login failed: " + r)

        return

    # This method does the get operation
    def get(self, path, params = None):
        # Validate authentication before requesting
        validation = self.validate_auth()
        if not validation:
            self.do_auth()


        cookies = dict(auth=self.auth, apiKey = self.api_key)
        return requests.get(url = VRCAPI.base + path, cookies = cookies, headers = VRCAPI.headers, params = params)
        

    def delete(self, path, params = None):
        # Validate authentication before requesting
        validation = self.validate_auth()
        if not validation:
            self.do_auth()

        cookies = dict(auth=self.auth, apiKey = self.api_key)
        return requests.delete(url = VRCAPI.base + path, cookies = cookies, headers = VRCAPI.headers, params = params)


    def post(self, path, params = None):
        # Validate authentication before requesting
        validation = self.validate_auth()
        if not validation:
            self.do_auth()

        cookies = dict(auth=self.auth, apiKey = self.api_key)
        return requests.post(url = VRCAPI.base + path, cookies = cookies, headers = VRCAPI.headers, data = params)

    # Just a method for testing purpose
    # Lists all the usernames of offline friends
    def list_friends(self):
        r = self.__get("/auth/user/friends", {"offset": 0, "n": 100, "offline": "true"})
        r.raise_for_status()
        print("list_friends return code: " + str(r.status_code))

        if r.status_code == 200:
            data = r.json()
            print("data len: " + str(len(data)))
            for i in range(len(data)):
                print("Friend No." + str(i) + " username:" + data[i]["username"])

    # Translate auth key to base64 and save into local file for future usage
    def save_auth(self):
        with open("login_information", "wb") as f:
            f.write(base64.b64encode(self.auth.encode()))
            f.close()

    # Load auth key from a local file
    def load_auth(self):
        if not exists("login_information"):
            return False

        data = b""
        with open("login_information", "rb") as f:
            data += f.read()
            f.close()
        
        self.auth = base64.b64decode(data).decode()
        return True
