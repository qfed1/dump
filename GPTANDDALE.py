import os
import glob
from termcolor import colored
import openai
import csv
import itertools
from pathlib import Path
from tqdm import tqdm
import bardapi

# Load API keys from CSV file
with open(Path("C:/Users/evanb/git/AI/NEWFILES/logins.csv"), 'r') as f:
    reader = csv.reader(f)
    api_keys = list(itertools.chain.from_iterable(reader))

# Initialize counter and key index
counter = 0
key_index = 0

# Set initial API key
openai.api_key = api_keys[key_index]

# Set your Bard API key
os.environ['_BARD_API_KEY'] = "WggfdnzaZhMKRwia9xVF4y08ZbyV5GBUE0Re4Y00Yu0SWWCvM14CIemjquE-W5gKoatCIA."

# Define the root directory
root_dir = "CONTRACTS"

def chat_with_gpt(prompt, custom_text):
    global counter
    global key_index

    # Initialize conversation history
    conversation_history = []

    # Add user input to conversation history
    conversation_history.append({"role": "user", "content": f"{custom_text}: {prompt}"})

    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=conversation_history
    )

    # Extract the model's message from the response
    gpt_message = response['choices'][0]['message']['content']

    # Add model's response to conversation history
    conversation_history.append({"role": "assistant", "content": gpt_message})

    # Increment counter after each prompt
    counter += 1

    # If counter reaches 24, switch API key
    if counter >= 24:
        counter = 0  # Reset counter
        key_index = (key_index + 1) % len(api_keys)  # Move to next key in a circular manner
        openai.api_key = api_keys[key_index]  # Update API key

    return gpt_message

def chat_with_bard(prompt, custom_text):
    try:
        # Concatenate the custom text and the prompt
        full_prompt = f"{custom_text}: {prompt}"
        
        # Send an API request and get a response.
        response = bardapi.core.Bard().get_answer(full_prompt)
        return response
    except Exception as e:
        print(f"Error while processing with Bard API: {e}")
        return "Error: Bard API failed"

# Get the total number of .sol files for the progress bar
total_files = sum(len(files) for _, _, files in os.walk(root_dir) if any(file.endswith('.sol') for file in files))

# Initialize progress bar
pbar = tqdm(total=total_files)

# Define csv writer for gpt-3 and bard
gpt3_writer = csv.writer(open('output_gpt3.csv', 'w', newline='', encoding='utf-8'))
bard_writer = csv.writer(open('output_bard.csv', 'w', newline='', encoding='utf-8'))

# Write headers
gpt3_writer.writerow(["Concatenated"])
bard_writer.writerow(["Concatenated"])

# Iterate over all subdirectories in the root directory
for dirpath, dirnames, filenames in os.walk(root_dir):
    # Check if the current directory is a 'src' directory or a contract directory
    if os.path.basename(dirpath) == 'src' or 'src' not in dirnames:
        # Use glob to find all .sol files in the current directory
        sol_files = glob.glob(os.path.join(dirpath, '*.sol'))

        # Process all found .sol files
        for sol_file in sol_files:
            # Print the filename in red
            print(colored(sol_file, 'red'))

            # Open the .sol file and read its contents
            with open(sol_file, 'r', encoding='utf-8') as file:
                prompt = file.read()

                # Here you can use the prompt variable as the input to your model
                custom_text = "Look for malicious solidity code, make the first word a YES or NO statement based on if you find any Red Flags"

            # Check if the prompt is too long
            # Check if the prompt is too long
            if len(prompt) > 4000:
                # Split the prompt into chunks and process each chunk separately
                chunks = [prompt[i:i + 4000] for i in range(0, len(prompt), 4000)]
                for chunk in chunks:
                    gpt_response = chat_with_gpt(chunk, custom_text)
                    bard_response = chat_with_bard(chunk, custom_text)

                    # Write the output to a CSV file for long prompts
                    gpt3_writer.writerow([f"{sol_file}\n{gpt_response}\n"])
                    bard_writer.writerow([f"{sol_file}\n{bard_response}\n"])
            else:
                gpt_response = chat_with_gpt(prompt, custom_text)
                bard_response = chat_with_bard(prompt, custom_text)

                # Write the output to a csv file
                gpt3_writer.writerow([f"{sol_file}\n{gpt_response}\n"])
                bard_writer.writerow([f"{sol_file}\n{bard_response}\n"])

        # Update the progress bar
        pbar.update(1)

pbar.close()
