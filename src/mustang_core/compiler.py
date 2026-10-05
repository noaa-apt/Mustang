import random

MAGIC = "MUSTANG-1"


def _transform_encode(byte_val: int, index: int) -> int:
    return byte_val * 3 + 17 + (index % 11)


def encode_bytes_to_tokens(data: bytes) -> str:
    values = [_transform_encode(b, i) for i, b in enumerate(data)]

    rng = random.Random(len(data))
    groups = []
    i = 0
    n = len(values)
    while i < n:
        size = min(rng.randint(1, 3), n - i)
        groups.append(":".join(str(v) for v in values[i:i + size]))
        i += size
    return " ".join(groups)


BOOTSTRAP_TEMPLATE = '''# {magic}
# Compiled by the Mustang compiler.

_MUSTANG_DATA = """{data}"""


def _mustang_run():
    values = []
    for _group in _MUSTANG_DATA.split():
        for _num in _group.split(":"):
            if _num:
                values.append(int(_num))
    _bytes = bytearray()
    for _i, _v in enumerate(values):
        _bytes.append((_v - 17 - (_i % 11)) // 3)
    _src = bytes(_bytes).decode("utf-8")
    exec(compile(_src, "<mustang>", "exec"), {{"__name__": "__main__"}})


_mustang_run()
'''


def compile_source(source_code: str, filename: str = "compiled.mustang") -> str:
    token_data = encode_bytes_to_tokens(source_code.encode("utf-8"))
    return BOOTSTRAP_TEMPLATE.format(magic=MAGIC, filename=filename, data=token_data)
