# AWS Deployment Guide for CarbonSaver

This guide will help you deploy CarbonSaver to AWS Free Tier using Elastic Beanstalk.

## Prerequisites

1. **AWS Account**: Create a free account at https://aws.amazon.com/free/
2. **AWS CLI**: Install from https://aws.amazon.com/cli/
3. **EB CLI**: Install Elastic Beanstalk CLI

```bash
pip install awsebcli
```

## Deployment Steps

### 1. Configure AWS Credentials

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`, `eu-west-1`)
- Default output format: `json`

### 2. Initialize Elastic Beanstalk Application

```bash
cd /Users/proost/Coding/CarbonSaver
eb init
```

Follow the prompts:
- Select your region
- Create new application: `CarbonSaver`
- Platform: `Python 3.11` or higher
- Use CodeCommit: `No`
- Setup SSH: `Yes` (optional, for debugging)

### 3. Create Environment and Deploy

```bash
eb create carbonsaver-env
```

This will:
- Create a t2.micro instance (free tier eligible)
- Set up load balancer (optional, can skip for free tier)
- Deploy your application
- Give you a URL like: `carbonsaver-env.eba-xxxxxxxx.us-east-1.elasticbeanstalk.com`

### 4. Deploy Updates

After making changes:

```bash
eb deploy
```

### 5. Open Your Application

```bash
eb open
```

## AWS Free Tier Limits

- **750 hours/month** of t2.micro instances (enough for 24/7 operation)
- **5 GB** of storage
- **15 GB** of bandwidth out
- **1 GB** of bandwidth in

## Monitoring

```bash
# Check application status
eb status

# View logs
eb logs

# SSH into instance (if configured)
eb ssh
```

## Environment Variables (if needed in future)

```bash
eb setenv KEY=value
```

## Cost Optimization Tips

1. **Use Single Instance**: Already configured in `.ebextensions/python.config`
2. **Stop when not in use**:
   ```bash
   eb terminate carbonsaver-env  # Delete environment
   ```
3. **Monitor usage**: Check AWS Billing Dashboard regularly

## Troubleshooting

### Application won't start
```bash
eb logs --all
```

### Check environment health
```bash
eb health --refresh
```

### Rebuild environment
```bash
eb rebuild
```

## Alternative: AWS EC2 Free Tier

If you prefer more control, you can also deploy to EC2:

1. Launch t2.micro instance with Ubuntu
2. Install Python, nginx, and dependencies
3. Use systemd to run the Flask app
4. Configure nginx as reverse proxy

(Detailed EC2 guide available if needed)

## Cleanup

To avoid charges after free tier expires:

```bash
# Terminate environment
eb terminate carbonsaver-env

# Delete application (optional)
# Go to AWS Console > Elastic Beanstalk > Delete application
```

## Security Notes

- The app is currently open to the internet
- Consider adding HTTPS (use AWS Certificate Manager - free)
- For production, add authentication/authorization
- Consider using AWS WAF for protection

## Support

- AWS Free Tier: https://aws.amazon.com/free/
- Elastic Beanstalk Docs: https://docs.aws.amazon.com/elasticbeanstalk/
- AWS Support: https://console.aws.amazon.com/support/
