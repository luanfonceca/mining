import requests, json

from pprint import pprint
from pymongo import MongoClient

from config import *

client = MongoClient()
db = getattr(client, DATABASE_NAME)

# User local storage
USERS = {}
DEFAULT_USER = dict(
    files=list(), back_end=0, front_end=0, 
    opened_issues=0, talker=0, links_shared=0, 
    channeler=0, setuper=0)


def update_user_channeler(user, value):
    if user in EXCLUDED_USERS:
        return

    if not value:
        value = 0

    if user not in USERS:
        USERS[user] = DEFAULT_USER.copy()

    USERS[user].update(channeler=value)


def update_user_links_shared(user, value):
    if user in EXCLUDED_USERS:
        return

    if not value:
        value = 0

    if user not in USERS:
        USERS[user] = DEFAULT_USER.copy()

    USERS[user].update(links_shared=value)


def update_user_talker(user, value):
    if user in EXCLUDED_USERS:
        return

    if not value:
        value = 0

    if user not in USERS:
        USERS[user] = DEFAULT_USER.copy()

    USERS[user].update(talker=value)


def update_user_opened_issues(user):
    if user in EXCLUDED_USERS:
        return

    if user not in USERS:
        USERS[user] = DEFAULT_USER.copy()

    old_issues = USERS.get(user).get('opened_issues', 0)
    USERS[user].update(opened_issues=old_issues + 1)


def update_user_commit_files(user, files):
    if user in EXCLUDED_USERS:
        return

    if user not in USERS:
        USERS[user] = DEFAULT_USER.copy()

    old_files = USERS.get(user).get('files', [])
    old_files.extend(files)
    USERS[user].update(files=old_files)

    front_end = USERS[user].get('front_end', 0)
    back_end = USERS[user].get('back_end', 0)
    setuper = USERS[user].get('setuper', 0)
    commiter = USERS[user].get('commiter', 0)
    front_end += len([f for f in old_files if any([q in f for q in FRONT_END_QUERIES])])
    back_end += len([f for f in old_files if any([q in f for q in BACK_END_QUERIES])])
    setuper += len([f for f in old_files if any([q in f for q in SETUPER_QUERIES])])
    commiter += 1
    USERS[user].update(
        front_end=front_end, 
        back_end=back_end, 
        setuper=setuper,
        commiter=commiter,
    )

def get_repos():
    repos = requests.get(REPOS_URL, auth=AUTH).json()

    if REPO_NAMES:
        repos = filter(lambda x: x.get('name') in REPO_NAMES, repos)

    if repos:
        db.repos.insert(repos)
    return repos

def get_issues(repo, state='open'):
    issues = requests.get(ISSUES_URL.format(repo=repo, state=state), auth=AUTH).json()
    if issues:
        for issue in issues:
            if issue.get('pull_request'):
                continue

            issue.update(_repo=repo)
            db.issues.insert(issue)
    return issues

def get_commits(repo):
    commits = []
    req = requests.get(COMMITS_URL.format(repo=repo), auth=AUTH)
    for ci in req.json():
        commit = requests.get(ci.get('url'), auth=AUTH).json()

        if ci.get('author'):
            author = ci.get('author').get('login')
        else:
            author = ci.get('commit').get('author').get('email')
        commit.update(_repo=repo, _user=author)
        commits.append(commit)
    db.commits.insert(commits)
    return commits


for repo in get_repos():
    print("Repo: %s" % repo.get('name'))
    for issue in get_issues(repo.get('name')):
        print("\tIssue: #%s" % issue.get('number'))
        if issue.get('state') == 'open':
            print("\tissue #%s aberta por @%s." % (
                  issue.get('number'),
                  issue.get('user').get('login')))
            update_user_opened_issues(issue.get('user').get('login'))
    for commit in get_commits(repo.get('name')):
        if commit.get('author'):
            author = commit.get('author').get('login')
        else:
            author = commit.get('commit').get('author').get('email')

        print("\tCommit #%s by @%s" % (commit.get('_id'), author))
        update_user_commit_files(
            author,
            [f.get('filename') for f in commit.get('files')]
        )


for user, data in USERS.iteritems():
    slack_user = SLACK_USERS.get(user, user)
    talker_data = json.loads(open('talker.json').read())
    update_user_talker(user, talker_data.get(slack_user))
    channeler_data = json.loads(open('channeler.json').read())
    update_user_channeler(user, channeler_data.get(slack_user))
    links_shared_data = json.loads(open('links-shared.json').read())
    update_user_links_shared(user, links_shared_data.get(slack_user))

    data.update(_user=user.lower())
    db.users.insert(data)
