import subprocess

try:
    subprocess.run(['./debug.sh'], check=True)
except subprocess.CalledProcessError as e:
    print(f'Command {e.cmd} failed with error {e.returncode}')