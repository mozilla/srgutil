# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import boto3
import json
import logging
import os
import requests
import requests.exceptions
import tempfile
import time
import threading
from srgutil.interfaces import IS3Data, IClock


logger = logging.getLogger(__name__)
FOUR_HOURS = 60 * 60 * 4


class Clock(IClock):
    def time(self):
        """Return epoch time in seconds like time.time()"""
        return time.time()


class S3CacheDelegate(object):
    """
    This class keeps a cache of JSON blobs and S3 bucket data.

    All data is expired simultaneously
    """
    def __init__(self, ctx):
        self._ctx = ctx

        # Set to 4 hours
        self._ttl = FOUR_HOURS
        self._refresh_expiry()

        self._lock = threading.RLock()
        self._json_cache = {}

    # Private
    def _refresh_expiry(self):
        self._expiry_time = self._ctx[IClock].time() + self._ttl

    def _expire_cache(self):
        with self._lock:
            clock = self._ctx[IClock]
            if clock.time() >= self._expiry_time:
                self._json_cache.clear()
                self._s3_json_cache.clear()
                self._refresh_expiry()

    # Public
    def __contains__(self, key):
        with self._lock:
            self._expire_cache()
            return key in self._json_cache

    def __getitem__(self, key):
        with self._lock:
            self._expire_cache()
            return self._json_cache[key]

    def __setitem__(self, key, value):
        with self._lock:
            self._json_cache[key] = value

    def __delitem__(self, key):
        with self._lock:
            del self._json_cache[key]


class S3Data(IS3Data):
    def __init__(self, ctx):
        assert IClock in ctx
        self._ctx = ctx
        self._delegate = S3CacheDelegate(ctx.child())

    # Private
    def _raw_http_get_json(self, uri):
        """ Perform an HTTP GET on the given uri, return the results as json.

        Args:
            uri: the string URI to fetch.

        Returns:
            A JSON object with the response or None if the status code of the
            response is an error code.
        """
        try:
            r = requests.get(uri)
            if r.status_code != requests.codes.ok:
                return None
            return r.json()
        except requests.exceptions.ConnectionError:
            return None

    def _raw_get_s3_json_content(self, s3_bucket, s3_key):
        """Download and parse a json file stored on AWS S3.

        The file is downloaded and then cached for future use.
        """

        raw_data = None
        try:
            s3 = boto3.resource('s3')
            raw_data = (
                s3
                .Object(s3_bucket, s3_key)
                .get()['Body']
                .read()
                .decode('utf-8')
            )
        except Exception:
            logger.exception("Failed to download from S3", extra={
                "bucket": s3_bucket,
                "key": s3_key})
            return None

        # It can happen to have corrupted files. Account for the
        # sad reality of life.
        try:
            return json.loads(raw_data)
        except ValueError:
            logging.error("Cannot parse JSON resource from S3", extra={
                "bucket": s3_bucket,
                "key": s3_key})

        return None

    # Public
    def set_delegate(self, delegate):
        self._delegate = delegate

    def fetch_json(self, url):
        """ Return JSON from HTTP GET
        """
        if self._delegate is not None:
            if url in self._delegate:
                return self._delegate[url]
        return self._raw_http_get_json(url)

    def get_s3_json_content(self, s3_bucket, s3_key):
        key = (s3_bucket, s3_key)
        if self._delegate is not None:
            if key in self._delegate:
                return self._delegate[key]
        return self._raw_get_s3_json_content(s3_bucket, s3_key)

    def store_json_to_s3(self, json_data, base_filename, date, prefix, bucket):
        """Saves the JSON data to a local file and then uploads it to S3.

        Two copies of the file will get uploaded: one with as "<base_filename>.json"
        and the other as "<base_filename><YYYYMMDD>.json" for backup purposes.

        :param json_data: A string with the JSON content to write.
        :param base_filename: A string with the base name of the file to use for saving
            locally and uploading to S3.
        :param date: A date string in the "YYYYMMDD" format.
        :param prefix: The S3 prefix.
        :param bucket: The S3 bucket name.
        """
        temp_dir = tempfile.gettempdir()
        FULL_FILENAME = os.path.join(temp_dir, "{}.json".format(base_filename))

        with open(FULL_FILENAME, "w+") as json_file:
            json_file.write(json_data)

        archived_file_copy =\
            "{}{}.json".format(base_filename, date)

        # Store a copy of the current JSON with datestamp.
        write_to_s3(FULL_FILENAME, archived_file_copy, prefix, bucket)
        write_to_s3(FULL_FILENAME, FULL_FILENAME, prefix, bucket)


def write_to_s3(source_file_name, s3_dest_file_name, s3_prefix, bucket):
    """Store the new json file containing current top addons per locale to S3.

    :param source_file_name: The name of the local source file.
    :param s3_dest_file_name: The name of the destination file on S3.
    :param s3_prefix: The S3 prefix in the bucket.
    :param bucket: The S3 bucket.
    """
    client = boto3.client('s3', 'us-west-2')
    transfer = boto3.s3.transfer.S3Transfer(client)

    # Update the state in the analysis bucket.
    key_path = s3_prefix + s3_dest_file_name
    transfer.upload_file(source_file_name, bucket, key_path)
