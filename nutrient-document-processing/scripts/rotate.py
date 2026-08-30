#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["nutrient-dws==3.1.0"]
# ///

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.common import create_client, write_binary_output, parse_page_range, handle_error, fix_negative_args
from lib.common import add_processor_confirmation_args


async def main() -> None:
    parser = argparse.ArgumentParser(description="Rotate pages in a PDF.")
    parser.add_argument("--input", required=True, help="Path or URL to the input PDF.")
    parser.add_argument(
        "--angle",
        required=True,
        type=int,
        choices=[90, 180, 270],
        help="Rotation angle in degrees (90, 180, or 270).",
    )
    parser.add_argument("--out", required=True, help="Output file path.")
    parser.add_argument("--pages", help="Inclusive page range in start:end format.")
    add_processor_confirmation_args(parser, "rotate PDF pages")
    args = parser.parse_args(fix_negative_args())

    pages = parse_page_range(args.pages) if args.pages else None

    client = create_client(args)
    result = await client.rotate(args.input, args.angle, pages)
    write_binary_output(result, args.out)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        handle_error(e)
