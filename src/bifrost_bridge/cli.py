import argparse
from typing import Any


def build_parser(description: str, arguments: list[dict[str, Any]]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    for argument in arguments:
        parser.add_argument(*argument["names"], **argument["kwargs"])
    return parser
