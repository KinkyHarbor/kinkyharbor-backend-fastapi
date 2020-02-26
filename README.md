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
  <dt>Boolean</dt>
  <dd>Default: False</dd>
  <dd>True (not case sensitive) => True</dd>
  <dd>Everything else => False</dd>
</dl>

### Variables
<dl>
  <dt>DEMO (Boolean)</dt>
  <dd>Disable verification for registration, password reset and email changes.</dd>
</dl>