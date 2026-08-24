#!/usr/bin/env python3
"""
Backend API tests for Kelvaros map application.
Tests the bug fix: nation_shapes must return exact province unions (no buffer/smoothing)
so borders and fills use identical geometry.
"""
import requests
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://dynasty-mapper-1.preview.emergentagent.com"

class KelvarosAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.issues = []

    def log(self, msg, level="INFO"):
        prefix = "✅" if level == "PASS" else "❌" if level == "FAIL" else "🔍"
        print(f"{prefix} {msg}")

    def test_api(self, name, endpoint, expected_status=200, method="GET", data=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        self.tests_run += 1
        self.log(f"Testing {name}...", "INFO")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if response.status_code == expected_status:
                self.tests_passed += 1
                self.log(f"PASS - {name} (status {response.status_code})", "PASS")
                return True, response.json() if response.content else {}
            else:
                self.log(f"FAIL - {name}: Expected {expected_status}, got {response.status_code}", "FAIL")
                self.issues.append(f"{name}: status {response.status_code} (expected {expected_status})")
                return False, {}

        except requests.exceptions.Timeout:
            self.log(f"FAIL - {name}: Request timeout", "FAIL")
            self.issues.append(f"{name}: timeout")
            return False, {}
        except Exception as e:
            self.log(f"FAIL - {name}: {str(e)}", "FAIL")
            self.issues.append(f"{name}: {str(e)}")
            return False, {}

    def run_all_tests(self):
        """Run all backend API tests"""
        print("\n" + "="*70)
        print("KELVAROS MAP API TESTS - Border Bug Fix Verification")
        print("="*70 + "\n")

        # Test 1: Root endpoint
        success, data = self.test_api("Root endpoint", "")
        if success:
            print(f"   Continent: {data.get('continent', 'N/A')}")
            print(f"   Year: {data.get('year', 'N/A')}")

        # Test 2: Map state endpoint (CRITICAL for bug fix)
        success, data = self.test_api("Map state endpoint", "map/state")
        if success:
            nations = data.get('nations', [])
            provinces = data.get('provinces', [])
            settlements = data.get('settlements', [])
            nation_shapes = data.get('nation_shapes', {})
            
            print(f"   Nations: {len(nations)}")
            print(f"   Provinces: {len(provinces)}")
            print(f"   Settlements: {len(settlements)}")
            print(f"   Nation shapes: {len(nation_shapes)}")

            # CRITICAL CHECK: Verify nation_shapes count
            if len(nations) == 118:
                self.log(f"Nations count correct: 118", "PASS")
                self.tests_passed += 1
            else:
                self.log(f"Nations count incorrect: {len(nations)} (expected 118)", "FAIL")
                self.issues.append(f"Nations count: {len(nations)} (expected 118)")
            self.tests_run += 1

            if len(provinces) == 1489:
                self.log(f"Provinces count correct: 1489", "PASS")
                self.tests_passed += 1
            else:
                self.log(f"Provinces count incorrect: {len(provinces)} (expected 1489)", "FAIL")
                self.issues.append(f"Provinces count: {len(provinces)} (expected 1489)")
            self.tests_run += 1

            # CRITICAL CHECK: nation_shapes must have entries for all nations
            if len(nation_shapes) == len(nations):
                self.log(f"Nation shapes count matches nations: {len(nation_shapes)}", "PASS")
                self.tests_passed += 1
            else:
                self.log(f"Nation shapes count mismatch: {len(nation_shapes)} shapes for {len(nations)} nations", "FAIL")
                self.issues.append(f"Nation shapes: {len(nation_shapes)} (expected {len(nations)})")
            self.tests_run += 1

            # Check that nation_shapes are not empty arrays
            empty_shapes = 0
            for nation in nations:
                nid = nation['id']
                shape = nation_shapes.get(nid, [])
                if not shape or len(shape) == 0:
                    empty_shapes += 1
            
            if empty_shapes == 0:
                self.log(f"All nation shapes have geometry", "PASS")
                self.tests_passed += 1
            else:
                self.log(f"Found {empty_shapes} nations with empty shapes", "FAIL")
                self.issues.append(f"{empty_shapes} nations have empty shapes")
            self.tests_run += 1

            # CRITICAL CHECK: Count interior holes across all nation_shapes
            # Bug fix should result in very few holes (a handful, not hundreds)
            total_holes = 0
            for nation in nations:
                nid = nation['id']
                shape = nation_shapes.get(nid, [])
                # Each shape is a list of polygons: [[[exterior], [hole1], [hole2], ...], ...]
                for polygon in shape:
                    if len(polygon) > 1:  # Has interior rings (holes)
                        total_holes += len(polygon) - 1  # -1 for exterior ring
            
            print(f"   Total interior holes across all nations: {total_holes}")
            if total_holes < 50:  # "a handful, not hundreds"
                self.log(f"Interior holes count is low: {total_holes} (good - bug fixed)", "PASS")
                self.tests_passed += 1
            else:
                self.log(f"Interior holes count is high: {total_holes} (may indicate bug)", "FAIL")
                self.issues.append(f"Interior holes: {total_holes} (expected < 50)")
            self.tests_run += 1

        # Test 3: Get a specific nation
        if success and len(nations) > 0:
            test_nation_id = nations[0]['id']
            success, nation_data = self.test_api(
                f"Get nation {test_nation_id}", 
                f"nation/{test_nation_id}"
            )
            if success:
                print(f"   Nation name: {nation_data.get('nation', {}).get('name', 'N/A')}")
                print(f"   Provinces: {len(nation_data.get('provinces', []))}")
                print(f"   Settlements: {len(nation_data.get('settlements', []))}")

        # Test 4: Get a specific settlement
        if success and len(settlements) > 0:
            test_settlement_id = settlements[0]['id']
            success, settlement_data = self.test_api(
                f"Get settlement {test_settlement_id}",
                f"settlement/{test_settlement_id}"
            )
            if success:
                print(f"   Settlement name: {settlement_data.get('settlement', {}).get('name', 'N/A')}")
                print(f"   Type: {settlement_data.get('settlement', {}).get('type', 'N/A')}")

        # Test 5: Trace overrides endpoint
        self.test_api("List trace overrides", "trace/overrides")

        # Print summary
        print("\n" + "="*70)
        print(f"TESTS SUMMARY: {self.tests_passed}/{self.tests_run} passed")
        print("="*70)
        
        if self.issues:
            print("\n❌ ISSUES FOUND:")
            for issue in self.issues:
                print(f"   - {issue}")
            return 1
        else:
            print("\n✅ ALL TESTS PASSED!")
            return 0

def main():
    tester = KelvarosAPITester(BACKEND_URL)
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
