import git


def get_git_hash():
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.commit.hexsha
    return repo.git.rev_parse(sha, short=4)
