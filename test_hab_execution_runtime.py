#!/usr/bin/env python3
"""
Phase 8-6: HAB → Execution Provider Integration Test
Independent HTTP servers for real runtime verification
"""

import http.server
import socketserver
import json
import threading
import time
import requests
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from phi_os.hab.dispatch_handler import HABDispatcher
from runtime.jarvis.core.engine import JarvisEngine

# Global configuration for test endpoint
TEST_HAB_ENDPOINT = "http://127.0.0.1:15003/api/hab/dispatch"

class JarvisHandler(http.server.BaseHTTPRequestHandler):
    """JARVIS intake endpoint"""
    
    def do_POST(self):
        if self.path == '/api/jarvis/task/intake':
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len)
            data = json.loads(body)
            
            # Use real JARVIS engine with test HAB endpoint
            jarvis = JarvisEngine(hab_endpoint=TEST_HAB_ENDPOINT)
            result = jarvis.intake_task(data.get('task_data', {}))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[JARVIS] {self.client_address[0]} - {format % args}")


class HABHandler(http.server.BaseHTTPRequestHandler):
    """HAB dispatch and execution endpoints"""
    
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)
        data = json.loads(body)
        
        dispatcher = HABDispatcher()
        
        if self.path == '/api/hab/dispatch':
            # Phase 8-5 dispatch
            result = dispatcher.dispatch(
                data.get('task_id'),
                data.get('correlation_id'),
                data.get('task_data', {})
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == '/api/hab/execute':
            # Phase 8-6 execute
            result = dispatcher.execute(
                data.get('task_id'),
                data.get('correlation_id'),
                data.get('hab_request_id'),
                data.get('task_data', {}),
                data.get('provider', 'local')
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        if '/api/hab/execution/status/' in self.path:
            execution_id = self.path.split('/')[-1]
            
            # Read from hab_execution.jsonl
            log_path = Path(__file__).parent / 'data' / 'hab_execution.jsonl'
            if not log_path.exists():
                self.send_response(404)
                self.end_headers()
                return
            
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    record = json.loads(line)
                    if record.get('execution_id') == execution_id:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(record).encode())
                        return
            
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[HAB] {self.client_address[0]} - {format % args}")


class ReuseTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run_servers():
    """Start JARVIS and HAB servers"""
    
    jarvis_server = ReuseTCPServer(("127.0.0.1", 15002), JarvisHandler)
    jarvis_thread = threading.Thread(target=jarvis_server.serve_forever)
    jarvis_thread.daemon = True
    jarvis_thread.start()
    print("[JARVIS] Server started on port 15002")
    
    hab_server = ReuseTCPServer(("127.0.0.1", 15003), HABHandler)
    hab_thread = threading.Thread(target=hab_server.serve_forever)
    hab_thread.daemon = True
    hab_thread.start()
    print("[HAB] Server started on port 15003")
    
    return jarvis_server, hab_server


def test_phase_8_6():
    """Execute one real task through HAB → LocalProvider pipeline"""
    
    print("\n" + "="*70)
    print("PHASE 8-6: HAB → Execution Provider Integration Test")
    print("="*70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # STEP 1: Human → JARVIS task intake
    print("\n[STEP 1] Human → JARVIS: Task intake")
    task_payload = {
        "task_data": {
            "description": "Phase 8-6 execution test: Simple text processing task",
            "type": "test_execution",
            "priority": "low"
        }
    }
    
    try:
        r = requests.post("http://127.0.0.1:15002/api/jarvis/task/intake", json=task_payload, timeout=5)
        print(f"  HTTP Status: {r.status_code}")
        if r.status_code != 200:
            print(f"  ERROR: {r.text}")
            return
        
        intake_result = r.json()
        task_id = intake_result.get('task_id')
        correlation_id = intake_result.get('correlation_id')
        hab_request_id = intake_result.get('hab_request_id')
        
        print(f"  task_id: {task_id}")
        print(f"  correlation_id: {correlation_id}")
        print(f"  hab_request_id: {hab_request_id}")
        print(f"  Status: {intake_result.get('status')}")
        print(f"  TRACE_EVIDENCE: {correlation_id}→{task_id}→{hab_request_id}")
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        return
    
    # STEP 2: HAB → Execute via LocalProvider (Phase 8-6)
    print("\n[STEP 2] HAB → Provider: Execute (LocalProvider)")
    execute_payload = {
        "task_id": task_id,
        "correlation_id": correlation_id,
        "hab_request_id": hab_request_id,
        "task_data": task_payload["task_data"],
        "provider": "local"
    }
    
    try:
        r = requests.post("http://127.0.0.1:15003/api/hab/execute", json=execute_payload, timeout=10)
        print(f"  HTTP Status: {r.status_code}")
        if r.status_code != 200:
            print(f"  ERROR: {r.text}")
            return
        
        exec_result = r.json()
        execution_id = exec_result.get('execution_id')
        
        print(f"  execution_id: {execution_id}")
        print(f"  provider: {exec_result.get('provider')}")
        print(f"  provider_status: {exec_result.get('provider_status')}")
        print(f"  Result status: {exec_result.get('status')}")
        print(f"  TRACE_CHAIN: {correlation_id}→{task_id}→{hab_request_id}→{execution_id}")
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        return
    
    # STEP 3: Read-back execution result
    print("\n[STEP 3] Read-back: Execution evidence persistence")
    
    time.sleep(0.5)
    
    try:
        url = f"http://127.0.0.1:15003/api/hab/execution/status/{execution_id}"
        r = requests.get(url, timeout=5)
        print(f"  HTTP Status: {r.status_code}")
        if r.status_code != 200:
            print(f"  ERROR: {r.text}")
            return
        
        exec_record = r.json()
        print(f"  execution_id: {exec_record.get('execution_id')}")
        print(f"  task_id: {exec_record.get('task_id')}")
        print(f"  correlation_id: {exec_record.get('correlation_id')}")
        print(f"  hab_request_id: {exec_record.get('hab_request_id')}")
        print(f"  provider: {exec_record.get('provider')}")
        print(f"  Record status: {exec_record.get('status')}")
        
        provider_response = exec_record.get('provider_response', {})
        print(f"  Provider response status: {provider_response.get('status')}")
        print(f"  Provider output: {str(provider_response.get('output', ''))[:80]}")
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        return
    
    # STEP 4: Verify trace linkage
    print("\n[STEP 4] Trace linkage verification")
    print(f"  correlation_id: {correlation_id}")
    print(f"  → task_id: {task_id}")
    print(f"  → hab_request_id: {hab_request_id}")
    print(f"  → execution_id: {execution_id}")
    
    if (exec_record.get('correlation_id') == correlation_id and
        exec_record.get('task_id') == task_id and
        exec_record.get('hab_request_id') == hab_request_id):
        print("  TRACE_LINKAGE: OK")
        trace_ok = True
    else:
        print("  TRACE_LINKAGE: MISMATCH")
        trace_ok = False
    
    # STEP 5: A-F Verification Matrix
    print("\n[STEP 5] A-F Phase 8-6 Verification")
    
    verification_matrix = {
        "A_HAB_RECEIVE": "VERIFIED" if hab_request_id else "UNVERIFIED",
        "B_PROVIDER_DISPATCH": "VERIFIED" if provider_response.get('status') == 'success' else "UNVERIFIED",
        "C_ACTUAL_EXECUTION": "VERIFIED" if provider_response.get('status') == 'success' else "UNVERIFIED",
        "D_EXECUTION_RESPONSE": "VERIFIED" if exec_result.get('status') == 'ok' else "UNVERIFIED",
        "E_EXECUTION_EVIDENCE_PERSISTENCE": "VERIFIED" if r.status_code == 200 else "UNVERIFIED",
        "F_TRACE_LINKAGE": "VERIFIED" if trace_ok else "UNVERIFIED",
    }
    
    for key, value in verification_matrix.items():
        print(f"  {key}: {value}")
    
    # Final status
    all_verified = all(v == "VERIFIED" for v in verification_matrix.values())
    print("\n" + "="*70)
    if all_verified:
        print("PHASE 8-6 = VERIFIED")
        print("All checks passed. Execution pipeline confirmed end-to-end.")
    else:
        print("PHASE 8-6 = UNVERIFIED / BLOCKED")
        print("Some checks failed. See matrix above.")
    print("="*70)
    
    # Output evidence
    print("\nRuntime Evidence:")
    print(f"  Correlation ID (Trace): {correlation_id}")
    print(f"  Task ID: {task_id}")
    print(f"  HAB Request ID: {hab_request_id}")
    print(f"  Execution ID: {execution_id}")
    print(f"  Verification Matrix: {json.dumps(verification_matrix, indent=2)}")
    print(f"  Timestamp: {datetime.now().isoformat()}")


if __name__ == "__main__":
    print("[Phase 8-6 Test] Starting independent HTTP servers...")
    
    jarvis_server, hab_server = run_servers()
    
    try:
        time.sleep(1)
        test_phase_8_6()
    finally:
        jarvis_server.shutdown()
        hab_server.shutdown()
        print("\n[Servers shutdown]")
