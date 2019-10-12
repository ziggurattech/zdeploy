# zdeploy
<b>zdeploy</b> is ZigguratTech's official deployment utility. We're currently using the tool to deploy the entire [ZGPS.live](https://zgps.live) stack.

zdeploy works off two core concepts ('recipes' and 'configs'). Recipes are modularized installation/migration procedures, and configs are source files with environment variables specifying where each recipe chain is to be deployed.

Install the tool using the following command, and let's get down to business with a real-world deployment example.

```
$ pip3 install https://github.com/ziggurattech/zdeploy
```

Imagine wanting to deploy a Postgres Docker instance via docker-compose. We're going to start by specifying out recipe internals first.
