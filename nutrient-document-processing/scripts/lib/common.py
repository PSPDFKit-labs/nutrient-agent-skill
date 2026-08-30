import argparse
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any, NoReturn

_NEGATIVE_VALUE_RE = re.compile(r"^-\d")


def _positive_number(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number greater than zero") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def add_processor_confirmation_args(
    parser: argparse.ArgumentParser, operation: str
) -> None:
    """Add the action-time gate required before a paid Processor API request."""
    parser.add_argument(
        "--estimated-credits",
        required=True,
        type=_positive_number,
        metavar="NUMBER",
        help="Credit estimate presented to and approved by the user for this run.",
    )
    parser.add_argument(
        "--confirm-external-processing",
        action="store_true",
        help=(
            "Confirm the user approved this exact operation, input transfer, and "
            "credit estimate immediately before this run."
        ),
    )
    parser.set_defaults(_processor_operation=operation)


def require_processor_confirmation(args: argparse.Namespace) -> None:
    """Fail before client creation unless this exact paid run was approved."""
    if not getattr(args, "confirm_external_processing", False):
        operation = getattr(args, "_processor_operation", "Processor API operation")
        estimate = getattr(args, "estimated_credits", "unknown")
        raise RuntimeError(
            "Paid DWS request blocked. Present the user with the operation "
            f"({operation}), files transferred, and estimated credits ({estimate}); "
            "obtain approval immediately before the run, then pass "
            "--confirm-external-processing."
        )


def create_client(args: argparse.Namespace):
    """Create a NutrientClient after the caller has passed the confirmation gate."""
    require_processor_confirmation(args)
    api_key = os.environ.get("NUTRIENT_API_KEY")
    if not api_key:
        raise RuntimeError(
            "NUTRIENT_API_KEY is not set. Configure it through the host's protected "
            "runtime environment or secrets manager; never paste its value into chat."
        )
    try:
        from nutrient_dws import NutrientClient
    except ImportError as exc:
        raise RuntimeError(
            "Unable to import nutrient_dws 3.1.0. Run the script with uv so its "
            f"pinned dependency is installed. Original error: {exc}"
        ) from exc
    return NutrientClient(api_key=api_key)


def _atomic_write_no_overwrite(path: str, data: bytes) -> Path:
    """Publish bytes atomically without replacing an existing destination."""
    out = Path(path).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() or out.is_symlink():
        raise FileExistsError(f"Refusing to overwrite existing output: {out}")

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=out.parent, prefix=f".{out.name}.", delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)
            os.chmod(temp_path, 0o600)
            temp_file.write(data)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.link(temp_path, out)
        return out
    except FileExistsError as exc:
        raise FileExistsError(f"Refusing to overwrite existing output: {out}") from exc
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def write_binary_output(result: dict, path: str) -> None:
    """Safely write a BufferOutput result to disk."""
    buffer = result.get("buffer")
    if not isinstance(buffer, (bytes, bytearray)):
        raise ValueError("Expected a BufferOutput containing bytes in 'buffer'.")
    out = _atomic_write_no_overwrite(path, bytes(buffer))
    mime = result.get("mimeType", "application/octet-stream")
    print(f"Wrote {out} ({mime})")


def write_text_output(content: str, path: str, mime: str = "text/plain") -> None:
    """Safely write text without replacing an existing destination."""
    if not isinstance(content, str):
        raise ValueError("Expected text content as a string.")
    out = _atomic_write_no_overwrite(path, content.encode("utf-8"))
    print(f"Wrote {out} ({mime})")


def write_json_data(data: Any, path: str) -> None:
    """Safely serialize JSON data without replacing an existing destination."""
    serialized = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    out = _atomic_write_no_overwrite(path, serialized.encode("utf-8"))
    print(f"Wrote {out} (application/json)")


def write_json_output(result: dict, path: str) -> None:
    """Write the data portion of a JsonContentOutput."""
    if "data" not in result:
        raise ValueError("Expected a JsonContentOutput containing 'data'.")
    write_json_data(result["data"], path)


def write_typed_output(result: dict, path: str) -> None:
    """Write BufferOutput, ContentOutput, or JsonContentOutput safely."""
    if "buffer" in result:
        write_binary_output(result, path)
    elif "content" in result:
        write_text_output(
            result["content"], path, result.get("mimeType", "text/plain")
        )
    elif "data" in result:
        write_json_output(result, path)
    else:
        raise ValueError("Unsupported DWS output: expected buffer, content, or data.")


