from app.adapters.diffing import generate_unified_diff, apply_unified_patch


def test_generate_unified_diff_has_expected_headers():
    original = "a\nb\nc\n"
    modified = "a\nB\nc\n"

    diff = generate_unified_diff(original, modified, "example.txt")

    assert "--- a/example.txt" in diff
    assert "+++ b/example.txt" in diff
    assert "@@ -1,3 +1,3 @@" in diff
    assert "-b\n" in diff
    assert "+B\n" in diff


def test_apply_unified_patch_replaces_line():
    original = "a\nb\nc\n"
    diff = (
        "--- a/example.txt\n"
        "+++ b/example.txt\n"
        "@@ -1,3 +1,3 @@\n"
        " a\n"
        "-b\n"
        "+B\n"
        " c\n"
    )

    updated = apply_unified_patch(original, diff)

    assert updated == "a\nB\nc\n"


def test_apply_unified_patch_inserts_line():
    original = "a\nc\n"
    diff = (
        "--- a/example.txt\n"
        "+++ b/example.txt\n"
        "@@ -1,2 +1,3 @@\n"
        " a\n"
        "+b\n"
        " c\n"
    )

    updated = apply_unified_patch(original, diff)

    assert updated == "a\nb\nc\n"


def test_apply_unified_patch_deletes_line():
    original = "a\nb\nc\n"
    diff = (
        "--- a/example.txt\n"
        "+++ b/example.txt\n"
        "@@ -1,3 +1,2 @@\n"
        " a\n"
        "-b\n"
        " c\n"
    )

    updated = apply_unified_patch(original, diff)

    assert updated == "a\nc\n"


def test_apply_unified_patch_noop_on_empty_diff():
    original = "a\nb\nc\n"

    updated = apply_unified_patch(original, "")

    assert updated == original