import re
from pathlib import Path

from bifrost_bridge.cli import build_parser
from bifrost_bridge import core


def process_plasmidfinder_data(
    input_path: str,
    output_path: str = "./output.tsv",
    replace_header: str | None = None,
    filter_columns: str | None = None,
    convert_coverage: bool = False,
    filter_contig: bool = False,
) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"The input file {input_path} does not exist.")

    df = core.DataFrame()
    df.import_data(input_file, file_type="tsv")
    if df.df.isna().iloc[0, 0]:
        Path(output_path).write_text("", encoding="utf-8")
        return

    if df.df.shape[0] == 1 and list(df.df.columns) == list(range(df.df.shape[1])):
        df.df.columns = df.df.iloc[0]
        df.df = df.df.iloc[1:]

    def process_coverage(value: str) -> str:
        parts = [item.strip() for item in str(value).split(",")]
        results = []
        for part in parts:
            if "/" in part:
                num, denom = part.split("/")
                try:
                    results.append(str(float(num.strip()) / float(denom.strip()) * 100))
                except Exception:
                    results.append(part)
            else:
                results.append(part)
        return ",".join(results)

    def extract_contig(value: str) -> str:
        parts = [item.strip() for item in str(value).split(",")]
        results = []
        for part in parts:
            match = re.search(r"\b(\w+)\d+\b", part)
            results.append(match.group(0) if match else part)
        return ",".join(results)

    if convert_coverage:
        df.df["Query / Template length"] = df.df["Query / Template length"].apply(process_coverage)
    if filter_contig:
        df.df["Contig"] = df.df["Contig"].apply(extract_contig)
    if filter_columns:
        df.filter_columns(filter_columns)
    if replace_header:
        df.rename_header(replace_header)
    df = df.collapse_rows()
    df.export_data(output_path, file_type="tsv")


def process_plasmidfinder_data_from_cli() -> None:
    parser = build_parser(
        "Process PlasmidFinder TSV output into a normalized TSV.",
        [
            {
                "names": ["input_path"],
                "kwargs": {"help": "Path to the input PlasmidFinder TSV file."},
            },
            {"names": ["--output_path"], "kwargs": {"default": "./output.tsv"}},
            {"names": ["--replace_header"], "kwargs": {"default": None}},
            {"names": ["--filter_columns"], "kwargs": {"default": None}},
            {"names": ["--convert_coverage"], "kwargs": {"action": "store_true"}},
            {"names": ["--filter_contig"], "kwargs": {"action": "store_true"}},
        ],
    )
    args = parser.parse_args()
    process_plasmidfinder_data(**vars(args))
