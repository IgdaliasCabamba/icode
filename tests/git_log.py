import pygit2

repo = pygit2.Repository("/home/igdalias/SmartCode"+'/.git')
last = repo[repo.head.target]

for commit in repo.walk(last.id, pygit2.GIT_SORT_TIME):
    for e in commit.tree:
        print(e.name)
        if e.type == 2:
            print(dir(e))