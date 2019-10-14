# zdeploy
[zdeploy](https://github.com/ziggurattech/zdeploy) is ZigguratTech's official deployment utility. We're currently using the tool to deploy the entire [ZGPS.live](https://zgps.live) stack.

zdeploy utilizes two core concepts (`Recipes` and `Configs`).
`Recipes` are modularized prodecures you can use to define the bits and pieces of your deployment process. Recipes tend to have a nature of dependency (A needing B, and B needing C). zdeploy uses a hashing mechanism to weed out duplication (A needing B and C, and both A and C needing X) to ensure deployments are always done the fastest way possible.
`Configs` are envirounment variable files that define where recipes are executed.

Install the tool using the following command, and let's get down to business with a real-world deployment example.

```
$ pip3 install https://github.com/ziggurattech/zdeploy
```

Imagine wanting to deploy a Postgres Docker instance via docker-compose. We're going to start by specifying out recipe internals first.
