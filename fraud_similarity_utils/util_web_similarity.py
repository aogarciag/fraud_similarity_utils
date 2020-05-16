from langdetect import detect
from bs4 import BeautifulSoup
import difflib
from parsel import Selector
from io import StringIO
import lxml.html
import itertools
import requests

def get_tags(doc):
    '''
    Get tags from a DOM tree
    :param doc: lxml parsed object
    :return:
    '''
    tags = list()

    for el in doc.getroot().iter():
        if isinstance(el, lxml.html.HtmlElement):
            tags.append(el.tag)
        elif isinstance(el, lxml.html.HtmlComment):
            tags.append('comment')
        else:
            raise ValueError('Don\'t know what to do with element: {}'.format(el))

    return tags

def get_classes(html):
    doc = Selector(text=html)
    classes = set(doc.xpath('//*[@class]/@class').extract())
    result = set()
    for cls in classes:
        for _cls in cls.split():
            result.add(_cls)
    return result


def detect_lang(url,return_text=False):
    try:
        if url[:4]!="http" and url[:3]!="www" and url[:5]!="https":
            url=f"https://{url}"
        page=requests.get(url)
        soup=BeautifulSoup(page.text, 'lxml')
        text=[p.text for p in soup.find_all('p')]
        text=' '.join(text)
        if return_text:
            return text,detect(text)
        else:
            return detect(text)
    except:
        return ''

def structural_similarity(tags1, tags2):
    """
    Computes the structural similarity between two DOM Trees
    :param document_1: html string
    :param document_2: html string
    :return: int
    """
    diff = difflib.SequenceMatcher()
    diff.set_seq1(tags1)
    diff.set_seq2(tags2)

    return diff.ratio()


def jaccard_similarity(set1, set2):
    set1 = set(set1)
    set2 = set(set2)
    intersection = len(set1 & set2)

    if len(set1) == 0 and len(set2) == 0:
        return 1.0

    denominator = len(set1) + len(set2) - intersection
    return intersection / max(denominator, 0.000001)


def style_similarity(tags1, tags2):
    """
    Computes CSS style Similarity between two DOM trees
    A = classes(Document_1)
    B = classes(Document_2)
    style_similarity = |A & B| / (|A| + |B| - |A & B|)
    :param page1: html of the page1
    :param page2: html of the page2
    :return: Number between 0 and 1. If the number is next to 1 the page are really similar.
    """
    return jaccard_similarity(tags1, tags2)


def get_url_structure(url):
    try:
        print(url)
        if url[:4]!="http" and url[:3]!="www" and url[:5]!="https":
            url=f"https://{url}"
        page = requests.get(url)
        return get_tags(lxml.html.parse(StringIO(page.text))), get_classes(page.text)
    except:
        return '',''
