import subprocess

command = ["slither", "0xe88e3057Fa90C89CFF2B23c6Ce534F3C27D52F8d", "--print", "human-summary"]

# Launch the subprocess with the given command.
# By default, subprocess.run will raise an exception if the command fails.
try:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    print(f"An error occurred while running the command: {e}")
    exit(1)

# If the command completed successfully, print the command's output.
print(result.stdout)
