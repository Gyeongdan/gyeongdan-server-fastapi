import json

import regex


def remove_comments(json_text):
    # Regex to match comments in the JSON string (both single line // and block /* */ comments)
    pattern = r"//.*?$|/\*.*?\*/"
    return regex.sub(pattern, "", json_text, flags=regex.MULTILINE | regex.DOTALL)


def parse(text):
    # First, remove comments from the JSON text
    clean_text = remove_comments(text)

    # Regex pattern to find a valid JSON using recursive matching
    pattern = r"\{(?:[^{}]+|(?R))*\}"
    matches = regex.findall(pattern, clean_text)

    # Assume the last match is the correct JSON (this might need more checks in real scenarios)
    json_data = matches[-1] if matches else None

    if json_data:
        try:
            return json.loads(json_data)
        except json.JSONDecodeError:
            return None
    else:
        return None
