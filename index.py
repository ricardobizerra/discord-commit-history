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

try:
    since_time = (datetime.now() - timedelta(days=3)).isoformat()
    # since_time without timezone and microseconds and in ISO 8601 format
    since_time_ = since_time[0:22] + "Z"

    for github_repo in repos_to_monitor:

        for branch in branches_to_monitor:
            response = requests.get(f"https://api.github.com/repos/{github_repo}/commits",
                                    params={"sha": branch, "since": since_time},
                                    headers={
                                        "Authorization": f"Bearer {github_token}",
                                        "X-GitHub-Api-Version": "2022-11-28",
                                        "Accept": "application/vnd.github+json"
                                    })
            response.raise_for_status()

            commits = response.json()
            
            if commits:
                for commit in commits:
                    commit_sha = commit["sha"][0:7]
                    commit_message = commit["commit"]["message"]
                    commit_author = commit["committer"]["login"]
                    commit_url = commit["html_url"]

                    # Send notification to Discord
                    webhook = DiscordWebhook(url=discord_webhook_url)
                    embed = DiscordEmbed(title="New Commit Detected",
                                            description=commit_message,
                                            color="3D7C4E")
                    embed.set_author(name=commit_author, icon_url=commit["author"]["avatar_url"])
                    embed.add_embed_field(name="Author", value=commit_author, inline=False)
                    embed.add_embed_field(name="Commit URL", value=commit_url, inline=False)
                    embed.add_embed_field(name="Branch", value=branch, inline=False)
                    webhook.add_embed(embed)
                    webhook.execute()

                    print(f"New commit detected: {commit_sha} - {commit_message}")

except Exception as e:
    print(f"An error occurred: {e}")
