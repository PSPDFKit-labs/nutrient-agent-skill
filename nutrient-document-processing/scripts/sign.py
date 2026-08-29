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
    create_client,
    write_binary_output,
    assert_local_file,
    read_json_file,
    add_processor_confirmation_args,
    verify_pdf_output,
    handle_error,
)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Digitally sign a PDF.",
        epilog="Note: sign() only supports local file inputs for the main PDF.",
    )
    parser.add_argument("--input", required=True, help="Local path to the input PDF.")
    parser.add_argument("--out", required=True, help="Output file path.")
    parser.add_argument(
        "--signature-json-file",
        required=True,
        help="Path to explicit signature config JSON; signatureType is required.",
    )
    parser.add_argument("--image", help="Local path to a signature image.")
    parser.add_argument(
        "--graphic-image", dest="graphic_image", help="Local path to a graphic image."
    )
    add_processor_confirmation_args(parser, "digitally sign PDF")
    args = parser.parse_args()

    input_path = assert_local_file(args.input, "input")

    signature_data = read_json_file(args.signature_json_file)
    if not isinstance(signature_data, dict) or signature_data.get("signatureType") not in {
        "cms",
        "cades",
    }:
        parser.error("--signature-json-file must contain signatureType 'cms' or 'cades'.")
    if signature_data["signatureType"] == "cades" and "cadesLevel" not in signature_data:
        parser.error("CAdES configuration must include cadesLevel (b-b, b-t, or b-lt).")

    options: dict = {}
    if args.image:
        options["image"] = assert_local_file(args.image, "image")
    if args.graphic_image:
        options["graphicImage"] = assert_local_file(args.graphic_image, "graphic-image")

    client = create_client(args)
    result = await client.sign(input_path, signature_data, options or None)
    write_binary_output(result, args.out)
    verify_pdf_output(args.out)
    print("Verify the embedded signature and trust chain with an independent PDF validator.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        handle_error(e)
