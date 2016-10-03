#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A library for decoding of bencoded files (part of BitTorrent protocol).
Written in pure Python, should work with Python 3.

Specification of Bencoding can be found here:
https://wiki.theory.org/BitTorrentSpecification#Bencoding

EXPERIMENTAL SOFTWARE - DO NOT USE IT IN PRODUCTION / STABLE PROJECTS!

Licensed under WTFPL by Jacek "d33tah" Wielemborek.
"""

import hashlib


class Bdecode(object):
    """Decodes a file encoded with bencoding format (part of BitTorrent).

    Note that the input file passed to the constructor might be any object that
    implements read() function - including StringIO instances.

    Attributes:
        info_hash (str): calculated info_hash. None if not known yet.

    WARNING:

    This is a light implementation, currently mostly for education purposes.
    This means that it might have security issues such as ones related to DoS
    with heavily nested dictionaries overflowing the stack.

    EXPERIMENTAL SOFTWARE - DO NOT USE IT IN PRODUCTION / STABLE PROJECTS!
    """

    def __init__(self, input_file, capture_for_infohash=None):
        """
        Args:
            input_file (file): a file to read from. Only f.read(n) will be
                used
            capture_for_infohash (bool): set this to False if you want to
                disable the calculation of info_hash - this might speed up
                parsing a bit
        """
        self._input_file = input_file
        if capture_for_infohash is None:
            self._capturing_for_infohash = False
            self._infohash_obj = hashlib.sha1()
            self.info_hash = None
        else:
            self._capturing_for_infohash = None

    def _read_bytes(self, n):
        ret = self._input_file.read(n)
        if self._capturing_for_infohash:
            self._infohash_obj.update(ret)
        return ret

    def _read_number_until(self, c):
        # Reads a number given character, then returns it as a string.

        ret = ""
        while True:
            v = self._read_bytes(1).decode('ascii')
            if v.isdigit() or v == '-':
                # I know that string appending is slow, but how large can
                # those numbers really be?
                ret += v
            else:
                if v != c:
                    errmsg = "ERROR: Expected '%s', got '%s'." % (c, v)
                    raise ValueError(errmsg)
                return ret

    def _read_dict(self):
        # Dictionary starts with "d", contains a stream of key-value pairs
        # and ends with "e".
        #
        # This one is the most complex read function because we also calculate
        # info_hash (comment out all is_info code and it gets tiny).
        ret = {}
        is_info = False
        while True:
            key = self.read_value()
            if key == b'info' and self._capturing_for_infohash is not None:
                # we're about to read value used for calculating info_hash.
                is_info = self._capturing_for_infohash = True
            if key is None:
                return ret
            value = self.read_value()
            if is_info:
                # we've read value for info_hash, stop growing the StringIO
                is_info = self._capturing_for_infohash = False
                self.info_hash = self._infohash_obj.hexdigest().upper()
            ret[key] = value

    def _read_list(self):
        # List starts with l, contains a stream of elements and ends with e.
        ret = []
        while True:
            v = self.read_value()
            if v is not None:
                ret += [v]
            else:
                return ret

    def _read_string(self, data_so_far):
        # A string is encoded as a number which means its length, followed by
        # a colon (":")
        t = data_so_far + self._read_number_until(":")
        ret = self._read_bytes(int(t))
        return ret

    def read_value(self):
        """Returns next bencoded object in the file. Note that typical torrent
        files contain one nested bencoded object."""
        t = self._read_bytes(1).decode('ascii')
        if t == 'e':
            return None
        elif t == 'd':
            return self._read_dict()
        elif t.isdigit():
            return self._read_string(data_so_far=t)
        elif t == 'l':
            return self._read_list()
        elif t == 'i':
            return self._read_number_until('e')
        else:
            raise ValueError("Unexpected type: %s" % t)

if __name__ == '__main__':

    import sys
    import base64
    import zlib

    if sys.version > '3':
        from io import BytesIO as StringIO
    else:
        from StringIO import StringIO

    # I have no idea what this torrent contains, I just entered "txt" on
    # ThePirateBay and looked for something small.
    sample_torrent_compressed = """
    eJydlDuS1DAQhhMOYjIIVjO2/BjrAMQES0QAstUzVo2sdkky88hJNqGKM3AJ0g25BFdBM2
    MbP4aqLSKX7a///rvVarFhXGtsdQk0ZZVzDVutnOHlHgzRh8aSg2VpnuarHgvpEPGgpHVK
    vTAQFE3m4EHqneKSlFiPuazntoZSgTWpKHUXiFEarsfkpifhiKK1RIA96fKKzpP/dYnGgH
    ZkZ8BKpYCg2d3V7F12z608zo3GrBVjsnBnRAIt24xdxtmduoVFU4PjquDOgTnNpKO8kw7X
    xHBT7EgNU1XaE7L5EvceScWN11IzB76jU6NSycJcCl+0aV7SGbW4gpv7je+6+dDzph0w0l
    SNrz7u0ULutoguzOOIWNj7SHnPQryYpwKsT3BLZIkGtwgZcgy5e7wWd6dhXqbDPWhicFpm
    lHQYNv6vgBq1vE6rx7xINBMpsWnA2NZsL4r7KxSvF+NUQSMNd1Dw03z2wk4x7w79kirKpj
    Of/stTSGk2Bhf2ytLzs4NM5pNhHfo7Id3iwKdc0xZKloXrujE9jCl6MVpI19+7RcCLPdB5
    Kwfw/5wuN9eYHZdEO81uIQ237f5egoz5j7UvNg3Z463sQOBBK+QCRLA1WAddO4KSlxUE3A
    WdFTkMup+NcM1KA35WRFCc/OptO7VVmCVr/379KVEHwjMyDPMkz9LMz92GgS5R+P2asA+P
    7x42MZN6iyJlCvTOVTKhCcRM8xp8+98jqsCCV3M2eNOgL84FhV+Okhth3xJ3dGHEGgklBF
    18miQ0hfT20UZr9vHp28/Xv88/8NUn9vn7s3j+9fQV4A/z+0UM"""

    sample_torrent_bin = base64.b64decode(sample_torrent_compressed)
    sample_torrent = zlib.decompress(sample_torrent_bin)

    f = StringIO(sample_torrent)
    b = Bdecode(f)
    val = b.read_value()
    print(b.info_hash)

    try:
        Bdecode(StringIO('z')).read_value()
        raise RuntimeError('This shall not pass!')
    except ValueError:
        pass

    try:
        Bdecode(StringIO('123d')).read_value()
        raise RuntimeError('This shall not pass either!')
    except ValueError:
        pass
