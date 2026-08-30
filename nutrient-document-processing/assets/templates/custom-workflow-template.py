#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["nutrient-dws==3.1.0"]
# ///

import argparse
import asyncio
import os
import sys
from pathlib import Path

from nutrient_dws.builder.constant import BuildActions

_installed_skill_dir = os.environ.get("NUTRIENT_SKILL_DIR")
if _installed_skill_dir:
    _scripts_dir = Path(_installed_skill_dir).expanduser().resolve() / "scripts"
else:
    _scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if not (_scripts_dir / "lib" / "common.py").is_file():
    raise RuntimeError(
        "Cannot locate the installed skill. Set NUTRIENT_SKILL_DIR to the "
        "directory containing SKILL.md before running a copied template."
    )
sys.path.insert(0, str(_scripts_dir))
from lib.common import (  # noqa: E402
    add_processor_confirmation_args,
    create_client,
    handle_error,
    write_workflow_output,
)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Template for multi-step custom workflows.")
    parser.add_argument("--input", required=True, help="Path or URL to the input document.")
    parser.add_argument("--out", required=True, help="Output file path.")
    add_processor_confirmation_args(parser, "custom Processor workflow")
    args = parser.parse_args()

    client = create_client(args)

    # Customize this action list for the requested pipeline.
    actions = [
        BuildActions.ocr("english"),
        BuildActions.watermark_text("DRAFT", {"opacity": 0.25, "rotation": 45}),
    ]

    result = await (
        client.workflow()
        .add_file_part(args.input, actions=actions)
        .output_pdf()
        .execute()
    )
    write_workflow_output(result, args.out)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        handle_error(e)
