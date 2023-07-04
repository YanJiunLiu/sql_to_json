import mysql.connector
import csv
import json
import argparse
import glob
import os


def argument():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--sql_dir", help="Add SQL Directory", type=str)
    parser.add_argument("-o", "--output_csv", help="Output json", type=str, default="output.json")
    return parser.parse_args()


def csv_to_json(csv_file_path: str):
    data = []
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data


def load_json(json_file_path, data):
    with open(json_file_path, 'w') as jsonfile:
        jsonfile.write(json.dumps(data, indent=4))


def main():
    args = argument()
    csv_dir = args.csv_dir
    output_json = args.output_json
    assert csv_dir, "Argument csv_dir is required."
    assert os.path.isdir(csv_dir), "Enter a valid csv_dir path"
    print("檢查路徑！")
    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    json_data = {}
    for csv_file_path in csv_files:
        key = os.path.basename(csv_file_path).replace("hospital_atg_", "").replace(".csv", "")
        print(f"csv to json: {key} 讀取資料")
        value = csv_to_json(csv_file_path)
        json_data[key] = value
        print(f"csv to json: {key} 轉換完成")
    load_json(output_json, json_data)


if __name__ == '__main__':
    config = {
        'host': 'mysql-seqslab-jmz6t2zh32m2y.mysql.database.azure.com',
        'user': 'Akbcvwqybwz236@mysql-seqslab-jmz6t2zh32m2y',
        'password': 'Piaixlgyz5grpyx!',
        'database': 'hospital_atg'
    }

    # 连接到MySQL数据库
    conn = mysql.connector.connect(**config)
    if conn.is_connected():
        print("MySQL连接成功")
    else:
        raise ConnectionError("MySQL连接失败")
    cursor = conn.cursor()
    print(f"cursor數值 {cursor}")
    # 执行查询获取所有表名
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    # 打印表名
    for table in tables:
        csv_file_path = f'csv/{table[0]}.csv'  # 替换为输出的CSV文件路径
        print(f"查询{table[0]}")
        cursor.execute(f"SELECT * FROM {table[0]};")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        print(f"寫入 csv/{table[0]}.csv")
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_names)
            writer.writerows(rows)

    cursor.close()
    conn.close()
    print("转换完成！")
