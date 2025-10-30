"""
Encryption Service for Sensitive Data
Encrypts/decrypts user bot credentials using Fernet symmetric encryption
"""

from cryptography.fernet import Fernet

from config.settings import settings


class EncryptionService:
    """Service for encrypting/decrypting sensitive credentials"""

    def __init__(self):
        """Initialize encryption service with cipher from settings"""
        encryption_key = settings.ENCRYPTION_KEY.get_secret_value()

        if not encryption_key:
            raise ValueError(
                "ENCRYPTION_KEY not configured! Generate one with: "
                'python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
            )

        try:
            self.cipher = Fernet(encryption_key.encode())
        except Exception as e:
            raise ValueError(f"Invalid ENCRYPTION_KEY format: {e}")

    def encrypt(self, value: str) -> str:
        """
        Encrypt string value

        Args:
            value: Plain text string to encrypt

        Returns:
            Encrypted string (base64 encoded)
        """
        if not value:
            return ""
        return self.cipher.encrypt(value.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        """
        Decrypt string value

        Args:
            encrypted: Encrypted string (base64 encoded)

        Returns:
            Decrypted plain text string
        """
        if not encrypted:
            return ""
        return self.cipher.decrypt(encrypted.encode()).decode()

    def encrypt_dict(self, data: dict, keys_to_encrypt: list[str]) -> dict:
        """
        Encrypt specific keys in dictionary

        Args:
            data: Dictionary with data
            keys_to_encrypt: List of keys to encrypt

        Returns:
            Dictionary with specified keys encrypted
        """
        encrypted_data = data.copy()
        for key in keys_to_encrypt:
            if key in encrypted_data and encrypted_data[key]:
                encrypted_data[key] = self.encrypt(str(encrypted_data[key]))
        return encrypted_data

    def decrypt_dict(self, data: dict, keys_to_decrypt: list[str]) -> dict:
        """
        Decrypt specific keys in dictionary

        Args:
            data: Dictionary with encrypted data
            keys_to_decrypt: List of keys to decrypt

        Returns:
            Dictionary with specified keys decrypted
        """
        decrypted_data = data.copy()
        for key in keys_to_decrypt:
            if key in decrypted_data and decrypted_data[key]:
                decrypted_data[key] = self.decrypt(decrypted_data[key])
        return decrypted_data


# Singleton instance
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """
    Get encryption service singleton

    Returns:
        EncryptionService instance
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
