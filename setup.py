from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="OCR_with_format",
    version="0.14",
    description="Wrapper to pytesseract to preserve space and formatting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="thiswillbeyourgithub",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    keywords=["OCR", "tesseract", "pytesseract", "format", "formatting", "space", "spacing", "spaces"],
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.10.0",
        "fire>=0.5.0",
        "ftfy>=6.1.1",
        "numpy>=1.21.5",
        "opencv-python>=4.7.0.72",
        "pytesseract>=0.3.10",
        "beartype>=0.19.0",
        "pandas>=2.2.3"
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "OCR_with_format=OCR_with_format.__init__:cli",
        ],
    },
    project_urls={
        "Homepage": "https://github.com/thiswillbeyourgithub/OCR_with_format",
    },
)
