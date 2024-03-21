# Instagram Python API

Automating login and actions on Instagram
   

## 1 Installation - Packages

Make sure Python is installed on your machine to run the command below:

```bash
$ pip install -r requirements.txt
```

## 1.1 Installation - Main Files Configurations

Production: [`.env`](.env)

Development: [`.env.development`](.env.development)


## 2 Datatabase - Installation MongoDB

In this project, the MongoDB database was used.

- Install [MongoDB](https://docs.mongodb.com/):

## 2.1 Datatabase - Replica Set MongoDB

Prisma requires that you have mongodb database replication for your NestJs application. Then proceed as follows, before start your project:

- **2.1.1** Edit Config:

  Linux: [`/etc/mongod.conf`](/etc/mongod.conf)

  Windows: [`C:\Program Files\MongoDB\Server\7.0\bin\mongod.cfg`]()

- **2.1.2** Uncomment and add the following line, pay attention to Python-like indentation:

```python
replication:
  replSetName: rs0 # Replace with a meaningful name for your replica set
```

- **2.1.3** Restart the mongod service

- **2.1.4** Environment variable

  Windows, Only:

  - Create an environment variable below if there is non as below, then restart your shell:

  ```bash
    $  setx PATH "%PATH%;C:\Program Files\MongoDB\Server\7.0\bin"
  ```

- **2.1.5** Open mongosh

  - Windows, Install [mongosh](https://www.mongodb.com/docs/mongodb-shell/) and run:

  ```bash
  $ mongosh
  ```

  - Linux, run:

  ```bash
  $ mongosh --port 26018 -u topSmm -p --authenticationDatabase topsmm #example of accessing a port other than the default 27017
  ```

- **2.1.6** Run inside the mongosh shell:

  ```bash
    > use admin;
    > rs.initiate();
    > exit();  #If everything is ok, leave
  ```

- **2.1.7** FAILS, ONLY:

  ONLY if rs.initiate() fails:

  ```bash
    > rs.initiate(
   {
      _id: "rs0",
      members: [
         { _id: 1, host : "localhost:26018" },
         { _id: 1, host : "localhost:26028" },
         { _id: 1, host : "localhost:26038" },
      ]
   } )
  ```

  ONLY, if the stick continues:

  ```bash
    > rs.add({host: "localhost:26018", priority: 0, votes: 0})
  ```

  ONLY and if it still fails, try using the **rs.status()** or **rs.config()** commands to obtain information about the replica members with their hosts. ports and their ids. With this information, try to fix it using an example below:

  ```bash
   > rs.reconfig(
    {
      _id: "rs0",
      members: [
        { _id: 0, host: "localhost:27017" },
        { _id: 1, host: "localhost:26018" },
        { _id: 2, host: "localhost:26028" },
        { _id: 3, host: "localhost:26038" }
      ]
    },{force:true})
  ```

  To avoid failure, try not to repeat hosts with a port for the same \_id, so you avoid making a mistake right at the beginning, otherwise you will have to keep adjusting. Always consult rs.status(), if it is not working, you may have to return to the default settings in `/etc/mongod.conf` , such as port 27017.

- **2.1.8** Go back to the system bash, and add new members to the replica set:

  - Linux:

  ```bash
  $ mongod --replSet rs0 --port 26028 --dbpath /var/www/mongod/db0
  $ mongod --replSet rs0 --port 26038 --dbpath /var/www/mongod/db1
  ```

  - Windows:

  ```bash
  $ mongod --port 27027 --replSet rs0 --dbpath="C:\data\db1"
  $ mongod --port 27037 --replSet rs0 --dbpath="C:\data\db2"
  ```

- **2.1.9** Add 2 instances to replica set using rs.add() within mongosh (see 2.1.5):

  ```bash
    > rs.add( { host: "127.0.0.1:27027", priority: 0, votes: 0 } )
    > rs.add( { host: "127.0.0.1:27037", priority: 0, votes: 0 } )
  ```

- **2.1.10** Check replica set status no mongosh

  ```bash
  > rs.status();
  > exit(); #If everything is ok, leave
  ```

## 3 Action Routes

[`app/common/routes/config`](app/common/routes/config)


## 4. Running the app

```bash
# start
$ python main.py

```



## Developer

- Author - [David Rodma](https://github.com/davidrodma/)

