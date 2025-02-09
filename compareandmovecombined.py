import csv
import os
import shutil
import subprocess
import sys
from datetime import datetime

def read_csv(file_path):
    """Reads a CSV file and returns a list of rows."""
    rows = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:  # skip empty rows
                rows.append(row)
    return rows

def write_csv(file_path, rows):
    """Writes the given rows to a CSV file."""
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def sort_rows_by_datetime(rows, datetime_index, datetime_format):
    """
    Sort rows by a datetime column.
    
    Adjust datetime_format if your datetime strings differ.
    """
    def parse_dt(row):
        try:
            return datetime.strptime(row[datetime_index], datetime_format)
        except Exception as e:
            # Fallback: if parsing fails, return a minimal datetime so the row sorts to the beginning.
            return datetime.min
    return sorted(rows, key=parse_dt)

def main():
    # Define file paths.
    new_csv_path = os.path.join("converted_csvs", "combined.csv")     # New incoming CSV.
    target_csv_path = os.path.join("combined", "combined.csv")          # Target CSV for new unique rows.
    history_csv_path = os.path.join("combined", "combined_old.csv")     # Persistent history of all data.

    # Specify the datetime column index and format.
    datetime_col_index = 0  # Assuming the first column contains the datetime.
    datetime_format = "%Y-%m-%d %H:%M:%S"  # Adjust if your datetime format is different.

    # Check that the new CSV exists.
    if not os.path.exists(new_csv_path):
        print(f"Error: The new CSV file does not exist at {new_csv_path}.")
        return

    # --- Step 1: Read the new CSV and separate header from data ---
    new_csv_rows = read_csv(new_csv_path)
    if not new_csv_rows:
        print("New CSV is empty.")
        return
    header = new_csv_rows[0]
    new_data = new_csv_rows[1:]
    
    # --- Remove internal duplicates from new_data ---
    unique_new_data = []
    seen = set()
    for row in new_data:
        row_tuple = tuple(row)
        if row_tuple not in seen:
            seen.add(row_tuple)
            unique_new_data.append(row)
    
    # --- Step 2: Load history from combined_old.csv (if it exists) ---
    # Use new CSV header as the default.
    history_header = header
    history_data = []
    if os.path.exists(history_csv_path):
        history_rows = read_csv(history_csv_path)
        if history_rows:
            history_header = history_rows[0]
            history_data = history_rows[1:]
    
    # Create a set for quick lookup of existing history rows.
    history_set = {tuple(row) for row in history_data}
    
    # --- Step 3: Filter out rows from new_data that already exist in history ---
    new_unique_data = []
    for row in unique_new_data:
        if tuple(row) not in history_set:
            new_unique_data.append(row)
    
    # --- Step 4: Archive the old target CSV (if it exists) ---
    if os.path.exists(target_csv_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archived_filename = f"combined+{timestamp}.csv"
        archived_path = os.path.join("combined", archived_filename)
        os.rename(target_csv_path, archived_path)
        print(f"Archived old target CSV as {archived_filename}")

    # --- Step 5: Write the new unique rows to the target CSV (with header) ---
    os.makedirs(os.path.dirname(target_csv_path), exist_ok=True)
    write_csv(target_csv_path, [header] + new_unique_data)
    print(f"New unique CSV written to {target_csv_path}")

    # --- Step 6: Update the history file (combined_old.csv) ---
    # Combine existing history with the new unique data.
    all_history_data = history_data + new_unique_data
    # Remove duplicates if any (this is precautionary).
    unique_history_data = []
    seen_history = set()
    for row in all_history_data:
        row_tuple = tuple(row)
        if row_tuple not in seen_history:
            seen_history.add(row_tuple)
            unique_history_data.append(row)
    # Sort the history data by the datetime column.
    sorted_history_data = sort_rows_by_datetime(unique_history_data, datetime_col_index, datetime_format)
    # Write the updated history file with the header and the sorted data rows.
    write_csv(history_csv_path, [header] + sorted_history_data)
    print(f"Updated history written to {history_csv_path}")

    # --- Step 7: Execute another Python script ---
    other_script = "upload.py"  # Update this path as needed.
    if os.path.exists(other_script):
        print(f"Executing {other_script} ...")
        subprocess.run([sys.executable, other_script])
    else:
        print(f"Error: {other_script} not found.")

if __name__ == "__main__":
    main()
