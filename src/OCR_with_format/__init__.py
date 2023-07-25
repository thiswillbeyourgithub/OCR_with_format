import fire
import pytesseract
import ftfy
import numpy as np
import cv2
from bs4 import BeautifulSoup
import re
from textwrap import dedent

# pre compiled regex
bbox_regex = re.compile(r'bbox\s(\d+)\s(\d+)\s(\d+)\s(\d+)')
confidence_regex = re.compile(r'x_wconf\s(\d+)')
newlines_regex = re.compile(r'\n\s*\n')

__version__ = "0.7"

# msic

def _get_wdim(ocrx_word):
    "parse the dimansion of the word from the ocrx object"
    return [int(x) for x in re.findall(bbox_regex, ocrx_word["title"])[0]]


def _get_wconf(ocrx_word):
    "parse the confidence on the word from the ocrx object"
    out = re.findall(confidence_regex, ocrx_word["title"])[0]
    return int(out)


def _do_ocr(img, lang, args):
    "run OCR on the image by pytesseract"
    return pytesseract.image_to_pdf_or_hocr(
            img,
            lang=lang,
            config=args,
            extension="hocr",
            )


def OCR_with_format(
        img_path: str,
        thresholding_method: str,
        language: str = "eng",
        output_path: str = None,
        tesseract_args: str = "--oem 3 --psm 11 -c preserve_interword_spaces=1",
        quiet=False,
        comparison_run=False,
        ):
    """
    Parameters
    ----------
    img_path: str
        path to the image you want to do OCR on

    thresholding_method: str
        any from "otsu", "otsu_gaussian", "adaptative_gaussian", "all"

        If "all", the three methods will be tried and the final output will be
        the one which maximizes the mean and median confidences over
        each parsed words.

    language: str, default eng
        language to look for in the image

    output_path: str, default None
        if not None, will output to this path and erase its previous content.

    tesseract_args: str, default "--oem 3 --psm 11 -c preserve_interword_spaces=1"
        default arguments for tesseract

    quiet: bool, default False
        if True, will only print the output and no logs

    comparison_run: bool, default False
        if True, will just output the raw output from pytesseract. This
        can be used to convince yourself of the usefullness of this project.

    """
    if quiet:
        pr = lambda x: None
    else:
        pr = print
    img = cv2.imread(img_path, flags=1)

    # remove alpha layer if found
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # take greyscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # preprocess several times then OCR, keep the one with the highest median confidence
    preprocessings = {}

    # sharpen a bit
    gray_sharp = cv2.addWeighted(gray, 1.5, cv2.GaussianBlur(gray, (0, 0), 10), -0.5, 0)

    if comparison_run:
        return pytesseract.image_to_string(
                img,
                lang=language,
                config="",
                )

    # source:
    # https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html#otsus-binarization
    if thresholding_method in ["otsu", "all"]:
        # Otsu's thresholding
        _, sharpened = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        preprocessings["otsu1_nosharp"] = {"image": sharpened}
        _, sharpened = cv2.threshold(gray_sharp, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        preprocessings["otsu1_sharp"] = {"image": sharpened}

    elif thresholding_method in ["otsu_gaussian", "all"]:
        # # Otsu's thresholding after Gaussian filtering
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, sharpened = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        preprocessings["otsu2_nosharp"] = {"image": sharpened}
        blur = cv2.GaussianBlur(gray_sharp, (5, 5), 0)
        _, sharpened = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        preprocessings["otsu2_sharp"] = {"image": sharpened}

    elif thresholding_method in ["adaptative_gaussian", "all"]:
        # # adaptative gaussian thresholding
        sharpened = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                21, -5)
        preprocessings["gauss_nosharp"] = {"image": sharpened}
        sharpened = cv2.adaptiveThreshold(
                gray_sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                21, -5)
        preprocessings["gauss_sharp"] = {"image": sharpened}
    else:
        raise Exception(f"Unexpected thresholding_method: '{thresholding_method}'")

    max_med = 0  # median
    max_mean = 0  # mean
    for method, value in preprocessings.items():
        # use pytesseract to get the text
        hocr_temp = _do_ocr(value["image"], lang=language, args=tesseract_args)

        # load hOCR content as html
        soup = BeautifulSoup(hocr_temp, 'html.parser')

        # get all words
        all_words_temp = soup.find_all('span', {'class': 'ocrx_word'})

        # get confidence
        confidences = []
        for w in all_words_temp:
            confidence = _get_wconf(w)
            confidences.append(confidence)
        med = np.median(confidences)
        preprocessings[method]["median"] = med
        mean = np.sum(confidences) / len(confidences)
        preprocessings[method]["mean"] = mean
        if med >= max_med and mean >= max_mean:
            max_med = med
            max_mean = mean
            best_method = method
            all_words = all_words_temp

    if thresholding_method == "auto":
        pr(f"Best preprocessing method: {best_method} with score {max_med:.2f} {max_mean:.2f}")
        for m, v in preprocessings.items():
            pr(f"* {m}: {v['median']:.2f}  {v['mean']:.2f}")
        del preprocessings

    # determine the average word height to use as threshold for the newlines
    # also average length of a letter
    heights = []
    lengths = []
    levels = []  # distance from top of the screen
    all_bbox = {}
    for word in all_words:
        all_bbox[word] = _get_wdim(word)
        bbox = all_bbox[word]
        levels.append(bbox[1])
        heights.append(bbox[3] - bbox[1])
        text = word.get_text()
        if " " not in text and len(text) >= 3 and len(text) <= 20:
            length_bbox = bbox[2] - bbox[0]
            lengths.append(length_bbox / len(text))
    char_width = np.median(lengths)  # unit: pixel per character
    median_height = np.median(heights)
    max_h = max(levels)
    min_h = min(levels)

    # figure out from the line indices how how much to ignore as same line
    sorted_lev = np.array(sorted(levels)[len(levels)//3:len(levels)*2//3])  # focus on middle third
    diff = (sorted_lev - np.roll(sorted_lev, +1))[1:-1]
    try:
        merge_thresh = np.quantile(diff[np.where(diff != 0)], 0.1)
    except Exception as err:
        pr(f"Set line merging threshold to 0 because caught exception: '{err}'")
        merge_thresh = 0
    pr(f"Line merging threshold: {merge_thresh}")

    # figure out the height of the line to scan at each iteration
    try:
        newline_threshold = np.quantile(diff[np.where(diff > median_height)], 0.5)
    except Exception as err:
        pr(f"Set newline threshold to median_height because caught exception: '{err}'")
        newline_threshold = median_height
    pr(f"Median line diff: {newline_threshold}, median height: {median_height}")

    # figure out the offset that maximizes the number of words per lines
    incr = 5
    offset_to_try = [i / incr * min_h / 2 for i in range(0, incr, 1)]
    scores = {}
    w_todo = all_words
    # skip the first section of the text because it's sometimes headers
    #w_todo = [w for w in all_words if _get_wdim(w)[1] > (max_h - min_h) / 5]
    for offset in offset_to_try:
        w_done = []
        scan_lines = [min_h + offset]
        while scan_lines[-1] < max_h + offset * 2:
            scan_lines.append(scan_lines[-1] + newline_threshold)
        temp = []
        for y_scan in scan_lines:
            buff = [w for w in w_todo if w not in w_done and all_bbox[w][1] <= y_scan + merge_thresh]
            if not buff:
                continue
            w_done.extend(buff)
            temp.append(len(buff))
        scores[offset] = sum(temp) / len(temp)

    for k, v in scores.items():
        if v == max(scores.values()):
            best_offset = k
            break
    pr(f"Best offset: {best_offset})")

    # reset the best iterator
    w_done = []
    w_todo = [w for w in all_words]
    scan_lines = [min_h + best_offset]
    while scan_lines[-1] < max_h + best_offset * 2:
        scan_lines.append(scan_lines[-1] + newline_threshold)
    output_str = ''
    prev_y1 = None

    for y_scan in scan_lines:
        # keep only words not added that are in the the scan line
        buff = [w for w in w_todo if w not in w_done and all_bbox[w][1] < y_scan]
        if not buff:
            # go straight to next line because no words matched
            continue
        w_done.extend(buff)

        # sort words to make sure they are left to right
        ocr_words = sorted(buff, key=lambda x: all_bbox[x][0])

        # Extract text and format information
        line_text = ''
        for idx, word in enumerate(ocr_words):
            text = word.get_text()
            x0, y0, x1, y1 = all_bbox[word]

            if idx:
                prev_x1, prev_y1 = all_bbox[ocr_words[idx-1]][2:4]
                spaces_before = ' ' * int(max(1, (x0 - prev_x1) / char_width))
            else:
                spaces_before = ' ' * int(max(1, ((x0) / char_width)))

            confidence = _get_wconf(word)

            # if confidence < 50:
            #     tqdm.write(f"* Low confidence: {confidence}: {text}")

            line_text += f'{spaces_before}{text}'

            if prev_y1 is not None and abs(y0 - prev_y1) >= newline_threshold:
                output_str += '\n'

        output_str += f'{line_text}\n'
        prev_y1 = y1

    # remove useless indentation
    output_str = dedent(output_str)

    # remove too many newlines
    while "\n\n" in output_str:
         output_str = output_str.replace("\n\n", "\n")
    #output_str = "\n".join([li for li in output_str.split("\n") if li.strip() != ""])
    #output_str = re.sub(newlines_regex, '\n', output_str)

    # just in case
    output_str = ftfy.fix_text(output_str)

    if output_path:
        with open(output_path, "w") as f:
            f.write(output_str)
        pr(f"Output written to '{output_path}'")
    else:
        return output_str


def cli():
    fire.Fire(OCR_with_format)


if __name__ == "__main__":
    out = fire.Fire(OCR_with_format)
