"""
Logging utility for AI Incident Resolution System
Provides structured logging with CloudWatch integration
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import boto3
from config import AWSConfig, LOG_LEVEL, LOG_FORMAT

# Initialize CloudWatch Logs client
cloudwatch_logs = boto3.client('logs', region_name=AWSConfig.REGION)

class StructuredLogger:
    """
    Structured logger with CloudWatch integration
    """
    
    def __init__(self, name: str, level: str = LOG_LEVEL):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level))
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level))
        formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _log_structured(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Log with structured context"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'context': context or {}
        }
        
        if level == 'INFO':
            self.logger.info(json.dumps(log_entry))
        elif level == 'WARNING':
            self.logger.warning(json.dumps(log_entry))
        elif level == 'ERROR':
            self.logger.error(json.dumps(log_entry))
        elif level == 'DEBUG':
            self.logger.debug(json.dumps(log_entry))
    
    def info(self, message: str, **context):
        """Log info message"""
        self._log_structured('INFO', message, context)
    
    def warning(self, message: str, **context):
        """Log warning message"""
        self._log_structured('WARNING', message, context)
    
    def error(self, message: str, **context):
        """Log error message"""
        self._log_structured('ERROR', message, context)
    
    def debug(self, message: str, **context):
        """Log debug message"""
        self._log_structured('DEBUG', message, context)
    
    def log_metric(self, metric_name: str, value: float, unit: str = 'None', **dimensions):
        """
        Log custom metric to CloudWatch
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: CloudWatch unit (Seconds, Count, etc.)
            dimensions: Additional dimensions for the metric
        """
        try:
            cloudwatch = boto3.client('cloudwatch', region_name=AWSConfig.REGION)
            
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow(),
                'Dimensions': [
                    {'Name': k, 'Value': str(v)} for k, v in dimensions.items()
                ]
            }
            
            cloudwatch.put_metric_data(
                Namespace=AWSConfig.CLOUDWATCH_NAMESPACE,
                MetricData=[metric_data]
            )
            
            self.info(f"Metric logged: {metric_name}", metric=metric_name, value=value)
            
        except Exception as e:
            self.error(f"Failed to log metric: {str(e)}", metric_name=metric_name)
    
    def log_incident_processing(self, incident_id: str, stage: str, duration: float, success: bool):
        """
        Log incident processing metrics
        
        Args:
            incident_id: Incident identifier
            stage: Processing stage (analysis, resolution, etc.)
            duration: Processing duration in seconds
            success: Whether processing was successful
        """
        self.info(
            f"Incident processing: {stage}",
            incident_id=incident_id,
            stage=stage,
            duration_seconds=duration,
            success=success
        )
        
        # Log metric to CloudWatch
        self.log_metric(
            metric_name='ProcessingTime',
            value=duration,
            unit='Seconds',
            Stage=stage,
            Success=str(success)
        )

def get_logger(name: str) -> StructuredLogger:
    """Get or create a structured logger instance"""
    return StructuredLogger(name)
