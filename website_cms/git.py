import os

from git import Git, Repo

REPO_ROOT = "site-data"

class GitRepo:
    def __init__(
        self, name, url=None, clone=False, create=False, root_path=REPO_ROOT
    ):
        self.name = name
        self.root_path = root_path
        self.path = f"{root_path}/{name}"

        assert url is not None
        assert not (clone and create)

        if clone:
            self.clone_repo(url, root_path)

        if create:
            self.create_repo(name, url, root_path)

    def clone_repo(self, url, root_path=REPO_ROOT):
        repo = Repo.clone_from(repo_url, root_path)
        repo.close()

    def create_repo(self, name, url, root_path=REPO_ROOT):
        if not os.access(root_path, os.F_OK):
            os.mkdir(root_path)

        repo = Repo.init(f"{root_path}/{name}")
        if len(repo.remotes) == 0:
            repo.create_remote("origin", url=url)
        print(repo.remotes)
        repo.close()

    def populate(self, template="default"):
        # TODO use copier

        self.update_files([
            (
                ".github/workflows/deploy.yaml",
                """
name: Static Upload
run-name: Uploading site version ...
on: [push]

jobs:
  static-upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "TEST"
                """,
            ),
        ])
        self.add([".github/workflows/deploy.yaml"])
        self.commit("add Github Actions workflow")

    def update_files(self, files):
        for file in files:
            # TODO validate strings
            filepath = f"{self.path}/{file[0]}"
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w+") as f:
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

    def push(self, branch=None):
        repo = Repo(self.path)
        origin = repo.remotes[0]
        print(repo.remotes)
        print(origin)

        git_ssh_identity_file = os.path.expanduser('~/.ssh/starmap-resources')
        git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file
        print(git_ssh_cmd)

        with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
            origin.fetch()
            if not branch:
                branch = "main"
            origin.push(f"main:{branch}").raise_if_error()


    def pull(self):
        repo = Repo(self.path)
        origin = repo.remotes[0]
        print(repo.remotes)
        print(origin)

        git_ssh_identity_file = os.path.expanduser('~/.ssh/starmap-resources')
        git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file
        print(git_ssh_cmd)

        with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
            origin.fetch()
            origin.pull("main:main")

