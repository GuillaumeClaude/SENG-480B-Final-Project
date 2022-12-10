from github import Github
from random import shuffle
import sys
import datetime
import json
import subprocess
import time
import requests

LANG = ""
outfile = 'out.csv'
TOKEN=''

if LANG == '':
    print('specify language')
    sys.exit()

if TOKEN == '':
    print('specify token')
    sys.exit()

g = Github(TOKEN)

rl = g.get_rate_limit()
core = rl.core
search = rl.search

coreRateLimit = core.limit
coreRemaining = core.remaining

print(rl.core.reset)

searchRateLimit = search.limit
searchRemaining = search.remaining

def updateRLs(rl):
    global coreRateLimit
    global coreRemaining
    global searchRateLimit
    global searchRemaining

    rl = g.get_rate_limit()
    core = rl.core
    search = rl.search

    coreRateLimit = core.limit
    coreRemaining = core.remaining

    print(rl.core.reset)

    searchRateLimit = search.limit
    searchRemaining = search.remaining

def wait(target):
    print('RATE LIMIT EXCEEDED\nIT IS NAPTIME')
    print('sleeping until')
    print(target)
    now = datetime.datetime.utcnow()
    print(now)
    delta = target - now
    print(delta)

    if delta > datetime.timedelta(0):
        print('sleeping', int(delta.total_seconds()))
        time.sleep(int(delta.total_seconds())+1)

def atomicwrite(ls):
    global outfile
    outstring = ','.join(ls)
    with open(outfile, "a") as myfile:
        myfile.write(outstring + '\n')

def prInfo(pull, num, repo, lang):
    title = pull.title
    print('title:', pull.title)

    created_at = pull.created_at
    print('created:', pull.created_at)

    changed_files = pull.changed_files
    print('files changed:', changed_files)

    merged = pull.merged
    print('merged:', pull.merged)
    if pull.merged:
        merged_at = pull.merged_at
        print('merged at:', pull.merged_at)

        minutes = int((merged_at - created_at).total_seconds() / 60.0)
        print('merge minutes:', minutes)

    additions = pull.additions
    print('additions:', pull.additions)

    deletions = pull.deletions
    print('deletions:', pull.deletions)

    atomicwrite([lang, repo, str(num), str(created_at), str(merged_at), str(minutes), str(changed_files), str(additions), str(deletions)])

def getPage(token, repo, page):
    url = 'https://api.github.com/search/issues?q=repo:' + repo + '+is:pr+is:merged&per_page=100&page=' + page
    headers = {'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + token}
    r = requests.get(url, headers=headers)
    return r.json()

def pull(num, repo, lang):
    global coreRemaining
    global coreRateLimit
    if coreRemaining < 5:
        wait(g.get_rate_limit().core.reset)
        coreRemaining = coreRateLimit

    coreRemaining -= 1
    p = r.get_pull(num)
    prInfo(p, num, repo, lang)
    print('===========')

def consume(repo, limit, rl, lang):
    global searchRemaining
    global searchRateLimit
    global TOKEN
    i = 1
    j = 0
    while True:
        if searchRemaining < 5:
            wait(g.get_rate_limit().search.reset)
            searchRemaining = searchRateLimit
        searchRemaining -= 1
        print(searchRemaining)
        #a = json.loads(subprocess.check_output(['./mergedpull.sh', repo, str(i), TOKEN]))
        a = getPage(TOKEN, repo, str(i))

        try:
            a = a['items']
        except:
            return

        if not a:
            print('empty stop')
            return

        for pr in a:
            if j>=limit:
                return

            j += 1
            pull(pr['number'], repo, lang)
            print(coreRemaining)

        i += 1

        updateRLs(rl)

with open('./repodata/' + LANG + '.json') as f:
    j = json.load(f)

shuffle(j)

for repo in j:
    reponame = repo['owner'] + '/' + repo['name']

    print('scraping repo', reponame)

    r = g.get_repo(reponame)
    consume(reponame, 1000, rl, LANG)

print('dobne')


