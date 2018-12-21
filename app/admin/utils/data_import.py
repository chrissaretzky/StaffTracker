import cerberus
from datetime import datetime


class Data_Import:
    def __init__(self):
        self.log = {}
        self.log['schema_errors'] = []

    def process_bad_type_errors(self, errors, data):
        for error in errors:
            key = ''.join(error.document_path)
            if error.constraint == 'number':
                data[key] = self.convert_yes_no_string_to_ints(
                    error.value, data[key])
                data[key] = self.convert_stringed_numbers_to_ints(
                    error.value, data[key])
            elif error.constraint == 'datetime':
                data[key] = self.convert_string_to_datetime_or_set_to_null(
                    error.value)
        return data

    def convert_yes_no_string_to_ints(self, error_value, data):
        if error_value == 'yes':
            data = 1
        elif error_value == 'no':
            data = 0

        return data

    def convert_string_to_datetime_or_set_to_null(self, error_value):
        data = None
        value_errors = []

        if error_value and not data:
            for fmt in ('%Y/%m/%d %H/%M/%S', '%m/%d/%Y %H:%M:%S',
                        '%m/%d/%Y %H:%M', '%m/%d/%Y', '%Y/%m/%d %H:%M',
                        '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S'):
                try:
                    data = datetime.strptime(error_value, fmt)
                except ValueError as ve:
                    value_errors.append(ve)
                    pass
        if not data:
            print(value_errors)

        return data

    def convert_stringed_numbers_to_ints(self, error_value, data):
        if isinstance(error_value, str):
            return int(data)
        else:
            return data


class Excel_Import(Data_Import):
    def __init__(self):
        super().__init__()

    def validate_import(self, data, schema):
        v = cerberus.Validator(schema)

        validated_data = []

        for d in data:
            if d:
                v.validate(d)
                if len(v.errors) > 0:
                    if cerberus.errors.BAD_TYPE in v._errors:
                        d = self.process_bad_type_errors(v._errors, d)
                    v.validate(d)

                if len(v.errors) > 0:
                    self.log.get('schema_errors').append(v.errors)
                else:
                    validated_data.append(d)
        return validated_data


# class Cursor_Import(Data_Import):
#     def __init__(self, data):
#     data should include the cursor and the schema

#     self.cursor = cursor
#     self.schema = schema
#     self.validated_data = self.validate_import()

#     def validate_import(self, cursor, schema):
#         v = cerberus.Validator(schema)
#         validated_list = []

#         for d in cursor:
#             d = dict(d)
#             v.validate(d)
#             if len(v.errors) > 0:
#                 if cerberus.errors.BAD_TYPE in v._errors:
#                     d = self.process_bad_type_errors(v._errors, d)
#                 v.validate(d)

#             if len(v.errors) > 0:
#                 self.log.get('schema_errors').append(v.errors)
#             else:
#                 validated_list.append(d)
#         return validated_list
