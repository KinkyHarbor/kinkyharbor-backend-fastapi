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

  <dt>Boolean</dt>
  <dd>Default: False</dd>
  <dd>True (not case sensitive) => True</dd>
  <dd>Everything else => False</dd>
</dl>

### Variables

<dl>
  <dt>JWT_KEY_PATH (String)</dt>
  <dd>Path to ECDSA keys for JWT signing</dd>
  <dd>Default: ../jwt-keys</dd>

  <dt>MONGO_HOST (String)</dt>
  <dd>Hostname of Mongo DB</dd>
  <dd>Default: localhost</dd>

  <dt>MONGO_DATABASE (String)</dt>
  <dd>Database in Mongo DB</dd>
  <dd>Default: kinkyharbor</dd>

  <dt>DEMO (Boolean)</dt>
  <dd>Disable verification for registration, password reset and email changes.</dd>
</dl>
