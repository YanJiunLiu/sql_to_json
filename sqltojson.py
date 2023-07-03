import re
import json

SQL_files = ["reads_summary_atg_20230619.sql", "hospital_atg_20230619.sql", "reads_summary_WES_summary_20230117.sql"]
# 開始讀取SQL檔案
for j, SQL_file in enumerate(SQL_files):
    with open(SQL_file, 'r') as file:
        statement = ''
        all_data = {}
        for i, line in enumerate(file):
            line = line.strip()
            if line.endswith(');') or line.endswith('/;') or line.endswith('\';') or line.endswith('/;'):
                statement += line
                create_table_match = re.search(r'^CREATE TABLE', statement, re.MULTILINE)
                if create_table_match:
                    table_name = re.findall(r'\`\w+\`', statement)[0].strip('`')
                    columns_matches = re.findall(r'\`\w+\` \w+\(\d+\)|\`\w+\` double|\`\w+\` text|\`\w+\` float', statement)
                    col_info = [(col.split(' ')[0].strip('`'), col.split(' ')[1]) for col in columns_matches]

                insert_into_match = re.search(r'^INSERT INTO ', statement, re.MULTILINE)
                if insert_into_match:
                    data = []
                    data_matches = re.findall(r"\(.*?\)", statement)
                    for match in data_matches:
                        reg = r'\'([^\']+)\'|[+-]?[0-9.]+|\'\''
                        init = re.search(reg, match, re.MULTILINE)
                        values = []
                        rematch = match
                        while init:
                            pos = init.end()
                            rematch = rematch[pos:]
                            values.append(init.group())
                            init = re.search(reg, rematch, re.MULTILINE)
                        record = {}
                        print(f"目前所在的table_name: {table_name}")
                        print(f"欄位長度：{len(col_info)}, 欄位訊息：{col_info}")
                        print(f"資料長度：{len(values)}")
                        if len(col_info) != len(values):
                            with open(f'error-{j}.txt', 'a+') as file:
                                file.write(f"{match}\n")
                            continue
                        for i, (col_name, col_type) in enumerate(col_info):
                            if 'int' in col_type:
                                record[col_name] = float(values[i])
                            else:
                                record[col_name] = values[i].strip('\'')
                        data.append(record)

                    all_data[table_name] = data
                statement = ''
            else:
                statement += line


json_data = json.dumps(all_data)
# print(json_data)
# # 將JSON資料寫入檔案
with open('output.json', 'w') as file:
    file.write(json_data)
