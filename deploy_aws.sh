#!/bin/bash
# Quick deployment script for CarbonSaver to AWS Elastic Beanstalk

echo "🌱 CarbonSaver - AWS Deployment Script"
echo "========================================"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "   pip install awscli"
    exit 1
fi

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "❌ Elastic Beanstalk CLI not found. Installing..."
    pip install awsebcli
fi

echo "✓ AWS CLI and EB CLI are installed"
echo ""

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Running 'aws configure'..."
    aws configure
fi

echo "✓ AWS credentials configured"
echo ""

# Initialize EB if not already done
if [ ! -d ".elasticbeanstalk" ]; then
    echo "📦 Initializing Elastic Beanstalk application..."
    eb init -p python-3.11 CarbonSaver --region us-east-1
else
    echo "✓ Elastic Beanstalk already initialized"
fi

echo ""
echo "🚀 Deployment Options:"
echo "1. Create new environment (first time deployment)"
echo "2. Deploy to existing environment"
echo "3. Open application in browser"
echo "4. View logs"
echo "5. Check status"
echo "6. Exit"
echo ""
read -p "Select option (1-6): " option

case $option in
    1)
        echo ""
        read -p "Enter environment name (default: carbonsaver-env): " env_name
        env_name=${env_name:-carbonsaver-env}
        echo "Creating environment: $env_name..."
        eb create $env_name --instance-type t2.micro --single
        echo "✅ Environment created! Opening in browser..."
        eb open
        ;;
    2)
        echo ""
        echo "Deploying to environment..."
        eb deploy
        echo "✅ Deployment complete!"
        ;;
    3)
        echo ""
        eb open
        ;;
    4)
        echo ""
        eb logs
        ;;
    5)
        echo ""
        eb status
        ;;
    6)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "📝 Useful commands:"
echo "  eb deploy          - Deploy changes"
echo "  eb open            - Open app in browser"
echo "  eb logs            - View logs"
echo "  eb status          - Check status"
echo "  eb terminate       - Delete environment"
