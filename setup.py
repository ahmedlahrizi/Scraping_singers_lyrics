from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'A basic script to get most used words by a singer using spacy and requests and Counter'

# Setting up
setup(
    name="scrap_singers",
    version=VERSION,
    author="Lahrizi Ahmed",
    author_email="fishy.anonyme@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['spacy', 'bs4', 'requests'],
    keywords=['python', 'singers', 'scrapping', 'web', 'lyrics', 'spacy', 'elon musk'],
    project_urls={
        'Documentation': "https://github.com/ahmedlahrizi/Scraping_singers_lyrics",
        "Bug Tracker": "https://github.com/ahmedlahrizi/Scraping_singers_lyrics",
        'Source': "https://github.com/ahmedlahrizi/Scraping_singers_lyrics"
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    package_dir={"": "scrap_singers"},
    python_requires=">=3.6"
)
