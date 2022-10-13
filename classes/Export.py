import re


class Export:
    def __init__(self, line: str, file_name: str, line_number: int):
        self.line = re.search(rf"export\s(.*)", line).group(1)
        self.file_name = file_name
        self.line_number = line_number
