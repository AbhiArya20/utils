import os
import time
import requests
import pandas as pd
from datetime import datetime


def get_access_token():
    with open('../access_token.txt', 'r') as f:
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
        time.sleep(1)  
        try:
            r = requests.post(url=graphql_api, json={"query": GQL}, headers=headers, timeout=30)
            if r.status_code != 200:
                print(f'Can not retrieve from {GQL}. Response status is {r.status_code}, content is {r.content}.')
            else:
                return r.json()
        except Exception as e:
            print(e)
            time.sleep(5)

lower_stars = 1e9

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
        self.gql_stars = self.gql_format % ("stars:>0 sort:stars", self.bulk_size, "%s")

    @staticmethod
    def parse_gql_result(result):
        res = []
        for repo in result["data"]["search"]["edges"]:
            repo_data = repo['node']
            res.append({
                'name': repo_data['name'],
                'stargazers_count': repo_data['stargazerCount'],
                'forks_count': repo_data['forkCount'],
                'language': repo_data['primaryLanguage']['name'] if repo_data['primaryLanguage'] is not None else None,
                'html_url': repo_data['url'],
                'owner': {
                    'login': repo_data['owner']['login'],
                },
                'open_issues_count': repo_data['openIssues']['totalCount'],
                'pushed_at': repo_data['pushedAt'],
                'description': repo_data['description']
            })
            global lower_stars
            lower_stars = min(lower_stars, repo_data['stargazerCount'])
        return res

    def get_repos(self, qql):
        cursor = ''
        repos = []
        for i in range(0, self.bulk_count):
            repos_gql = get_graphql_data(qql % cursor)
            cursor = ', after:"' + repos_gql["data"]["search"]["pageInfo"]["endCursor"] + '"'
            repos += self.parse_gql_result(repos_gql)
            print("Get repos of most stars, repos count: %d" % len(repos))
        return repos

    def get_all_repos(self):
        print("Get repos of most stars...")
        count = 0
        repos_stars = []
        while(count < 1000):
            print("Get repos of most stars, count: %d" % count)
            if(count == 0):
                repos_stars.extend(self.get_repos(self.gql_stars))
            else:
                repos_stars.extend(self.get_repos(self.gql_format % (f"stars:<{lower_stars} sort:stars", self.bulk_size, "%s")))
            count += 1
        print("Get repos of most stars success!")
        return repos_stars


class WriteFile(object):
    def __init__(self, repos_stars):
        self.repos_stars = repos_stars
        self.col = ['rank', 'repo_name', 'stars', 'forks', 'language', 'repo_url', 'username', 'issues',
                    'last_commit', 'description']

    def repo_to_df(self, repos):
        repos_list = []
        for idx, repo in enumerate(repos):
            repo_info = [idx + 1, repo['name'], repo['stargazers_count'], repo['forks_count'], repo['language'],
                         repo['html_url'], repo['owner']['login'], repo['open_issues_count'], repo['pushed_at'],
                         repo['description']]
            repos_list.append(repo_info)
        return pd.DataFrame(repos_list, columns=self.col)

    def save_to_csv(self):
        df_all = pd.DataFrame(columns=self.col)
        df_repos = self.repo_to_df(repos=self.repos_stars)
        df_all = pd.concat([df_all, df_repos], ignore_index=True)

        save_date = datetime.now().strftime("%Y-%m-%d")
        os.makedirs('../data', exist_ok=True)
        df_all.to_csv('../data/github-ranking-' + save_date + '.csv', index=False, encoding='utf-8')
        print('Save data to data/github-ranking-' + save_date + '.csv')

def run_by_gql():
    ROOT_PATH = os.path.abspath(os.path.join(__file__, "../../"))
    os.chdir(os.path.join(ROOT_PATH, 'source'))

    processor = ProcessorGQL()  
    repos_stars = processor.get_all_repos()
    wt_obj = WriteFile(repos_stars)
    wt_obj.save_to_csv()

if __name__ == "__main__":
    run_by_gql()
