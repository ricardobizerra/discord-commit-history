import requests
from datetime import datetime, timedelta
from discord_webhook import DiscordWebhook, DiscordEmbed
import dotenv
import os

dotenv.load_dotenv()

repo = "."
repos_to_monitor = []
while repo != "":
    repo = input("Enter the repositories you want to monitor: ")
    if repo != "": repos_to_monitor.append(repo)

github_token = os.getenv("GITHUB_TOKEN")  # Replace with your GitHub token
discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")  # Replace with your Discord webhook URL

branch = "."
branches_to_monitor = []
while branch != "":
    branch = input("Enter the branches you want to monitor: ")
    if branch != "": branches_to_monitor.append(branch)
since_days = int(input("Enter the number of days to monitor: "))
until_days = int(input("Enter the number of days to monitor: ") or 0)

try:
    since_time = (datetime.now() - timedelta(days=since_days)).isoformat()
    # since_time without timezone and microseconds and in ISO 8601 format
    since_time_ = since_time[0:22] + "Z"

    until_time = (datetime.now() - timedelta(days=until_days)).isoformat()
    # until_time without timezone and microseconds and in ISO 8601 format
    until_time_ = until_time[0:22] + "Z"

    for github_repo in repos_to_monitor:

        for branch in branches_to_monitor:
            response = requests.get(f"https://api.github.com/repos/{github_repo}/commits",
                                    params={"sha": branch, "since": since_time, "until": until_time},
                                    headers={
                                        "Authorization": f"Bearer {github_token}",
                                        "X-GitHub-Api-Version": "2022-11-28",
                                        "Accept": "application/vnd.github+json"
                                    })
            response.raise_for_status()

            commits = response.json()
            
            if commits:
                description = ""
                for commit in commits:
                    commit_sha = commit["sha"][0:7]
                    commit_message = commit["commit"]["message"]
                    commit_author = commit["author"]["login"]
                    commit_author_url = commit["author"]["html_url"]
                    commit_icon_url = commit["author"]["avatar_url"]
                    commit_url = commit["html_url"]
                    description += f"[`{commit_sha}`]({commit_url}) {commit_message}\n"

                # Send notification to Discord
                if len(commits) == 1:
                    title = f"[{github_repo.split('/')[1]}:{branch}] {len(commits)} new commit"
                else:
                    title = f"[{github_repo.split('/')[1]}:{branch}] {len(commits)} new commits"
                webhook = DiscordWebhook(url=discord_webhook_url)
                embed = DiscordEmbed(title=title,
                                        description=description,
                                        color="3D7C4E")
                embed.set_author(name=commit_author, url=commit_author_url, icon_url=commit_icon_url)
                webhook.add_embed(embed)
                webhook.execute()

except Exception as e:
    print(f"An error occurred: {e}")
