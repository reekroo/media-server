from pydantic import BaseModel

class BaseDigestConfig(BaseModel):
    rpc_method: str
    enabled: bool = True