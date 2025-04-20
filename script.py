# import time
# import subprocess
# import sqlite3
# import re
# from multiprocessing import Process, Manager
# import RPi.GPIO as GPIO
# from threading import Thread

# # Database and Proxmark3 configurations
# DATABASE_PATH = "tags.db"
# PROXMARK3_CLIENT_PATH = "proxmark3/pm3"
# DEVICE_PATH = "/dev/ttyACM0"

# # GPIO Pin Configuration
# STEP_PIN = 21  # GPIO pin for the STEP signal
# DIR_PIN = 20   # GPIO pin for the DIR signal
# STEPS_PER_REV = 3200  # Steps per revolution (for 1/16 microstepping)
# DEGREES_PER_STEP = 360 / STEPS_PER_REV  # Degrees per step calculation
# MOTOR_DELAY = 0.0005  # Delay between motor steps (in seconds)

# # Batch write configuration
# BATCH_WRITE_INTERVAL = 10  # Seconds between batch writes
# new_tags = []  # List to hold new tags for batch writes

# # GPIO setup for the stepper motor
# def setup_motor():
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(STEP_PIN, GPIO.OUT)
#     GPIO.setup(DIR_PIN, GPIO.OUT)
#     GPIO.output(STEP_PIN, GPIO.LOW)
#     GPIO.output(DIR_PIN, GPIO.LOW)

# # Stepper motor control function
# def rotate_motor(degrees, direction=1, delay=MOTOR_DELAY):
#     steps = int(degrees / DEGREES_PER_STEP)  # Calculate the number of steps
#     GPIO.output(DIR_PIN, GPIO.HIGH if direction == 1 else GPIO.LOW)
#     for _ in range(steps):
#         GPIO.output(STEP_PIN, GPIO.HIGH)
#         time.sleep(delay)
#         GPIO.output(STEP_PIN, GPIO.LOW)
#         time.sleep(delay)

# # Thread-based motor control
# def motor_thread(degrees, direction):
#     t = Thread(target=rotate_motor, args=(degrees, direction))
#     t.start()

# # Database setup
# def ensure_database():
#     connection = sqlite3.connect(DATABASE_PATH)
#     cursor = connection.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS tags (
#             tag_id TEXT PRIMARY KEY
#         )
#     """)
#     connection.close()

# # Load all tags into cache
# def load_cache():
#     connection = sqlite3.connect(DATABASE_PATH)
#     cursor = connection.cursor()
#     cursor.execute("SELECT tag_id FROM tags")
#     tag_cache = {row[0] for row in cursor.fetchall()}
#     connection.close()
#     return tag_cache

# # Add tags to the batch for writing
# def add_tag_to_database(tag_id, cache):
#     if tag_id not in cache:
#         new_tags.append(tag_id)
#         cache.add(tag_id)  # Update the in-memory cache

# # Batch write new tags to the database
# def batch_write_to_database():
#     while True:
#         time.sleep(BATCH_WRITE_INTERVAL)
#         if new_tags:
#             connection = sqlite3.connect(DATABASE_PATH)
#             cursor = connection.cursor()
#             try:
#                 cursor.executemany("INSERT INTO tags (tag_id) VALUES (?)", [(tag,) for tag in new_tags])
#                 connection.commit()
#                 print(f"Added {len(new_tags)} new tags to the database.")
#                 new_tags.clear()  # Clear the batch
#             except sqlite3.IntegrityError:
#                 print("Some tags already exist in the database.")
#             finally:
#                 connection.close()

# # RFID reader with non-blocking subprocess read
# def read_rfid(shared_list):
#     import os, select
#     process = subprocess.Popen(
#         [PROXMARK3_CLIENT_PATH, "-p", DEVICE_PATH],
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#         bufsize=1
#     )
#     process.stdin.write("lf hid watch\n")
#     process.stdin.flush()

#     os.set_blocking(process.stdout.fileno(), False)

#     last_seen = {}
#     debounce_time = 0.5  # Short debounce time in seconds

#     while True:
#         ready, _, _ = select.select([process.stdout], [], [], 0.1)
#         if process.stdout in ready:
#             line = process.stdout.read().strip()
#             match = re.search(r"TAG ID:\s*([0-9A-Fa-f]+)", line)
#             if match:
#                 tag_id = match.group(1)
#                 current_time = time.time()

#                 # Debounce: Skip if seen recently
#                 if tag_id in last_seen and current_time - last_seen[tag_id] < debounce_time:
#                     continue

#                 last_seen[tag_id] = current_time
#                 shared_list.append(tag_id)  # Add tag to shared list

# # Tag processing
# def process_tags(shared_list):
#     ensure_database()
#     cache = load_cache()  # Load known tags into memory

#     while True:
#         if shared_list:
#             tag_id = shared_list.pop(0)  # Get the first tag from the shared list
#             if tag_id in cache:
#                 print(f"Tag {tag_id} exists in the database! Access granted.")
#                 motor_thread(90, 1)  # Rotate motor clockwise
#                 time.sleep(5)  # Wait 5 seconds
#                 motor_thread(90, 0)  # Rotate motor back
#             else:
#                 print(f"Tag {tag_id} not found in the database! Access denied.")
#                 user_input = input(f"Would you like to add tag {tag_id} to the database? (yes/no): ").strip().lower()
#                 if user_input == "yes":
#                     add_tag_to_database(tag_id, cache)
#                 else:
#                     print("Tag not added.")

