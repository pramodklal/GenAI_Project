"""
Data Loader for Vector Database
Loads historical incident data into OpenSearch for semantic search
"""

import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
from utils.opensearch_client import get_opensearch_client
from utils.logger import get_logger

logger = get_logger(__name__)

class HistoricalDataLoader:
    """
    Loads historical incidents into vector database
    """
    
    def __init__(self):
        self.opensearch = get_opensearch_client()
        self.logger = logger
    
    def generate_sample_incidents(self, count: int = 1000) -> List[Dict[str, Any]]:
        """
        Generate sample historical incidents for pilot project
        
        Args:
            count: Number of incidents to generate
            
        Returns:
            list: Sample incidents with embeddings
        """
        categories = ['Performance', 'Availability', 'Network', 'Security']
        priorities = [1, 2, 3, 4]
        severities = ['Critical', 'High', 'Medium', 'Low']
        
        # Sample incident templates
        performance_templates = [
            "High CPU usage ({cpu}%) detected on {system}. Response time degraded from {time1}ms to {time2}ms.",
            "Memory leak detected on {system}. Memory usage increased from {mem1}% to {mem2}% over {hours} hours.",
            "Database query performance degradation. Average query time increased from {time1}ms to {time2}ms.",
            "Application thread pool exhausted on {system}. {count} pending requests in queue.",
            "Disk I/O bottleneck on {system}. Read/write latency increased to {latency}ms."
        ]
        
        availability_templates = [
            "{system} service down. Last successful health check {minutes} minutes ago.",
            "Database connection pool exhausted. Max connections ({count}) reached.",
            "Load balancer health check failing for {system}. {count} failed checks in last {minutes} minutes.",
            "Kubernetes pod {system} in CrashLoopBackOff state. Restart count: {count}.",
            "Service {system} returning HTTP 503 errors. Error rate: {percent}%."
        ]
        
        systems = ['web-prod-01', 'app-server-01', 'db-primary', 'cache-cluster', 
                  'api-gateway', 'worker-node-03', 'message-queue', 'auth-service']
        
        incidents = []
        
        for i in range(count):
            category = random.choice(categories)
            priority = random.choice(priorities)
            
            # Select template based on category
            if category == 'Performance':
                template = random.choice(performance_templates)
                description = template.format(
                    cpu=random.randint(85, 99),
                    system=random.choice(systems),
                    time1=random.randint(100, 500),
                    time2=random.randint(1000, 5000),
                    mem1=random.randint(60, 75),
                    mem2=random.randint(85, 99),
                    hours=random.randint(2, 12),
                    count=random.randint(50, 500),
                    latency=random.randint(500, 2000)
                )
            elif category == 'Availability':
                template = random.choice(availability_templates)
                description = template.format(
                    system=random.choice(systems),
                    minutes=random.randint(5, 30),
                    count=random.randint(10, 100),
                    percent=random.randint(50, 95)
                )
            else:
                description = f"{category} issue detected on {random.choice(systems)}"
            
            # Generate deterministic embedding
            import hashlib
            import numpy as np
            hash_obj = hashlib.sha256(description.encode())
            seed = int(hash_obj.hexdigest(), 16) % (2**32)
            np.random.seed(seed)
            embedding = np.random.randn(1536).tolist()
            
            # Generate timestamp (last 90 days)
            timestamp = datetime.utcnow() - timedelta(days=random.randint(1, 90))
            
            # Generate resolution
            resolution_time = random.randint(10, 240)
            resolved_at = timestamp + timedelta(minutes=resolution_time)
            
            resolution_templates = [
                "Restarted service and cleared cache. Issue resolved.",
                "Increased resource limits. CPU threshold adjusted to prevent false alarms.",
                "Fixed memory leak in application code. Deployed patch.",
                "Scaled up instance count. Added 2 additional nodes.",
                "Database index optimization. Query performance restored."
            ]
            
            incident = {
                'incident_id': f'INC{str(i+10000).zfill(7)}',
                'embedding': embedding,
                'description': description,
                'resolution': random.choice(resolution_templates),
                'category': category,
                'priority': priority,
                'severity': severities[priority - 1],
                'affected_systems': [random.choice(systems)],
                'timestamp': timestamp.isoformat(),
                'resolved_at': resolved_at.isoformat(),
                'resolution_time_minutes': resolution_time,
                'symptoms': description,
                'root_cause': f"{category} issue due to resource constraints or configuration"
            }
            
            incidents.append(incident)
        
        return incidents
    
    def load_historical_data(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Load historical incidents into OpenSearch
        
        Args:
            incidents: List of incidents to load
            
        Returns:
            dict: Loading result
        """
        try:
            self.logger.info(f"Starting to load {len(incidents)} incidents")
            
            start_time = time.time()
            
            # Bulk index incidents
            result = self.opensearch.bulk_index_incidents(incidents)
            
            load_time = time.time() - start_time
            
            self.logger.info(f"Data loading completed", 
                           total=result['total'],
                           success=result['success'],
                           failed=result['failed'],
                           load_time=round(load_time, 2))
            
            return {
                'success': True,
                'total_incidents': result['total'],
                'successful': result['success'],
                'failed': result['failed'],
                'load_time_seconds': round(load_time, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Data loading failed: {str(e)}")
            raise
    
    def verify_data_load(self) -> Dict[str, Any]:
        """
        Verify data was loaded successfully
        
        Returns:
            dict: Verification result
        """
        try:
            count = self.opensearch.get_incident_count()
            
            # Test query
            import numpy as np
            test_embedding = np.random.randn(1536).tolist()
            similar = self.opensearch.query_similar_incidents(
                embedding=test_embedding,
                top_k=5
            )
            
            self.logger.info(f"Data verification: {count} incidents indexed, {len(similar)} test results")
            
            return {
                'total_incidents': count,
                'test_query_results': len(similar),
                'status': 'success' if count > 0 else 'failed'
            }
            
        except Exception as e:
            self.logger.error(f"Data verification failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }

def main():
    """Main function to load historical data"""
    print("=" * 60)
    print("Historical Data Loader for AI Incident Resolution")
    print("=" * 60)
    
    loader = HistoricalDataLoader()
    
    # Step 1: Create index
    print("\n1. Creating OpenSearch index...")
    try:
        loader.opensearch.create_index()
        print("✓ Index created successfully")
    except Exception as e:
        print(f"✗ Index creation failed: {e}")
        return
    
    # Step 2: Generate sample data
    print("\n2. Generating 1000 sample historical incidents...")
    incidents = loader.generate_sample_incidents(count=1000)
    print(f"✓ Generated {len(incidents)} incidents")
    
    # Step 3: Load data
    print("\n3. Loading data into OpenSearch...")
    result = loader.load_historical_data(incidents)
    
    if result['success']:
        print(f"✓ Successfully loaded {result['successful']} incidents")
        print(f"  Load time: {result['load_time_seconds']} seconds")
        
        if result['failed'] > 0:
            print(f"  ⚠ {result['failed']} incidents failed to load")
    else:
        print("✗ Data loading failed")
        return
    
    # Step 4: Verify
    print("\n4. Verifying data load...")
    verification = loader.verify_data_load()
    
    if verification['status'] == 'success':
        print(f"✓ Verification successful")
        print(f"  Total incidents: {verification['total_incidents']}")
        print(f"  Test query returned: {verification['test_query_results']} results")
    else:
        print(f"✗ Verification failed: {verification.get('error')}")
    
    print("\n" + "=" * 60)
    print("Data loading completed!")
    print("=" * 60)

if __name__ == '__main__':
    main()
