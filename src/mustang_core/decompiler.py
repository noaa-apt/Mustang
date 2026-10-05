import re

_DATA_PATTERN = re.compile(r'_MUSTANG_DATA\s*=\s*"""(.*?)"""', re.DOTALL)


def _transform_decode(token_val: int, index: int) -> int:
    return (token_val - 17 - (index % 11)) // 3


def decode_tokens_to_bytes(token_str: str) -> bytes:
    values = []
    for group in token_str.split():
        for num in group.split(":"):
            if num:
                values.append(int(num))
    out = bytearray(_transform_decode(v, i) for i, v in enumerate(values))
    return bytes(out)


def decompile_file_text(mustang_file_text: str) -> str:
    match = _DATA_PATTERN.search(mustang_file_text)
    if not match:
        raise ValueError(
            "This does not look like a valid Mustang compiled file? "
            "(no _MUSTANG_DATA block found)."
        )
    token_data = match.group(1)
    raw_bytes = decode_tokens_to_bytes(token_data)
    return raw_bytes.decode("utf-8")
