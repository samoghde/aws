# AWS Lambda: Start/Stop EC2 Instances by Key Pair

This project contains a Python AWS Lambda function that create&start or stop&delete EC2 instances based on their associated key pair name.

## 🛠️ Setup

1. Create an IAM role with the permissions in `iam-policy.json`.
2. Deploy `lambda_function.py` to AWS Lambda.
3. Use `event.json` to test the function manually or trigger it via EventBridge.

## 🧪 Testing

You can test the function using the AWS Lambda console or CLI:

```bash
aws lambda invoke \
  --function-name ec2-control-lambda \
  --payload file://event.json \
  output.json
