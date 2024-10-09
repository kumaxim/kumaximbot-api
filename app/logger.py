from logging import StreamHandler, getLogger
from pythonjsonlogger.jsonlogger import JsonFormatter


class YcLoggingFormatter(JsonFormatter):
    """
        @see https://yandex.cloud/ru/docs/functions/operations/function/logs-write?utm_referrer=about%3Ablank#primery-funkcij
    """
    def add_fields(self, log_record, record, message_dict):
        super(YcLoggingFormatter, self).add_fields(log_record, record, message_dict)
        log_record['logger'] = record.name
        log_record['level'] = str.replace(str.replace(record.levelname, "WARNING", "WARN"), "CRITICAL", "FATAL")


# logging.getLogger().setLevel(logging.DEBUG)

handler = StreamHandler()
handler.setFormatter(YcLoggingFormatter('%(message)s %(level)s %(logger)s'))

logger = getLogger()
logger.addHandler(handler)
logger.propagate = False
