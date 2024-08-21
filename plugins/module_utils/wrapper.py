# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Wrapper for common client requests.

Classes:
    APIError: Unexpected Cherry Servers API error.
    MissingParameterError: Missing required module arguments.
    Request: Client request data.
    Wrapper: Main wrapper functionality.
"""

from collections.abc import Sequence, Callable
from dataclasses import dataclass
from optparse import Option
from typing import Union, Optional, List

from ansible.module_utils import basic as utils
from . import client


class APIError(Exception):
    """Unexpected Cherry Servers API error."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class MissingParameterError(Exception):
    """Missing required module arguments."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass
class Request:
    """Client request data.

    Args:
        method(str): HTTP(S) method, such as GET or POST.
        url(str): endpoint URL, without the _base_url, as defined in CherryServersClient.
        timeout(int): timeout in seconds.
        params(dict): additional query parameters.

    """

    method: str
    url: str
    timeout: int
    params: dict


class Wrapper:
    """Cherry Servers client resource wrapper.

    Methods:
        get_resource_by_id(req: Request, name: str) -> Optional[dict]: retrieve a resource by its ID.
        create_resource(required_params: Sequence[str], name: str, req: Request, normalize: bool = True) -> dict:
            create a new Cherry Servers resource.
    """

    def __init__(
        self,
        api_client: client.CherryServersClient,
        module: utils.AnsibleModule,
        normalization_fun: Callable[[dict], dict],
    ):
        self.api_client = api_client
        self.module = module
        self.normalization_fun = normalization_fun

    def get_resource_by_id(self, req: Request, name: str) -> Optional[dict]:
        """Retrieve a resource by its ID."""
        status, resp = self.api_client.send_request(
            "GET",
            req.url,
            req.timeout,
        )
        if status not in (200, 404):
            raise APIError(f"Error retrieving {name} resource: {resp}")
        if status == 200:
            return self.normalization_fun(resp)
        return None

    def get_resources(self, req: Request, name: str, keys: Sequence[str]) -> List[dict]:
        """Find resources that match module parameters.

        Args:
            req(Request): Client request data.
            name(str): name of the resource.
            keys(Sequence[str]): keys by which to match resources and module arguments.
                For example, most resources can be matched by `id`.

        Raises:
            APIError: Unexpected Cherry Servers API error.

        Returns:
            List[dict]: Matching resources.
        """
        params = self.module.params

        status, resp = self.api_client.send_request("GET", req.url, req.timeout)
        if status != 200:
            raise APIError(f"Error retrieving {name} resources: {resp}")

        matching_resources = []

        for resource in resp:
            if any(resource[k] == params[k] for k in keys):
                matching_resources.append(resource)

        return matching_resources

    def create_resource(
        self,
        required_params: Sequence[str],
        name: str,
        req: Request,
        normalize: bool = True,
    ) -> dict:
        """Create a new resource.

        Args:
            required_params(Sequence[str]): required module parameters.
            name(str): name of the resource.
            req(Request): Client request data.
            normalize(bool): normalize the resource after creating it.

        Raises:
            MissingParameterError: Missing required module arguments.
            APIError: Unexpected Cherry Servers API error.

        Returns:
            dict: created resource.
        """

        params = self.module.params

        if any(params[k] is None for k in required_params):
            raise MissingParameterError(
                f"Missing required options for {name} resource creation."
            )

        if self.module.check_mode:
            self.module.exit_json(changed=True)

        status, resp = self.api_client.send_request(
            req.method, req.url, req.timeout, **req.params
        )

        if status != 201:
            raise APIError(f"Failed to create {name} resource: {resp}")

        if normalize:
            return self.normalization_fun(resp)
        return resp

    def delete_resource(self, req: Request, name: str):
        """Delete resource."""

        status, resp = self.api_client.send_request(req.method, req.url, req.timeout)
        if status != 204:
            raise APIError(f"Failed to delete {name} resource: {resp}")
