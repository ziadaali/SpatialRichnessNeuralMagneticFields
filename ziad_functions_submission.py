import sys

def generate_field_list(field_string):
    fields = field_string.split('_')
    all_fields = []
    for field in fields:
        if field[0] == 'm':
            new_field = []
            subfields = field[1:].split('x')
            for subfield in subfields:
                new_field.append(int(subfield))
        else:
            new_field = int(field)
        all_fields.append(new_field)
    return all_fields
