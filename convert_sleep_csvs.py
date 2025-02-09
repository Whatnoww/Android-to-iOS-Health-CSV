import csv
from datetime import datetime, timedelta
import argparse
import os
import glob
import subprocess
import sys

def process_file(input_file, output_file, combined_writer):
    """
    Process a single CSV file:
      - Reads each row,
      - Converts the start datetime (from the "Date" field) and calculates the end datetime (by adding the duration),
      - Writes the converted row to the individual output file and to the combined CSV writer.
    """
    with open(input_file, 'r', newline='') as infile, \
         open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)
        # Write header for the individual output file.
        writer.writerow(["start datetime", "end datetime", "sleep"])
        
        for row in reader:
            try:
                # Parse the start datetime from the "Date" field.
                # Expected format: "YYYY.MM.DD HH:MM:SS"
                start_dt = datetime.strptime(row["Date"], "%Y.%m.%d %H:%M:%S")
            except ValueError as e:
                print(f"Error parsing date in file {input_file}: {e}")
                continue

            try:
                # Get the duration (in seconds) and add to start_dt.
                duration_seconds = int(row["Duration in seconds"])
            except ValueError as e:
                print(f"Error parsing duration in file {input_file}: {e}")
                continue

            end_dt = start_dt + timedelta(seconds=duration_seconds)
            start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
            end_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")
            sleep_stage = row["Sleep stage"]

            # Write the converted row to the individual file.
            writer.writerow([start_str, end_str, sleep_stage])
            # Also write the same row to the combined CSV.
            combined_writer.writerow([start_str, end_str, sleep_stage])

def main():
    parser = argparse.ArgumentParser(
        description="Convert multiple sleep CSV files and join them into a single CSV file."
    )
    parser.add_argument("input_dir", help="Directory containing input CSV files")
    parser.add_argument("output_dir", help="Directory to store converted CSV files")
    parser.add_argument("--combined", default="combined.csv",
                        help="Filename for the combined CSV output (default: combined.csv)")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    combined_filename = args.combined

    # Create the output directory if it doesn't exist.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Prepare the combined CSV file.
    combined_path = os.path.join(output_dir, combined_filename)
    combined_file = open(combined_path, 'w', newline='')
    combined_writer = csv.writer(combined_file)
    # Write header for the combined CSV.
    combined_writer.writerow(["start datetime", "end datetime", "sleep"])

    # Find all CSV files in the input directory.
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    if not csv_files:
        print(f"No CSV files found in directory: {input_dir}")
        combined_file.close()
        return

    # Process each CSV file.
    for input_file in csv_files:
        base_name = os.path.basename(input_file)
        output_file = os.path.join(output_dir, base_name)
        print(f"Processing '{input_file}' -> '{output_file}'")
        process_file(input_file, output_file, combined_writer)

    combined_file.close()
    print(f"Combined CSV file created at: {combined_path}")

    other_script = "compareandmovecombined.py"  # Update this path as needed.
    if os.path.exists(other_script):
        print(f"Executing {other_script} ...")
        subprocess.run([sys.executable, other_script])
    else:
        print(f"Error: {other_script} not found.")

if __name__ == "__main__":
    main()
