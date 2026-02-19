"""
AWS Service Clients Factory
Provides singleton instances of AWS service clients
"""

import boto3
from typing import Optional
from config import AWSConfig
from utils.logger import get_logger

logger = get_logger(__name__)

class AWSClients:
    """
    Singleton factory for AWS service clients
    """
    _bedrock_runtime = None
    _opensearch = None
    _s3 = None
    _secrets_manager = None
    _cloudwatch = None
    _lambda_client = None
    
    @classmethod
    def get_bedrock_runtime(cls):
        """Get Bedrock Runtime client"""
        if cls._bedrock_runtime is None:
            try:
                cls._bedrock_runtime = boto3.client(
                    'bedrock-runtime',
                    region_name=AWSConfig.REGION
                )
                logger.info("Bedrock Runtime client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Bedrock Runtime client: {str(e)}")
                raise
        return cls._bedrock_runtime
    
    @classmethod
    def get_s3(cls):
        """Get S3 client"""
        if cls._s3 is None:
            try:
                cls._s3 = boto3.client(
                    's3',
                    region_name=AWSConfig.REGION
                )
                logger.info("S3 client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {str(e)}")
                raise
        return cls._s3
    
    @classmethod
    def get_secrets_manager(cls):
        """Get Secrets Manager client"""
        if cls._secrets_manager is None:
            try:
                cls._secrets_manager = boto3.client(
                    'secretsmanager',
                    region_name=AWSConfig.REGION
                )
                logger.info("Secrets Manager client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Secrets Manager client: {str(e)}")
                raise
        return cls._secrets_manager
    
    @classmethod
    def get_cloudwatch(cls):
        """Get CloudWatch client"""
        if cls._cloudwatch is None:
            try:
                cls._cloudwatch = boto3.client(
                    'cloudwatch',
                    region_name=AWSConfig.REGION
                )
                logger.info("CloudWatch client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize CloudWatch client: {str(e)}")
                raise
        return cls._cloudwatch
    
    @classmethod
    def get_lambda(cls):
        """Get Lambda client"""
        if cls._lambda_client is None:
            try:
                cls._lambda_client = boto3.client(
                    'lambda',
                    region_name=AWSConfig.REGION
                )
                logger.info("Lambda client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Lambda client: {str(e)}")
                raise
        return cls._lambda_client
    
    @classmethod
    def get_secret(cls, secret_name: str) -> dict:
        """
        Retrieve secret from AWS Secrets Manager
        
        Args:
            secret_name: Name of the secret to retrieve
            
        Returns:
            dict: Secret value as dictionary
        """
        try:
            client = cls.get_secrets_manager()
            response = client.get_secret_value(SecretId=secret_name)
            
            import json
            if 'SecretString' in response:
                return json.loads(response['SecretString'])
            else:
                import base64
                return json.loads(base64.b64decode(response['SecretBinary']))
                
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}': {str(e)}")
            raise

def get_aws_clients():
    """Get AWS clients factory instance"""
    return AWSClients()
