# bifrost_bridge

`bifrost_bridge` converts outputs from multiple bioinformatics QC tools into normalized TSV files and can combine them into a single QC table.

## Development

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

## CLI

Installed commands:

- `bridge_mlst`
- `bridge_fastp`
- `bridge_quast`
- `bridge_plasmidfinder`
- `bridge_amrfinderplus`
- `bridge_bracken`
- `bridge_pmlst`
- `bridge_rmlst`
- `bridge_shovill`
- `bridge_ssiamb`
- `bridge_qc`

Use `--help` on each command for arguments.
