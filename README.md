# kinkyharbor-backend-fastapi
Backend in FastAPI

Generate JWT key with
```bash
# https://gist.github.com/maxogden/62b7119909a93204c747633308a4d769

openssl ecparam -genkey -name secp521r1 -noout -out ecdsa-p521-private.pem
openssl ec -in ecdsa-p521-private.pem -pubout -out ecdsa-p521-public.pem 
```