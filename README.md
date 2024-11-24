# transaction-api
<b>Simple API service allowing authorized clients to send transactions &amp; fetch transactions history</b>

<b>To run API:</b>
1) git clone "https://github.com/tegularis/transaction-api.git"
2) run postgresql and rabbitmq servers
3) create & fill <b>config/config.yml</b> according to <b>config/config_example.yml</b> fields


# authentication:

every request must contain headers field <b>AUTH-TOKEN</b> containing a JWT-token obtained from <b>authorization</b> service (https://github.com/tegularis/transaction-auth)

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
            "balance": 100.0
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

sends a transaction to receiver in case you have sufficient balance, returns transaction uuid

<b>body example:</b>

---

    "data": {
        "receiver_uuid": "a724ce5b-f977-47e4-8ee2-8a39ffbfe93e",
        "amount": 100.0
    }
<b>response example:</b>


    "ok": true,
    "message": "processing transaction",
    "content": {
        "data": {
            "uuid": "639e4024-1292-4308-9cf3-7787e7179b3c"
        }
    }

<b>after transaction is processed, if your balance is sufficient, transaction status is set to "completed", if your balance is insufficient, transaction status is set to "cancelled"</b>

---

    GET: /transaction/history

returns client`s transactions list<br/>

<b>possible parameters:<br/><br/></b>
<b>limit</b>: int - <i>limit of transactions to fetch</i> (OPTIONAL)<br/> 
<b>offset</b>: int - <i>offset of transactions to fetch</i> (OPTIONAL)<br/>
<b>status</b>: str - <i>status of transactions</i> (OPTIONAL, possible statuses: "revised", "completed", "cancelled")<br/>
<b>side</b>: str  - <i>side of transactions</i> (OPTIONAL, possible statuses: "sender", "receiver")<br/> 
<br/>
<b>response example:</b>

    "ok": true,
    "message": "success",
    "content": {
        "data": {
            "list": [
                {
                    "date": null,
                    "id": 10,
                    "amount": 10.0,
                    "uuid": null,
                    "status": "revised",
                    "receiver_id": 1,
                    "sender_id": 2
                },
                {
                    "date": "2024-11-24T18:30:34.023724",
                    "id": 18,
                    "amount": 10.0,
                    "uuid": "639e4024-1292-4308-9cf3-7787e7179b3c",
                    "status": "completed",
                    "receiver_id": 1,
                    "sender_id": 2
                },
                {
                    "date": "2024-11-24T17:47:11.513008",
                    "id": 2,
                    "amount": 100.0,
                    "uuid": "dff04a35-9f02-4f72-8e4e-ac7a4fd82b6d",
                    "status": "completed",
                    "receiver_id": 2,
                    "sender_id": null
                }
            ]
        }
    }


---
