import csv
import json
from pathlib import Path

# Define the file path
file_path = Path(r"C:\Users\evanb\git\AI\NEWFILES\OBEYORDIE\output_bard.csv")

# Check if the file exists
if not file_path.exists():
    print("File does not exist")
    exit()

# Load your data
json_data = []
with file_path.open('r', encoding='utf-8') as f:
    for line in f:
        json_data.append(json.loads(line))

# Write to CSV
with open('output_flattened.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    
    # Write the header
    header = ['content', 'conversation_id', 'response_id', 'textQuery0', 'textQuery1']
    max_choices = max(len(item['choices']) for item in json_data)
    for i in range(max_choices):
        header.extend([f'choice_id_{i}', f'choice_content_{i}'])
    writer.writerow(header)

    # Write the data
    for item in json_data:
        row = [item['content'], item['conversation_id'], item['response_id'], item['textQuery'][0], item['textQuery'][1]]
        for i in range(max_choices):
            if i < len(item['choices']):
                row.extend([item['choices'][i]['id'], item['choices'][i]['content'][0]])
            else:
                row.extend([None, None])  # Write None if there are no more choices
        writer.writerow(row)
