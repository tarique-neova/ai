import boto3
import json


class IAMUser:
    def create_iam_user(username, s3_permissions):
        iam = boto3.client('iam')

        response = iam.create_user(UserName=username)
        user_arn = response['User']['Arn']

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": s3_permissions,
                    "Resource": "arn:aws:s3:::*"
                }
            ]
        }

        iam.put_user_policy(
            UserName=username,
            PolicyName=f"{username}-s3-policy",
            PolicyDocument=json.dumps(policy_document)
        )

        return user_arn

    def update_user_permissions(username, new_permissions):
        iam = boto3.client('iam')

        try:
            existing_policy_response = iam.get_user_policy(UserName=username, PolicyName=f"{username}-s3-policy")
            existing_policy_document = existing_policy_response['PolicyDocument']

            # Update the permissions in the existing policy document
            existing_policy_document['Statement'][0]['Action'] = new_permissions

            # Update the policy with the new permissions
            iam.put_user_policy(
                UserName=username,
                PolicyName=f"{username}-s3-policy",
                PolicyDocument=json.dumps(existing_policy_document)
            )

            return f"Permissions updated for user {username}. New permissions: {', '.join(new_permissions)}"
        except Exception as e:
            return f"An error occurred: {e}"

    def delete_iam_user(username):
        iam = boto3.client('iam')

        try:
            # Detach all policies
            policies = iam.list_user_policies(UserName=username)['PolicyNames']
            for policy in policies:
                iam.delete_user_policy(UserName=username, PolicyName=policy)

            # Delete the user
            iam.delete_user(UserName=username)
            return f"User {username} deleted successfully."
        except Exception as e:
            return f"An error occurred: {e}"
