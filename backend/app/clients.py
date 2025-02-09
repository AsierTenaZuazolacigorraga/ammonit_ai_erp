import logging
import os

from O365 import Account, FileSystemTokenBackend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutlookClient:
    def __init__(self, id, secret, email, scopes):
        self.id = id
        self.secret = secret
        self.email = email
        self.scopes = scopes
        self.token_backend = FileSystemTokenBackend(
            token_path=os.path.join(
                os.getcwd(),
                "..",
                ".gitignores",
                "azure_tokens",
            ),
            token_filename=self.email,
        )
        self.account = Account(
            (self.id, self.secret),
            token_backend=self.token_backend,
            tenant_id="consumers",
        )

        if self.account.is_authenticated:
            pass
            # logger.info("Token loaded successfully.")
        else:
            if self.account.authenticate(scopes=self.scopes):
                pass
                # logger.info("Authenticated successfully")
            else:
                logger.info("Authentication failed")
