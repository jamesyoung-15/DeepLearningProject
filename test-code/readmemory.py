import psutil
import ctypes
import sys, os
import re



# Specify the process name of the target application
process_name = "mupen64plus"

# Find the process by name
process = None
for p in psutil.process_iter(['pid', 'name']):
    if p.info['name'] == process_name:
        process = psutil.Process(p.info['pid'])
        break

if process is None:
    print(f"No process found with the name '{process_name}'.")
    exit(1)

# pid of process
pid = process.pid
print(process_name + " process has pid of: " + str(pid))


# # Specify the address you want to read from
# # 0x1644D0: Current progress
# # 0x0F6BBC: Velocity
# # 0x0F69A4: X Position
# # 0x0F69AC: Y Position
# # 0xF69A8: Z Position
# # bb4fb900
# address = 0x80339E3C

# fd = open(f"/proc/{pid}/mem", "rb")
# fd.seek(address)
# value = fd.read(4) # read an int32
# print(int.from_bytes(value, byteorder='little'))


maps_file = open("/proc/%s/maps" % pid, 'r')
mem_file = open("/proc/%s/mem" % pid, 'r')
for line in maps_file.readlines():  # for each mapped region
    m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', line)
    if m.group(3) == 'r':  # if this is a readable region
        start = int(m.group(1), 16)
        end = int(m.group(2), 16)
        mem_file.seek(start)  # seek to region start
        chunk = mem_file.read(end - start)  # read region contents
        #print chunk,  # dump contents to standard output
        mem_dump = open(pid+".bin", "wb")
        mem_dump.write(str(chunk,))
        mem_dump.close()
maps_file.close()
mem_file.close()