import requests
import re
import simplejson as json
import configargparse
import yaml
from jinja2 import Template

parser = configargparse.ArgumentParser(description="Make roadmaps out of github milestones")
parser.add_argument('--config', required=True, help='path to config file', env_var='config') #TODO implement
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
    {% for parent in milestone.parents -%}
    "{{ parent.safe_id }}" -> "{{ milestone.safe_id }}";
    {% endfor %}
  {% endfor -%}
{% raw %}
}
{% endraw %}
"""
milestones = dict()
# regex for parent detection e.g. "/depends org/repo/1"
parent_rex = re.compile( '^/depends ([\S]+)$', re.MULTILINE)

# color_div makes fractions that graphviz likes
def color_div(x,y):
    if y == 0:
        return 0 # gradient
    q = x/y
    if q > .99:
        return .99 # 1 turns black
    if q < .01:
        return .01
    return q

def is_open(issue):
    return issue['state'] == 'OPEN'

def add_milestones(milestones, data, repository):
    for milestone in data:
        issue_count = milestone['issues']['nodes'].__len__()

        # id: org/repo/milestone_number
        id = f"{repository}/{milestone['url'].split('/')[-1]}".lower()

        # if description not null, find parents
        # put a skeleton milestone in the map for each parent if not already there
        parents = []
        if milestone['description'] is not None:
            for item in parent_rex.findall(milestone['description']):
                parent_id = item.lower()
                parent = {
                            'title': "???",
                            'id': parent_id,
                            'safe_id': parent_id.replace('/', '_'),
                            }
                parents.append(parent)
                if parent_id not in milestones:
                    milestones[parent_id] = parent

        # count open issues
        issue_open_count = sum(map(is_open, milestone['issues']['nodes']))
        issue_open_fraction = round(color_div(issue_open_count,issue_count), 2)
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
#  TEAM:
  #  repos:
    #  - org/repo1
    #  - org/repo2
    with open(filename, 'r') as f:
         roadmaps = yaml.safe_load(f).items()
    return roadmaps

for roadmap_name, roadmap in get_roadmaps(options.config):
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
    # print( json.dumps(milestones, indent=4))

    # render graphviz
    tm = Template(template)
    dot = tm.render(milestones=milestones.values())
    print(roadmap_name)
    print(dot)
