[![Build stable](https://github.com/KinkyHarbor/kinkyharbor-backend-fastapi/workflows/Build%20stable%20Docker%20image/badge.svg)](https://hub.docker.com/r/kinkyharbor/kinkyharbor-backend-fastapi/tags)
[![Build latest](https://github.com/KinkyHarbor/kinkyharbor-backend-fastapi/workflows/Build%20latest%20Docker%20image/badge.svg)](https://hub.docker.com/r/kinkyharbor/kinkyharbor-backend-fastapi/tags)
[![codecov](https://codecov.io/gh/KinkyHarbor/kinkyharbor-backend-fastapi/branch/development/graph/badge.svg)](https://codecov.io/gh/KinkyHarbor/kinkyharbor-backend-fastapi)
[![Maintainability](https://api.codeclimate.com/v1/badges/135715f257043669493e/maintainability)](https://codeclimate.com/github/KinkyHarbor/kinkyharbor-backend-fastapi/maintainability)

# Backend in FastAPI

Generate JWT key and store in `jwt-keys` folder

```bash
# https://gist.github.com/maxogden/62b7119909a93204c747633308a4d769

cd jwt-keys
openssl ecparam -genkey -name secp521r1 -noout -out private.pem
openssl ec -in private.pem -pubout -out public.pem
```

## Env variables

### Types of variables

<dl>
  <dt>String</dt>
  <dd>Default: See variable</dd>

  <dt>Int (number)</dt>
  <dd>Default: See variable</dd>

  <dt>Boolean</dt>
  <dd>Default: False</dd>
  <dd>True (not case sensitive) => True</dd>
  <dd>Everything else => False</dd>
</dl>

### Variables

<dl>
  <dt>DEBUG (Boolean)</dt>
  <dd>Set log level to DEBUG</dd>
  <dd>Default: False</dd>

  <dt>FRONTEND_URL (String)</dt>
  <dd>Base url of the frontend</dd>
  <dd>Mandatory, no default</dd>

  <dt>CORS (String)</dt>
  <dd>List of allowed origins for CORS. Origins are separated by semicolon. Schema is mandatory.</dd>
  <dd>Default: value of FRONTEND_URL</dd>

  <dt>EMAIL_FROM_NAME (String)</dt>
  <dd>"From" name in emails</dd>
  <dd>Default: Kinky Harbor</dd>

  <dt>EMAIL_FROM_ADDRESS (String)</dt>
  <dd>Sender address of emails</dd>
  <dd>Mandatory, no default</dd>

  <dt>EMAIL_HOSTNAME (String)</dt>
  <dd>Hostname of the mail server</dd>
  <dd>Default: localhost</dd>

  <dt>EMAIL_PORT (Int)</dt>
  <dd>Port of the mail server</dd>
  <dd>Default: 25</dd>

  <dt>EMAIL_SECURITY (String)</dt>
  <dd>Sets the security type for SMTP</dd>
  <dd>Allowed values: tls_ssl, starttls, unsecure</dd>
  <dd>Default: tls_ssl</dd>

  <dt>EMAIL_USERNAME (String)</dt>
  <dd>Username for mail server</dd>
  <dd>No default (empty string)</dd>

  <dt>EMAIL_PASSWORD (String)</dt>
  <dd>Password for mail server</dd>
  <dd>No default (empty string)</dd>

  <dt>JWT_KEY_PATH (String)</dt>
  <dd>Path to ECDSA keys for JWT signing</dd>
  <dd>Default: ../jwt-keys</dd>

  <dt>MONGO_HOST (String)</dt>
  <dd>Hostname of Mongo DB</dd>
  <dd>Default: localhost</dd>

  <dt>MONGO_DATABASE (String)</dt>
  <dd>Database in Mongo DB</dd>
  <dd>Default: kinkyharbor</dd>
</dl>

## Big thanks to

- [Leonardo Giordani](https://github.com/lgiordani) for his [awesome book](https://leanpub.com/clean-architectures-in-python) and [good examples](https://github.com/pycabook) on the Clean Architecture
