# imports ---------------------------------------------------------------------
import os
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

from utils.osim_model_parser import parse_model
from sto_generator import read_input, write_header, write_columns

from utils.md_logger import log_md
try:
    from utils.get_md_log_file import md_log_file
except ImportError:
    md_log_file = None


# Parse args ------------------------------------------------------------------
def parse_arguments():
    """
    Parse CLI arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate an initial mesh for mmg based mesh adaptation",
        add_help=False,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help='Use switches followed by "=" to use CLI file autocomplete, example "-i="',
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        help="Path to input .osim model",
        required=True,
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="Path to input data file (.sto/.mat)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Filename for output .sto file",
    )
    parser.add_argument(
        "-l",
        "--log",
        action="store_true",
        help="Activate to log run",
    )
    return parser.parse_args()


# Main ------------------------------------------------------------------------
@log_md(md_log_file)
def sto_from_model(
    model_file,
    input_file,
    output_file,
):
    output_file = (
        Path(model_file.stem + "_moco_track_states.sto")
        if output_file is None
        else output_file
    )

    print(f"-- Reading data file: {input_file}")
    df, header = read_input(input_file)

    print(f"-- Reading model: {model_file}")
    states = parse_model(model_file)

    df2 = pd.DataFrame(0, index=range(len(df["time"])), columns=states)
    df2["time"] = df["time"]

    for state in states:
        if "jointset" in state and "ground" not in state:
            print(f" - Writing state: {state}")
            df2[state] = df[state]

    # Get rid of leftover empty matlab lists ([])
    df2 = df2.map(lambda x: 0 if isinstance(x, np.ndarray) and len(x) == 0 else x)

    write_header(output_file, header)
    write_columns(df2, output_file)
    print(f"-- Output .sto generated:\n - {output_file}")


if __name__ == "__main__":
    args = parse_arguments()

    model_file = Path(args.model)
    input_file = Path(args.input)
    output_file = Path(args.output) if args.output else None

    if model_file.parents[0]:
        os.chdir(model_file.parents[0])

    print(args.log)

    sto_from_model(
        model_file,
        Path(args.input),
        output_file,
    )
