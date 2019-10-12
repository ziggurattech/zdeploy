# zdeploy
<b>zdeploy</b> is ZigguratTech's official deployment utility. We're currently using the tool to deploy the entire [ZGPS.live](https://zgps.live) stack.

zdeploy works off two core concepts ('recipes' and 'configs'). Recipes are modularized installation/migration procedures, and configs are source files with environment variables specifying where each recipe chain is to be deployed.

Install the tool using the following command, and let's get down to business with a real-world deployment example.

```
$ pip3 install https://github.com/ziggurattech/zdeploy
```

Imagine wanting to deploy a Postgres Docker instance via docker-compose. You'd start by writing a recipe directory as follows:

1. Create a directory and name it `recipes/`.
2. Now create a recipe directory under `recipes/`, and name it whatever you want. In our case, we're going to call it `postgres`.
3. Create a file under `recipes/postgres/` and name it `run`. This is going to be tne entry point to your recipe. This file will essentlly be a program written in your favorite programming/scripting language. We're going to write our script in `Bash` here.
> Copy and paste the following snippet into your `run` file:
```
set -e # This allows the script to bail at the first error it encounters
```

4. TBD
