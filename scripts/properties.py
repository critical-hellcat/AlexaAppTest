#!/usr/bin/env python3

from github import Github
from git import Repo
from datetime import datetime
import os
import shutil

# === Configuration ===
import os

my = os.getenv("MY_OWN")

print(f"API Key is: {my}")


source_token =  my
destination_token = my
source_repo_name = 'critical-hellcat/CustomProcessorTest'
source_base_path = 'Properties'
destination_sub_path = 'assistant/onboard/src/main/resources'
repo_dir = os.getcwd()

# === Authenticate with GitHub ===
source_github = Github(source_token)
dest_github = Github(destination_token)
source_repo = source_github.get_repo(source_repo_name)
dest_repo = dest_github.get_repo('critical-hellcat/AlexaAppTest')

# === Load current Git repo ===
repo = Repo(repo_dir)
origin = repo.remotes.origin

def branch_exists(repo, branch_name):
    try:
        repo.get_branch(branch_name)
        return True
    except:
        return False

def get_subdirectories(path):
    contents = source_repo.get_contents(path)
    return [c for c in contents if c.type == 'dir']

def get_all_files(path):
    contents = source_repo.get_contents(path)
    files = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == 'dir':
            contents.extend(source_repo.get_contents(file_content.path))
        else:
            files.append(file_content)
    return files

subdirs = get_subdirectories(source_base_path)

for subdir in subdirs:
    folder_name = subdir.name
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    new_branch = f"import-properties-{folder_name}-{timestamp}"
    base_branch = folder_name if folder_name == "develop" else f"platform/{folder_name}"

    print(f"\nProcessing folder: {folder_name}")

    repo.git.checkout('HEAD', b=new_branch)

    # === Get files
    files = get_all_files(subdir.path)

    # === Clean destination path
    full_dest_path = os.path.join(repo_dir, destination_sub_path)
    if os.path.exists(full_dest_path):
        shutil.rmtree(full_dest_path)
    os.makedirs(full_dest_path, exist_ok=True)

    # === Write files to destination
    for file in files:
        rel_path = os.path.relpath(file.path, subdir.path)
        dest_path = os.path.join(full_dest_path, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(file.decoded_content.decode('utf-8'))

    # === Commit and push
    repo.git.add(A=True)
    repo.index.commit(f"Import properties from ATC: {folder_name}")
    origin.push(new_branch)

    # === Create PR if base branch exists
    if branch_exists(dest_repo, base_branch):
        pr = dest_repo.create_pull(
            title=f"Import Properties from {folder_name}",
            body=f"This PR imports files from `{source_base_path}/{folder_name}` into `{destination_sub_path}`.",
            head=new_branch,
            base=base_branch
        )
        print(f"✅ Draft PR created: {pr.html_url}")
    else:
        print(f"⚠️ Base branch '{base_branch}' does not exist. Skipping PR.")

# # === Create a new branch ===
# repo.git.checkout('-b', new_branch)
#
# # === Get files from source repo via GitHub API ===
# files = source_repo.get_contents(properties_path)
#
# for file in files:
#     if file.type == 'file':
#         content = file.decoded_content.decode('utf-8')
#         file_path = os.path.join(repo_dir, properties_path, file.name)
#         os.makedirs(os.path.dirname(file_path), exist_ok=True)
#         with open(file_path, 'w', encoding='utf-8') as f:
#             f.write(content)
#
# repo.git.add(A=True)
# repo.index.commit("Import /Properties from source repo")
# origin.push(new_branch)
#
# pr = dest_repo.create_pull(
#     title="Import /Properties from source repo",
#     body="Imported files from source repo's /Properties folder.",
#     head=new_branch,
#     base='main'
# )
#
# print(f"Pull request created: {pr.html_url}")