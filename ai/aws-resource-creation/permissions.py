class MapPermissions:
    def map_s3_permissions(permission_desc):
        # Map natural language descriptions to S3 permissions
        if 'least privileged' in permission_desc:
            return ['s3:ListBucket', 's3:GetObject']
        elif 'read' in permission_desc:
            return ['s3:GetObject']
        elif 'write' in permission_desc:
            return ['s3:PutObject']
        elif 'none' in permission_desc:
            return []
        else:
            return []