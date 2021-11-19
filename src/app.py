import requests
import re
import simplejson as json
import configargparse
import yaml
from jinja2 import Template

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

template = """
{% raw -%}
digraph {
  node [shape=plaintext fontsize=16,bgcolor=white,  fillcolor=white, style=filled]
  edge [length=100, color=gray, fontcolor=black]
{% endraw -%}
  {% for milestone in milestones -%}
  "{{ milestone.safe_id }}" [label=<
 <TABLE HREF="{{ milestone.url }}" BORDER="1" cellspacing="0" cellborder="0">
    <TR>
        <TD>{{ milestone.title }}</TD>
    </TR>
    <TR>
        <TD bgcolor="Turquoise;{{ milestone.issues_open_fraction }}:white"><FONT POINT-SIZE="14.0" COLOR="gray">{{ milestone.id }}   {{ milestone.issues_open }}/{{ milestone.issues_total }}</FONT></TD>
    </TR>
  </TABLE>>];
  {% endfor -%}
{% raw %}
}
{% endraw %}
"""
milestones = dict()
# regex for parent detection e.g. "/depends org/repo/1"
parent_rex = re.compile( '^/depends ([\S]+)$', re.MULTILINE)

# safe_div returns 0 if divisor is 0
def safe_div(x,y):
    if y == 0:
        return 0
    return x / y

def is_open(issue):
    return issue['state'] == 'OPEN'

def add_milestones(milestones, data, repository):
    for milestone in data:
        issue_count = milestone['issues']['nodes'].__len__()

        # id: org/repo/milestone_number
        id = f"{repository}/{milestone['url'].split('/')[-1]}".lower()

        # if description not null, find parents
        parents = []
        if milestone['description'] is not None:
            parents = parent_rex.findall(milestone['description'])
            for parent in parents:
                parent = parent.lower()
                if parent not in milestones:
                    milestones[parent] = {'title': "???"}

        # count open issues
        issue_open_count = sum(map(is_open, milestone['issues']['nodes']))
        issue_open_fraction = round(safe_div(issue_open_count,issue_count), 2)
        milestones[id] = {
            'id': id,
            'safe_id': id.replace('/', '_'),
            'title': milestone['title'],
            'description': milestone['description'],
            'url': milestone['url'],
            'issues_total': issue_count,
            'issues_open': issue_open_count,
            'issues_open_fraction': issue_open_fraction,
            'parents': parents,
        }
    return milestones

# load map list from yaml
def get_roadmaps(filename):
    # e.g. 
#  SRE:
  #  repos:
    #  - fatmap/aws-dns-zones
    #  - fatmap/enhancements
    with open(filename, 'r') as f:
         roadmaps = yaml.safe_load(f).items()
    return roadmaps

for roadmap_name, roadmap in get_roadmaps('roadmaps.yaml'):
    for repo in roadmap.get('repos', []):
        owner,name = repo.split('/')
        # Insert repo and org info into the query.
        q = query
        q = q.replace('MYORG', owner)
        q = q.replace('MYREPO', name)
        result = run_query(q)
        repository = repo.lower()
        data = result['data']['repository']['milestones']['nodes']
        milestones = add_milestones(milestones, data, repository)
        #  print(json.dumps(result, indent=4))

    tm = Template(template)
    dot = tm.render(milestones=milestones.values())
    print(roadmap_name)
    print(dot)
    print( json.dumps(milestones, indent=4))

