#
# NMBU - Get CSV from Forskningsrådet
#
# API docs: https://api.forskningsradet.no/swagger-ui/index.html?configUrl=/v3/api-docs/swagger-config#
#
import jwt
import requests
import uuid
import os
import json 
from datetime import datetime, timezone, timedelta
from OpenSSL import crypto
from dotenv import load_dotenv

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

# Get company certificate and private key
p12 = crypto.load_pkcs12(open(cert_path, 'rb').read(), bytes(password, "utf-8"))
private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())
cert = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())
raw_cert = ''.join(str(cert).split('\\n')[1:-2]) # Strip PEM header and footer

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
applicationResultsRes = request.get("https://api.forskningsradet.no/soknaderesultaterCSV", headers=hdr")
projectsRes = requests.get("https://api.forskningsradet.no/prosjekterCSV", headers=hdr)

# Save results to file
with open(outputDir+"/"+"applications.csv", "wb") as outfile:
    outfile.write(applicationsRes.content)
with open(outputDir+"/"+"application_results.csv", "wb") as outfile:
    outfile.write(applicationResultsRes.content)
with open(outputDir+"/"+"projects.csv", "wb") as outfile:
    outfile.write(projectsRes.content)


