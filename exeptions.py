class CCAppException(Exception):
    def __init__(self, text):
        super().__init__(text)

class CCAppValueErrorException(CCAppException):
    pass

class CCAppUniqueItemException(CCAppException):
    pass

class CCAppDataFormatException(CCAppException):
    pass
