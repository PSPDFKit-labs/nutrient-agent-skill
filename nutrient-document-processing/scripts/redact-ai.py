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
from lib.common import (
    add_processor_confirmation_args,
    assert_local_file,
    create_client,
    fix_negative_args,
    handle_error,
    parse_page_range,
    verify_pdf_output,
    write_binary_output,
)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage AI redaction annotations for review; never apply them.",
        epilog="Review the staged PDF visually before a separately approved apply step.",
    )
    parser.add_argument("--input", required=True, help="Local path to the input PDF.")
    parser.add_argument("--criteria", required=True, help="Natural-language redaction criteria.")
    parser.add_argument("--out", required=True, help="Output file path.")
    parser.add_argument("--pages", help="Inclusive page range in start:end format.")
    add_processor_confirmation_args(parser, "stage AI redaction annotations")
    args = parser.parse_args(fix_negative_args())

    pages = parse_page_range(args.pages) if args.pages else None
    input_path = assert_local_file(args.input, "input")

    client = create_client(args)
    result = await client.create_redactions_ai(input_path, args.criteria, "stage", pages)
    write_binary_output(result, args.out)
    verify_pdf_output(args.out)
    print("Staged only. Visually review every annotation before any apply-redactions run.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        handle_error(e)
