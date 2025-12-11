# Postman Testing Guide - CloudFormation Template Conversion API

This guide shows how to test all three API endpoints using Postman.

---

## Prerequisites

1. **Postman installed** - Download from https://www.postman.com/downloads/
2. **Flask API running** - `python app.py`
3. **AWS credentials configured** - For CloudFormation access
4. **Existing CloudFormation stack** - For GET and POST operations

---

## Endpoint 1: GET - Fetch CloudFormation Template

### Steps in Postman

1. Click **New** → **HTTP Request**
2. Set method dropdown to **GET**
3. Paste URL: `http://192.168.1.10:5000/template/cyberlence-public-subnet-cfn`
4. Click **Send**

### Expected Response

```json
{
    "template": {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Conditions": {
            "CreateAssoc": {
                "Fn::And": [
                    {
                        "Fn::Equals": [
                            {
                                "Ref": "SubnetId"
                            },
                            ""
                        ]
                    },
                    {
                        "Fn::Equals": [
                            {
                                "Ref": "RouteTableId"
                            },
                            ""
                        ]
                    }
                ]
            },
            "CreateRoute": {
                "Fn::Equals": [
                    {
                        "Ref": "RouteTableId"
                    },
                    ""
                ]
            },
            "CreateSubnet": {
                "Fn::Equals": [
                    {
                        "Ref": "SubnetId"
                    },
                    ""
                ]
            },
            "UseProvidedRouteTable": {
                "Fn::Not": [
                    {
                        "Fn::Equals": [
                            {
                                "Ref": "RouteTableId"
                            },
                            ""
                        ]
                    }
                ]
            }
        },
        "Description": "CloudFormation template to create a public subnet and route to an existing Internet Gateway",
        "Outputs": {
            "PublicSubnetId": {
                "Description": "ID of the created public subnet",
                "Value": {
                    "Fn::If": [
                        "CreateSubnet",
                        {
                            "Ref": "CFNPublicSubnet"
                        },
                        {
                            "Ref": "SubnetId"
                        }
                    ]
                }
            }
        },
        "Parameters": {
            "InternetGatewayId": {
                "Description": "ID of an existing Internet Gateway to route traffic to",
                "Type": "String"
            },
            "PublicCidr": {
                "Description": "CIDR block for the public subnet (e.g. 10.0.1.0/24)",
                "Type": "String"
            },
            "RouteTableId": {
                "Default": "",
                "Description": "Optional existing Route Table ID to associate the subnet with (leave empty to create a new route table)",
                "Type": "String"
            },
            "SubnetId": {
                "Default": "",
                "Description": "Optional existing Subnet ID to use instead of creating a new subnet",
                "Type": "String"
            },
            "VpcId": {
                "Description": "ID of the VPC in which to create the subnet",
                "Type": "String"
            }
        },
        "Resources": {
            "CFNPublicRoute": {
                "Condition": "CreateRoute",
                "Properties": {
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "GatewayId": {
                        "Ref": "InternetGatewayId"
                    },
                    "RouteTableId": {
                        "Fn::If": [
                            "UseProvidedRouteTable",
                            {
                                "Ref": "RouteTableId"
                            },
                            {
                                "Ref": "CFNPublicRouteTable"
                            }
                        ]
                    }
                },
                "Type": "AWS::EC2::Route"
            },
            "CFNPublicRouteTable": {
                "Properties": {
                    "VpcId": {
                        "Ref": "VpcId"
                    }
                },
                "Type": "AWS::EC2::RouteTable"
            },
            "CFNPublicSubnet": {
                "Condition": "CreateSubnet",
                "Properties": {
                    "CidrBlock": {
                        "Ref": "PublicCidr"
                    },
                    "MapPublicIpOnLaunch": true,
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "cfn-public-subnet"
                        }
                    ],
                    "VpcId": {
                        "Ref": "VpcId"
                    }
                },
                "Type": "AWS::EC2::Subnet"
            },
            "CFNRouteTableAssoc": {
                "Properties": {
                    "RouteTableId": {
                        "Ref": "RouteTableId"
                    },
                    "SubnetId": {
                        "Fn::If": [
                            "CreateSubnet",
                            {
                                "Ref": "CFNPublicSubnet"
                            },
                            {
                                "Ref": "SubnetId"
                            }
                        ]
                    }
                },
                "Type": "AWS::EC2::SubnetRouteTableAssociation"
            }
        }
    }
}
```

**Note:** Copy this response - you'll use it for the next endpoint **PUT**!

---

## Endpoint 2: PUT - Convert Public Subnet to Private

### Steps in Postman

1. Click **New** → **HTTP Request**
2. Set method dropdown to **PUT**
3. Paste URL: `http://192.168.1.10:5000/template/convert`
4. Click **Headers** tab
5. Add header:
   - **Key:** `Content-Type`
   - **Value:** `application/json`
6. Click **Body** tab
7. Select **raw** (radio button)
8. Select **JSON** (dropdown on right)
9. Paste this JSON body that you get in **GET** Method:

```json
<Paste Get Method Output>
```

10. Click **Send**

### Expected Response

