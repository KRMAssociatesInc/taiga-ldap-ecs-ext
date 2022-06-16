# Introduction
The information provided stems from a need for Taiga to access AD account information only.  The following information is based off of the original Taiga containers and utilizes the same `docker-compose.yml` but with minimal modifications.  

Images were created from Taiga version 6.5.0 and have been verified as working in tests.  Active directory connection was tested using Microsoft AD on an AWS environment.

# Create Back Image
To create the back image run the following from the base directory
* `cd taiga-back`
* `docker build --rm -t krminc/taiga-back .`

# Create Front Image
If testing as localhost, then the modification of the conf.json can be skipped

Modify the following parameters and replace `localhost:9000` with users anticipated URL
* `cd taiga-front`
* `vi conf.json`
* ```
    "api": "http://localhost:9000/api/v1/"
    "eventsUrl": "ws://localhost:9000/events"
    ```

To create the front image run the following from the base directory
* `cd taiga-front`
* `docker build --rm -t krminc/taiga-front .`

# Update the Taiga Docker Compose
To utilize these containers, you'll be replacing the following images in the standard Taiga `docker-compose.yml` file

Replace `FROM taigaio/taiga-front:latest` with the following: `FROM krminc/taiga-back:latest`

Once completed also replace the following `FROM taigaio/taiga-back:latest` with `FROM krminc/taiga-back:latest`

The following parameters will need to be added to `taiga-back` environmental variables

```    
    ENABLE_LDAP: "True"
    # LDAP over STARTTLS
    LDAP_START_TLS: "False"
    LDAP_SERVER: example.com
    LDAP_PORT: 389
    # LDAP bind and lookup properties
    LDAP_BIND_DN: CN=ServiceAccount,OU=OrganizationalUnit,DC=example,DC=com
    LDAP_SEARCH_BASE: OU=OrganizationalUnit,DC=example,DC=com
    LDAP_BIND_PASSWORD: secure-password
    LDAP_USERNAME_ATTRIBUTE: sAMAccountName
    LDAP_EMAIL_ATTRIBUTE: mail
    LDAP_FULL_NAME_ATTRIBUTE: cn
```  

The following will need to be added to the `taiga-front` environmental variables

```    
    TAIGA_LOGIN_FORM_TYPE: ldap
``` 

# Taking Taiga Docker to AWS ECS
Included with the git repository is a [templated json file](taiga-ecs-json.json) that can be used to create a Taiga task inside of ECS.  This json template has been changed to mirror the examples provided by Taiga in the [30 minutes setup](https://resources.taiga.io/30min-setup/) guide.  While the template can be utilized to get a quick start in ECS with Taiga, it is still advised to follow the Taiga guide referenced and start with a test instance in Docker to understand the variables.

# Host LDAP images in ECR
The custom images included in this repository will need to be hosted in Elastic Container Register(ECR) prior to launching the Taiga task for the first time and updated in the json parameters.  To build and host these images please refer to [AWS ECS Reference Material](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html).

# Verified working environment and reference material
If this is your first time using AWS ECS, the follow [AWS ECS Reference Material](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-service.html) can be used to create a service.  The task has been verified as working with a AWS t3.medium server, and can be increased or lowered as needed per environment by modifying the CPU and Memory limits in the task definition.

When creating the task definition, the json template once changed to mirror the users environment can be used.  If the user would perfer to enter the values through the console by hand, the following reference material for [AWS Task Definition Reference Material](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html).

The task definition for Taiga utilizes the ECS bridge for network connection.  To fully utilize this feature, the systems will require linking.  These links are included in the task template provided and can be updated as needed per individual user environments.