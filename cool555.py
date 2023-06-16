import os
import subprocess

# Path to the directory containing the slither executable
# Replace with your actual path
slither_dir = "/root/Desktop/dump/slither"

# Change to the slither directory
os.chdir(slither_dir)

command = ["slither", "0x22dA8601bD4738A7cb1A935d4990F1C5C0De3769", "--print", "human-summary"]

# Launch the subprocess with the given command.
try:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    print(f"An error occurred while running the command: {e}\nError message:\n{e.stderr}")
    exit(1)


# If the command completed successfully, print the command's output.
print(result.stdout)

