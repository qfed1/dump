import os
import subprocess

# Get the current working directory
cwd = os.getcwd()

# Change to the slither subdirectory
os.chdir(os.path.join(cwd, "slither"))

command = ["slither", "0x7F37f78cBD74481E593F9C737776F7113d76B315", "--print", "human-summary"]

# Launch the subprocess with the given command.
try:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    print(f"An error occurred while running the command: {e}")
    exit(1)

# If the command completed successfully, print the command's output.
print(result.stdout)
