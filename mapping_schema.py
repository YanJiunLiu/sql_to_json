import re
from typing import Dict
import argparse
import os
import json


class MyDict(Dict):
    def extra_get(self, extra_string: str, index: int):
        reg_complier = re.compile(r'{{\w+\.\w+}}')
        assert reg_complier.match(extra_string), "Your extra_string doesn`t match {{\w+\.\w+}}"
        key1, key2 = re.findall(r'\w+', extra_string)
        return self[key1][index][key2]

    def extra_function(self, extra_string: str, index: int):
        reg_complier = re.compile(r'>>>[\w\W\.]+<<<')
        assert reg_complier.match(extra_string), "Your extra_string doesn`t match {{\w+\.\w+}}"
        variables = re.findall(r'{{\w+\.\w+}}', extra_string)
        print(f"extra_string::{extra_string}")
        for var in variables:
            extra_value = self.extra_get(extra_string=var, index=index)
            if isinstance(extra_value, str):
                extra_value = "'" + extra_value + "'"
            extra_string = extra_string.replace(var, extra_value)
        execute_string = extra_string.replace(">>>", "").replace("<<<", "")
        print(f"execute_string:{execute_string}")
        return eval(execute_string)


def argument():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_json", help="Add input JSON", type=str)
    parser.add_argument("-o", "--output_json", help="Output json", type=str, default="output.json")
    return parser.parse_args()


def main(schema: str):
    args = argument()
    input_json = args.input_json
    assert input_json, "Argument input_json is required."
    assert os.path.isfile(input_json), "Enter a valid input_json path"
    with open(input_json, 'r') as json_file:
        json_data = json.loads(json_file.read())

    reg = r">>>.*?<<<"
    functions = re.findall(reg, schema)

    reg = r'{{\w+\.\w+}}'
    variables = re.findall(reg, schema)

    json_data = MyDict(json_data)

    # for index, _ in enumerate(json_data["sample"]):
    for index, _ in enumerate(range(0, 1, 1)):
        new_schema = schema
        for function in functions:
            extra_value = json_data.extra_function(function, index)
            new_schema = new_schema.replace(function, f'{extra_value}')

        for variable in variables:
            extra_value = json_data.extra_get(variable, index)
            if not extra_value:
                extra_value = ''
            new_schema = new_schema.replace(variable, extra_value)

        print(new_schema)
    return 0


if __name__ == '__main__':
    schema = """
    {
        "subject":{
            "alternate_ids":["{{sample.client}}", "{{sample.client_en}}", "{{sample.phone}}"],
            "date_of_birth":"{{sample.birth_date}}",
            "gender":{
                "id": ">>>'GSSO:000090' if {{sample.gender}} == 'Male' else 'GSSO:000089' if {{sample.gender}} == 'Female' else 'GSSO:009485'<<<"
            },
            "time_at_last_encounter":{
                "gestational_age":{
                    "week":"{{sample.weeks}}",
                    "day":"{{sample.prepro_date}}"
                }
            }
        },
        "meta_data":{
            "created_by":">>>[f'Organization/{teacher[\"t_group\"]}' for teacher in self[\"teacher_copy\"] if teacher[\"t_no\"]=={{sample.t_no}}][0]<<<",
            "created":"{{sample.keyin_date}}",
            "submitted_by":"Practitioner/{{sample.t_no}}"
        }
    }
    """
    main(schema=schema)