# if __name__ == "__main__":
#     manager = Manager()
#     shared_list = manager.list()  # Shared list for communication

#     setup_motor()

#     try:
#         # Start the batch writer in a separate thread
#         batch_writer = Thread(target=batch_write_to_database, daemon=True)
#         batch_writer.start()

#         # Start processes for RFID reading and tag processing
#         reader_process = Process(target=read_rfid, args=(shared_list,))
#         processor_process = Process(target=process_tags, args=(shared_list,))

#         reader_process.start()
#         processor_process.start()

#         reader_process.join()
#         processor_process.join()
#     except KeyboardInterrupt:
#         print("Shutting down...")
#     finally:
#         GPIO.cleanup()


##DEBUGGING CODE
import time
import subprocess
import sqlite3
import re
import os
import select
from threading import Thread
import RPi.GPIO as GPIO

# Database and Proxmark3 configurations
DATABASE_PATH = "tags.db"
PROXMARK3_CLIENT_PATH = "./proxmark3/pm3"
DEVICE_PATH = "/dev/ttyACM0"

# GPIO Pin Configuration
STEP_PIN = 21  # GPIO pin for the STEP signal
DIR_PIN = 20   # GPIO pin for the DIR signal
STEPS_PER_REV = 3200  # Steps per revolution (for 1/16 microstepping)
DEGREES_PER_STEP = 360 / STEPS_PER_REV  # Degrees per step calculation
MOTOR_DELAY = 0.0001  # Delay between motor steps (in seconds)

# Debounce Configuration
DEBOUNCE_INTERVAL = 0.1  # Time (in seconds) to wait before reprocessing the same tag
motor_running = False  # Track motor activity

# GPIO setup for the stepper motor
def setup_motor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(STEP_PIN, GPIO.OUT)
    GPIO.setup(DIR_PIN, GPIO.OUT)
    GPIO.output(STEP_PIN, GPIO.LOW)
    GPIO.output(DIR_PIN, GPIO.LOW)

# Stepper motor control function
def rotate_motor(degrees, direction=1, delay=MOTOR_DELAY):
    steps = int(degrees / DEGREES_PER_STEP)  # Calculate the number of steps
    GPIO.output(DIR_PIN, GPIO.HIGH if direction == 1 else GPIO.LOW)
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(delay)

# Thread-based motor control
def motor_thread(tag_id, last_seen_tags):
    global motor_running
    motor_running = True  # Indicate motor is active
    rotate_motor(720, direction=1)  # Rotate 250 degrees clockwise
    time.sleep(5)  # Wait for 2 seconds
    rotate_motor(720, direction=0)  # Rotate back to the original position
    motor_running = False  # Indicate motor is done
    del last_seen_tags[tag_id]  # Allow the tag to be processed again

# Database setup
def ensure_database():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            tag_id TEXT PRIMARY KEY
        )
    """)
    connection.close()

# Load all tags into cache
def load_cache():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT tag_id FROM tags")
    tag_cache = {row[0] for row in cursor.fetchall()}
    connection.close()
    return tag_cache

# Add a tag to the database
def add_tag_to_database(tag_id, cache):
    if tag_id not in cache:
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO tags (tag_id) VALUES (?)", (tag_id,))
            connection.commit()
            cache.add(tag_id)  # Update in-memory cache
        except sqlite3.IntegrityError:
            pass  # Tag already exists
        finally:
            connection.close()

# RFID processing with Proxmark3 using `lf hid read`
def read_rfid():
    global motor_running

    try:
        # Start the Proxmark3 client
        process = subprocess.Popen(
            [PROXMARK3_CLIENT_PATH, "-p", DEVICE_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line-buffered for faster processing
        )

        last_seen_tags = {}  # Track the last processed time for each tag
        ensure_database()
        cache = load_cache()  # Load tags into memory

        while True:
            # Send the `lf hid read` command
            process.stdin.write("lf hid read\n")
            process.stdin.flush()

            # Check if there's output to read
            ready, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)
            for output_stream in ready:
                line = output_stream.readline().strip()
                if not line:
                    continue  # Skip empty lines

                print(f"DEBUG: Raw output: {line}")  # Print raw output for debugging

                # Parse TAG ID from the line
                match = re.search(r"raw:\s*([0-9A-Fa-f]+)", line)
                if match:
                    tag_id = match.group(1)
                    print(f"Detected RFID tag: {tag_id}")

                    # Skip if motor is running
                    if motor_running:
                        continue

                    # Check debounce interval
                    current_time = time.time()
                    if tag_id in last_seen_tags and current_time - last_seen_tags[tag_id] < DEBOUNCE_INTERVAL:
                        continue

                    last_seen_tags[tag_id] = current_time  # Update last seen time

                    # Process tag: Check database and act
                    if tag_id in cache:
                        print(f"Tag {tag_id} found in database. Access granted.")
                        Thread(target=motor_thread, args=(tag_id, last_seen_tags)).start()
                    else:
                        print(f"Tag {tag_id} not found in database. Adding to database.")
                        add_tag_to_database(tag_id, cache)

    except Exception as e:
        print(f"Error occurred: {e}")  # Print the exception for debugging

if __name__ == "__main__":
    setup_motor()

    try:
        # Start RFID reading
        read_rfid()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        GPIO.cleanup()