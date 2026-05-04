from database import (
    deserialize_rsa_pub, decrypt_rsa_priv,
    deserialize_ecc_pub, decrypt_private_key,
    field_decrypt, verify_user_mac
)


class User:
    def __init__(self, row):
        self.id           = row['id']
        self.role         = row['role']
        self.otp_secret   = row['otp_secret']
        self.password_hash = row['password_hash']
        self.salt          = row['salt']
        self.mac_valid     = verify_user_mac(row)

        # decrypted plaintext fields
        self.username = field_decrypt(row['username_enc'])
        self.email    = field_decrypt(row['email_enc'])
        self.contact  = field_decrypt(row['contact_enc'])

        # deserialized keys (public — always available)
        self.rsa_pub = deserialize_rsa_pub(row['rsa_pub'])
        self.ecc_pub = deserialize_ecc_pub(row['ecc_pub'])

        # decrypted private keys (use only when needed)
        self._rsa_priv_enc = row['rsa_priv_enc']
        self._ecc_priv_enc = row['ecc_priv_enc']

    def get_rsa_priv(self):
        return decrypt_rsa_priv(self._rsa_priv_enc)

    def get_ecc_priv(self):
        return decrypt_private_key(self._ecc_priv_enc)

    def is_admin(self):
        return self.role == 'admin'
