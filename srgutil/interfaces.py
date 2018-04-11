from abc import ABC, abstractmethod


class IS3Data(ABC):
    """
    Helper functions for S3 access.  No caching is provided.
    """

    @abstractmethod
    def fetch_json(uri):
        """ Perform an HTTP GET on the given uri, return the results as json.

        Args:
            uri: the string URI to fetch.

        Returns:
            A JSON object with the response or None if the status code of the
            response is an error code.
        """

    @abstractmethod
    def get_s3_json_content(s3_bucket, s3_key):
        """Download and parse a json file stored on AWS S3.

        The file is downloaded and then cached for future use.
        """


class IClock(ABC):
    """
    """
    # TODO:
    pass
