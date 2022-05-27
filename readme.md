Forskningsrådet API 
===================
This is a Python script that generates a JWT Grant token from Maskinporten and fetches application- and project CSV files from [Forskningsrådet](https://www.forskningsradet.no/).

You can find additional documentation from [Forskningsrådet](https://api.forskningsradet.no/swagger-ui/index.html?configUrl=/v3/api-docs/swagger-config#/) and [Maskinporten](https://docs.digdir.no/docs/Maskinporten/maskinporten_auth_server-to-server-oauth2.html).

Configure 
---------
Create a .env file based on the .env.example file in this project.
To connect to maskinporten you will need a certificate, referenced by filename in your .env file
Client ID can be obtained from [Digdir Samarbeid](https://minside-samarbeid.digdir.no/my-organisation/integrations/admin). You need to create a new intergration of type "Maskinporten", with the scope "rcn:prosjektapi".

Install
-------
```
python3 -m pip install requests pyjwt pyOpenSSL python-dotenv
```

Run
------
```
python3 nfr.py
```

Credits
-------
John Short, Anders Nordbø

Norwegian University of Life Sciences | NMBU - Systemseksjonen