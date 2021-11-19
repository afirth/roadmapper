import requests
import re
import simplejson as json
import configargparse

parser = configargparse.ArgumentParser(description="Make roadmaps out of github milestones")
parser.add_argument('--owner', required=True, help='owner', env_var='OWNER')
parser.add_argument('--repo', required=True, help='github repository', env_var='REPO')
parser.add_argument('--token', required=True, help='github token that can query repo', env_var='GITHUB_TOKEN')
options = parser.parse_args()


headers ={
  "Authorization": "",
  "Accept": "application/vnd.github.vixen-preview+json"
}
headers['Authorization']="Bearer {}".format(options.token)

def run_query(query):
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("query failed: {}. {}".format(request.status_code, query))


# TODO pagination + a proper graphql client
query = """
{
  repository(owner: "MYORG", name: "MYREPO") {
    description
    url
    milestones(states: [OPEN],first:100) {
      nodes{
        title
        description
        url
        issues(states:[OPEN,CLOSED], first:100){
          nodes{
            title
            state
            url
          }
          pageInfo{
             endCursor
             hasNextPage
          }
        }
      }
      pageInfo{
        endCursor
        hasNextPage
      }
    }
  }
}
"""

accum = dict()
# regex for parent detection e.g. "/depends org/repo/1"
parent_rex = re.compile( '^/depends ([\S]+)$', re.MULTILINE)

def add_milestones(accum, milestones):
    for milestone in milestones:
        print(milestone['title']) # TODO remove
        issue_count = milestone['issues']['nodes'].__len__()

        # id: org/repo/milestone_number
        id = f"{options.owner}/{options.repo}/{milestone['url'].split('/')[-1]}".lower()

        # if description not null, find parents
        parents = []
        if milestone['description'] is not None:
            parents = parent_rex.findall(milestone['description'])
            for parent in parents:
                parent = parent.lower()
                if parent not in accum:
                    accum[parent] = {'title': "???"}

        # count open issues
        def condidtion(issue):
            return issue['state'] == 'OPEN'
        open_count = sum(map(condidtion, milestone['issues']['nodes']))
        accum[id] = {
            'title': milestone['title'],
            'description': milestone['description'],
            'url': milestone['url'],
            'issues_total': issue_count,
            'issues_open': open_count,
            'parents': parents,
        }
    return accum

repos = []
repos.append(dict(owner=options.owner, repo=options.repo))
# Insert repo and org info into the query.
for repo in repos:
    query = query.replace('MYORG', repo['owner'])
    query = query.replace('MYREPO', repo['repo'])
    result = run_query(query)
    milestones = result['data']['repository']['milestones']['nodes']
    accum = add_milestones(accum, milestones)
    print(json.dumps(result, indent=4))

print( json.dumps(accum, indent=4))

