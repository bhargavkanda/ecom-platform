from psycopg2.extras import NumericRange
from psycopg2._range import NumberRangeAdapter


class TypedNumericRange(NumericRange):
    pg_type = None


class Int4NumericRange(TypedNumericRange):
    pg_type = b'int4range'


class TypedNumericRangeAdapter(NumberRangeAdapter):
   def getquoted(self):
    return super(TypedNumericRangeAdapter, self).getquoted() + b'::' + self.adapted.pg_type


