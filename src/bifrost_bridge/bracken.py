from pathlib import Path

import pandas as pd

from bifrost_bridge.cli import build_parser
from bifrost_bridge import core


def process_bracken_data(
    input_path: str,
    output_path: str = "./output.tsv",
    add_header: str = "%ofreads, reads, notsure, rank, taxid, name",
    replace_header: str | None = None,
    filter_columns: str | None = None,
) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"The input file {input_path} does not exist.")

    df = core.DataFrame()
    df.import_data(input_file, file_type="tsv", add_header=add_header)
    df.df = pd.concat(
        [
            df.df[df.df["rank"] == "U"],
            df.df[df.df["rank"] == "S"].sort_values(by="%ofreads", ascending=False),
        ]
    ).head(3)

    df_output = core.DataFrame()
    if len(df.df) > 2 and df.df.iloc[2]["name"]:
        df_output.df = pd.DataFrame(
            {
                "species1_unclassified_name": [df.df.iloc[1]["name"].lstrip() + " + unclassified"],
                "species1_unclassified_pct": [
                    df.df.iloc[1]["%ofreads"] + df.df.iloc[0]["%ofreads"]
                ],
                "species1_name": [df.df.iloc[1]["name"].lstrip()],
                "species1_pct": [df.df.iloc[1]["%ofreads"]],
                "species2_name": [df.df.iloc[2]["name"].lstrip()],
                "species2_pct": [df.df.iloc[2]["%ofreads"]],
                "unclassified_name": [df.df.iloc[0]["name"].lstrip()],
                "unclassified_pct": [df.df.iloc[0]["%ofreads"]],
            }
        )
    else:
        df_output.df = pd.DataFrame(
            {
                "species1_unclassified_name": [df.df.iloc[1]["name"].lstrip() + " + unclassified"],
                "species1_unclassified_pct": [
                    df.df.iloc[1]["%ofreads"] + df.df.iloc[0]["%ofreads"]
                ],
                "species1_name": [df.df.iloc[1]["name"].lstrip()],
                "species1_pct": [df.df.iloc[1]["%ofreads"]],
                "species2_name": [""],
                "species2_pct": [""],
                "unclassified_name": [df.df.iloc[0]["name"].lstrip()],
                "unclassified_pct": [df.df.iloc[0]["%ofreads"]],
            }
        )

    if replace_header:
        df_output.rename_header(replace_header)
    if filter_columns:
        df_output.filter_columns(filter_columns)
    df_output.export_data(output_path, file_type="tsv")


def process_bracken_data_from_cli() -> None:
    parser = build_parser(
        "Process Bracken output into a normalized TSV.",
        [
            {"names": ["input_path"], "kwargs": {"help": "Path to the input Bracken report file."}},
            {"names": ["--output_path"], "kwargs": {"default": "./output.tsv"}},
            {
                "names": ["--add_header"],
                "kwargs": {"default": "%ofreads, reads, notsure, rank, taxid, name"},
            },
            {"names": ["--replace_header"], "kwargs": {"default": None}},
            {"names": ["--filter_columns"], "kwargs": {"default": None}},
        ],
    )
    args = parser.parse_args()
    process_bracken_data(**vars(args))
