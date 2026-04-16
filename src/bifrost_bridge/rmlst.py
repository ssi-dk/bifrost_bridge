from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from bifrost_bridge.cli import build_parser
from bifrost_bridge import core


def process_rmlst_data(
    input_path: str,
    output_path: str = "./output.tsv",
    parsed: bool = False,
    replace_header: str | None = None,
    filter_columns: str | None = None,
    add_header: str | None = None,
) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"The input file {input_path} does not exist.")

    df = core.DataFrame()
    if parsed:
        df.import_data(input_file, file_type="tsv")
        if df.df.isna().iloc[0, 0]:
            Path(output_path).write_text("", encoding="utf-8")
            return
        if filter_columns:
            df.filter_columns(filter_columns)
        if replace_header:
            df.rename_header(replace_header)
        df.export_data(output_path, file_type="tsv")
        return

    if input_file.stat().st_size > 0:
        with input_file.open(encoding="utf-8") as rmlst_json:
            rmlst_dict = json.load(rmlst_json)
        rmlst_dict.pop("exact_matches")
        taxon_prediction_df = pd.json_normalize(rmlst_dict["taxon_prediction"])
        taxon_prediction_df = (
            taxon_prediction_df.apply(
                lambda vector: ",".join([str(item) for item in vector]), axis=0
            )
            .to_frame()
            .T
        )
        df.df = taxon_prediction_df
        if filter_columns:
            df.filter_columns(filter_columns)
        if replace_header:
            df.rename_header(replace_header)
        df.export_data(output_path, file_type="tsv")
        return

    empty_df = pd.DataFrame(
        columns=[col.strip() for col in (replace_header or "").split(",") if col.strip()]
    )
    empty_df.to_csv(output_path, index=False)


def process_rmlst_data_from_cli() -> None:
    parser = build_parser(
        "Process rMLST JSON or parsed TSV output into a normalized TSV.",
        [
            {"names": ["input_path"], "kwargs": {"help": "Path to the input rMLST file."}},
            {"names": ["--output-path"], "kwargs": {"default": "./output.tsv"}},
            {"names": ["--parsed"], "kwargs": {"action": "store_true"}},
            {"names": ["--replace-header"], "kwargs": {"default": None}},
            {"names": ["--filter-columns"], "kwargs": {"default": None}},
            {"names": ["--add-header"], "kwargs": {"default": None}},
        ],
    )
    args = parser.parse_args()
    process_rmlst_data(**vars(args))
