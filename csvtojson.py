import csv
import json
import argparse
import glob
import os


def argument():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--csv_dir", help="Add CSV Directory", type=str)
    parser.add_argument("-o", "--output_json", help="Output json", type=str, default="data.json")
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
    main()
    print("轉換完成！")
