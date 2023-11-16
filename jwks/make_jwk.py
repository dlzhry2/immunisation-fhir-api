#!/usr/bin/env python3
"""
make_jwk.py

Create a JWK from a PEM Public Key

Usage:
  make_jwk.py  PUBLIC_KEY_FILE  KEY_ID  ENV  APP_ID
  make_jwk.py (-h | --help)

Options:
  -h --help                        Show this screen.
"""
import sys
import pathlib
import argparse
import json
import uuid
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

ENVIRONMENTS = [
    "internal-dev",
    "internal-dev-sandbox",
    "internal-qa",
    "internal-qa-sandbox",
    "ref",
    "dev",
    "sandbox",
    "int",
    "prod",
    "paas",
]
JWKS_ROOT_DIR = pathlib.Path(__file__).absolute().parent.parent.joinpath("jwks")

def generate_jwk(public_key, key_id):
    # Generate an RSA key from the provided PEM public key
    public_key_bytes = public_key.encode('utf-8')
    crypto_public_key = serialization.load_pem_public_key(public_key_bytes, backend=default_backend())

    # Extract public key components for JWK
    numbers = crypto_public_key.public_numbers()

    jwk = {
        "kty": "RSA",
        "kid": key_id,
        "use": "sig",
        "alg": "RS512",  # Change this according to your needs
        "n": numbers.n,
        "e": numbers.e,
    }

    return jwk

def main():
    parser = argparse.ArgumentParser(description='Create a JWK from a PEM Public Key')
    parser.add_argument('PUBLIC_KEY_FILE', help='Path to the PEM Public Key file')
    parser.add_argument('KEY_ID', help='Key ID')
    parser.add_argument('ENV', choices=ENVIRONMENTS, help='Environment')
    parser.add_argument('APP_ID', help='App ID')

    args = parser.parse_args()

    # Check public key file exists
    pk_file = args.PUBLIC_KEY_FILE
    if not pathlib.Path(pk_file).exists():
        print(f"Unable to find PUBLIC_KEY_FILE: {pk_file}", file=sys.stderr)
        sys.exit(1)

    # Validate environment
    env = args.ENV
    if env not in ENVIRONMENTS:
        print(f"Invalid ENV: {env}", file=sys.stderr)
        print(f"Must be one of {ENVIRONMENTS}", file=sys.stderr)
        sys.exit(1)

    # Validate app_id
    app_id = args.APP_ID
    if env != "paas":  # Don't validate for PaaS clients
        try:
            uuid.UUID(app_id, version=4)
        except ValueError:
            print(f"Invalid APP_ID: {app_id}, expecting a uuid4", file=sys.stderr)
            sys.exit(1)

    # Build the public key
    with open(pk_file) as f:
        public_key = f.read()

    # Generate JWK
    new_key = generate_jwk(public_key, args.KEY_ID)

    # Create empty keystore
    jwks = {"keys": []}

    jwks_env_dir = JWKS_ROOT_DIR.joinpath(env)

    # If file already exists, load existing keystore
    jwks_file = jwks_env_dir.joinpath(f"{app_id}.json")
    if jwks_file.exists():
        with open(jwks_file) as f:
            try:
                jwks = json.load(f)
            except json.decoder.JSONDecodeError:
                # If the file exists but is empty
                jwks = {"keys": []}

    # Check if key already present
    for key in jwks["keys"]:
        if key["kid"] == new_key["kid"]:
            print(f"kid already present in {jwks_file}", file=sys.stderr)
            print(json.dumps(jwks, indent=2), file=sys.stderr)
            sys.exit(1)

    if not jwks_env_dir.exists():
        jwks_env_dir.mkdir()

    # Add key and write
    jwks["keys"].append(new_key)
    with open(jwks_file, "w") as f:
        json.dump(jwks, f, indent=2)

    print(json.dumps(jwks, indent=2))

if __name__ == "__main__":
    main()
