"""
End-to-End Pipeline Test
Tests complete incident resolution workflow (Steps 1-5)
"""

import json
import time
from datetime import datetime
from step3_orchestrator import IncidentOrchestrator
from step4_analyzer import IncidentAnalyzer
from step5_resolution_generator import ResolutionGenerator
from utils.logger import get_logger

logger = get_logger(__name__)

class PipelineTest:
    """
    End-to-end pipeline test for Phase 1 pilot
    """
    
    def __init__(self):
        self.orchestrator = IncidentOrchestrator()
        self.analyzer = IncidentAnalyzer()
        self.generator = ResolutionGenerator()
        self.logger = logger
    
    def create_test_incidents(self) -> list:
        """Create test incidents for validation"""
        return [
            {
                'incident_id': 'INC0012345',
                'priority': 1,
                'category': 'Performance',
                'description': 'High CPU usage (95%) detected on production server web-prod-01. Application response time degraded from 200ms to 2500ms. Memory usage also elevated at 89%.',
                'affected_systems': ['web-prod-01', 'app-server-cluster'],
                'timestamp': '2026-01-08T10:30:00Z',
                'severity': 'Critical',
                'source': 'Dynatrace'
            },
            {
                'incident_id': 'INC0012346',
                'priority': 2,
                'category': 'Availability',
                'description': 'Database connection pool exhausted. Max connections (100) reached. Services returning HTTP 503 errors.',
                'affected_systems': ['db-primary', 'api-gateway'],
                'timestamp': '2026-01-08T11:15:00Z',
                'severity': 'High',
                'source': 'ServiceNow'
            },
            {
                'incident_id': 'INC0012347',
                'priority': 1,
                'category': 'Performance',
                'description': 'Memory leak detected in Java application. Heap usage increased from 60% to 95% over 4 hours. Frequent GC pauses causing timeouts.',
                'affected_systems': ['app-server-01', 'app-server-02'],
                'timestamp': '2026-01-08T12:00:00Z',
                'severity': 'Critical',
                'source': 'Dynatrace'
            }
        ]
    
    def test_single_incident(self, incident: dict) -> dict:
        """
        Test single incident through complete pipeline
        
        Args:
            incident: Test incident data
            
        Returns:
            dict: Test result
        """
        test_start = time.time()
        
        print(f"\n{'='*70}")
        print(f"Testing Incident: {incident['incident_id']}")
        print(f"Category: {incident['category']} | Priority: {incident['priority']}")
        print(f"{'='*70}")
        
        try:
            # Step 3: Orchestration
            print("\n[Step 3] Running Orchestrator...")
            orch_result = self.orchestrator.process_incident(incident)
            
            if orch_result['statusCode'] != 200:
                print(f"✗ Orchestration failed: {orch_result.get('body')}")
                return {'success': False, 'stage': 'orchestration', 'error': orch_result}
            
            orch_data = json.loads(orch_result['body'])
            print(f"✓ Orchestration completed in {orch_data['processing_time_seconds']}s")
            
            # Step 4: Analysis
            print("\n[Step 4] Running Incident Analyzer...")
            context = orch_data['context']
            analysis_result = self.analyzer.analyze_incident(context)
            
            if analysis_result['statusCode'] != 200:
                print(f"✗ Analysis failed: {analysis_result.get('body')}")
                return {'success': False, 'stage': 'analysis', 'error': analysis_result}
            
            analysis_data = json.loads(analysis_result['body'])
            print(f"✓ Analysis completed")
            print(f"  - Incident Type: {analysis_data['analysis']['analysis']['incident_type']}")
            print(f"  - Severity: {analysis_data['analysis']['analysis']['severity_assessment']}")
            print(f"  - Embedding Dimension: {analysis_data['analysis']['embedding_dimension']}")
            
            # Step 5: Resolution Generation
            print("\n[Step 5] Running Resolution Generator...")
            resolution_result = self.generator.generate_resolution(analysis_data['analysis'])
            
            if resolution_result['statusCode'] == 404:
                print("⚠ No similar incidents found in database")
                return {'success': False, 'stage': 'resolution', 'error': 'No similar incidents'}
            
            if resolution_result['statusCode'] != 200:
                print(f"✗ Resolution generation failed: {resolution_result.get('body')}")
                return {'success': False, 'stage': 'resolution', 'error': resolution_result}
            
            resolution_data = json.loads(resolution_result['body'])
            report = resolution_data['report']
            
            print(f"✓ Resolution generated in {resolution_data['processing_time_seconds']}s")
            print(f"\n4-Section Report Generated:")
            print(f"  Section 1: {report['section_1_similar_incidents']['count']} similar incidents found")
            print(f"  Section 2: Root cause - {report['section_2_root_cause']['primary_cause'][:80]}...")
            print(f"  Section 3: {len(report['section_3_resolution_steps']['steps'])} resolution steps")
            print(f"  Section 4: Confidence score - {report['section_4_metadata']['confidence_score']}")
            
            # Calculate total time
            total_time = time.time() - test_start
            
            print(f"\n{'='*70}")
            print(f"✓ INCIDENT PROCESSED SUCCESSFULLY")
            print(f"  Total Pipeline Time: {round(total_time, 2)} seconds")
            print(f"  Target: <3 seconds | Achieved: {'✓' if total_time < 3 else '✗'}")
            print(f"{'='*70}")
            
            return {
                'success': True,
                'incident_id': incident['incident_id'],
                'total_time': round(total_time, 2),
                'meets_target': total_time < 3,
                'report': report
            }
            
        except Exception as e:
            print(f"\n✗ Pipeline test failed: {str(e)}")
            self.logger.error(f"Pipeline test failed for {incident['incident_id']}: {str(e)}")
            return {
                'success': False,
                'incident_id': incident['incident_id'],
                'error': str(e)
            }
    
    def run_test_suite(self):
        """Run complete test suite"""
        print("\n" + "="*70)
        print("AI INCIDENT RESOLUTION SYSTEM - PHASE 1 PILOT")
        print("End-to-End Pipeline Test")
        print("="*70)
        
        incidents = self.create_test_incidents()
        results = []
        
        for incident in incidents:
            result = self.test_single_incident(incident)
            results.append(result)
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUITE SUMMARY")
        print("="*70)
        
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        
        if successful > 0:
            avg_time = sum(r['total_time'] for r in results if r['success']) / successful
            meets_target = sum(1 for r in results if r.get('meets_target', False))
            
            print(f"\nPerformance Metrics:")
            print(f"  Average Processing Time: {round(avg_time, 2)} seconds")
            print(f"  Meets <3s Target: {meets_target}/{successful} ({round(meets_target/successful*100, 1)}%)")
        
        print("\n" + "="*70)
        
        return results

def main():
    """Main test execution"""
    test = PipelineTest()
    results = test.run_test_suite()
    
    # Save results
    with open('pipeline_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\nTest results saved to: pipeline_test_results.json")

if __name__ == '__main__':
    main()
