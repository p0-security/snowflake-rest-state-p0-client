# Python Client for P0 Snowflake Rest State Management

This is a Python client for the P0 Snowflake Rest State Management API. It is a simple wrapper around the API, and is intended to be used to run simple drift detection and remediation.

## Installation

1. Install required packages using

`pip install -r requirements.txt`

## Usage

1. To run example.py, you will need to set the following environment variables in .env file:

   - P0_BASE_URL : https://api.p0.app/o
   - P0_TENANT_ID : The tenant id for the tenant you want to run the check for
   - P0_TOKEN : The api token for the tenant, which can be generated from the P0 web app

2. Run the example file **main**.py file. This will run a check and remediation for the given tenant.

3. You can use the client to run checks and remediation for your tenant by calling the `run_check_and_remediation` function with the appropriate parameters.

```
from p0_client import run_check_and_remediation
import os

run_check_and_remediation(os.environ.get('P0_BASE_URL'),
                                os.environ.get('P0_TENANT_ID'),
                                os.environ.get('P0_TOKEN'))
```
