import pandas as pd
import pandas_schema
from pandas_schema import Column
from pandas_schema.validation import CustomElementValidation
import numpy as np
from decimal import *


def check_decimal(dec):
    try:
        Decimal(dec)
    except InvalidOperation:
        return False
    return True


def check_int(num):
    try:
        int(num)
    except ValueError:
        return False
    return True


def do_validation():
    # read the data
    data = pd.read_csv('data.csv')

    # define validation elements
    decimal_validation = [CustomElementValidation(lambda d: check_decimal(d), 'is not decimal')]
    int_validation = [CustomElementValidation(lambda i: check_int(i), 'is not integer')]
    null_validation = [CustomElementValidation(lambda d: d is not np.nan, 'this field cannot be null')]

    # define validation schema
    schema = pandas_schema.Schema([
            Column('dec1', decimal_validation + null_validation),
            Column('dec2', decimal_validation),
            Column('dec3', decimal_validation),
            Column('dec4', decimal_validation),
            Column('dec5', decimal_validation),
            Column('dec6', decimal_validation),
            Column('dec7', decimal_validation),
            Column('company_id', int_validation + null_validation),
            Column('currency_id', int_validation + null_validation),
            Column('country_id', int_validation + null_validation)])

    # apply validation
    errors = schema.validate(data)
    errors_index_rows = [e.row for e in errors]
    data_clean = data.drop(index=errors_index_rows)

    # save data
    pd.DataFrame({'col':errors}).to_csv('errors.csv')
    data_clean.to_csv('clean_data.csv')


if __name__ == '__main__':
    do_validation()
