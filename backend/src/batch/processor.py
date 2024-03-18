from collections import OrderedDict

from typing import List

from batch.errors import DecoratorUnhandledError, TransformerRowError
from batch.immunization_api import ImmunizationApi
from batch.logs import LogData, BatchLogger
from batch.parser import DataParser
from batch.transformer import DataRecordTransformer


class BatchProcessor:
    headers: List[str]

    def __init__(self, parser: DataParser,
                 row_transformer: DataRecordTransformer,
                 api: ImmunizationApi,
                 log: BatchLogger):
        self.parser = parser
        self.row_transformer = row_transformer
        self.api = api
        self.log = log

    def process(self) -> None:
        rows = self.parser.parse_rows()
        headers = next(rows)
        self.headers = [h.lower() for h in headers]

        row_no = 0
        for row in rows:
            cur_row = row_no
            row_no += 1  # Inc now so it'll be correct in case of an exception
            record = OrderedDict(zip(self.headers, row))
            try:
                record = self.row_transformer.transform(record)
            except (DecoratorUnhandledError, TransformerRowError) as trans_err:
                self.log_row(trans_err, cur_row)
                continue
            except Exception as unhandled_err:
                self.log_row(unhandled_err, cur_row)
                continue

            self._send_data(record)

    def _send_data(self, data: dict) -> None:
        self.api.create_immunization(data)

    def log_row(self, exception: Exception, row: int = -1) -> None:
        if isinstance(exception, (DecoratorUnhandledError, TransformerRowError)):
            log_data = LogData(row=row)
        elif isinstance(exception, Exception):
            log_data = LogData(row=row)
        log_data = LogData()
        self.log.log(log_data)
