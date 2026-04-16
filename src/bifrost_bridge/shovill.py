from __future__ import annotations

import re
from pathlib import Path

from bifrost_bridge.cli import build_parser
from bifrost_bridge import core


def process_shovill_data(
    input_path: str, output_path: str = "./output.tsv", average_coverage: bool = True
) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"The input file {input_path} does not exist.")

    avg_coverage = None
    with input_file.open("r", encoding="utf-8") as handle:
        for line in handle:
            match = re.search(r"Average coverage is ([\d\.]+) and alpha is", line)
            if match:
                avg_coverage = float(match.group(1))
                break

    df = core.DataFrame()
    if average_coverage:
        df.add_column("Average_Coverage", [avg_coverage])
    df.export_data(output_path, file_type="tsv")


def process_shovill_data_from_cli() -> None:
    parser = build_parser(
        "Process Shovill log output into a normalized TSV.",
        [
            {"names": ["input_path"], "kwargs": {"help": "Path to the input Shovill log file."}},
            {"names": ["--output-path"], "kwargs": {"default": "./output.tsv"}},
            {
                "names": ["--no-average-coverage"],
                "kwargs": {"action": "store_false", "dest": "average_coverage"},
            },
        ],
    )
    args = parser.parse_args()
    process_shovill_data(**vars(args))
