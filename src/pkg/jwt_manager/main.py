from typing import Union
import jwt


class JwtManager:
    def __init__(self, cfg):
        self.cfg = cfg

    def encode(self, payload: dict) -> str:
        return jwt.encode(payload, self.cfg["jwt"]["secret"], algorithm=self.cfg["jwt"]["algorithm"])

    def decode(self, token: str) -> Union[dict, None]:
        return jwt.decode(token, self.cfg["jwt"]["secret"], algorithms=[self.cfg["jwt"]["algorithm"]])