import subprocess
import os

proxmark3_client_path = os.path.join(os.getcwd(), "proxmark3", "pm3")
device_path = "/dev/tty.usbmodemiceman1"

try:
    process = subprocess.Popen([proxmark3_client_path, "-p", device_path],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

    output, error = process.communicate(input="lf hid watch\n")

    if process.returncode == 0:
        print("Command executed successfully:")
        print(output)
    else:
        print("Error occurred:")
        print(error)
except Exception as e:
    print(f"Error: {e}")
