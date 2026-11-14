import sys
import unittest
from datetime import timedelta
from unittest.mock import MagicMock

# Ensure the backend directory is in path
sys.path.append(".")

class TestTrustSellCoreSecurity(unittest.TestCase):
    """
    Verification Suite for the Trust Sell Secure Backend.
    Tests core cryptography, JWT issuance, and Pydantic validation parameters.
    """
    
    def test_01_imports(self):
        """Verify all MVC components and models import cleanly without syntax issues."""
        try:
            from app.config.settings import settings
            from app.config.db import db_manager
            from app.models.user import UserDB
            from app.models.seller import SellerDB
            from app.models.brand import BrandDB
            from app.schemas.auth import LoginRequest
            from app.services.security import get_password_hash, verify_password
            from app.services.verification import validate_and_save_upload
            
            self.assertIsNotNone(settings)
            self.assertIsNotNone(db_manager)
            print("✓ Success: All MVC components and dependencies imported successfully.")
        except Exception as e:
            self.fail(f"Failure: Import check failed. Error: {str(e)}")

    def test_02_password_security(self):
        """Test password hashing and verification to ensure cryptographic strength."""
        from app.services.security import get_password_hash, verify_password

        pwd_1 = "SecurePassword123!"
        pwd_2 = "AnotherSecurePwd999"

        # Hash passwords
        hash_1 = get_password_hash(pwd_1)
        hash_2 = get_password_hash(pwd_2)

        # Basic validations
        self.assertNotEqual(pwd_1, hash_1)
        self.assertTrue(hash_1.startswith("$2b$")) # standard bcrypt prefix

        # Verification tests
        self.assertTrue(verify_password(pwd_1, hash_1))
        self.assertTrue(verify_password(pwd_2, hash_2))
        self.assertFalse(verify_password(pwd_1, hash_2))
        self.assertFalse(verify_password("wrong_pwd", hash_1))
        print("✓ Success: Cryptographic password hashing and verification passed.")

    def test_03_jwt_tokens(self):
        """Test JSON Web Token (JWT) encoding, decoding, expiration, and payload integrity."""
        from app.services.security import create_access_token, decode_access_token

        payload = {
            "sub": "60c72b2f9b1d8b2a3c8e4d56",
            "role": "seller",
            "email": "seller@trustsell.com"
        }

        # Create JWT token
        token = create_access_token(data=payload, expires_delta=timedelta(minutes=10))
        self.assertIsInstance(token, str)

        # Decode token and verify claims
        decoded = decode_access_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["sub"], payload["sub"])
        self.assertEqual(decoded["role"], payload["role"])
        self.assertEqual(decoded["email"], payload["email"])
        
        # Verify expiration exists
        self.assertIn("exp", decoded)
        print("✓ Success: JWT access token creation and decoding claims integrity passed.")

    def test_04_user_db_dict_serialization(self):
        """Test UserDB database model serialization hides nothing and normalizes emails."""
        from app.models.user import UserDB

        user = UserDB(
            name="Alice",
            email="AliceNew@Example.Com", # Mixed case to test email normalization
            phone="+923001234567",
            hashed_password="some_hashed_password_string",
            role="seller",
            selfie_url="uploads/sellers/selfie/test.jpg"
        )

        user_dict = user.to_dict()
        self.assertEqual(user_dict["email"], "alicenew@example.com") # lowercase
        self.assertEqual(user_dict["role"], "seller")
        self.assertEqual(user_dict["selfie_url"], "uploads/sellers/selfie/test.jpg")
        print("✓ Success: Pydantic database models serialize and sanitize inputs perfectly.")

if __name__ == "__main__":
    print("====================================================")
    print("Running Security & Import Verifications for Trust Sell...")
    print("====================================================")
    unittest.main()
