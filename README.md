# AWS Security Developer - Assignment

Simple Flask app implementing the three required endpoints for this assignment.

**Prerequisites**
- Python 3.8+
- AWS credentials configured in environment (or via `aws configure`) with permissions for CloudFormation and EC2
- Terraform installed (if you will deploy infra via the included Terraform files)

### AWS Credentials Setup

**Option 1: AWS CLI Configure**
```bash
aws configure
```

**Option 2: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

**Option 3: AWS Profile**
```bash
export AWS_PROFILE="your-profile-name"
```

### Verify AWS Access
```bash
aws sts get-caller-identity
```

## Quick Start

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### Step 2: Deploy Infrastructure

**Option 1: Create Manually**

See **CLOUD_MANUAL_SETUP.md** in this repository, for step-by-step instructions on how to Create AWS infrastructure manually.

**Option 2: Create by Using Terraform (recommended)**

***Terraform Deployment:***
```powershell
cd .\terraform
terraform init
terraform plan -out plan.tfplan
terraform apply "plan.tfplan"
```

### Step 3: Setup (Python app)

**Windows PowerShell:**
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 4: Run the Flask API locally

```powershell
python app.py
```

The API will be available at:
- `http://127.0.0.1:5000` (local)
- `http://192.168.1.10:5000` (network)

---

## APIs

### **GET** `/template/<stack_name>`
- Fetches the CloudFormation template for `stack_name` via Boto3
- If the returned template is YAML, converts it to JSON before returning
- Example:
  ```powershell
  curl http://127.0.0.1:5000/template/your-stack-name
  ```

### **PUT** `/template/convert`
- **IMPORTANT:** This is a PUT request, not GET. You must send a JSON body.
- Body: JSON with a `template` field: either (a) an object, or (b) a string containing YAML or JSON.
- The endpoint parses the template, removes `AWS::EC2::Route` resources that route `0.0.0.0/0` (or `::/0`) to an Internet Gateway, and sets `MapPublicIpOnLaunch` to `false` for `AWS::EC2::Subnet` resources.
- Returns the modified template (JSON object). 
- **Example (PowerShell - CORRECT):**
  ```powershell
  # Create a JSON file with the template
  # Content: { "template": { "AWSTemplateFormatVersion": "2010-09-09", "Resources": { ... } } }
  
  Invoke-RestMethod -Uri http://127.0.0.1:5000/template/convert `
    -Method Put `
    -ContentType 'application/json' `
    -Body (Get-Content -Raw template_payload.json)
  ```
- **Example (curl - CORRECT):**
  ```powershell
  curl -X PUT -H "Content-Type: application/json" `
    -d '{"template": {...}}' `
    http://127.0.0.1:5000/template/convert
  ```
- **Common Error:** Calling without `-Method Put` or `-X PUT` will treat it as GET and fail with "Stack with id convert does not exist"

### **POST** `/changeset`
- Body: JSON `{ "stack_name": "your-stack", "template": { ... }, "parameters": { ... } }` where `template` is a full JSON CloudFormation template.
- The endpoint creates a CloudFormation ChangeSet (type `UPDATE`) and polls until creation completes or fails; it returns `ChangeSetId`, `Status`, and `StatusReason` when available.
- **Important:** Your CloudFormation stack may require parameters. Include them in the request:
  ```json
  {
    "stack_name": "your-stack-name",
    "template": { ... },
    "parameters": {
      "VpcId": "vpc-12345",
      "InternetGatewayId": "igw-12345",
      "PublicCidr": "10.0.1.0/24"
    }
  }
  ```
- Example (PowerShell):
  ```powershell
  Invoke-RestMethod -Uri http://127.0.0.1:5000/changeset -Method Post -ContentType 'application/json' -Body (Get-Content -Raw changeset_payload.json)
  ```

---
## For Detailed Testing with Postman

See **POSTMAN_TESTING.md** in this repository, for step-by-step instructions on how to test all three endpoints using Postman with examples.

---

## Verifying ChangeSet Execution

After creating a ChangeSet via POST, follow these steps to verify and execute it:

### Step 1: Review ChangeSet in AWS Console

1. Go to **AWS Console**
2. Navigate to **CloudFormation**
3. Find your stack: ex- `cyberlence-public-subnet-cfn` (or your stack name)
4. Click the **"Change sets"** tab
5. You should see your newly created ChangeSet
6. Review the changes listed

### Step 2: Expected Changes

The ChangeSet should show these modifications:

**Resource Changes:**
- `CFNPublicSubnet` - **MODIFY** 
  - `MapPublicIpOnLaunch: true` → `MapPublicIpOnLaunch: false`
- `CFNPublicRoute` - **REMOVE** (if present)
  - Removes route to Internet Gateway (0.0.0.0/0 → igw-xxx)

### Step 3: Execute the ChangeSet

1. In the ChangeSet details, click **"Execute"** button on top right side.
2. Confirm when prompted
3. Wait for stack update to complete (2-5 minutes)
4. Stack status should show **UPDATE_COMPLETE**

### Step 4: Verify Subnet is Now Private

After execution, verify the changes:

1. Go to **EC2 Dashboard**
2. Click **"Subnets"** on the left sidebar
3. Find your subnet (tag: `cfn-public-subnet`)
4. Click on it and check:

 **MapPublicIpOnLaunch should be:** `false`
   - Subnet Details → "Auto-assign IPv4" = "No"

**Route Table should have NO route to IGW**
   - Click "Route Table" tab
   - Check routes - should NOT have `0.0.0.0/0 → igw-xxx`
   - Should only have local route: `10.0.0.0/16 → local`

---

## Teardown (Clean Up)

**IMPORTANT**: Always teardown to avoid AWS charges!

To tear down everything managed by Terraform (preferred when you used the included Terraform files):

```powershell
cd .\terraform
terraform destroy -auto-approve
```

This will destroy the VPC, IGW, Terraform-created subnets and the CloudFormation stack that Terraform created. If you created additional resources manually (outside Terraform) you must delete them separately.
