import argparse
import os
import csv

from rosbag2_py import ConverterOptions
from rosbag2_py import SequentialReader
from rosbag2_py import StorageOptions

def create_reader(bag_dir: str) -> SequentialReader:
    storage_options = StorageOptions(
        uri=bag_dir,
        storage_id="sqlite3",
    )
    converter_options = ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )

    reader = SequentialReader()
    reader.open(storage_options, converter_options)
    return reader


def calc_topic_size(bag_path: str, csv_path: str):
    reader = create_reader(bag_path)
    type_map = {}
    for topic_type in reader.get_all_topics_and_types():
        type_map[topic_type.name] = topic_type.type

    stat = {}
    total_data_size = 0
    while reader.has_next():
        (topic, data, stamp) = reader.read_next()
        if topic != '/rosout':
            data_size = len(data)
            total_data_size += data_size
            if topic in stat:
                stat[topic] += data_size
            else:
                stat[topic] = data_size
    sorted_stat = sorted(stat.items(), key=lambda i: i[1], reverse=True)

    with open(csv_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["total_data_size(byte)->", total_data_size])
        writer.writerow(["order", "topic_name", "topic_size", "percentage"])
        for i, (topic, size) in enumerate(sorted_stat):
            writer.writerow([i+1, topic, size, size / total_data_size * 100])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bag_path", type=str)
    parser.add_argument("--csv_path", "-c", type=str, default="./analyze.csv")
    args = parser.parse_args()
    calc_topic_size(os.path.expandvars(args.bag_path), os.path.expandvars(args.csv_path))

if __name__ == "__main__":
    main()
