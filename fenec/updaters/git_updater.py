import subprocess


def get_changed_files_since_last_update(last_commit_hash: str) -> list[str]:
    """
    Returns a list of Python files that have been changed since the last update.

    Args:
        `last_commit_hash` (str): The commit hash of the last update.

    Returns:
        `list[str]`: A list of changed Python file paths.
    """
    git_command = f"git diff --name-only {last_commit_hash} HEAD"

    result = subprocess.run(git_command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Git command failed: {result.stderr}")

    changed_files = result.stdout.strip().split("\n")
    return [file for file in changed_files if file.endswith(".py")]


def get_current_commit_hash() -> str:
    """
    Retrieves the current commit hash.

    Returns:
        `str`: The current commit hash.
    """
    git_command = "git rev-parse HEAD"

    result = subprocess.run(git_command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Git command failed: {result.stderr}")

    return result.stdout.strip()
