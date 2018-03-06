# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2014-2018 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
from pathlib import Path, PurePosixPath
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import etree, objectify

from io import BufferedReader, DEFAULT_BUFFER_SIZE
from hashlib import md5

import hcpsdk


class MultipartUploader:
    '''
    Class for parallel file uploads using HS3 MPU.
    '''

    def __init__(self, target, hash=False, retries=0):
        '''
        :param target:      an **hcpsdk.Target** object
        :param hash:        check the returned hash
        :param retries:     the number of retries until giving up on a
                            Request
        '''
        self.logger = logging.getLogger(__name__ + '.MultipartUpload')
        self.target = target
        self.hash = hash
        self.retries = retries

    def PUT(self, url, body, psz=5, workers=20):
        '''
        Upload a single file using S3 MPU.

        :param url:     the url to request w/o the server part
                        (i.e: /path/object); url quoting will be done if
                        necessary, but existing quoting will not be touched
        :param body:    the payload to send (this needs to be a file or
                        file-like object, strings are not supported)
        :param workers: no. of worker threads to use
        :param psz:     upload part size in MB (min. 1, max. 5000)
        '''
        path = PurePosixPath('/hs3' + str(url))
        body = Path(str(body))  # convert to pathlib.Path
        self.size = body.stat().st_size  # the size of the file to upload
        psz *= 1024**2  # the part size in bytes
        _parts = int(self.size/psz)  # the number of parts

        # init MPU, gain the UploadId
        con = hcpsdk.Connection(self.target, retries=self.retries)
        upid = self.__mpu_init(con, url)
        mpuinittime = con.service_time2
        self.log.warning('MPUinit to {} | MPUinit time: {:>10,.3f}'.format(con.address, mpuinittime))

        # upload the parts
        starttime = time()
        partetags = {}
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Start the load operations and mark each future with its URL
            parts = {
            executor.submit(self._uploadpart, upid, file, path, _p[0] + 1,
                            _p[1], psz): _p[0] + 1 for _p in
            enumerate(range(0, self.size, psz))}

            _failed = False
            sumuploadtime = 0.0
            for future in as_completed(parts):
                part = parts[future]
                try:
                    result, mpuuploadtime = future.result()
                    sumuploadtime += mpuuploadtime
                except Exception as e:
                    self.log.error('Part {} raised exception: {}'.format(part, e))
                    _failed = True
                else:
                    partetags.update(result)

        realtime = time() - starttime
        mbsec = self.size / realtime / 1024 / 1024
        self.log.warning('MPU all uploads: sum upload time: {:,.3f} | real time: {:,.3f} | MB/sec: {:,.3f}'
                         .format(sumuploadtime, realtime, mbsec))

        # Complete MPU
        if not _failed:
            etag = self.__mpu_complete(con, file, path, upid, partetags)

        con.close()

    def _uploadpart(self, upid, file, path, partno, sbyte, size):
        '''
        Upload part *partno* of size *size* from *file*.

        :param upid:    the upload Id
        :param file:    a pathlib.Path object of the file to upload
        :param path:    a pathlib.PurePosixPath objet with the target path
        :param partno:  the parts no.
        :param sbyte:   the start byte for this part
        :param size:    a parts size
        '''
        # for the final part, we need to fix the size to the remainder
        if size > self.size - sbyte:
            size = self.size - sbyte
        con = hcpsdk.Connection(self.tgt, retries=3)
        phdl = PartialReader(file, sbyte, size, hash=self.hash)

        try:
            con.PUT(str(path / file), body=phdl,
                    params={'uploadId': upid, 'partNumber': partno},
                    headers={'Expect': '100-continue',
                             'Content-Length': size})
        except Exception as e:
            self.log.error('PUT({}) raised\n{}'.format(str(path / file), e))
            con.close()
            raise
        else:
            if con.response_status != 200:
                self.log.error('response: {}: upid: {} | partno: {} | '
                               'sbyte: {:,} | size: {:,}'
                               .format(con.response_status, upid, partno,
                                       sbyte, size))
                con.close()
                raise hcpsdk.HcpsdkError('not 200')
            else:
                mpuuploadtime = con.service_time2
                mbsec = size / mpuuploadtime / 1024 / 1024
                self.log.warning('MPU upload part {} to {} | upload time: '
                                 '{:,.3f} | MB/sec: {:,.3f}'
                                 .format(partno, con.address, mpuuploadtime, mbsec))

        con.close()

        return {partno: con.getheader('Etag').strip('"')}, mpuuploadtime

    def __mpu_init(self, con, url):
        '''
        Begin a MultiPartUpload.

        :param con:     the hcpsdk.Connection object
        :param url:     the target URL
        :return:        the upload id
        '''
        try:
            con.POST(url, params={'uploads': True})
        except Exception as e:
            self.log.error('POST {} failed: \n{}'.format(url, e))
            raise
        else:
            if con.response_status != 200:
                self.log.error('POST {} failed with {}'
                               .format(url, con.response_status))
            else:
                # ToDo: rebuild with etree ?
                root = objectify.fromstring(con.read())
                upid = root[0].UploadId

        return upid

    def __mpu_complete(self, con, file, path, upid, partetags):
        '''
        Complete a MultiPartUpload.

        :return:
        '''

        # ToDo: rebuild with lxml (or etree)
        sxml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' \
               '<CompleteMultipartUpload\n' \
               '  xmlns="http://s3.amazonaws.com/doc/2006-03-01/">\n'
        pxml = '  <Part>\n' \
               '    <PartNumber>{}</PartNumber>\n' \
               '    <ETag>{}</ETag>\n' \
               '  </Part>\n'
        exml = '</CompleteMultipartUpload>\n'

        # Create required XML
        body = sxml
        for _p in sorted(partetags.keys()):
            body += pxml.format(_p, partetags[_p])
        body += exml
        # ic()
        # ic(body)

        try:
            con.POST(str(path / file), body=body, params={'uploadId': upid})
        except Exception as e:
            self.log.error('POST {} failed: \n{}'.format(str(path / file), e))
            raise
        else:
            if con.response_status == 200:
                _body = con.read()
                root = objectify.fromstring(_body)
                etag = root[0].ETag
                mpucomplete = con.service_time2
                self.log.warning('MPUcomplete to {} | {:,.3f}'
                                 .format(con.address, mpucomplete))

        return etag

    def __mpu_abort(self):
        '''
        Begin a MultiPartUpload.

        :return:
        '''


