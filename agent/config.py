from dataclasses import dataclass
from pathlib import Path
import re

_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")

@dataclass(frozen=True)
class Config:
    repository_root: Path
    output_root: Path
    max_slice_lines: int = 100
    max_file_bytes: int = 1048576
    max_files: int = 10000
    command_timeout: int = 60

    def __post_init__(self):
        for value in (self.max_slice_lines, self.max_file_bytes, self.max_files, self.command_timeout):
            if type(value) is not int or value <= 0:
                raise ValueError("Limits must be positive integers")

    def repository(self, relative):
        root = self.repository_root.resolve()
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Repository outside permitted root")
        if not path.is_dir():
            raise ValueError("Repository does not exist")
        if path.is_symlink() or (path / ".git").is_symlink():
            raise ValueError("Repository or git metadata cannot be a symlink")
        return path

    def output(self, relative="."):
        root = self.output_root.resolve()
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Output outside permitted root")
        path.mkdir(parents=True, exist_ok=True)
        return path
