import unicodedata
import re
import math

def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)

def text_to_id(text):
    """
    Convert input text to id.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    text= str(text).replace("nan","")
    text = strip_accents(text.lower())
    text = re.sub('[ ]+', '_', text)
    text = re.sub('[^0-9-a-zA-Z_-]', '', text)
    return text.title().replace("_"," ")

def format_cp(x):
    try:
        if math.isnan(x):
            return 0
        else:
            return int(x)
    except:
        return 0

def format_email(x):
    return text_to_id(x.split("@")[0])

def get_hour_interval(mx_hour):
    if mx_hour<6:
        return 1
    elif mx_hour<12:
        return 2
    elif mx_hour<18:
        return 3
    else:
        return 4