```json
{
    "modified_template": {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Conditions": {
            "CreateAssoc": {
                "Fn::And": [
                    {
                        "Fn::Equals": [
                            {
                                "Ref": "SubnetId"
                            },
                            ""
                        ]
                    },
                    {
                        "Fn::Equals": [
                            {
                                "Ref": "RouteTableId"
                            },
                            ""
                        ]
                    }
                ]
            },
            "CreateRoute": {
                "Fn::Equals": [
                    {
                        "Ref": "RouteTableId"
                    },
                    ""
                ]
            },
            "CreateSubnet": {
                "Fn::Equals": [
                    {
                        "Ref": "SubnetId"
                    },
                    ""
                ]
            },
            "UseProvidedRouteTable": {
                "Fn::Not": [
                    {
                        "Fn::Equals": [
                            {
                                "Ref": "RouteTableId"
                            },
                            ""
                        ]
                    }
                ]
            }
        },
        "Description": "CloudFormation template to create a public subnet and route to an existing Internet Gateway",
        "Outputs": {
            "PublicSubnetId": {
                "Description": "ID of the created public subnet",
                "Value": {
                    "Fn::If": [
                        "CreateSubnet",
                        {
                            "Ref": "CFNPublicSubnet"
                        },
                        {
                            "Ref": "SubnetId"
                        }
                    ]
                }
            }
        },
        "Parameters": {
            "InternetGatewayId": {
                "Description": "ID of an existing Internet Gateway to route traffic to",
                "Type": "String"
            },
            "PublicCidr": {
                "Description": "CIDR block for the public subnet (e.g. 10.0.1.0/24)",
                "Type": "String"
            },
            "RouteTableId": {
                "Default": "",
                "Description": "Optional existing Route Table ID to associate the subnet with (leave empty to create a new route table)",
                "Type": "String"
            },
            "SubnetId": {
                "Default": "",
                "Description": "Optional existing Subnet ID to use instead of creating a new subnet",
                "Type": "String"
            },
            "VpcId": {
                "Description": "ID of the VPC in which to create the subnet",
                "Type": "String"
            }
        },
        "Resources": {
            "CFNPublicRoute": {
                "Condition": "CreateRoute",
                "Properties": {
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "GatewayId": {
                        "Ref": "AWS::NoValue"
                    },
                    "RouteTableId": {
                        "Fn::If": [
                            "UseProvidedRouteTable",
                            {
                                "Ref": "RouteTableId"
                            },
                            {
                                "Ref": "CFNPublicRouteTable"
                            }
                        ]
                    }
                },
                "Type": "AWS::EC2::Route"
            },
            "CFNPublicRouteTable": {
                "Properties": {
                    "VpcId": {
                        "Ref": "VpcId"
                    }
                },
                "Type": "AWS::EC2::RouteTable"
            },
            "CFNPublicSubnet": {
                "Condition": "CreateSubnet",
                "Properties": {
                    "CidrBlock": {
                        "Ref": "PublicCidr"
                    },
                    "MapPublicIpOnLaunch": false,
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "cfn-public-subnet"
                        }
                    ],
                    "VpcId": {
                        "Ref": "VpcId"
                    }
                },
                "Type": "AWS::EC2::Subnet"
            }
        }
    }
}
```

**Changes Made:**
- `MapPublicIpOnLaunch` changed from `true` → `false`
- `PublicRoute` resource removed (no IGW route)

**Note:** Copy this `modified_template` object - you'll use it for the next endpoint **POST**!

---

## Endpoint 3: POST - Create CloudFormation ChangeSet

### Steps in Postman

1. Click **New** → **HTTP Request**
2. Set method dropdown to **POST**
3. Paste URL: `http://192.168.1.10:5000/changeset`
4. Click **Headers** tab
5. Add header:
   - **Key:** `Content-Type`
   - **Value:** `application/json`
6. Click **Body** tab
7. Select **raw** (radio button)
8. Select **JSON** (dropdown on right)
9. Paste this JSON body that you get in PUT Method and do this Changes:

```json
<Paste PUT Method Output>
```

## Required: Add Stack Parameters

Your CloudFormation stack ***REQUIRES*** these,stack name, parameters. Add them to every POST request:

```json
{
    "stack_name": "cyberlence-public-subnet-cfn",
    "template": { ... },
    "parameters": {
      "InternetGatewayId": "igw-12345",
      "PublicCidr": "10.0.2.0/24",
      "RouteTableId": "rtb-12345",
      "VpcId": "vpc-12345"
     }
}
```

**Important:** Replace these values with your actual AWS resources:
- `cyberlence-public-subnet-cfn` → your stack name
- `vpc-12345` → your actual VPC ID (from AWS Console)
- `igw-12345` → your Internet Gateway ID (from AWS Console)
- `rtb-12345` → your actual Route Table ID (from AWS Console)
- `10.0.2.0/24` → your subnet CIDR block

10. Click **Send**

### Expected Response

```json
{
  "ChangeSetId": "arn:aws:cloudformation:us-east-1:061051259785:changeSet/cs-1765485877-dfb2d7/97711896-1859-41cd-b961-f6119568865f",
  "Status": "CREATE_COMPLETE",
  "StatusReason": null
}
```

**Success Indicators:**
- `Status` is `CREATE_COMPLETE`
- `ChangeSetId` is provided (long AWS ARN)
- No error message

---

## Complete Workflow Summary

### Step-by-Step

1. **GET** template from CloudFormation
   - Copy the response template

2. **PUT** template through conversion endpoint
   - Paste the GET response
   - Receive modified template
   - Copy the modified template

3. **POST** modified template to create ChangeSet
   - Paste the modified template
   - Provide your stack name
   - ChangeSet is created!

4. **Execute in AWS Console**
   - Go to CloudFormation → Stacks
   - Click your stack
   - Click "Change sets" tab
   - Click "Execute" to apply changes

---
**Questions?** Check the main README.md for more details in this repository.