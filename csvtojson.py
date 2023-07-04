import csv
import json
import argparse
import glob
import os


def argument():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--csv_dir", help="Add CSV Directory", type=str)
    parser.add_argument("-o", "--output_json", help="Output json", type=str, default="output.json")
    return parser.parse_args()


def csv_to_json(csv_file_path: str):
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row


def load_json(json_file_path, data):
    with open(json_file_path, 'w') as jsonfile:
        jsonfile.write(json.dumps(data))


def main():
    args = argument()
    csv_dir = args.csv_dir
    output_json = args.output_json
    assert csv_dir, "Argument csv_dir is required."
    assert os.path.isdir(csv_dir), "Enter a valid csv_dir path"
    print("檢查路徑！")
    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    for csv_file_path in csv_files:
        key = os.path.basename(csv_file_path).replace("hospital_atg_", "").replace(".csv", "")
        print(f"csv to json: {key} 讀取資料")

        json_file_path = f"json/{key}.json"
        with open(json_file_path, 'a') as jsonfile:
            jsonfile.write("{\n")
            jsonfile.write(f"\t\"{key}\":[\n")
        tranform = csv_to_json(csv_file_path)
        value = next(tranform, None)
        while value:
            value = next(tranform, None)
            load_json(json_file_path, value)
        with open(json_file_path, 'a') as jsonfile:
            jsonfile.write("\n]")
            jsonfile.write("\n}")

        print(f"csv to json: {key} 轉換完成")

    print("转换完成！")


if __name__ == '__main__':
    main()
