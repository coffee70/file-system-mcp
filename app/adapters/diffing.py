import difflib
import re
from typing import List


_HUNK_HEADER_RE = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? \+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@"
)


def generate_unified_diff(original: str, modified: str, path: str) -> str:
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)

    diff_lines = list(
        difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
            lineterm="\n",  # ensure each diff line ends with newline
        )
    )

    # ensure every diff line ends with a newline
    normalized = []
    for line in diff_lines:
        if not line.endswith("\n"):
            line = line + "\n"
        normalized.append(line)

    return "".join(normalized)


def apply_unified_patch(original: str, diff_text: str) -> str:
    if not diff_text.strip():
        return original

    diff_lines = diff_text.splitlines(keepends=True)
    original_lines = original.splitlines(keepends=True)

    result: List[str] = []
    src_index = 0
    i = 0

    while i < len(diff_lines):
        line = diff_lines[i]

        if line.startswith("--- ") or line.startswith("+++ "):
            i += 1
            continue

        if not line.startswith("@@"):
            i += 1
            continue

        match = _HUNK_HEADER_RE.match(line.rstrip("\n"))
        if not match:
            raise ValueError(f"Invalid unified diff hunk header: {line!r}")

        old_start = int(match.group("old_start"))
        old_count = int(match.group("old_count") or "1")

        target_src_index = max(old_start - 1, 0)

        if target_src_index < src_index:
            raise ValueError("Overlapping or out-of-order hunks are not supported.")

        result.extend(original_lines[src_index:target_src_index])
        src_index = target_src_index
        i += 1

        consumed_from_source = 0

        while i < len(diff_lines):
            hunk_line = diff_lines[i]

            if hunk_line.startswith("@@"):
                break

            if hunk_line.startswith("--- ") or hunk_line.startswith("+++ "):
                break

            if hunk_line.startswith("\\"):
                i += 1
                continue

            prefix = hunk_line[:1]
            content = hunk_line[1:] if prefix in {" ", "+", "-"} else hunk_line

            if prefix == " ":
                if src_index >= len(original_lines):
                    raise ValueError("Patch context exceeds original content.")
                if original_lines[src_index].rstrip("\n") != content.rstrip("\n"):
                    raise ValueError(
                        "Patch context mismatch.\n"
                        f"Expected: {original_lines[src_index]!r}\n"
                        f"Got:      {content!r}"
                    )
                result.append(original_lines[src_index])
                src_index += 1
                consumed_from_source += 1

            elif prefix == "-":
                if src_index >= len(original_lines):
                    raise ValueError("Patch removal exceeds original content.")
                if original_lines[src_index].rstrip("\n") != content.rstrip("\n"):
                    raise ValueError(
                        "Patch removal mismatch.\n"
                        f"Expected: {original_lines[src_index]!r}\n"
                        f"Got:      {content!r}"
                    )
                src_index += 1
                consumed_from_source += 1

            elif prefix == "+":
                result.append(content)

            else:
                raise ValueError(f"Unsupported diff line: {hunk_line!r}")

            i += 1

        if old_count == 0:
            # Pure insertion hunk; nothing required from source.
            pass
        elif consumed_from_source != old_count:
            raise ValueError(
                f"Patch hunk source line count mismatch: expected {old_count}, got {consumed_from_source}"
            )

    result.extend(original_lines[src_index:])
    return "".join(result)