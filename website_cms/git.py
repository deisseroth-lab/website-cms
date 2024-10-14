import os

from git import Repo

REPO_ROOT = "site-data"

class GitRepo:
    def __init__(self, name, url="", path="", root_path=REPO_ROOT):
        self.name = name
        self.root_path = root_path
        if not path:
            self.path = f"{root_path}/{name}"
        else:
            self.path = f"{root_path}/{path}"

        if len(url) > 0:
            self.clone_repo(url, root_path)
        elif len(path) != 0:
            self.repo = self.create_repo(name, root_path)


    def clone_repo(self, url, root_path=REPO_ROOT):
        repo = Repo.clone_from(repo_url, root_path)
        repo.close()

    def create_repo(self, name, root_path=REPO_ROOT):
        if not os.access(root_path, os.F_OK):
            os.mkdir(root_path)

        repo = Repo.init(f"{root_path}/{name}")
        repo.close()

    def populate(self, template="default"):
        # copier?
        pass

    def update_files(self, files):
        for file in files:
            # TODO validate strings
            with open(f"{self.path}/{file[0]}", "w") as f:
                f.write(file[1])


    def add(self, files=["."]):
        repo = Repo(self.path)
        repo.index.add(files)
        repo.close()

    def commit(self, message=None):
        if not message:
            message = "Automated commit message from website-cms."

        repo = Repo(self.path)
        repo.index.commit(message)
        repo.close()
