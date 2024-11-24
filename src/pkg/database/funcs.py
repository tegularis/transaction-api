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
        SELECT (credit.cr - debit.db) AS balance FROM credit, debit;
        """
    )
    res = session.execute(query, {"client_id": client_id}).fetchone()
    if not res:
        return 0
    return res.balance

def create_transaction(amount: float, receiver_uuid: str, sender_id: int, status: str):
    query = (
        """
        INSERT INTO 
        transaction(status, amount, receiver_id, sender_id)
        VALUES(%s, %s, (SELECT id FROM client WHERE uuid = %s), %s)
        RETURNING uuid;
        """
    )
    res = session.execute(query, status, amount, receiver_uuid, sender_id)
    return res