def write_workflow_output(result: dict, path: str) -> None:
    """Write a WorkflowResult to disk, raising on failure."""
    if not result.get("success") or not result.get("output"):
        errors = result.get("errors") or []
        messages = "; ".join(str(error.get("error", error)) for error in errors)
        raise RuntimeError(f"Workflow failed: {messages or 'unknown error'}")
    write_typed_output(result["output"], path)


def verify_pdf_output(path: str) -> None:
    """Perform a deterministic local sanity check on a produced PDF."""
    pdf_path = Path(path).expanduser()
    if not pdf_path.is_file() or pdf_path.stat().st_size < 5:
        raise RuntimeError(f"Output verification failed: missing or empty PDF {pdf_path}")
    with pdf_path.open("rb") as pdf_file:
        if pdf_file.read(5) != b"%PDF-":
            raise RuntimeError(f"Output verification failed: not a PDF {pdf_path}")
    print(f"Verified PDF container: {pdf_path}")


def parse_page_range(value: str) -> dict:
    """Parse an inclusive, zero-based ``start:end`` Processor page range."""
    parts = str(value).split(":")
    if len(parts) != 2:
        raise ValueError(
            f"Invalid page range '{value}'. Use inclusive start:end (for example 0:4)."
        )
    result: dict[str, int] = {}
    for index, name in enumerate(("start", "end")):
        if parts[index] == "":
            continue
        try:
            result[name] = int(parts[index])
        except ValueError as exc:
            raise ValueError(f"Invalid {name} in page range '{value}'.") from exc
    if not result:
        raise ValueError(
            f"Invalid page range '{value}'. Use inclusive start:end (for example 0:4)."
        )
    if "start" in result and "end" in result:
        start, end = result["start"], result["end"]
        if (start >= 0 and end >= 0 and start > end) or (
            start < 0 and end < 0 and start > end
        ):
            raise ValueError(f"Page range start must not follow end: '{value}'.")
    return result


def parse_csv(value: str) -> list[str]:
    """Split a comma-separated string into trimmed, non-empty strings."""
    if not value:
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]


def parse_integer_csv(value: str) -> list[int]:
    """Split a comma-separated string into integers."""
    result = []
    for item in parse_csv(value):
        try:
            result.append(int(item))
        except ValueError as exc:
            raise ValueError(f"Invalid integer value: '{item}'") from exc
    return result


def assert_local_file(value: str, arg: str) -> str:
    """Require an existing local regular file."""
    candidate = str(value).strip()
    if candidate.startswith(("http://", "https://")):
        raise ValueError(f"--{arg} must be a local file path for this operation.")
    path = Path(candidate).expanduser()
    if not path.is_file():
        raise ValueError(f"--{arg} is not an existing local file: {path}")
    return str(path)


def read_json_file(path: str) -> Any:
    """Read and parse a JSON file."""
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in file ({path}): {exc}") from exc


def read_secret_file(path: str, label: str) -> str:
    """Read a secret from an owner-only local file, never from argv."""
    secret_path = Path(assert_local_file(path, label))
    file_mode = stat.S_IMODE(secret_path.stat().st_mode)
    if file_mode & 0o077:
        raise PermissionError(
            f"--{label} must be owner-only (chmod 600 {secret_path})."
        )
    value = secret_path.read_text(encoding="utf-8").rstrip("\r\n")
    if not value:
        raise ValueError(f"--{label} is empty.")
    return value


def parse_json_string(value: str) -> Any:
    """Parse a non-secret JSON string."""
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON string: {exc}") from exc


def fix_negative_args() -> list[str]:
    """Reattach negative numeric values to their argparse flag."""
    argv = sys.argv[1:]
    result = []
    index = 0
    while index < len(argv):
        argument = argv[index]
        if (
            argument.startswith("--")
            and "=" not in argument
            and index + 1 < len(argv)
            and _NEGATIVE_VALUE_RE.match(argv[index + 1])
        ):
            result.append(f"{argument}={argv[index + 1]}")
            index += 2
        else:
            result.append(argument)
            index += 1
    return result


def handle_error(error: Exception) -> NoReturn:
    """Print an error without a traceback or secret values and exit 1."""
    print(str(error), file=sys.stderr)
    raise SystemExit(1)
