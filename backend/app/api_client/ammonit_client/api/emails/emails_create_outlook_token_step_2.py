from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.body_emails_create_outlook_token_step_2 import BodyEmailsCreateOutlookTokenStep2
from ...models.emails_create_outlook_token_step_2_response_emails_create_outlook_token_step_2 import (
    EmailsCreateOutlookTokenStep2ResponseEmailsCreateOutlookTokenStep2,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: BodyEmailsCreateOutlookTokenStep2,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/emails/outlook-token-step-2/",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[EmailsCreateOutlookTokenStep2ResponseEmailsCreateOutlookTokenStep2, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = EmailsCreateOutlookTokenStep2ResponseEmailsCreateOutlookTokenStep2.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[EmailsCreateOutlookTokenStep2ResponseEmailsCreateOutlookTokenStep2, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BodyEmailsCreateOutlookTokenStep2,
) -> Response[Union[EmailsCreateOutlookTokenStep2ResponseEmailsCreateOutlookTokenStep2, HTTPValidationError]]:
    """Create Outlook Token Step 2

     Create outlook token step 2.

    Args:
        body (BodyEmailsCreateOutlookTokenStep2):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[EmailsCreateOutlookTokenStep2ResponseEmailsCreateOutlookTokenStep2, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BodyEmailsCreateOutlookTokenStep2,
) -> Optional[Union[EmailsCreateOutlookTokenStep2ResponseEmailsCreateOutlookTokenStep2, HTTPValidationError]]:
    """Create Outlook Token Step 2

     Create outlook token step 2.

    Args:
        body (BodyEmailsCreateOutlookTokenStep2):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[EmailsCreateOutlookTokenStep2ResponseEmailsCreateOutlookTokenStep2, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BodyEmailsCreateOutlookTokenStep2,
) -> Response[Union[EmailsCreateOutlookTokenStep2ResponseEmailsCreateOutlookTokenStep2, HTTPValidationError]]:
    """Create Outlook Token Step 2

     Create outlook token step 2.

    Args:
        body (BodyEmailsCreateOutlookTokenStep2):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[EmailsCreateOutlookTokenStep2ResponseEmailsCreateOutlookTokenStep2, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BodyEmailsCreateOutlookTokenStep2,
) -> Optional[Union[EmailsCreateOutlookTokenStep2ResponseEmailsCreateOutlookTokenStep2, HTTPValidationError]]:
    """Create Outlook Token Step 2

     Create outlook token step 2.

    Args:
        body (BodyEmailsCreateOutlookTokenStep2):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[EmailsCreateOutlookTokenStep2ResponseEmailsCreateOutlookTokenStep2, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
