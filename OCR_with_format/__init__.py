import fire
from beartype import beartype

from .ocr_with_format import OCR_with_format

__ALL__  = ["OCR_with_format"]

__VERSION__ = OCR_with_format.__VERSION__

@beartype
def cli() -> None:
    _ = fire.Fire(OCR_with_format().OCR)

if __name__ == "__main__":
    cli()
