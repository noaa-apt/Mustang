__version__ = "2.3.6"

from .compiler import compile_source
from .decompiler import decompile_file_text

__all__ = ["compile_source", "decompile_file_text", "__version__"]
