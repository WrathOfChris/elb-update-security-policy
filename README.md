elb-update-security-policy
==========================

ELB Security Policy Update tool

# Install
elb-update-security-policy is available from PyPi and can be installed via pip:

```
pip install elb-update-security-policy
```

# Example

## Update all ELBs postfixed with '-stage'

```
elb-update-security-policy --old ELBSecurityPolicy-2014-10 --new ELBSecurityPolicy-2015-02 '*-stage'
```

# Usage

## elb-update-security-policy

```
usage: elb-update-security-policy [-h] [-a] [-r REGION] --old OLD --new NEW
                        [--regex] ELB [ELB ...]

ELB Update Security Policy

positional arguments:
  ELB                   list of ELBs or regexes to match

optional arguments:
  -h, --help            show this help message and exit
  -a, --auto            auto-detect (default: False)
  -r REGION, --region REGION
                        ec2 region (default: None)
  --old OLD             old security-policy-name (default: None)
  --new NEW             new security-policy-name (default: None)
  --regex               use regex instead of simple match (default: False)
```
