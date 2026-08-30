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
    create_client,
    handle_error,
    parse_csv,
    read_secret_file,
    write_binary_output,
)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Protect a PDF with user/owner passwords.")
    parser.add_argument("--input", required=True, help="Path or URL to the input PDF.")
    parser.add_argument(
        "--user-password-file",
        required=True,
        help="Owner-only local file containing the user password (chmod 600).",
    )
    parser.add_argument(
        "--owner-password-file",
        required=True,
        help="Owner-only local file containing the owner password (chmod 600).",
    )
    parser.add_argument("--out", required=True, help="Output file path.")
    parser.add_argument("--permissions", help="Comma-separated list of permissions.")
    add_processor_confirmation_args(parser, "password-protect PDF")
    args = parser.parse_args()

    permissions = parse_csv(args.permissions) if args.permissions else None
    user_password = read_secret_file(args.user_password_file, "user-password-file")
    owner_password = read_secret_file(args.owner_password_file, "owner-password-file")

    client = create_client(args)
    result = await client.password_protect(
        args.input, user_password, owner_password, permissions
    )
    write_binary_output(result, args.out)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        handle_error(e)
