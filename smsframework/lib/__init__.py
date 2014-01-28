import re


def digits_only(num):
    """ Remove all non-digit characters from the phone number

        :type num: str
        :param num: Phone number
        :rtype: str
    """
    return re.sub(r'[^\d]+', '', num)
