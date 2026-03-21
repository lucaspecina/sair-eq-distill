"""
Cycle 5c cheatsheet generator.

Strategy: Three surgical changes to the backed-up cheatsheet:

1. Refine composite rule: n_vars>=5 => TRUE (92% accurate)
   Changes 2 lines total.

2. Add STOP-EARLY instruction after decision tree to reduce
   token exhaustion (~14 None responses per 200 problems).

3. Fix misleading example: Example 3 says "n_other >= 2 => TRUE"
   but should say "n_other >= 3 => TRUE" to match the actual rule.
   The model may misread ">=2" as a blanket rule and miss the
   x_occ>=3 exception at n_other=2.
"""

import os
import sys
from pathlib import Path


def generate_cheatsheet():
    """Read backup cheatsheet and make targeted surgical edits."""

    base = Path(__file__).parent.parent / "cheatsheets" / "session_backup.txt"
    content = base.read_text(encoding='utf-8')

    # Change 1: Refine composite in QUICK REFERENCE
    old_composite_line = "composite = composite              => lean FALSE"
    new_composite_lines = (
        "composite, eq1 has >=5 vars       => TRUE  (92%)\n"
        "composite, eq1 has <5 vars        => FALSE"
    )
    content = content.replace(old_composite_line, new_composite_lines)

    # Change 2: Refine composite in Node 3
    old_node3 = (
        "NODE 3: Is Eq1 self-referential? (form x = T where x appears in T)\n"
        "  YES => Go to NODE 3A.\n"
        "  NO => If both sides of Eq1 are compound terms, lean FALSE.\n"
        "        Otherwise lean FALSE."
    )
    new_node3 = (
        "NODE 3: Is Eq1 self-referential? (form x = T where x appears in T)\n"
        "  YES => Go to NODE 3A.\n"
        "  NO => Both sides compound? Count distinct vars in Eq1.\n"
        "        If Eq1 has >=5 distinct vars => TRUE (strong equation).\n"
        "        Otherwise => FALSE."
    )
    content = content.replace(old_node3, new_node3)

    # Change 3: Add STOP-EARLY instruction
    stop_early = (
        "\nIMPORTANT: Once you reach a verdict via the decision tree above,\n"
        "OUTPUT IT IMMEDIATELY. Do not re-verify with magma computations.\n"
        "The rules are pre-validated. Trust them and save reasoning tokens.\n"
    )
    marker = "================================================================\nCOUNTEREXAMPLE MAGMA DETAILS (for Node 2)"
    content = content.replace(marker, stop_early + "\n" + marker)

    # Change 4: Fix Examples 3 and 5 rule citation
    # "n_other >= 2 => Answer: TRUE." should be "n_other >= 3 => Answer: TRUE."
    # Both examples have n_other=3, so the correct rule is >= 3, not >= 2.
    # Using ">=2" could make the model think it applies to n_other=2 cases
    # unconditionally, missing the x_occ>=3 exception.
    old_example = "n_other >= 2 => Answer: TRUE."
    new_example = "n_other >= 3 => Answer: TRUE."
    content = content.replace(old_example, new_example)

    return content.strip()


def main():
    os.chdir(Path(__file__).parent.parent)

    cheatsheet = generate_cheatsheet()

    # Verify size
    size = len(cheatsheet.encode('utf-8'))
    print(f"Cheatsheet size: {size} bytes ({size/1024:.1f}KB)")
    assert size <= 10240, f"Too large: {size} bytes"

    # Write to current.txt
    output_path = Path("cheatsheets/current.txt")
    output_path.write_text(cheatsheet, encoding='utf-8')
    print(f"Written to {output_path}")

    # Also save a versioned backup
    backup_path = Path("cheatsheets/cycle5_v3.txt")
    backup_path.write_text(cheatsheet, encoding='utf-8')
    print(f"Backup saved to {backup_path}")


if __name__ == '__main__':
    main()
