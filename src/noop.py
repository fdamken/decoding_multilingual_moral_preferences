class NoOp:
    # noinspection PyMissingConstructor
    def __init__(self):
        pass

    def __getattr__(self, *args, **kwargs) -> None:
        raise NotImplementedError(f"call to noop __setattr__({args}, {kwargs})")

    def __setattr__(self, *args, **kwargs) -> None:
        raise NotImplementedError(f"call to noop __setattr__({args}, {kwargs})")
