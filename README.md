<p align="center">
  <img src="assets/img/icon4.png" alt="Icon">
</p>

# Zdeploy
[zdeploy](https://github.com/ziggurattech/zdeploy) is [ZigguratTech](http://ziggurat.tech)'s official deployment utility. We are currently using the tool to deploy the entire [ZGPS.live](https://zgps.live) stack.

Imagine wanting to deploy a [Postgres](https://www.postgresql.org) [Docker](https://www.docker.com) instance via [docker-compose](https://docs.docker.com/compose). If you are going to do this manually, you would normally install Docker first, then docker-compose, and then deploy your desired Postgres instance. If you are using a Bash script for the task, you probably have the entire procedure laid out in a single script. This is fine until you find out you need to deploy other things like a Redis instance for example. You are now either obligated to append to that one script you have maintained or <b>if you like to keep it clean</b>, you would consider splitting the Docker to docker-compose to Postgres script into three separate scripts and run them consecutively once for the Postgres instance and once again for Redis (because hey, how would your script know Docker and docker-compose are already present on the host before attempting to deploy Redis?). You have it all sorted out, and then you find out that not only do you have to deploy the two instances on different hosts, but you also deploy a single config file to a third host with the access info and login credentials of the two instances. You see how maintaining the legacy behavior becomes more painful over time, and now you get the point.

<b>So how does Zdeploy solve the problem?</b>

Zdeploy utilizes two core concepts (`Recipes` and `Configs`).

`Recipes` are modularized procedures you can use to define the bits and pieces of your deployment process. Recipes tend to have a nature of dependency (A needing B, and B needing C). Zdeploy uses a hashing mechanism to weed out duplication (A needing B and C, and both A and C needing X) to ensure deployments are always done the fastest way possible.

`Configs` are environment variable files that define <b>where</b> recipes are executed.

Use the following command to install Zdeploy, and let us get down to business with a real-world deployment example.

```
$ pip3 install git+https://github.com/ziggurattech/zdeploy
```

Configuration directory structure:
```
Project Directory
├─ config.json
├─ configs directory
├─ Recipes directory
|  ├─ Recipe 1
|  |   ├─ `run` script
|  |   └─ `require` script
|  ├─ Recipe 2
|  |   ├─ `run` script
|  |   └─ `require` script
|  ├─ Recipe N
|  |   ├─ `run` script
|  |   └─ `require` script
```

> Project directory title, config file names, and recipe names are arbitrary.

> `config.json` is an <b>optional</b> config file used to modify the defaults. Some of the command-line argument defaults can be overwritten there too.

> `run` serves as the entry point to every recipe.

> `require` is a dependency file. The content of this file can be (1) other recipes, (2) system packages, or a combination of both. This file is cached to allow Zdeploy to eliminate duplication across hosts. More on that in a bit.

We will explore a premade sample to understand how all the parts fit together. Check out the [sample-zdeploy](https://github.com/ziggurattech/sample-zdeploy) repository (e.g. `git clone https://github.com/ziggurattech/sample-zdeploy`) and follow along.


In sample-zdeploy we have three recipes (`fail2ban`, `docker`, and `redis`). All of these recipes are written in Bash, though they need not be. Your scripting options so unlimited you can even use your own domain-specific language!

The `require` file in `docker` and `redis` defines their prerequisites. These prerequisites can be other recipes and/or system packages. You'll notice that we have `curl`,  `gnupg2`, `software-properties-common`, `ca-certificates`, and `lsb-release` in the `docker` recipe directory and `docker` in the `redis` recipe directory. The aforementioned list of packages will be installed using a default installer (this can be changed in `config.json` or via a CLI argument), because their names do not refer to actual recipe directory titles under our `recipes` directory, while the `docker` prerequisite refers to our `docker` recipe because we do have a directory with that title.

The `dev.zgps.live` configuration file we have under the `configs` directory satisfies our 'where' constraints. We have packages, and this is the file that lets Zdeploy know where to deploy them and in what order:


```
export RECIPES=(FAIL2BAN REDIS)

export FAIL2BAN=track.zgps.live
export REDIS=track.zgps.live
```

`RECIPES` is a special environment variable that takes a list of package names (all in upper-case) and deploys them in the order they are provided. We then define our host URLs/IPs by exporting them as environment variables as shown above.

In this case, if we run `zdeploy -c dev.zgps.live` while at the project root directory, our `fail2ban` recipe will deploy first, then the `docker` recipe (because it's a prerequisite of `redis` which is defined next in `configs/dev.zgps.live`), then `redis` deploys last. The output will confirm this behavior.

## config.json
`config.json` allows you to overwrite the defaults. While the defaults may suit your needs, it is highly recommended to maintain your own defaults in a `config.json` to avoid backward compatibility issues when working with future releases of Zdeploy.

Here is a sample config.json file:

```json
{
	"logs": "artifacts/logs",
	"cache": "artifacts/cache",
	"recipes": "recipes",
	"configs": "configs",
	"force": "yes",
	"installer": "pip install",
}
```

Here is a list of all supported config parameters to date:

| Parameter | Description                                                                                           | Required | Type    | Default            |
|-----------|-------------------------------------------------------------------------------------------------------|----------|---------|--------------------|
| configs   | Host configuration directory path                                                                     | No       | String  | configs            |
| recipes   | Recipes directory path                                                                                | No       | String  | recipes            |
| cache     | Deployment cache directory path                                                                       | No       | String  | cache              |
| logs      | Deployment logs directory path                                                                        | No       | String  | logs               |
| installer | Default installer, used when an unrecognized dependency is found in the `require` file                | No       | String  | apt-get install -y |
| force     | Force entire deployment every time (default is to pick up with a previous failing deployment left off | No       | String  | no                 |
| user      | Default username (used for recipes that don't specify a username, i.e. RECIPE_USER).                  | No       | String  | root               |
| password  | Default password (used in case a private key isn't auto-detected).                                    | No       | String  | None               |
| port      | Default port number (used for recipes that don't specify a port number, i.e. RECIPE_PORT).            | No       | Integer | 22                 |

> NOTE: This table will be updated to always support the most recent release of Zdeploy.

## Development

Install development tools and run lint, type checks, and the test suite:

```bash
pip install -r requirements.txt
pylint zdeploy
pyright zdeploy
pytest
```

## Author
[Fadi Hanna Al-Kass](https://github.com/alkass)
