

for ta in $( cat aws-regions )
do
    securityGroupId=`aws ec2 create-security-group   --region $ta --group-name ssh --description "ssh access" --query 'GroupId' --output text`
    aws ec2 authorize-security-group-ingress  --region $ta --group-name 'ssh' --protocol tcp --port 22 --cidr 0.0.0.0/0

    securityGroupId=`aws ec2 create-security-group  --region $ta --group-name tinc --description "tinc access" --query 'GroupId' --output text`
    aws ec2 authorize-security-group-ingress  --region $ta --group-name 'tinc' --protocol tcp --port 655 --cidr 0.0.0.0/0
    aws ec2 authorize-security-group-ingress  --region $ta --group-name 'tinc' --protocol udp --port 655 --cidr 0.0.0.0/0
done