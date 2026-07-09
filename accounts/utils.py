
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


class AccountPasswordResetTokenGenerator(PasswordResetTokenGenerator):
   
    pass


account_token_generator = AccountPasswordResetTokenGenerator()