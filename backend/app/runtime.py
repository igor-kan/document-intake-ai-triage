def detect_ml_frameworks() -> dict:
    status = {"tensorflow": False, "torch": False}
    try:
        import tensorflow  # noqa: F401
        status["tensorflow"] = True
    except Exception:
        pass

    try:
        import torch  # noqa: F401
        status["torch"] = True
    except Exception:
        pass

    return status
