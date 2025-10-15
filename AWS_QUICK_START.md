# AWS Deployment - Quick Reference

## Initial Setup (One-time)

```bash
# 1. Install AWS CLI
pip install awscli awsebcli

# 2. Configure AWS credentials
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Format (json)

# 3. Initialize EB
cd /Users/proost/Coding/CarbonSaver
eb init -p python-3.11 CarbonSaver --region us-east-1

# 4. Create environment
eb create carbonsaver-env --instance-type t2.micro --single
```

## Daily Commands

```bash
# Deploy changes
eb deploy

# Open app in browser
eb open

# View logs
eb logs

# Check status
eb status

# SSH into instance (if configured)
eb ssh
```

## Your App URL
After deployment, your app will be at:
`http://carbonsaver-env.<region>.elasticbeanstalk.com`

Example: `http://carbonsaver-env.us-east-1.elasticbeanstalk.com`

## Free Tier Limits
✅ 750 hours/month t2.micro (24/7 for 31 days)
✅ 5 GB storage
✅ 15 GB bandwidth out

## Cost: $0/month (within free tier)

## Troubleshooting

```bash
# View detailed logs
eb logs --all

# Rebuild environment
eb rebuild

# Terminate and start fresh
eb terminate carbonsaver-env
eb create carbonsaver-env --instance-type t2.micro --single
```

## Stop/Start to Save Costs

```bash
# Terminate (can recreate anytime)
eb terminate carbonsaver-env

# Recreate when needed
eb create carbonsaver-env --instance-type t2.micro --single
```

## Alternative: Using the Script

```bash
./deploy_aws.sh
# Then select option 1 for first deployment
# Or option 2 for updates
```
