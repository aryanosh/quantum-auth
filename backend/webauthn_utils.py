import logging
import json
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    AuthenticatorAttachment,
    RegistrationCredential,
    AuthenticationCredential,
    AuthenticatorTransport,
)

logger = logging.getLogger(__name__)

class WebAuthnUtils:
    def __init__(self, rp_id, rp_name, origin):
        self.rp_id = rp_id
        self.rp_name = rp_name
        self.origin = origin

    def generate_registration_options(self, user, existing_credentials=None):
        try:
            options = generate_registration_options(
                rp_id=self.rp_id,
                rp_name=self.rp_name,
                user_id=str(user.id).encode(),
                user_name=user.username,
                authenticator_selection=AuthenticatorSelectionCriteria(
                    authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                    user_verification=UserVerificationRequirement.PREFERRED,
                    resident_key=None,
                ),
                exclude_credentials=existing_credentials or [],
            )
            return options
        except Exception as e:
            logger.error(f"Error generating registration options: {e}")
            raise

    def verify_registration_response(self, credential_response, challenge, expected_origin=None):
        try:
            credential = RegistrationCredential.parse_raw(json.dumps(credential_response))
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=challenge,
                expected_origin=expected_origin or self.origin,
                expected_rp_id=self.rp_id,
            )
            return verification
        except Exception as e:
            logger.error(f"Error verifying registration response: {e}")
            raise

    def generate_authentication_options(self, credentials):
        try:
            options = generate_authentication_options(
                rp_id=self.rp_id,
                user_verification=UserVerificationRequirement.PREFERRED,
                allow_credentials=credentials
            )
            return options
        except Exception as e:
            logger.error(f"Error generating authentication options: {e}")
            raise

    def verify_authentication_response(self, credential_response, challenge, public_key, sign_count):
        try:
            credential = AuthenticationCredential.parse_raw(json.dumps(credential_response))
            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=challenge,
                expected_origin=self.origin,
                expected_rp_id=self.rp_id,
                credential_public_key=public_key,
                credential_current_sign_count=sign_count,
            )
            return verification
        except Exception as e:
            logger.error(f"Error verifying authentication response: {e}")
            raise
