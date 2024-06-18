import re
import textwrap


def clean_text(text):
    return re.sub(r"[\n\r\t]+", "", textwrap.dedent(text))
