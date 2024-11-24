# transaction-api
<b>Simple API service allowing authorized clients to send transactions &amp; fetch transactions history</b>

# authentication:

every request must contain headers field <b>AUTH-TOKEN</b> containing a JWT-token obtained from <b>authorization</b> service

---
# methods:

---
    GET: /client/get_me

returns client`s data

<b>example:</b>


    "ok": true,
    "message": "success",
    "content": {
        "data": {
            "uuid": "a724ce5b-f977-47e4-8ee2-8a39ffbfe93e",
            "login": "your-login",
            "password": "your-password",
            "balance": 100
        }
    }

---

    POST: /client/set_password

updates password

<b>body example:</b>


    "data": {
        "password": "your-new-password"
    }
<b>response example:</b>


    "ok": true,
    "message": "success",
    "content": {}

---

    POST: /transaction/send

sends a transaction to receiver in case you have sufficient balance

<b>body example:</b>


    "data": {
        "receiver_uuid": "a724ce5b-f977-47e4-8ee2-8a39ffbfe93e",
        "amount": 100
    }
<b>response example:</b>


    "ok": true,
    "message": "success",
    "content": {}
