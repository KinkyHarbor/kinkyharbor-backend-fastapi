# Backend in FastAPI

Generate JWT key and store in `jwt-keys` folder
```bash
# https://gist.github.com/maxogden/62b7119909a93204c747633308a4d769

cd jwt-keys
openssl ecparam -genkey -name secp521r1 -noout -out private.pem
openssl ec -in private.pem -pubout -out public.pem 
```