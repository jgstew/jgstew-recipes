#!/usr/local/autopkg/python

import os
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["GitCommitSubprocess"]


class GitCommitSubprocess(Processor):
    """An AutoPkg processor to commit changed files to a Git repository."""

    input_variables = {
        "repo_path": {
            "required": True,
            "description": "Path to the Git repository.",
        },
        "commit_message": {
            "required": True,
            "description": "Commit message for the changes.",
        },
        "push_changes": {
            "required": False,
            "description": "Whether to push changes to the remote repository. Defaults to False.",
            "default": False,
        },
        "remote_name": {
            "required": False,
            "description": "Name of the remote to push to. Defaults to 'origin'.",
            "default": "origin",
        },
        "branch_name": {
            "required": False,
            "description": "Name of the branch to commit to. Defaults to 'main'.",
            "default": "main",
        },
    }
    output_variables = {}

    description = __doc__

    def run_git_command(self, args, cwd=None):
        """Helper function to run Git commands."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise ProcessorError(f"Git command failed: {e.stderr}")

    def main(self):
        repo_path = self.env["repo_path"]
        commit_message = self.env["commit_message"]
        push_changes = self.env.get("push_changes", False)
        remote_name = self.env.get("remote_name", "origin")
        branch_name = self.env.get("branch_name", "main")

        # Check if the directory is a Git repository
        if not os.path.isdir(os.path.join(repo_path, ".git")):
            raise ProcessorError(f"{repo_path} is not a Git repository.")

        # Check for changes
        status_output = self.run_git_command(["status", "--porcelain"], cwd=repo_path)
        if not status_output:
            self.output("No changes to commit.")
            return

        # Stage all changes
        self.run_git_command(["add", "."], cwd=repo_path)

        # Commit changes
        self.run_git_command(["commit", "-m", commit_message], cwd=repo_path)
        self.output(f"Committed changes with message: {commit_message}")

        # Push changes if requested
        if push_changes:
            self.run_git_command(["push", remote_name, branch_name], cwd=repo_path)
            self.output(f"Pushed changes to {remote_name}/{branch_name}.")


if __name__ == "__main__":
    PROCESSOR = GitCommitSubprocess()
    PROCESSOR.execute_shell()
