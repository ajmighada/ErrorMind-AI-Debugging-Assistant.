"""Safe, rule-based analysis of pasted Python error messages.

Never executes supplied source code or traceback text.
"""
from __future__ import annotations

import re


GUIDANCE = {
    "NameError": (
        "Python tried to use a name that has not been defined in the current scope.",
        "Check spelling, capitalization, and whether the variable or function was defined before use.",
    ),
    "TypeError": (
        "An operation received a value of an incompatible type.",
        "Inspect the types of the variables involved. Convert values deliberately if appropriate.",
    ),
    "ValueError": (
        "A value is of the expected general type but is not valid for this operation.",
        "Inspect the actual input value and validate it before conversion or processing.",
    ),
    "IndexError": (
        "Your code tried to access a sequence position that does not exist.",
        "Inspect the list length and the index; valid indexes run from 0 to len(sequence)-1.",
    ),
    "KeyError": (
        "Your code tried to access a dictionary key that was not found.",
        "Check the key spelling, or use .get() when missing keys are expected.",
    ),
    "ZeroDivisionError": (
        "Your code attempted division or modulo by zero.",
        "Check the denominator and decide how your program should handle zero.",
    ),
    "ModuleNotFoundError": (
        "Python could not find a module your code tried to import.",
        "Check the active environment, module spelling, and which package provides that module.",
    ),
    "ImportError": (
        "An import failed, even though the module might exist.",
        "Check the exported name, installed package version, and circular imports.",
    ),
    "FileNotFoundError": (
        "The program tried to open a file or directory that was not found.",
        "Check the current working directory and file path; consider using pathlib.Path.",
    ),
    "AttributeError": (
        "Your code tried to access an attribute or method that the object doesn't have.",
        "Inspect the object's type and available attributes; check for None and misspellings.",
    ),
    "SyntaxError": (
        "Python could not parse the code as valid Python syntax.",
        "Inspect the indicated line and its preceding line for missing punctuation or brackets.",
    ),
    "IndentationError": (
        "Python detected inconsistent or missing indentation.",
        "Align the affected block and avoid mixing tabs with spaces.",
    ),
    "TabError": (
        "Tabs and spaces were mixed inconsistently in indentation.",
        "Convert indentation consistently to four spaces per level.",
    ),
    "RecursionError": (
        "A recursive function called itself too deeply.",
        "Review the base case and whether each recursive call moves toward it.",
    ),
    "AssertionError": (
        "An assertion evaluated to False.",
        "Inspect the asserted condition and the values that violate it.",
    ),
}

# Find exception name on the *last* exception line, not inside arbitrary code.
_EXCEPTION_LINE = re.compile(
    r"^\s*(?:[\w.]+\.)?([A-Za-z_]\w*(?:Error|Exception))\s*:\s*(.*?)\s*$"
)
_LINE_REFERENCE = re.compile(r'\bFile\s+"([^"]+)",\s*line\s+(\d+)')


def analyze_error(traceback_text: str) -> dict[str, str | int | None]:
    """Extract an error category, location, and a cautious suggested next step."""
    if not traceback_text or not traceback_text.strip():
        return {
            "error_type": "No error supplied",
            "message": "Paste a Python error or traceback.",
            "file": None,
            "line": None,
            "explanation": "The analyzer needs an error message.",
            "suggestion": "Run your program and copy the error message that Python prints.",
        }

    exception_type = "UnknownError"
    message = "Could not identify a Python exception line."
    for line in traceback_text.splitlines():
        match = _EXCEPTION_LINE.match(line)
        if match:
            exception_type, message = match.group(1), match.group(2)

    locations = _LINE_REFERENCE.findall(traceback_text)
    file_name = locations[-1][0] if locations else None
    line_number = int(locations[-1][1]) if locations else None

    if exception_type == "UnknownError":
        explanation = "The input doesn't match a standard Python exception message."
        suggestion = "Include the last line of the traceback, such as 'TypeError: ...'."
    else:
        explanation, suggestion = GUIDANCE.get(
            exception_type,
            (
                "Python raised an exception while executing the program.",
                "Read the exception message and check the indicated source line.",
            ),
        )

    if exception_type == "NameError":
        var_match = re.search(r"name ['\"]([^'\"]+)['\"] is not defined", message)
        if var_match:
            suggestion = f"Check where '{var_match.group(1)}' is defined and whether its name is spelled correctly."
    elif exception_type == "TypeError" and "unsupported operand type" in message:
        suggestion = (
            "Two incompatible types were used together. If a numeric string should be a number, "
            "convert it with int() or float(); if you meant to combine text, use str()."
        )
    elif exception_type == "ModuleNotFoundError":
        mod_match = re.search(r"No module named ['\"]([^'\"]+)['\"]", message)
        if mod_match:
            suggestion = (
                f"Check whether the module '{mod_match.group(1)}' is installed in your active "
                "Python environment. Verify its package name before installing anything."
            )

    return {
        "error_type": exception_type,
        "message": message,
        "file": file_name,
        "line": line_number,
        "explanation": explanation,
        "suggestion": suggestion,
    }
