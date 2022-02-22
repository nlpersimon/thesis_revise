import argparse
import requests
from bs4 import BeautifulSoup as bs
import urllib
import pdfkit
import re
import tqdm


def prepare_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, dest='input')
    parser.add_argument('-o', '--output', type=str, dest='output')
    return parser


def generate_html_str(txt_file_path):
    with open(txt_file_path) as f:
        paragraphs = f.read().split('\n\n')
    paragraphs_html = []
    for paragraph in tqdm.tqdm(paragraphs):
        paragraph = paragraph.strip().replace('\n', ' ')
        if is_title(paragraph):
            html_str = create_title_html(paragraph)
        else:
            html_str = get_suggest_html(paragraph)
        paragraphs_html.append(html_str)
    return '\n'.join(paragraphs_html)


def is_title(text):
    return re.findall('(chapter|section|subsection|subsubsection)\{', text)


def create_title_html(text):
    start = text.index('{') + 1
    title = text[start:-1]  # exclude '}'
    if text.startswith('chapter'):
        tag = 'h1'
    elif text.startswith('section'):
        tag = 'h2'
    elif text.startswith('subsection'):
        tag = 'h3'
    elif text.startswith('subsubsection'):
        tag = 'h4'
    else:
        raise ValueError
    return f'<{tag}>{title}</{tag}>'


def get_suggest_html(paragraph):
    paragraph = paragraph.strip().replace('\n', ' ')
    res = requests.get(
        f'http://jedi.nlplab.cc:5488/{urllib.parse.quote(paragraph.strip())}')
    soup = bs(res.text, 'html.parser')
    table = soup.select('table')[0]
    table['width'] = '100%'
    return str(table)


def main():
    parser = prepare_parser()
    args = parser.parse_args()

    html_str = generate_html_str(args.input)
    pdfkit.from_string(html_str, args.output)
    return


if __name__ == "__main__":
    main()
