import requests
from bs4 import BeautifulSoup
import gitlab

class Agent:
    def __init__(self, url, use_ldap=False, username=None, password=None, private_token=None, is_admin=False, api_version=4):
        self.url = url
        self.use_ldap = use_ldap
        self.username = username
        self.password = password
        self.private_token = private_token
        self.is_admin = is_admin
        self.api_version = api_version

        self.session = requests.Session()
        self.gitlab = None

    def auth(self, private_token=None):
        if private_token is not None:
            self.private_token = private_token

        self.gitlab = gitlab.Gitlab(self.url, private_token=self.private_token, keep_base_url=True)
        try:
            self.gitlab.auth()
        except gitlab.exceptions.GitlabAuthenticationError:
            return False

        self.is_admin = getattr(self.gitlab.user, 'is_admin', False)
        
        return True

    def get_csrf_token(self):
        r = self.session.get(f"{self.url}/")
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.find("meta", {"name": "csrf-token"})["content"]

    def login(self, username=None, password=None, use_ldap=False):
        if username is not None and password is not None:
            self.username = username
            self.password = password
            self.use_ldap = use_ldap

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

    def create_pat(self, user_id=None, token_name="labrat", token_scopes=["api", "create_runner"]):
        if user_id is None:
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
                return response_json.get("new_token")
            except ValueError:
                return None
        elif self.is_admin:
            response = self.gitlab.users.get(user_id, lazy=True).personal_access_tokens.create({
                "name": token_name,
                "scopes": token_scopes,
            })
            return response.token
        else:
            print(f"[-] Cannot create PAT for user {user_id}. {self.username} is not an admin")
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
            is_admin=data.get("is_admin", False),
            use_ldap=data.get("use_ldap", False),
            api_version=data.get("api_version", 4)
        )