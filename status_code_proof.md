### Status Code Proof (curl -i output)

## GET /health (expect 200)
HTTP/1.1 200 OK
date: Mon, 05 Jan 2026 17:43:57 GMT
server: uvicorn
content-length: 15
content-type: application/json
x-request-id: cd73b25a-edb2-4fe8-92c0-30b5bf2f717f

{"status":"ok"}
## GET /does-not-exist (expect 404)
HTTP/1.1 404 Not Found
date: Mon, 05 Jan 2026 17:44:15 GMT
server: uvicorn
content-length: 22
content-type: application/json
x-request-id: 1985e7c6-2e28-4f92-adba-fc83cd42b3ca

{"detail":"Not Found"}
## GET /favicon.ico (expect 204)
HTTP/1.1 204 No Content
date: Mon, 05 Jan 2026 17:44:27 GMT
server: uvicorn
x-request-id: a445cab1-5fe7-4fc5-813c-223504b5a9eb


## POST /v1/auth/login wrong password (expect 401)
HTTP/1.1 401 Unauthorized
date: Mon, 05 Jan 2026 17:44:47 GMT
server: uvicorn
content-length: 32
content-type: application/json
x-request-id: 1c65a44e-9360-4132-a83a-a9e97dcc4eef

{"detail":"Invalid credentials"}
## POST /v1/auth/register invalid input (expect 422)
HTTP/1.1 422 Unprocessable Entity
date: Mon, 05 Jan 2026 17:44:58 GMT
server: uvicorn
content-length: 365
content-type: application/json
x-request-id: ff5fe68b-0b6c-42c2-93b9-67648790952f

{"detail":[{"type":"value_error","loc":["body","email"],"msg":"value is not a valid email address: An email address must have an @-sign.","input":"not-an-email","ctx":{"reason":"An email address must have an @-sign."}},{"type":"value_error","loc":["body","password"],"msg":"Value error, Password must be at least 8 characters long","input":"x","ctx":{"error":{}}}]}


Generated against Dockerized API at http://127.0.0.1:8000 on 2026-01-05.