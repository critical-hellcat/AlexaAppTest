from github import Github
from git import Repo
import os
import shutil

# === Configuration ===
import os

api_key = os.getenv("MY_API_KEY")

print(f"API Key is: {api_key}")

source_token =  api_key
destination_token = api_key
source_repo_name = 'critical-hellcat/CustomProcessorTest'
properties_path = 'Properties'
repo_dir = os.getcwd()
new_branch = 'read-properties-from-atc'

# === Authenticate with GitHub ===
source_github = Github(source_token)
dest_github = Github(destination_token)
source_repo = source_github.get_repo(source_repo_name)
dest_repo = dest_github.get_repo('critical-hellcat/AlexaAppTest')

# === Load current Git repo ===
repo = Repo(repo_dir)
origin = repo.remotes.origin

# === Create a new branch ===
repo.git.checkout('-b', new_branch)

# === Get files from source repo via GitHub API ===
files = source_repo.get_contents(properties_path)

for file in files:
    if file.type == 'file':
        content = file.decoded_content.decode('utf-8')
        file_path = os.path.join(repo_dir, properties_path, file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

repo.git.add(A=True)
repo.index.commit("Import /Properties from source repo")
origin.push(new_branch)

pr = dest_repo.create_pull(
    title="Import /Properties from source repo",
    body="Imported files from source repo's /Properties folder.",
    head=new_branch,
    base='main'
)

print(f"Pull request created: {pr.html_url}")