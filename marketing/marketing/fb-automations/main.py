from utils.post_handler import post_from_csv
import os

if __name__ == "__main__":
    # Choose your CSV file
    csv_path = os.path.join("data", "waterice_specials.csv")

    # Post all items in the CSV
    post_from_csv(csv_path)
