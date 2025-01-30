""" API Client for making HTTP requests to the API server. """

import os
import requests
from fastapi.testclient import TestClient
from core_api.api import get_app, generate_user_agent

import core_framework as util
from core_framework.constants import ENV_API_HOST_URL

from core_cli import __version__


class APIClient:
    """API Client for making HTTP requests to the API server.

    This client supports both local and remote modes. In local mode, it uses
    FastAPI's TestClient (httpx.Client) to make requests to a locally running instance of the
    API. In remote mode, it uses the `requests` library to make HTTP requests
    to a remote API server.

    Attributes:
        local (bool): Indicates if the client is in local mode.
        api_url (str): The base URL for the API.
        validate_ssl (bool): Whether to validate SSL certificates.
        api_client (TestClient): The FastAPI TestClient instance for local mode.
        user_agent (str): The User-Agent string for the client.
    """

    _instance = None

    def __init__(self):
        self.local = util.is_local_mode()
        self.api_url = os.getenv(ENV_API_HOST_URL, "http://localhost:8000")
        self.validate_ssl = False
        self.api_client = TestClient(get_app()) if self.local else None
        self.user_agent = generate_user_agent("core-cli", __version__)

    def _set_defaults(self, kwargs):
        if not self.local:
            kwargs["verify"] = self.validate_ssl
        headers = kwargs["headers"] if "headers" in kwargs else {}
        headers.update({"User-Agent": self.user_agent})

    def get(self, url, params=None, **kwargs):
        """Sends a GET request.

        Args:
            url (str): URL for the new Request object.
            params (dict, optional): Dictionary, list of tuples or bytes to send in the query string for the Request.
            **kwargs: Optional arguments that request takes.

        Returns:
            requests.Response: Response object.
        """
        self._set_defaults(kwargs)
        if self.local and self.api_client:
            return self.api_client.get(url, params=params, **kwargs)
        return requests.get(url, params, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        """Sends a POST request.

        Args:
            url (str): URL for the new Request object.
            data (dict, optional): Dictionary, list of tuples, bytes, or file-like object to send in the body of the Request.
            json (dict, optional): A JSON serializable Python object to send in the body of the Request.
            **kwargs: Optional arguments that request takes.

        Returns:
            requests.Response: Response object.
        """
        self._set_defaults(kwargs)
        if self.local and self.api_client:
            return self.api_client.post(url, data=data, json=json, **kwargs)
        return requests.post(url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        """Sends a PUT request.

        Args:
            url (str): URL for the new Request object.
            data (dict, optional): Dictionary, list of tuples, bytes, or file-like object to send in the body of the Request.
            **kwargs: Optional arguments that request takes.

        Returns:
            requests.Response: Response object.
        """
        self._set_defaults(kwargs)
        if self.local and self.api_client:
            return self.api_client.put(url, data=data, **kwargs)
        return requests.put(url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        """Sends a DELETE request.

        Args:
            url (str): URL for the new Request object.
            **kwargs: Optional arguments that request takes.

        Returns:
            requests.Response: Response object.
        """

        self._set_defaults(kwargs)
        if self.local and self.api_client:
            return self.api_client.delete(url, **kwargs)
        return requests.delete(url, **kwargs)

    def patch(self, url, data=None, **kwargs):
        """Sends a PATCH request.

        Args:
            url (str): URL for the new Request object.
            data (dict, optional): Dictionary, list of tuples, bytes, or file-like object to send in the body of the Request.
            **kwargs: Optional arguments that request takes.

        Returns:
            requests.Response: Response object.
        """
        self._set_defaults(kwargs)
        if self.loca and self.api_client:
            return self.api_client.patch(url, data=data, **kwargs)
        return requests.patch(url, data=data, **kwargs)

    def head(self, url, **kwargs):
        """Sends a HEAD request.

        Args:
            url (str): URL for the new Request object.
            **kwargs: Optional arguments that request takes. If `allow_redirects` is not provided, it will be set to `False` (as opposed to the default request behavior).

        Returns:
            requests.Response: Response object.
        """
        self._set_defaults(kwargs)
        if self.local and self.api_client:
            return self.api_client.head(url, **kwargs)
        return requests.head(url, **kwargs)

    def options(self, url, **kwargs):
        """Sends a OPTIONS request.

        Args:
            url (str): URL for the new Request object.
            **kwargs: Optional arguments that request takes.

        Returns:
            requests.Response: Response object.
        """
        self._set_defaults(kwargs)
        if self.local and self.api_client:
            return self.api_client.options(url, **kwargs)
        return requests.options(url, **kwargs)

    @classmethod
    def get_instance(cls) -> "APIClient":
        if cls._instance is None:
            cls._instance = APIClient()
        return cls._instance
