import requests
import os
import sys
import subprocess


# Function to get all repositories of a user/organization
def get_repositories(github_user, github_token=None):
    repos = []
    page = 1
    while True:
        response = requests.get(
            f"https://api.github.com/users/{github_user}/repos?per_page=100&page={page}",
            headers=(
                {"Authorization": f"token {github_token}"}
                if (github_token != None)
                else {}
            ),
        )
        if response.status_code != 200:
            print("Error fetching repositories:", response.json())
            break
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos


# Function to clone repositories
def clone_repositories(github_user, clone_dir, forked_repo, github_token):
    if not os.path.exists(clone_dir):
        os.makedirs(clone_dir)
    skipped = 0
    repos = get_repositories(github_user, github_token)

    for repo in repos:
        # Skip forked or private repositories
        if not forked_repo and repo["fork"]:
            skipped += 1
            print(f"Skipping repository: {repo['full_name']} (Fork or private)")
            continue

        repo_url = repo["clone_url"]
        repo_name = repo["name"].replace(".", "-")
        repo_path = os.path.join(clone_dir, repo_name)

        # Clone the repository if it's not already cloned
        if not os.path.exists(repo_path):
            print(f"Cloning repository: {repo['full_name']}")
            try:
                subprocess.run(
                    f"git clone {repo_url}",
                    shell=True,
                    text=True,
                    capture_output=True,
                    cwd=os.path.join(clone_dir),
                    encoding="utf-8",
                )
            except Exception as e:
                print(f"Failed to clone {repo['full_name']}: {e}")
                sys.exit(1)
        else:
            print(f"Repository already cloned: {repo['full_name']}")

    print(f"Completed {len(repos)-skipped} Skipped {skipped}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python clone_repos.py <github_user> <destination_path>")
        sys.exit(1)

    github_user = sys.argv[1]
    clone_dir = sys.argv[2]
    forked_repo = sys.argv[3] if len(sys.argv) == 4 else False

    print("")

    github_token = input("Enter your GitHub token: ")

    print("")

    if github_token == "" or github_token == "\n":
        print("Cloning only public repositories", end=" ")
        github_token = None
    else:
        print("Cloning all repositories", end=" ")

    if forked_repo == "-f" or forked_repo == "--forked":
        print("including forked")
    else:
        print("except forked")

    print("")

    clone_repositories(
        github_user, clone_dir, True if forked_repo else False, github_token
    )


if __name__ == "__main__":
    main()
