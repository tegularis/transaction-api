import uuid

from sqlalchemy import text

from src.pkg.database.models import session


def get_balance(client_id: int) -> float:
    query = text(
        """
        WITH credit AS (
            SELECT SUM(amount) AS cr FROM transaction 
            WHERE receiver_id = :client_id AND status = 'completed'
        ),
        debit AS (
            SELECT SUM(amount) AS db FROM transaction 
            WHERE sender_id = :client_id AND status = 'completed'
        )
        SELECT (COALESCE(credit.cr, 0) - COALESCE(debit.db, 0)) AS balance FROM credit, debit;
        """
    )
    res = session.execute(query, {"client_id": client_id}).fetchone()
    if not res:
        return 0
    return res.balance

def create_transaction(amount: float, receiver_uuid: str, sender_id: int, status: str):
    query = text(
        """
        INSERT INTO 
        transaction(status, amount, receiver_id, sender_id, date, uuid)
        VALUES(:status, :amount, (SELECT id FROM client WHERE uuid = :receiver_uuid), :sender_id, NOW(), :uuid)
        RETURNING transaction.uuid;
        """
    )
    res = session.execute(query,
                          {"status": status,
                           "amount": amount,
                           "receiver_uuid": receiver_uuid,
                           "sender_id": sender_id,
                           "uuid": uuid.uuid4()}
                          ).fetchone()
    session.commit()
    if not res:
        return
    return res.uuid
