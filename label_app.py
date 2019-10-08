from github3 import GitHub
from pathlib import Path
from cryptography.hazmat.backends import default_backend
import time
import json
import os
import jwt
import requests


def get_issue_handle(owner, repo, pem, app_id, issue_number):
    "Returns handle for the issue (which is also the PR)"
    with open('app.pem', 'w') as f:
        f.write(pem)
    app = GitHubApp(pem_path='app.pem', app_id=app_id)
    i_id = app.get_installation_id(owner=owner, repo=repo)
    client = app.get_installation(i_id)
    issue_handle = client.issue(username=owner, repository=repo, number=issue_number)
    return issue_handle

def get_pr_metadata(owner, repo, pr_number, token):
    "fetch information about the pr"
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Accept": "application/vnd.github.v3+json",
               "Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    return response

class GitHubApp(GitHub):
    """
    This is a small wrapper around the github3.py library
    
    Provides some convenience functions for testing purposes.
    """
    
    def __init__(self, pem_path, app_id):
        super().__init__()
        
        self.path = Path(pem_path)
        self.app_id = app_id
        
        if not self.path.is_file():
            raise ValueError(f'argument: `pem_path` must be a valid filename. {pem_path} was not found.')        
    
    def get_app(self):
        with open(self.path, 'rb') as key_file:
            client = GitHub()
            client.login_as_app(private_key_pem=key_file.read(),
                        app_id=self.app_id)
        return client
    
    def get_installation(self, installation_id):
        "login as app installation without requesting previously gathered data."
        with open(self.path, 'rb') as key_file:
            client = GitHub()
            client.login_as_app_installation(private_key_pem=key_file.read(),
                                             app_id=self.app_id,
                                             installation_id=installation_id)
        return client
        
    def get_jwt(self):
        """
        This is needed to retrieve the installation access token (for debugging). 
        
        Useful for debugging purposes.  Must call .decode() on returned object to get string.
        """
        now = self._now_int()
        payload = {
            "iat": now,
            "exp": now + (60),
            "iss": self.app_id
        }
        with open(self.path, 'rb') as key_file:
            private_key = default_backend().load_pem_private_key(key_file.read(), None)
            return jwt.encode(payload, private_key, algorithm='RS256')
    
    def get_installation_id(self, owner, repo):
        "https://developer.github.com/v3/apps/#find-repository-installation"
        url = f'https://api.github.com/repos/{owner}/{repo}/installation'

        headers = {'Authorization': f'Bearer {self.get_jwt().decode()}',
                   'Accept': 'application/vnd.github.machine-man-preview+json'}
        
        response = requests.get(url=url, headers=headers)
        if response.status_code != 200:
            raise Exception(f'Status code : {response.status_code}, {response.json()}')
        return response.json()['id']

    def get_installation_access_token(self, installation_id):
        "Get the installation access token for debugging."
        
        url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
        headers = {'Authorization': f'Bearer {self.get_jwt().decode()}',
                   'Accept': 'application/vnd.github.machine-man-preview+json'}
        
        response = requests.post(url=url, headers=headers)
        if response.status_code != 201:
            raise Exception(f'Status code : {response.status_code}, {response.json()}')
        return response.json()['token']


    def _extract(self, d, keys):
        "extract selected keys from a dict."
        return dict((k, d[k]) for k in keys if k in d)
    
    def _now_int(self):
        return int(time.time())

    def generate_installation_curl(self, endpoint):
        iat = self.get_installation_access_token()
        print(f'curl -i -H "Authorization: token {iat}" -H "Accept: application/vnd.github.machine-man-preview+json" https://api.github.com{endpoint}')

if __name__ == "__main__":
    pem = os.getenv('INPUT_APP_PEM')
    app_id = os.getenv('INPUT_APP_ID')
    trigger_phrase = os.getenv('INPUT_TRIGGER_PHRASE')
    trigger_label = os.getenv('INPUT_INDICATOR_LABEL')
    payload_fname = os.getenv('GITHUB_EVENT_PATH')
    test_payload_fname = os.getenv('INPUT_TEST_EVENT_PATH')
    github_token = os.getenv('GITHUB_TOKEN')

    if trigger_label and not (pem and app_id):
        raise EnvironmentError("If you supply a value for INDICATOR_LABEL you must also provide APP_PEM and APP_ID to authenticate as a GitHub App.")
    assert github_token, "Error: system environment variable GITHUB_TOKEN must be provided."
    assert app_id, "Error: must supply input APP_ID"
    assert trigger_phrase, "Error: must supply input TRIGGER_PHRASE"
    assert payload_fname or test_payload_fname, "Error: System environment variable GITHUB_EVENT_PATH or TEST_EVENT_PATH not found"
    
    fname = payload_fname if not test_payload_fname else test_payload_fname
    owner, repo = os.getenv('GITHUB_REPOSITORY').split('/')
    
    with open(fname, 'r') as f:
        payload = json.load(f)

    issue_data = payload['issue']
    issue_number = issue_data['number']
    comment_data = payload['comment']
    username = comment_data['user']['login']
    
    assert 'issue' in payload and 'comment' in payload, 'Error: this action is designed to operate on the event issue_comment only.'

    # For Output Variable BOOL_TRIGGERED
    triggered = False
    if 'pull_request' in issue_data and trigger_phrase in comment_data['body']:
        triggered = True

        response = get_pr_metadata(owner=owner, repo=repo, pr_number=issue_number, token=github_token)
        assert response, f"Error: unable to retrieve PR metadata: {response.status_code}"
        head_branch = response.json()['head']['ref']
        head_sha = response.json()['head']['sha']

        if trigger_label and pem:
            issue_handle = get_issue_handle(owner=owner, repo=repo, pem=pem, app_id=app_id, issue_number=issue_number)
            result = issue_handle.add_labels(trigger_label)
            labels = [x.name for x in result]
            assert result and trigger_label in labels, "issue annotation on PR not successfull."
            print(f'Successfully added label {trigger_label} to {issue_handle.state} PR: {issue_handle.html_url}')
            
        # emit output variablesOne w
        trailing_text = comment_data['body'].split(trigger_phrase)[-1]
        trailing_line = trailing_text.splitlines()[0].strip() if trailing_text.splitlines() else ''
        trailing_token = trailing_line.split()[0] if trailing_line.split() else ''
        print(f"::set-output name=TRAILING_LINE::{trailing_line}")
        print(f"::set-output name=TRAILING_TOKEN::{trailing_token}")
        print(f"::set-output name=PULL_REQUEST_NUMBER::{issue_number}")
        print(f"::set-output name=COMMENTER_USERNAME::{username}")
        print(f"::set-output name=BRANCH_NAME::{head_branch}")
        print(f"::set-output name=SHA::{head_sha}")
    
    print(f"::set-output name=BOOL_TRIGGERED::{triggered}")