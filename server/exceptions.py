class Error(Exception):
    code = 'error'
    message = '服务器错误'

    def __init__(self, message=None):
        if message is not None:
            self.message = message

    def __str__(self):
        return f'{self.code}: {self.message}'

    @property
    def json(self):
        return {
            'code': self.code,
            'message': self.message,
        }


class WrongArguments(Error):
    code = 'wrong_arguments'
    message = '参数错误'


class WrongFormat(Error):
    code = 'wrong_format'
    message = '格式错误'


class NotFound(Error):
    code = 'not_found'
    message = '对象不存在'
