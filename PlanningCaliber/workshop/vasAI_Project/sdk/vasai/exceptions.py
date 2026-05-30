class VasAIError(Exception):
    pass

class VasAIConnectionError(VasAIError):
    pass

class VasAINotFoundError(VasAIError):
    pass

class VasAIAuthError(VasAIError):
    pass
