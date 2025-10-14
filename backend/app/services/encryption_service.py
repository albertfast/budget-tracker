from cryptography.fernet import Fernet
from typing import Optional
import base64
import os
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        self.cipher_suite = self._initialize_cipher()
    
    def _initialize_cipher(self) -> Fernet:
        """Initialize encryption cipher with key from settings"""
        if settings.ENCRYPTION_KEY:
            try:
                key = settings.ENCRYPTION_KEY.encode()
                return Fernet(key)
            except Exception as e:
                logger.error(f"Invalid encryption key: {str(e)}")
                raise ValueError("Invalid encryption key configuration")
        else:
            # Generate a new key for development (not recommended for production)
            logger.warning("No encryption key provided, generating temporary key")
            key = Fernet.generate_key()
            return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            if not data:
                return ""
            
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise Exception("Failed to encrypt data")
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            if not encrypted_data:
                return ""
            
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise Exception("Failed to decrypt data")
    
    def encrypt_plaid_token(self, access_token: str) -> str:
        """Encrypt Plaid access token for database storage"""
        return self.encrypt(access_token)
    
    def decrypt_plaid_token(self, encrypted_token: str) -> str:
        """Decrypt Plaid access token for API calls"""
        return self.decrypt(encrypted_token)

# Initialize encryption service
encryption_service = EncryptionService()

def encrypt_sensitive_data(data: str) -> str:
    """Helper function to encrypt sensitive data"""
    return encryption_service.encrypt(data)

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Helper function to decrypt sensitive data"""
    return encryption_service.decrypt(encrypted_data)