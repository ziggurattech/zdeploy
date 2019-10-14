# zdeploy
[zdeploy](https://github.com/ziggurattech/zdeploy) is ZigguratTech's official deployment utility. We're currently using the tool to deploy the entire [ZGPS.live](https://zgps.live) stack.

Imagine wanting to deploy a Postgres Docker instance via docker-compose. If you're going to do this manually, you'd normally install Docker first, then docker-compose, and then deploy your desired Postgres instance. If you're using a Bash script for the task, you probably have the entire procedure stored in a single script. This is fine until you find out you need to deploy other things like a Redis instance for example. You're now either obligated to append to that one script you've maintained, or <b>if you like to keep it clean</b>, you'd probably consider splitting the Docker to docker-compose to Postgres script into three separate scripts and run then consecutivly once for the Postgres instance and once again for Redis (because hey, how does your script know Docker and docker-compose are already present on the host before attempting to deploy Redis). You have it all sorted out, and then you find out not only do you have to deploy the two instances on two different hosts, but you also have deploy a single config file to a third hosts where the access info and login credentials of both the Postgres instance and the Redis instance. You see how maintaining the legacy behavior becomes more painful over time, and now you get the point.

<b>So how does zdeploy solve the problem?</b>

zdeploy utilizes two core concepts (`Recipes` and `Configs`).

`Recipes` are modularized prodecures you can use to define the bits and pieces of your deployment process. Recipes tend to have a nature of dependency (A needing B, and B needing C). zdeploy uses a hashing mechanism to weed out duplication (A needing B and C, and both A and C needing X) to ensure deployments are always done the fastest way possible.

`Configs` are envirounment variable files that define where recipes are executed.

use the following command to install zdeploy, and let's get down to business with a real-world deployment example.

```
$ pip3 install https://github.com/ziggurattech/zdeploy
```


## Author
[Fadi Hanna Al-Kass](https://github.com/alkass)
