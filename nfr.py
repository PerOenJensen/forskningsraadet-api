#
# NMBU - Get CSV from Forskningsradet
#
# API docs: https://api.forskningsradet.no/swagger-ui/index.html?configUrl=/v3/api-docs/swagger-config#
#
import jwt
import requests
import uuid
import os
import json 
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate


# Function to strip the PEM header and footer
def strip_pem_header_footer(cert_pem):
    # Decode PEM certificate to string, split into lines, and filter out the header/footer
    stripped_lines = [line for line in cert_pem.decode().splitlines() if not line.startswith('-----')]
    # Join the filtered lines back together
    cert_raw = ''.join(stripped_lines)
    return cert_raw

load_dotenv()

outputDir = os.getenv("OUTPUT_DIR")

# Cert
password = os.getenv("CERT_PASSWORD")
cert_path = os.getenv("CERT_PATH")

# JWT
issuer = os.getenv("CLIENT_ID")
audience = os.getenv("AUDIENCE")
scope = os.getenv("SCOPE")

# Maskinporten
maskinportenEndpoint = os.getenv("ENDPOINT")

# Load the PKCS12 certificate and private key
p12_data = None
p12 = None

with open(cert_path, "rb") as f:
    p12_data = f.read()
    p12 = pkcs12.load_key_and_certificates(p12_data, password.encode())

# Get company certificate and private key
private_key = p12[0].private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
cert = p12[1].public_bytes(serialization.Encoding.PEM)
raw_cert = strip_pem_header_footer(cert)

# Generate JWT
iat = datetime.now(tz=timezone.utc)
exp = datetime.now(tz=timezone.utc) + timedelta(seconds=120)
jti = str(uuid.uuid4())
encodedJwt = jwt.encode({"iss": issuer, "aud": audience, "scope": scope, "jti": jti, "iat": iat, "exp": exp}, private_key, algorithm="RS256", headers={"x5c": [raw_cert]})

# Get Bearer token
maskinportenPost = {"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": encodedJwt}
maskinportenRes = requests.post(maskinportenEndpoint, data = maskinportenPost).json()
bearerToken = maskinportenRes["access_token"]

# Make call to NFR
hdr = {'Authorization': 'Bearer {}'.format(bearerToken), 'User-Agent': 'nmbu' }
applicationsRes = requests.get("https://api.forskningsradet.no/soknaderCSV", headers=hdr)
applicationResultsRes = requests.get("https://api.forskningsradet.no/soknadsresultaterCSV", headers=hdr)
projectsRes = requests.get("https://api.forskningsradet.no/prosjekterCSV", headers=hdr)

# Save results to file
with open(outputDir+"/"+"applications.csv", "wb") as outfile:
    outfile.write(applicationsRes.content)
with open(outputDir+"/"+"application_results.csv", "wb") as outfile:
    outfile.write(applicationResultsRes.content)
with open(outputDir+"/"+"projects.csv", "wb") as outfile:
    outfile.write(projectsRes.content)
