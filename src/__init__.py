__all__ = ["RiskMAS"]


def __getattr__(name: str):
    if name == "RiskMAS":
        from .mas import RiskMAS
        return RiskMAS
    raise AttributeError(name)