class PartialReader(BufferedReader):
    '''
    Provide (binary!) read access to just a part of a file, as it would be the
    entire file.
    '''

    def __init__(self, file, pos, amount, hash=False):
        '''
        Open a file, seek to *pos* and allow read for up to *size* bytes
        :param file:    a pathlib.Path object for the file to open
        :param pos:     the start position in the file
        :param hash:    if the read bytes shall be hashed
        :param amount:  the no. of bytes to care for
        '''
        self.amount = amount
        self.hash = md5() if hash else None
        self._numbytesread = 0

        # open the file and position to the start byte
        super().__init__(open(file, 'rb'))
        super().seek(pos)

    def read(self, size=DEFAULT_BUFFER_SIZE):
        '''
        Read and return <size> bytes from the file.

        :param size:    the bytes to read, or all available data if zero
        :return:        the read bytes
        '''

        # check if we already have delivered all data
        if self._numbytesread >= self.amount:
            data = b''
        else:
            data = super().read(size)
            self._numbytesread += len(data)

        if self.hash:
            self.hash.update(data)

        return data

    def gethash(self):
        '''
        Return the calculated hash.
        '''
        return self.hash.hexdigest() if self.hash else None

    def is_closed(self):
        '''
        Return False if file is closed.
        '''
        return super().is_closed()

    def close(self):
        '''
        Close the file.
        '''
        super().close()
