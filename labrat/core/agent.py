from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import gitlab

class Agent:
    def __init__(self, url, use_ldap=False, username=None, password=None, private_token=None, api_version=4, section=None):
        self.url = url
        self.host = urlparse(url).hostname
        self.use_ldap = use_ldap
        self.username = username
        self.password = password
        self.private_token = private_token
        self.api_version = api_version
        self.section = section

        self.session = requests.Session()
        self.gitlab = None
        self.id = None
        self.is_admin = False
        self.is_bot = False
        self.is_authenticated = False

    @property
    def label(self):
        return f"{self.username}@{self.host}"

    def auth(self, private_token=None):
        if private_token is not None:
            self.private_token = private_token

        self.gitlab = gitlab.Gitlab(self.url, private_token=self.private_token, keep_base_url=True, api_version=self.api_version)
        self.gitlab.auth()
        self.is_authenticated = True

        user = self.gitlab.user
        self.id = user.id
        self.username = user.username
        self.section = self.section if self.section else f"{self.id}@{self.host}"
        self.is_admin = getattr(self.gitlab.user, 'is_admin', False)
        self.is_bot = getattr(self.gitlab.user, 'bot', False)

    def get_csrf_token(self):
        r = self.session.get(f"{self.url}/")
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.find("meta", {"name": "csrf-token"})["content"]

    def login(self):
        csrf_token = self.get_csrf_token()
        if self.use_ldap:
            payload = {
                "authenticity_token": csrf_token,
                "username": self.username,
                "password": self.password,
                "user[remember_me]": 1,
            }
            self.session.post(f"{self.url}/users/auth/ldapmain/callback", data=payload)
        else:
            payload = {
                "authenticity_token": csrf_token,
                "user[login]": self.username,
                "user[password]": self.password,
                "user[remember_me]": 1,
            }
            self.session.post(f"{self.url}/users/sign_in", data=payload)

    def create_pat(self, token_name="private token", token_scopes=["api", "read_repository", "write_repository"]):
        csrf_token = self.get_csrf_token()
        payload = {
            "personal_access_token[name]": token_name,
            "personal_access_token[scopes][]": token_scopes,
        }
        headers = {"X-CSRF-Token": csrf_token}
        r = self.session.post(
            f"{self.url}/-/user_settings/personal_access_tokens",
            data=payload,
            headers=headers
        )

        try:
            response_json = r.json()
            if "new_token" in response_json:
                return response_json.get("new_token")
            else:
                return response_json.get("token")
        except ValueError:
            return None

    def to_dict(self):
        return {
            key: value
            for key, value in {
                "url": self.url,
                "username": self.username,
                "password": self.password,
                "private_token": self.private_token,
                "is_admin": self.is_admin,
                "use_ldap": self.use_ldap,
                "api_version": self.api_version,
            }.items()
            if value is not None
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            url=data.get("url"),
            username=data.get("username"),
            password=data.get("password"),
            private_token=data.get("private_token"),
            use_ldap=(True if data.get("use_ldap") == "True" else False),
            api_version=int(data.get("api_version", 4)),
            section=data.get("_name", None)
        )
    
    def __repr__(self):
        return self.to_dict().__repr__()