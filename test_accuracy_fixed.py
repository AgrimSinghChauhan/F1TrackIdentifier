#!/usr/bin/env python3
"""
F1 Circuit Identifier - Comprehensive Accuracy Testing Suite
Target: 99.99% accuracy (0.01% error rate)
"""

import json
import time
import sys
import os
from typing import Dict, List, Tuple, Any
from f1_circuit_bot_core import F1CircuitIdentifier

class AccuracyTester:
    def __init__(self):
        try:
            self.identifier = F1CircuitIdentifier()
            print(f"Loaded {len(self.identifier.circuits)} F1 circuits from database")
        except Exception as e:
            print(f"Failed to initialize: {e}")
            sys.exit(1)
        
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def run_comprehensive_tests(self) -> float:
        """Run all test categories and return overall accuracy"""
        print("\nF1 CIRCUIT IDENTIFIER - COMPREHENSIVE ACCURACY TESTING")
        print("=" * 70)
        print(f"Target Accuracy: 99.99% (Maximum 0.01% error rate)")
        print(f"Database Size: {len(self.identifier.circuits)} circuits")
        print("=" * 70)
        
        # Test categories
        test_categories = [
            ("Exact Country Matches", self.test_exact_country_matches),
            ("Exact Circuit Name Matches", self.test_exact_name_matches),
            ("City/Region Matches", self.test_city_region_matches),
            ("Alias Recognition", self.test_alias_recognition),
            ("Grand Prix Name Matches", self.test_grand_prix_matches),
            ("Multi-Hint Combinations", self.test_multi_hint_combinations),
            ("Partial Name Matching", self.test_partial_name_matching),
            ("Case Insensitive Matching", self.test_case_insensitive),
            ("Edge Cases & Error Handling", self.test_edge_cases),
            ("Confidence Scoring Validation", self.test_confidence_scoring)
        ]
        
        category_results = []
        
        for category_name, test_function in test_categories:
            print(f"\nTesting: {category_name}")
            print("-" * 50)
            
            category_passed, category_total, category_accuracy = test_function()
            category_results.append((category_name, category_passed, category_total, category_accuracy))
            
            print(f"   Results: {category_passed}/{category_total} passed ({category_accuracy:.2f}%)")
            
            if category_accuracy < 99.0:
                print(f"   WARNING: Below 99% threshold!")
            elif category_accuracy >= 99.99:
                print(f"   TARGET: Exceeds 99.99% target!")
            else:
                print(f"   PASS: Above 99% threshold")
        
        # Calculate overall accuracy
        overall_accuracy = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        # Display summary
        self.display_summary(category_results, overall_accuracy)
        
        return overall_accuracy
    
    def test_exact_country_matches(self) -> Tuple[int, int, float]:
        """Test exact country name matching"""
        passed = 0
        total = 0
        
        for circuit_id, circuit_data in self.identifier.circuits.items():
            country = circuit_data["country"]
            
            # Test exact country match
            result = self.identifier.analyze_by_hints_only({"country": country})
            
            if (result and result.get("primary_guess") and 
                result["primary_guess"]["country"] == country and
                result.get("confidence_score", 0) >= 0.5):
                passed += 1
            else:
                actual_name = None
                if result and result.get("primary_guess"):
                    actual_name = result["primary_guess"].get("track_name")
                self.log_failure("Exact Country", {"country": country}, 
                               circuit_data["name"], actual_name)
            
            total += 1
        
        self.passed_tests += passed
        self.total_tests += total
        
        return passed, total, (passed / total * 100) if total > 0 else 0
    
    def test_exact_name_matches(self) -> Tuple[int, int, float]:
        """Test exact circuit name matching"""
        passed = 0
        total = 0
        
        for circuit_id, circuit_data in self.identifier.circuits.items():
            circuit_name = circuit_data["name"]
            
            # Test exact name match
            result = self.identifier.analyze_by_hints_only({"name": circuit_name})
            
            if (result and result.get("primary_guess") and 
                result["primary_guess"]["track_name"] == circuit_name and
                result.get("confidence_score", 0) >= 0.7):
                passed += 1
            else:
                actual_name = None
                if result and result.get("primary_guess"):
                    actual_name = result["primary_guess"].get("track_name")
                self.log_failure("Exact Name", {"name": circuit_name}, 
                               circuit_name, actual_name)
            
            total += 1
        
        self.passed_tests += passed
        self.total_tests += total
        
        return passed, total, (passed / total * 100) if total > 0 else 0
    
    def test_city_region_matches(self) -> Tuple[int, int, float]:
        """Test city/region matching"""
        passed = 0
        total = 0
        
        for circuit_id, circuit_data in self.identifier.circuits.items():
            city_region = circuit_data["city_region"]
            country = circuit_data["country"]
            
            # Test city + country combination
            result = self.identifier.analyze_by_hints_only({
                "country": country,
                "city": city_region
            })
            
            if (result and result.get("primary_guess") and 
                result["primary_guess"]["track_name"] == circuit_data["name"] and
                result.get("confidence_score", 0) >= 0.8):
                passed += 1
            else:
                actual_name = None
                if result and result.get("primary_guess"):
                    actual_name = result["primary_guess"].get("track_name")
                self.log_failure("City+Country", {"country": country, "city": city_region}, 
                               circuit_data["name"], actual_name)
            
            total += 1
        
        self.passed_tests += passed
        self.total_tests += total
        
        return passed, total, (passed / total * 100) if total > 0 else 0
    
    def test_alias_recognition(self) -> Tuple[int, int, float]:
        """Test alias and alternative name recognition"""
        passed = 0
        total = 0
        
        # Test known aliases
        alias_tests = [
            ("spa", "Circuit de Spa-Francorchamps"),
            ("monaco", "Circuit de Monaco"),
            ("silverstone", "Silverstone Circuit"),
            ("monza", "Autodromo Nazionale Monza"),
            ("suzuka", "Suzuka International Racing Course"),
            ("interlagos", "Autódromo José Carlos Pace"),
            ("cota", "Circuit of the Americas"),
            ("imola", "Autodromo Enzo e Dino Ferrari"),
            ("barcelona", "Circuit de Barcelona-Catalunya"),
            ("zandvoort", "Circuit Zandvoort"),
            ("melbourne", "Albert Park Circuit"),
            ("baku", "Baku City Circuit"),
            ("jeddah", "Jeddah Corniche Circuit"),
            ("miami", "Miami International Autodrome")
        ]
        
        for alias, expected_circuit in alias_tests:
            result = self.identifier.analyze_by_hints_only({"name": alias})
            
            if (result and result.get("primary_guess") and 
                result["primary_guess"]["track_name"] == expected_circuit and
                result.get("confidence_score", 0) >= 0.4):
                passed += 1
            else:
                actual_name = None
                if result and result.get("primary_guess"):
                    actual_name = result["primary_guess"].get("track_name")
                self.log_failure("Alias", {"name": alias}, 
                               expected_circuit, actual_name)
            
            total += 1
        
        self.passed_tests += passed
        self.total_tests += total
        
        return passed, total, (passed / total * 100) if total > 0 else 0
    
    def test_grand_prix_matches(self) -> Tuple[int, int, float]:
        """Test Grand Prix name matching"""
        passed = 0
        total = 0
        
        for circuit_id, circuit_data in self.identifier.circuits.items():
            gp_name = circuit_data["grand_prix"]
            
            # Test Grand Prix name match
            result = self.identifier.analyze_by_hints_only({"grand_prix": gp_name})
            
            if (result and result.get("primary_guess") and 
                result["primary_guess"]["track_name"] == circuit_data["name"] and
                result.get("confidence_score", 0) >= 0.5):
                passed += 1
            else:
                actual_name = None
                if result and result.get("primary_guess"):
                    actual_name = result["primary_guess"].get("track_name")
                self.log_failure("Grand Prix", {"grand_prix": gp_name}, 
                               circuit_data["name"], actual_name)
            
            total += 1
        
        self.passed_tests += passed
        self.total_tests += total
        
        return passed, total, (passed / total * 100) if total > 0 else 0
    
    def test_multi_hint_combinations(self) -> Tuple[int, int, float]:
        """Test multiple hint combinations"""
        passed = 0
        total = 0
        
        # Test various combinations
        test_combinations = [
            ({"country": "Belgium", "name": "spa"}, "Circuit de Spa-Francorchamps"),
            ({"country": "Monaco", "city": "Monte Carlo"}, "Circuit de Monaco"),
            ({"country": "United Kingdom", "name": "silverstone"}, "Silverstone Circuit"),
            ({"country": "Italy", "city": "Monza"}, "Autodromo Nazionale Monza"),
            ({"country": "Japan", "name": "suzuka"}, "Suzuka International Racing Course"),
            ({"country": "Brazil", "city": "São Paulo"}, "Autódromo José Carlos Pace"),
            ({"country": "United States", "city": "Austin"}, "Circuit of the Americas"),
            ({"country": "Austria", "name": "red bull ring"}, "Red Bull Ring"),
            ({"country": "Singapore", "grand_prix": "Singapore Grand Prix"}, "Marina Bay Street Circuit"),
            ({"country": "Netherlands", "city": "Zandvoort"}, "Circuit Zandvoort")
        ]
        
        for hints, expected_circuit in test_combinations:
            result = self.identifier.analyze_by_hints_only(hints)
            
            if (result and result.get("primary_guess") and 
                result["primary_guess"]["track_name"] == expected_circuit and
                result.get("confidence_score", 0) >= 0.7):
                passed += 1
            else:
                actual_name = None
                if result and result.get("primary_guess"):
                    actual_name = result["primary_guess"].get("track_name")
                self.log_failure("Multi-Hint", hints, 
                               expected_circuit, actual_name)
            
            total += 1
        
        self.passed_tests += passed
        self.total_tests += total
        
        return passed, total, (passed / total * 100) if total > 0 else 0
    
    def test_partial_name_matching(self) -> Tuple[int, int, float]:
        """Test partial name matching"""
        passed = 0
        total = 0
        
        partial_tests = [
            ("francorchamps", "Circuit de Spa-Francorchamps"),
            ("monte carlo", "Circuit de Monaco"),
            ("americas", "Circuit of the Americas"),
            ("villeneuve", "Circuit Gilles Villeneuve"),
            ("hermanos", "Autódromo Hermanos Rodríguez"),
            ("marina bay", "Marina Bay Street Circuit"),
            ("las vegas", "Las Vegas Strip Circuit"),
            ("yas marina", "Yas Marina Circuit")
        ]
        
        for partial_name, expected_circuit in partial_tests:
            result = self.identifier.analyze_by_hints_only({"name": partial_name})
            
            if (result and result.get("primary_guess") and 
                result["primary_guess"]["track_name"] == expected_circuit and
                result["confidence_score"] >= 0.3):
                passed += 1
            else:
                actual_name = None
                if result and result.get("primary_guess"):
                    actual_name = result["primary_guess"].get("track_name")
                self.log_failure("Partial Name", {"name": partial_name}, 
                               expected_circuit, actual_name)
            
            total += 1
        
        self.passed_tests += passed
        self.total_tests += total
        
        return passed, total, (passed / total * 100) if total > 0 else 0
    
    def test_case_insensitive(self) -> Tuple[int, int, float]:
        """Test case insensitive matching"""
        passed = 0
        total = 0
        
        case_tests = [
            ({"country": "BELGIUM"}, "Circuit de Spa-Francorchamps"),
            ({"name": "MONACO"}, "Circuit de Monaco"),
            ({"city": "silverstone"}, "Silverstone Circuit"),
            ({"name": "MONZA"}, "Autodromo Nazionale Monza"),
            ({"country": "japan", "name": "SUZUKA"}, "Suzuka International Racing Course")
        ]
        
        for hints, expected_circuit in case_tests:
            result = self.identifier.analyze_by_hints_only(hints)
            
            if (result and result.get("primary_guess") and 
                result["primary_guess"]["track_name"] == expected_circuit and
                result["confidence_score"] >= 0.4):
                passed += 1
            else:
                actual_name = None
                if result and result.get("primary_guess"):
                    actual_name = result["primary_guess"].get("track_name")
                self.log_failure("Case Insensitive", hints, 
                               expected_circuit, actual_name)
            
            total += 1
        
        self.passed_tests += passed
        self.total_tests += total
        
        return passed, total, (passed / total * 100) if total > 0 else 0
    
    def test_edge_cases(self) -> Tuple[int, int, float]:
        """Test edge cases and error handling"""
        passed = 0
        total = 0
        
        edge_cases = [
            ({}, None),  # No hints
            ({"country": "NonExistent"}, None),  # Invalid country
            ({"name": "FakeCircuit"}, None),  # Invalid circuit
            ({"city": "UnknownCity"}, None),  # Invalid city
            ({"country": ""}, None),  # Empty hint
            ({"name": "   "}, None),  # Whitespace only
        ]
        
        for hints, expected_result in edge_cases:
            result = self.identifier.analyze_by_hints_only(hints)
            
            if expected_result is None:
                # Should return no confident match or very low confidence
                if (not result or not result.get("primary_guess") or 
                    result.get("confidence_score", 0) < 0.3):
                    passed += 1
                else:
                    actual_name = None
                    if result and result.get("primary_guess"):
                        actual_name = result["primary_guess"].get("track_name")
                    self.log_failure("Edge Case", hints, "No match", actual_name)
            
            total += 1
        
        self.passed_tests += passed
        self.total_tests += total
        
        return passed, total, (passed / total * 100) if total > 0 else 0
    
    def test_confidence_scoring(self) -> Tuple[int, int, float]:
        """Test confidence scoring accuracy"""
        passed = 0
        total = 0
        
        confidence_tests = [
            # High confidence tests (should be >= 0.8)
            ({"country": "Belgium", "name": "Circuit de Spa-Francorchamps"}, 0.8),
            ({"country": "Monaco", "city": "Monte Carlo", "name": "monaco"}, 0.8),
            
            # Medium confidence tests (should be 0.4-0.7)
            ({"country": "Italy"}, 0.4),
            ({"name": "silverstone"}, 0.4),
            
            # Low confidence tests (should be < 0.4)
            ({"city": "Unknown"}, 0.0),
            ({}, 0.0)
        ]
        
        for hints, min_expected_confidence in confidence_tests:
            result = self.identifier.analyze_by_hints_only(hints)
            actual_confidence = result.get("confidence_score", 0) if result else 0
            
            if min_expected_confidence == 0.0:
                # Should be very low or no match
                if actual_confidence <= 0.3:
                    passed += 1
                else:
                    self.log_failure("Low Confidence", hints, f"<= 0.3", f"{actual_confidence:.3f}")
            else:
                # Should meet minimum confidence
                if actual_confidence >= min_expected_confidence:
                    passed += 1
                else:
                    self.log_failure("Confidence Score", hints, f">= {min_expected_confidence}", f"{actual_confidence:.3f}")
            
            total += 1
        
        self.passed_tests += passed
        self.total_tests += total
        
        return passed, total, (passed / total * 100) if total > 0 else 0
    
    def log_failure(self, test_type: str, hints: Dict, expected: str, actual: str):
        """Log test failure for debugging"""
        self.test_results.append({
            "type": test_type,
            "hints": hints,
            "expected": expected,
            "actual": actual,
            "status": "FAILED"
        })
    
    def display_summary(self, category_results: List, overall_accuracy: float):
        """Display comprehensive test summary"""
        print("\n" + "=" * 70)
        print("COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 70)
        
        print(f"\nOVERALL ACCURACY: {overall_accuracy:.4f}%")
        print(f"Tests Passed: {self.passed_tests}/{self.total_tests}")
        print(f"Target: 99.99% (Error rate: 0.01%)")
        
        if overall_accuracy >= 99.99:
            print("*** TARGET ACHIEVED! 99.99% accuracy reached! ***")
        elif overall_accuracy >= 99.0:
            print("EXCELLENT: Above 99% threshold")
        elif overall_accuracy >= 95.0:
            print("WARNING: Good performance but below target")
        else:
            print("ERROR: Performance needs improvement")
        
        print(f"\nCATEGORY BREAKDOWN:")
        print("-" * 50)
        
        for category_name, passed, total, accuracy in category_results:
            status = "TARGET" if accuracy >= 99.99 else "PASS" if accuracy >= 99.0 else "WARN" if accuracy >= 95.0 else "FAIL"
            print(f"{status:>6} {category_name:<30} {passed:>3}/{total:<3} ({accuracy:>6.2f}%)")
        
        # Show failures if any
        failures = [r for r in self.test_results if r["status"] == "FAILED"]
        if failures:
            print(f"\nFAILED TESTS ({len(failures)} total):")
            print("-" * 50)
            for i, failure in enumerate(failures[:10], 1):  # Show first 10 failures
                print(f"{i:2d}. {failure['type']}: {failure['hints']}")
                print(f"    Expected: {failure['expected']}")
                print(f"    Got: {failure['actual']}")
            
            if len(failures) > 10:
                print(f"    ... and {len(failures) - 10} more failures")
        
        print("\n" + "=" * 70)

def main():
    """Run comprehensive accuracy testing"""
    print("Starting F1 Circuit Identifier Accuracy Testing...")
    
    tester = AccuracyTester()
    
    start_time = time.time()
    overall_accuracy = tester.run_comprehensive_tests()
    end_time = time.time()
    
    print(f"\nTotal testing time: {end_time - start_time:.2f} seconds")
    
    # Final verdict
    if overall_accuracy >= 99.99:
        print("*** SUCCESS: 99.99% accuracy target ACHIEVED! ***")
        return 0
    else:
        error_rate = 100 - overall_accuracy
        print(f"Target not met. Error rate: {error_rate:.4f}% (Target: <= 0.01%)")
        return 1

if __name__ == "__main__":
    sys.exit(main())