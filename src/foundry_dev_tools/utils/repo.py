"""This file provides helper function for git repos."""
import logging
import subprocess
import warnings
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def get_repo() -> "tuple[str,str,str]":
    """Get the repository RID from the current working directory.

    Returns:
        tuple[str,str,str]: repo_rid,git_ref,git_revision_hash
    """
    if git_dir := traverse_to_git_project_top_level_dir(Path.cwd(), use_git=True):
        gradle_props = git_dir.joinpath("gradle.properties")
        if gradle_props.is_file():
            try:
                with gradle_props.open("r") as gpf:
                    for line in gpf.readlines():
                        if line.startswith("transformsRepoRid"):
                            return (
                                line.split("=")[1].strip(),
                                get_git_ref(git_dir),
                                get_git_revision_hash(git_dir),
                            )
            except:  # noqa
                pass
            raise Exception(
                "Can't get repository RID from the gradle.properties file. Malformed file?"
            )
        raise Exception(
            "There is no gradle.properties file at the top of the git repository, can't get repository RID."
        )
    raise Exception(
        "If you don't provide a repository RID you need to be in a repository directory"
        " to detect what you want to build."
    )


def get_git_ref(git_dir: "Path | None") -> str:
    """Get the branch ref in the supplied git directory.

    Args:
        git_dir (Path | None): a Path to a git directory or None
            if None it will use the current working directory
    """
    return (
        subprocess.check_output(
            [
                "git",
                "symbolic-ref",
                "HEAD",
            ],
            cwd=git_dir,
        )
        .decode("ascii")
        .strip()
    )


def get_git_revision_hash(git_dir: "Path | None") -> str:
    """Get the git revision hash.

    Args:
        git_dir (Path | None): a Path to a git directory or None
            if None it will use the current working directory
    """
    return (
        subprocess.check_output(
            [
                "git",
                "rev-parse",
                "HEAD",
            ],
            cwd=git_dir,
        )
        .decode("ascii")
        .strip()
    )


def traverse_to_git_project_top_level_dir(
    git_dir: Path, use_git: bool = False
) -> "Path | None":
    """Get git top level directory.

    Args:
        git_dir (Path): the path to a (sub)directory of a git repo
        use_git (bool): if true use real git executable,
            otherwise use minimal python only implementation

    Returns:
        Path | None: the path to the toplevel git directory or
            None if nothing was found.

    """
    if use_git:
        return Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], cwd=git_dir
            )
            .decode("utf-8")
            .strip()
        )
    if git_dir.joinpath(".git").is_dir():
        return git_dir
    for p in git_dir.resolve().parents:
        if p.joinpath(".git").is_dir():
            return p
    return None


def find_project_config_file(
    project_directory: Path, use_git: bool = False
) -> "Path | None":
    """Get the project config file in a git repo.

    Args:
        project_directory (Path): the (sub)directory of the project
        use_git (bool): passed to :py:meth:traverse_to_git_project_top_level_dir

    Returns:
        Path | None: Path to the project config or None if no file was found
    """
    if project_directory.is_dir():
        git_directory = traverse_to_git_project_top_level_dir(
            project_directory, use_git=use_git
        )
        if not git_directory:
            LOGGER.debug(
                "Project-based config file could not be loaded, is project not managed with git?"
            )
            return None

        project_config_file = git_directory / ".foundry_dev_tools"

        if project_config_file.is_file():
            return project_config_file

        foundry_local_project_config_file = git_directory / ".foundry_local_config"

        if foundry_local_project_config_file.is_file():
            warnings.warn(
                "Foundrylocal has been renamed to Foundry DevTools.\n"
                f"Move the old config file {foundry_local_project_config_file} to {project_config_file}\n"
                "The fallback to the old config file will be removed in the future!",
                category=DeprecationWarning,
            )
            return foundry_local_project_config_file
    return None
