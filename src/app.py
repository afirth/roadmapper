import requests
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

def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
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
# Insert repo and org info into the query.
query = query.replace('MYREPO', options.repo )
query = query.replace('MYORG', options.owner )

result = run_query(query) # Execute the query
print(json.dumps(result))
#print result
#remaining_rate_limit = result["data"]["rateLimit"]["remaining"] # Drill down the dictionary
#print("Remaining rate limit - {}".format(remaining_rate_limit))
