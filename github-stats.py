import time
import requests

def get_access_token():
    with open('./access_token.txt', 'r') as f:
        access_token = f.read().strip()
    return access_token

def get_graphql_data(GQL):
    access_token = get_access_token()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Authorization': 'bearer {}'.format(access_token),
    }
    s = requests.session()
    s.keep_alive = False 
    graphql_api = "https://api.github.com/graphql"
    for _ in range(5):
        try:
            r = requests.post(url=graphql_api, json={"query": GQL}, headers=headers, timeout=30)
            if r.status_code != 200:
                print(f'Can not retrieve from {GQL}. Response status is {r.status_code}, content is {r.content}.')
            else:
                return r.json()
        except Exception as e:
            print(e)
            time.sleep(60)

class ProcessorGQL(object):
    def __init__(self):
        self.gql_format = """query{
    search(query: "%s", type: REPOSITORY, first:%d %s) {
      pageInfo { endCursor }
                edges {
                    node {
                        ...on Repository {
                            id
                            name
                            url
                            forkCount
                            stargazerCount
                            owner {
                                login
                            }
                            description
                            pushedAt
                            primaryLanguage {
                                name
                            }
                            openIssues: issues(states: OPEN) {
                                totalCount
                            }
                        }
                    }
                }
            }
        }
        """
        self.bulk_size = 100
        self.bulk_count = 10
        self.lower_stars = 1e9

    def parse_gql_result(self, result):
        res = []
        for repo in result["data"]["search"]["edges"]:
            repo_data = repo['node']
            res.append( f"{repo_data['name']}, {repo_data['stargazerCount']}, {repo_data['forkCount']}, {repo_data['primaryLanguage']['name'] if repo_data['primaryLanguage'] is not None else None}, {repo_data['url']}, {repo_data['owner']['login']}, {repo_data['openIssues']['totalCount']}, {repo_data['pushedAt']}, {repo_data['description'].replace(',', ' | ') if(repo_data['description']) else ""}" )
        self.lower_stars = min(self.lower_stars, repo_data['stargazerCount'])
        return res
    
    def get_repos(self, qql):
        cursor = ''
        for i in range(0, self.bulk_count):
            time.sleep(1)
            repos_gql = get_graphql_data(qql % cursor)
            cursor = ', after:"' + repos_gql["data"]["search"]["pageInfo"]["endCursor"] + '"'
            repos = self.parse_gql_result(repos_gql)
            with open('repositories.csv', 'a', encoding='utf-8') as f:
                f.write("\n".join(repos)+"\n")

    def get_all_repos(self):
        count = 1
        while(count <= 100):
            if(count % 10 == 0):
                time.sleep(5)
            print("Get repos of most stars, count: %d" % count)
            if(count == 0):
                self.get_repos(self.gql_format % (f"stars:>0 sort:stars", self.bulk_size, "%s"))
            else:
                self.get_repos(self.gql_format % (f"stars:<{self.lower_stars} sort:stars", self.bulk_size, "%s"))
            count += 1
        print("Get repos of most stars success!")

if __name__ == "__main__":
    processor = ProcessorGQL()
    processor.get_all_repos()
