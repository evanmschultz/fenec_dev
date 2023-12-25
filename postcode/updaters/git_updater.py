import subprocess


class UpdateUsingGit:
    """
    DO NOT USE: The necessary functionality for this class is not yet implemented.

    A class that provides methods to get the names of the Python modules that have been changed using on version control.

    Use this class to get all the file names for the Python modules that have been changes since the last commit or since
    a specific commit. You can get the `commit_hash` for a specific commit by going to the commit on GitHub and copying
    the hash from the URL. For example, the commit hash for the following commit is `e8856d2`, or you can use the terminal, for
    instance: `git log --author="username" --grep="commit message" --format="%H"` if you know all the details of the commit.

    Methods:
        - `get_module_names_updated_since_last_commit()`: Returns a list of the modules that have been changed since the last commit.
        - `get_module_names_updated_since_commit(commit_hash: str)`: Returns a list of the modules that have been changed since the specified commit.

    Examples:
        ```Python
        from postcode.updaters.git_updater import UpdateUsingGit

        # Get the names of the modules that have been changed since the last commit
        changed_modules_name_list = UpdateUsingGit.get_module_names_updated_since_last_commit()
        ```
    """

    @staticmethod
    def get_module_names_updated_since_last_commit() -> list[str]:
        """
        Returns a list of the modules that have been changed since the last commit.

        Runs the following command using subprocess:
            (git ls-files --others --exclude-standard; git diff --name-only HEAD) | sort | uniq

        Returns:
            - list[str]: A list of the modules that have been changed since the last commit.

        Raises:
            - Exception: If the git command fails.
        """

        git_command = "(git ls-files --others --exclude-standard; git diff --name-only HEAD) | sort | uniq"

        result: subprocess.CompletedProcess[str] = subprocess.run(
            git_command, shell=True, capture_output=True, text=True
        )
        if result.returncode != 0:
            raise Exception("Git command failed: " + result.stderr)

        changed_files: list[str] = result.stdout.strip().split("\n")

        return [file for file in changed_files if file.endswith(".py")]

    @staticmethod
    def get_module_names_updated_since_commit(commit_hash: str) -> list[str]:
        """
        Returns a list of the Python modules that have been changed since the specified commit.

        Args:
            - commit (str): The commit hash or reference to compare the current state against.

        Runs the following command using subprocess:
            (git ls-files --others --exclude-standard; git diff --name-only COMMIT) | sort | uniq

        Returns:
            - list[str]: A list of the modules that have been changed since the specified commit.

        Raises:
            - Exception: If the git command fails.
        """

        git_command = f"(git ls-files --others --exclude-standard; git diff --name-only {commit_hash}) | sort | uniq"

        result: subprocess.CompletedProcess[str] = subprocess.run(
            git_command, shell=True, capture_output=True, text=True
        )
        if result.returncode != 0:
            raise Exception("Git command failed: " + result.stderr)

        changed_files: list[str] = result.stdout.strip().split("\n")

        return [file for file in changed_files if file.endswith(".py")]

    @staticmethod
    def __get_updated_modules(directory: str | None = None) -> list[str]:
        """
        DO NOT USE: The necessary functionality for this method is not yet implemented.

        Returns a list of the modules that have been changed since the last commit based on a directory path.
        """
        git_ls_files_cmd = "git ls-files --others --exclude-standard"
        git_diff_cmd = "git diff --name-only HEAD"

        if directory:
            git_ls_files_cmd += f" '{directory}'"
            git_diff_cmd += f" '{directory}'"

        git_command: str = f"({git_ls_files_cmd}; {git_diff_cmd}) | sort | uniq"

        result: subprocess.CompletedProcess[str] = subprocess.run(
            git_command, shell=True, capture_output=True, text=True
        )
        if result.returncode != 0:
            raise Exception("Git command failed: " + result.stderr)

        changed_files: list[str] = result.stdout.strip().split("\n")

        return [file for file in changed_files if file.endswith(".py")]


if __name__ == "__main__":
    print(UpdateUsingGit.get_module_names_updated_since_commit("e8856d2"))
