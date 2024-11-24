import datetime


def get_seconds_since_epoch():
    ep = datetime.datetime(1970, 1, 1, 0, 0, 0)
    return (datetime.datetime.utcnow() - ep).total_seconds()
