#!/usr/bin/env python3
"""
Diagnostic script to test Anthropic API key
"""
import os
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Anthropic API Key Diagnostic")
print("=" * 60)

# 1. Check if .env file exists
env_path = Path(__file__).parent / ".env"
print(f"\n1. Checking .env file:")
print(f"   Path: {env_path}")
print(f"   Exists: {env_path.exists()}")

if env_path.exists():
    with open(env_path, 'r') as f:
        env_content = f.read()
        if 'ANTHROPIC_API_KEY' in env_content:
            # Extract the key line (without showing the full key)
            key_line = [line for line in env_content.split('\n') if line.startswith('ANTHROPIC_API_KEY')]
            if key_line:
                key_parts = key_line[0].split('=')
                if len(key_parts) > 1:
                    key_value = key_parts[1].strip()
                    print(f"   Key found: Yes")
                    print(f"   Key length: {len(key_value)} characters")
                    print(f"   Key starts with: {key_value[:20]}...")
                    print(f"   Key ends with: ...{key_value[-10:]}")
                    print(f"   Has whitespace: {key_value != key_value.strip()}")
                    print(f"   Looks like placeholder: {key_value.startswith('your_') or 'placeholder' in key_value.lower()}")
                else:
                    print(f"   ⚠️  Key line found but no value after '='")
            else:
                print(f"   ❌ ANTHROPIC_API_KEY not found in .env")
        else:
            print(f"   ❌ ANTHROPIC_API_KEY not in .env file")

# 2. Try loading from settings
print(f"\n2. Loading from app.core.config:")
try:
    from app.core.config import settings
    print(f"   ✅ Settings loaded successfully")
    print(f"   ANTHROPIC_API_KEY exists: {bool(settings.ANTHROPIC_API_KEY)}")
    if settings.ANTHROPIC_API_KEY:
        key = settings.ANTHROPIC_API_KEY
        print(f"   Key length: {len(key)} characters")
        print(f"   Key starts with: {key[:20]}...")
        print(f"   Key ends with: ...{key[-10:]}")
        print(f"   Key format check:")
        print(f"      - Starts with 'sk-ant-': {key.startswith('sk-ant-')}")
        print(f"      - Has correct prefix: {key.startswith('sk-ant-api03-') or key.startswith('sk-ant-api04-')}")
except Exception as e:
    print(f"   ❌ Error loading settings: {e}")
    sys.exit(1)

# 3. Try creating Anthropic client
print(f"\n3. Creating Anthropic client:")
try:
    from anthropic import Anthropic
    print(f"   ✅ Anthropic SDK imported")
    print(f"   SDK version: {Anthropic.__version__ if hasattr(Anthropic, '__version__') else 'unknown'}")
    
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    print(f"   ✅ Client created successfully")
    print(f"   Client has 'messages' attribute: {hasattr(client, 'messages')}")
except Exception as e:
    print(f"   ❌ Error creating client: {e}")
    sys.exit(1)

# 4. Test API call
print(f"\n4. Testing API call:")
print(f"   Using model: {settings.DEFAULT_MODEL}")
try:
    response = client.messages.create(
        model=settings.DEFAULT_MODEL,
        max_tokens=10,
        messages=[{'role': 'user', 'content': 'Hi'}]
    )
    print(f"   ✅ API call successful!")
    print(f"   Response: {response.content[0].text[:50]}...")
    print(f"   ✅ Your API key is VALID and working!")
except Exception as e:
    print(f"   ❌ API call failed:")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error message: {str(e)}")
    
    # Check for specific error types
    error_str = str(e).lower()
    
    if 'credit' in error_str or 'balance' in error_str or 'billing' in error_str:
        print(f"\n   🔍 Billing/Credit Error:")
        print(f"   ✅ Your API key is VALID, but your account has insufficient credits.")
        print(f"   The API key authentication worked, but you need to add credits.")
        print(f"\n   💡 Next steps:")
        print(f"   1. Go to: https://console.anthropic.com/settings/billing")
        print(f"   2. Add credits to your account")
        print(f"   3. Or upgrade your plan")
        print(f"   4. Once credits are added, the API will work")
    elif '401' in str(e) or 'authentication' in error_str or 'invalid' in error_str:
        print(f"\n   🔍 Authentication Error Details:")
        print(f"   This means Anthropic rejected your API key.")
        print(f"   Possible causes:")
        print(f"   1. Key is invalid or expired")
        print(f"   2. Key was revoked")
        print(f"   3. Key doesn't have required permissions")
        print(f"   4. Key format is incorrect")
        print(f"\n   💡 Next steps:")
        print(f"   1. Go to: https://console.anthropic.com/settings/keys")
        print(f"   2. Verify your key is active")
        print(f"   3. Create a new key if needed")
        print(f"   4. Copy the FULL key (starts with sk-ant-api03- or sk-ant-api04-)")
        print(f"   5. Update backend/.env with: ANTHROPIC_API_KEY=<your-full-key>")
        print(f"   6. Restart your backend server")
    else:
        print(f"\n   🔍 Other Error:")
        print(f"   Check the error message above for details")
    
    sys.exit(1)

print(f"\n" + "=" * 60)
print("✅ All checks passed! Your API key is working correctly.")
print("=" * 60)

