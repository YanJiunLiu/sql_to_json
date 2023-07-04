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
        for var in variables:
            extra_value = self.extra_get(extra_string=var, index=index)
            if isinstance(extra_value, str):
                extra_value = "'" + extra_value + "'"
            extra_string = extra_string.replace(var, extra_value)
        execute_string = extra_string.replace(">>>", "").replace("<<<", "")
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

        new_schema = new_schema.replace('\n', '').replace('        ','')
        print(eval(new_schema))
    return 0


if __name__ == '__main__':
    schema = """
    {
        "id":"{{sample.id}}",
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
            "submitted_by":"Practitioner/{{sample.t_no}}",
            "external_references":[
                {
                    "reference":"CONSENT:",
                    "description": "Individual consent for research purpose."
                } if '{{sample.permit}}' == 'Y' else None
            ],
            "priority":"urgent" if "{{sample.urgent_doc}}" == "是" else "routine",
            "updates":[
                {
                    "timestamp":"1000-01-01",
                    "comment":"CREATION:{{sample.id}}",
                    "updated_by":"pause31@cgmmgb.onmicrosoft.com"
                } if "{{sample.keyin_date}}"=="0000-00-00" else {
                    "timestamp":"{{sample.keyin_date}}",
                    "comment":"CREATION:{{sample.id}}",
                    "updated_by":"pause31@cgmmgb.onmicrosoft.com"
                },
                {
                    "timestamp":"1000-01-01",
                    "comment":"MODIFICATION:{{sample.id}}",
                    "updated_by":"pause31@cgmmgb.onmicrosoft.com"
                } if "{{sample.modify_date}}"=="0000-00-00" else {
                    "timestamp":"{{sample.modify_date}}",
                    "comment":"MODIFICATION:{{sample.id}}",
                    "updated_by":"pause31@cgmmgb.onmicrosoft.com"
                },
                {
                    "timestamp":"1000-01-01",
                    "comment":"COMPLETION:{{sample.id}}",
                    "updated_by":"pause31@cgmmgb.onmicrosoft.com"
                } if "{{sample.check_date}}"=="0000-00-00" else {
                    "timestamp":"{{sample.check_date}}",
                    "comment":"COMPLETION:{{sample.id}}",
                    "updated_by":"pause31@cgmmgb.onmicrosoft.com"
                },
                {
                    "timestamp":"1000-01-01",
                    "comment":"READMISSION:{{sample.id}}",
                    "updated_by":"pause31@cgmmgb.onmicrosoft.com"
                } if "{{sample.submit_date}}"=="0000-00-00" else {
                    "timestamp":"{{sample.submit_date}}",
                    "comment":"READMISSION:{{sample.id}}",
                    "updated_by":"pause31@cgmmgb.onmicrosoft.com"
                }
            ],
            "phenotypic_features": {
                "description":">>>'單胞胎' if {{sample.fetus}} == '1' else "異卵雙胞" if  {{sample.fetus}} == '2' else '同卵雙胞' if {{sample.fetus}} == '3' else '多胞胎' if {{sample.fetus}} == '4' else '很多胞胎' if {{sample.fetus}} == '5' else ''<<<",
                "type":{
                    "id": "http://purl.bioontology.org/ontology/RCD/X75WE"
                }
            }
        }
    }
    """
    main(schema=schema)
