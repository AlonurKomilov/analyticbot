"""
API Key Encryption Service
===========================

Encrypts and decrypts user API keys using Fernet symmetric encryption.
"""

import logging
from typing import Optional
from cryptography.fernet import Fernet
from config.settings import settings

logger = logging.getLogger(__name__)


class APIKeyEncryption:
    """Handles encryption/decryption of user API keys."""
    
    def __init__(self):
        """Initialize with encryption key from settings."""
        # Get encryption key from environment
        encryption_key = getattr(settings, 'API_KEY_ENCRYPTION_KEY', None)
        
        if not encryption_key:
            # Generate a new key if not configured (development only)
            logger.warning("⚠️ API_KEY_ENCRYPTION_KEY not set, generating temporary key")
            encryption_key = Fernet.generate_key().decode()
            logger.warning(f"Generated key: {encryption_key}")
            logger.warning("⚠️ Add this to .env: API_KEY_ENCRYPTION_KEY={encryption_key}")
        
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
            
        self.cipher = Fernet(encryption_key)
    
    def encrypt(self, api_key: str) -> str:
        """
        Encrypt an API key.
        
        Args:
            api_key: Plain text API key
            
        Returns:
            Encrypted API key as string
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        encrypted = self.cipher.encrypt(api_key.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_key: str) -> str:
        """
        Decrypt an API key.
        
        Args:
            encrypted_key: Encrypted API key
            
        Returns:
            Plain text API key
        """
        if not encrypted_key:
            raise ValueError("Encrypted key cannot be empty")
        
        try:
            decrypted = self.cipher.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt API key: {e}")
            raise ValueError("Invalid or corrupted API key")


# Singleton instance
_encryption_instance: Optional[APIKeyEncryption] = None


def get_encryption() -> APIKeyEncryption:
    """Get singleton encryption instance."""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = APIKeyEncryption()
    return _encryption_instance
