## AWS ENVIRONMENT SETUP

Before being able to start the project, it is necessary to execute few steps in order to prepare the AWS environment. In
particular, we need to set up the S3 bucket to upload files on it, and the Redshift Cluster to be able to create tables
on it and to import data in those tables as well.

### PERMISSIONS CONFIGURATION

1. #### Creating an AIM USER

   The very first thing we want to do is to create an IAM
   user. [AWS best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#delegate-using-roles)
   suggest the usage of the AWS entity called roles, which are a handful tool in real production scenarios where there
   are many resources, as well as many users and many applications.

   \
   Simply speaking, **we don't want the user to be always in charge of specific permissions**, but **we want the user to
   temporarily "borrow" them when needed**, and only then. This will be clearer later, but for now let's just
   acknowledge that "borrowing" permissions is something that can be done through the association of a specific user
   with a specific **role** (i.e. a named set of permissions) and that this is the reason why we are not attaching any
   direct permission now.

   \
   To create an IAM user, it is possible to
   use [this link](https://console.aws.amazon.com/iam/home?region=eu-central-1#/users$new?step=details)

   \
   For now, we just want to specificy the following configuration:

   ```
   User name: data-engineer
   Access type: Programmatic access
   ```

   \
   AWS Console will remind you that this user has no permissions yet and that it will be useless without any. Don't
   worry, as already explained, this is the expected behaviour for now.

   \
   AWS Console will also provide you with an _Access key ID_, and a _Secret access key_. Note them down or download the
   CSV where they are stored since we'll store them later as environment variables.


2. #### Creating an AWS USER ROLE

   To create a role for an AWS User, you
   can [click here](https://console.aws.amazon.com/iam/home?region=eu-central-1#/roles$new?step=type&roleType=crossAccount)
   . It will ask you the ID associated with you AWS account.

   \
   After that, it will ask you to define a policy. **The policy is the AWS entity which regulates the permissions that a
   role grants.** AWS provides a list of presets, you can just check the `AmazonS3FullAccess` box and go on.

   ```
   Role name: user-s3-full-access 
   ```

   Note down the _Role ARN_ of the just created role, as we will need it in the next step.

   \
   Now that we created an AWS user role, we also have to allow programmatic entities to assume that role. The service in
   AWS that is responsible for this is
   the **[AWS Security Token Service](https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html)** (**STS**), so
   what we have to do now is to create a new policy that allow anyone having the right credentials, to assume
   the `user-s3-full-access` role.

   \
   [Click here](https://console.aws.amazon.com/iam/home?region=eu-central-1#/policies$new) to create a new policy.

   Then select the JSON tab and paste the following JSON:

   ```
   {
      "Version": "2012-10-17",
      "Statement": {
          "Effect": "Allow",
          "Action": "sts:AssumeRole",
          "Resource": "XXXXXXXXX"
      }
   }
   ```

   Instead of `XXXXXXXXX` you have to put the Rone ARN of the role we created and that I previously told you to note
   down.

   ```
   Name: s3-full-access-policy
   ```

   With this policy, we are saying to STS to let a programmatic entity to assume the AWS user role we created. This
   means that the programmatic entity will have the possibility to "borrow" the S3 bucket full-permissions of the role
   we specified. Of course, this programmatic entity can't be generic but must be specified.

   \
   In fact, finally, we get to decide which IAM user this policy may be applied. It can be done, assuming the name of
   our IAM user is `data-engineer` as I previously suggested,
   through [this link](https://console.aws.amazon.com/iam/home?region=eu-central-1#/users/data-engineer$addPermissions?step=permissions&permissionType=policies)
   . Otherwise, it must be searched in
   the [policy management page](https://console.aws.amazon.com/iam/home?region=eu-central-1#/policies).

3. #### Creating an AWS SERVICE ROLE

   A role is not something that can only been associate to AIM users. **Roles can be associated with AWS Services as
   well.** We want to programmatically query Redshift but also we would like Redshift to be able when queried to read
   data from an S3 bucket. To do that, it will need a permission. Similarly to how we did for the AIM user, we will not
   associate to Redshift permantent permissions, but we will grant it a role that will allow to "borrow" the permissions
   it needs only when they are actually needed.

   \
   To create a role for an AWS Service, you
   can [click here](https://console.aws.amazon.com/iam/home?region=eu-central-1#/roles$new?step=type), then select the
   service `Redshift`, and pick the `customizable use case` option. We will have then to associate a policy to this
   role.

   \
   Our Redshift instance will need an `AmazonS3ReadOnlyAccess` policy, so it is the one that we will select from the AWS
   preset list.

   ```
   Role name: redshift-s3-readonly-access
   ```

### S3 BUCKET CREATION

An S3 bucket is a public storage resource and as
such [AWS bucket naming rules](https://docs.aws.amazon.com/AmazonS3/latest/userguide/BucketRestrictions.html) impose the
strict directive that **each bucket in the world must have a unique name**. It can be created
from [this link](https://s3.console.aws.amazon.com/s3/bucket/create?region=eu-central-1).

### VPC CONFIGURATION

**Virtual Private Cloud** (**VPC**) is one of the most important AWS Services, since it allows an easy private networks
creation and management, which is of course something we are interested into, since we want to host a database on
Redshift.

To create a VPC you can
follow [this link](https://eu-central-1.console.aws.amazon.com/vpc/home?region=eu-central-1#CreateVpc:)

```
Name tag: my-vpc 
IPv4 CIDR block: 10.0.0.0/16
```

Now we have to create the rules that determine the behavour of the incoming/outcoming traffic of the VPN we just
created. To do so, we have to create a [**security
group**](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html)

A security group can be
created [from here](https://eu-central-1.console.aws.amazon.com/vpc/home?region=eu-central-1#CreateSecurityGroup:).

```
Security group name: my-security-group 
VPC: my-vpc 
Description: Set of rules that filter traffic coming into and outto the Redshift instance.

Inbound rule:  
   type: Redshift 
   traffic source: 0.0.0.0/0  
 
Add outbound rule:  
   type: Redshift 
   traffic source: 0.0.0.0/0
```

**NOTE:** This setup allows Redshift to be programmatically queried from everywhere. If you have a static IP, or you
only want to query Redshift within another AWS Server, you may want to specific here the definite IP or IP range you
will use.

In productions use case scenarios it also comes handy for security or operations reasons to create multiple subnets and
to decide which subnet has to host which services. In this use case it would be an overkill, so we will just create one.

To create a subnet, [go here](https://eu-central-1.console.aws.amazon.com/vpc/home?region=eu-central-1#CreateSubnet:)
and use the following configuration:

```
VPN: my-vpc 
Subnet name: my-subnet
IPv4 CIDR block: 10.0.0.0/24
```

We have now to specify in which subnet (in our case we don't have that much choice since we just created one) we want
that our Redshift cluster may be hosted.

This can be done through an
AWS [cluster subnet group](https://docs.aws.amazon.com/redshift/latest/mgmt/working-with-cluster-subnet-groups.html). A
cluster subnet group allows to specify a set of subnets to be used by a cluster.

A Redshift cluster subnet group can be
created [from here](https://eu-central-1.console.aws.amazon.com/redshiftv2/home?region=eu-central-1#create-subnet-group)
. Use this configuration:

```
Name: "my-cluster-subnet-group"
Description: "Amazon Redshift will now create the cluster on one of the subnets in the group. Useful to group resources based on your security and operation."
VPN: my-vpn 
```

Then, click on `Add all the subnets for this VPC` (as already said, in our case it will only be one).

In order to manage the Redshift Cluster connections, we need an [**Elastic Network
Interface**](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html),
a [** VPC Internet Gateway**](https://docs.aws.amazon.com/it_it/vpc/latest/userguide/VPC_Internet_Gateway.html) and
a [**VPC Route Table**](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html).

The Elastic Network Interface can be
created [here](https://eu-central-1.console.aws.amazon.com/ec2/v2/home?region=eu-central-1#CreateNetworkInterface).

```
Description: my-network-interface 
Subnet: my-subnet 
Security group: my-security-group
```

The Internet
Gateway, [here](https://eu-central-1.console.aws.amazon.com/vpc/home?region=eu-central-1#CreateInternetGateway:).

```
Name tag: my-internet-gateway
```

Now you have to go to
the [internet Gateways management console](https://eu-central-1.console.aws.amazon.com/vpc/home?region=eu-central-1#igws)
and to attach `my-internet-gateway` to `my-vpc`.

Finally, you
can [create a new route table](https://eu-central-1.console.aws.amazon.com/vpc/home?region=eu-central-1#CreateRouteTable:)

```
Tag name: my-vpc-route-table 
VPC: my-vpc Route
```

Then you have to go
the [Route Table management console](https://eu-central-1.console.aws.amazon.com/vpc/home?region=eu-central-1#RouteTables:sort=routeTableId)
and:

1. Click on the `Routes` tab, then on `Edit route` and finally on `Add route`.

     ```
   Destination: 0.0.0.0/0 
   Target: my-internet-gateway
   ```

2. Click on the `Subnet Associations` tab, then on `Edit subnet associations` and finally check `my-subnet` and `Save`.

### S3 REDSHIFT CREATION

[AWS Redshift](https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html) is a fully managed data warehouse service.

It is a very powerful tool, and a real overkill for the simple use cases like the one we are showing here. In order to
be used, It needs one or more cluster to be created. We can do
so [from here](https://eu-central-1.console.aws.amazon.com/redshiftv2/home?region=eu-central-1#create-cluster).

```
Cluster-identifier: my-redshift-cluster
Free trial configuration: dc2.large | 1 node, 2 vCPU (gen 2) / node x 1 = 2 vCPU, 160 GB x 1 nodes = 160 GB
Database name: dev  
Database port: 5439
Master user name: XXXXXXXX 
Master user password: XXXXXXXX

Cluster permissions: redshift-s3-readonly-access
Additional configurations:
   Network and Security:
      VPC: my-vpn
      VPC security groups: my-security-group
      Cluster subnet group: my-cluster-subnet-group
      Publicly accessible: Enable
```

Note down the values used for `Database name`, `Database port`, `Master user name` and `Master user password`, since
they will be set as environment variables.
 
     

