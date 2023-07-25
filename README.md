# OCR_with_format
* simple wrapper that postprocesses pytesseract's hOCR output to maintain format and spacings.

## How to
* install `python -m pip install OCR_with_format`
* see usage `OCR_with_format --help` (executing with `python -m` is not supported)

## Usage
```
NAME
    OCR_with_format

SYNOPSIS
    OCR_with_format IMG_PATH THRESHOLDING_METHOD <flags>

POSITIONAL ARGUMENTS
    IMG_PATH
        Type: str
        path to the image you want to do OCR on
    THRESHOLDING_METHOD
        Type: str
        any from "otsu", "otsu_gaussian", "adaptative_gaussian", "all"

        If "all", the three methods will be tried and the final output will be the one which maximizes the mean and median confidences over each parsed words.

FLAGS
    -l, --language=LANGUAGE
        Type: str
        Default: 'eng'
        language to look for in the image
    -o, --output_path=OUTPUT_PATH
        Type: Optional[str]
        Default: None
        if not None, will output to this path and erase its previous content.
    -t, --tesseract_args=TESSERACT_ARGS
        Type: str
        Default: '-...
        default arguments for tesseract
    -q, --quiet=QUIET
        Default: False
        if True, will only print the output and no logs
    -c, --comparison_run=COMPARISON_RUN
        Default: False
        if True, will just output the raw output from pytesseract. This can be used to convince yourself of the usefullness of this project.

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
```

## Example

* Image:
  * ![](https://github.com/thiswillbeyourgithub/OCR_with_format/blob/295e724b758045dc952934b6f0d98172fdc9a12e/screenshot.png?raw=true)
* output from `python ./__init__.py ./screenshot.png --thresholding_method="all"  --quiet`
```
                                                                    @Unwateh (1) ~        Fork (3)                  (©
    OCR_with_format                          [     Pir ][                   | [  &            <) [     s        -]
                                                                                          About
                                                                                                                              &
                                                                                          Wrapper around pytesseract to
¥ Branches  © Tags                                                                     postprocess in a way that preserves
                                                                                          spacing and formattings.
  i  thiswillbeyourgithub addded license                        10 minutes ago  O 4
                                                                                          &5 GPL-3.0 license
  @  LICENSE            addded license                             10 minutes ago    - Activity
  [u]  __init__.py           minor                                      11 minutes ago     ¢ Ostars
  [u]  requirements.txt       added empty requirements                  11 minutes ago    <& 1 watching
                                                                                          Y  Oforks
  Help people interested in this repository understand your project by
  adding a README.                                                                      Releases
                                                                                          Create No releases a new published release
                                                                                          Packages
                                                                                          No packages published
                                                                                          Publish your first package
                                                                                          Languages
                                                                                          ———
                                                                                           ® Python 100.0%
```
* output from `python ./__init__.py ./screenshot.png --quiet --comparison_run`
  *
```
OCR_with_format

[ pin | [ @unwateh (@) ~ | [ & Fork (O)

-] [ ¢ s (0

¥ main ~

¥ Branches © Tags

Wrapper around pytesseract to
postprocess in a way that preserves

. . . spacing and formattings.
- thiswillbeyourgithub addded license 10 minutes ago 'O 4
&5 GPL-3.0 license
@ LICENSE addded license 10 minutes ago A Activity
0O _init__py minor 11 minutes ago ¢ Ostars
O requirements.txt added empty requirements 11 minutes ago | @ 1watching
% 0forks
Help people interested in this repository understand your project by
adding a README. Releases

No releases published
Create a new release

Packages

No packages published
Publish your first package

Languages

————
@ Python 100.0%
```
