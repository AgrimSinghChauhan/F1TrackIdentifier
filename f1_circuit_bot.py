import json
import csv
import os
import re
from typing import Dict, List, Optional, Any

class F1CircuitIdentifier:
    def __init__(self, csv_path: str = "f1_circuits_2023_2025.csv"):
        self.circuits = {}
        self.csv_path = csv_path
        self._validate_and_load_data()
        
    def _validate_and_load_data(self) -> None:
        """Validate CSV file exists and load circuit data with error handling."""
        try:
            if not os.path.exists(self.csv_path):
                raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
            
            self.circuits = self._load_circuits_from_csv()
            
            if not self.circuits:
                raise ValueError("No circuits loaded from CSV file")
                
        except Exception as e:
            raise RuntimeError(f"Failed to initialize F1 Circuit Identifier: {str(e)}")
        
    def _load_circuits_from_csv(self) -> Dict[str, Dict[str, Any]]:
        """Load and validate circuit data from CSV with comprehensive error handling."""
        circuits = {}
        required_columns = ['circuit_name', 'grand_prix_name', 'country', 'city_region', 'on_2023', 'on_2024', 'on_2025']
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Validate CSV headers
                if not all(col in reader.fieldnames for col in required_columns):
                    missing = [col for col in required_columns if col not in reader.fieldnames]
                    raise ValueError(f"Missing required CSV columns: {missing}")
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Validate required fields are not empty
                        if not all(row.get(col, '').strip() for col in required_columns[:4]):
                            continue  # Skip incomplete rows
                        
                        circuit_id = self._normalize_circuit_id(row['circuit_name'])
                        
                        # Parse boolean values safely
                        years = []
                        for year, col in [('2023', 'on_2023'), ('2024', 'on_2024'), ('2025', 'on_2025')]:
                            if str(row.get(col, '')).strip().lower() in ['true', '1', 'yes']:
                                years.append(year)
                        
                        f1_usage = f"F1 calendar: {', '.join(years)}" if years else "Not on current F1 calendar"
                        
                        circuits[circuit_id] = {
                            "name": row['circuit_name'].strip(),
                            "grand_prix": row['grand_prix_name'].strip(),
                            "country": row['country'].strip(),
                            "city_region": row['city_region'].strip(),
                            "f1_usage": f1_usage,
                            "years": years,
                            "features": self._get_circuit_features(row['circuit_name'].strip()),
                            "aliases": self._generate_aliases(row['circuit_name'].strip(), row['country'].strip())
                        }
                        
                    except Exception as e:
                        print(f"Warning: Error processing row {row_num}: {str(e)}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        except Exception as e:
            raise RuntimeError(f"Error reading CSV file: {str(e)}")
            
        return circuits
    
    def _normalize_circuit_id(self, circuit_name: str) -> str:
        """Create normalized circuit ID with comprehensive cleaning."""
        if not circuit_name:
            raise ValueError("Circuit name cannot be empty")
        
        # Remove special characters and normalize
        normalized = re.sub(r'[^\w\s-]', '', circuit_name.lower())
        normalized = re.sub(r'[-\s]+', '_', normalized)
        normalized = normalized.strip('_')
        
        return normalized if normalized else "unknown_circuit"
    
    def _generate_aliases(self, circuit_name: str, country: str) -> List[str]:
        """Generate alternative names and aliases for better matching."""
        aliases = []
        
        # Add country-based aliases
        aliases.append(f"{country.lower()}_gp")
        aliases.append(f"{country.lower()}_circuit")
        
        # Add common abbreviations and variations
        name_variations = {
            "Circuit de Spa-Francorchamps": ["spa", "spa_francorchamps", "belgium_gp"],
            "Circuit de Monaco": ["monaco", "monte_carlo", "monaco_gp"],
            "Silverstone Circuit": ["silverstone", "british_gp", "uk_gp"],
            "Autodromo Nazionale Monza": ["monza", "italian_gp", "italy_gp"],
            "Suzuka International Racing Course": ["suzuka", "japanese_gp", "japan_gp"],
            "Circuit of the Americas": ["cota", "austin", "us_gp", "usa_gp"],
            "Red Bull Ring": ["austria_gp", "spielberg", "red_bull_ring"]
        }
        
        if circuit_name in name_variations:
            aliases.extend(name_variations[circuit_name])
            
        return list(set(aliases))  # Remove duplicates
    
    def _get_circuit_features(self, circuit_name: str) -> List[str]:
        """Enhanced circuit feature mapping with more comprehensive data."""
        feature_map = {
            "Circuit de Spa-Francorchamps": ["long_straight", "eau_rouge", "high_speed", "elevation", "weather_variable"],
            "Circuit de Monaco": ["tight_corners", "street_circuit", "harbor", "barriers", "slow_speed"],
            "Silverstone Circuit": ["maggots_becketts", "fast_flowing", "high_speed", "copse", "abbey"],
            "Autodromo Nazionale Monza": ["long_straights", "chicanes", "high_speed", "parabolica", "temple_of_speed"],
            "Suzuka International Racing Course": ["figure_eight", "crossover", "technical", "130r", "spoon_curve"],
            "Autódromo José Carlos Pace": ["s_curves", "elevation", "anti_clockwise", "senna_s", "interlagos"],
            "Marina Bay Street Circuit": ["street_circuit", "night_race", "tight_corners", "singapore_sling", "barriers"],
            "Circuit of the Americas": ["elevation", "technical", "modern", "turn_1_climb", "esses"],
            "Red Bull Ring": ["short_lap", "elevation", "overtaking", "mountain", "austria"],
            "Bahrain International Circuit": ["desert", "night_race", "modern", "bahrain", "middle_east"],
            "Jeddah Corniche Circuit": ["street_circuit", "high_speed", "night_race", "saudi_arabia", "corniche"],
            "Albert Park Circuit": ["park_circuit", "australia", "melbourne", "lake", "semi_street"],
            "Baku City Circuit": ["street_circuit", "long_straight", "tight_corners", "azerbaijan", "castle"],
            "Miami International Autodrome": ["modern", "stadium", "miami", "usa", "artificial"],
            "Autodromo Enzo e Dino Ferrari": ["imola", "italy", "technical", "tamburello", "variante_alta"],
            "Circuit de Barcelona-Catalunya": ["technical", "spain", "barcelona", "testing", "turn_3"],
            "Circuit Gilles Villeneuve": ["island", "canada", "montreal", "hairpin", "wall_of_champions"],
            "Hungaroring": ["technical", "hungary", "budapest", "twisty", "overtaking_difficult"],
            "Circuit Zandvoort": ["banked_corners", "netherlands", "dunes", "historic", "narrow"],
            "Lusail International Circuit": ["desert", "qatar", "modern", "night_race", "middle_east"],
            "Autódromo Hermanos Rodríguez": ["altitude", "mexico", "stadium", "peraltada", "thin_air"],
            "Las Vegas Strip Circuit": ["street_circuit", "night_race", "usa", "strip", "casinos"],
            "Yas Marina Circuit": ["modern", "uae", "abu_dhabi", "hotel", "twilight_race"],
            "Shanghai International Circuit": ["modern", "china", "shanghai", "long_back_straight", "technical"]
        }
        return feature_map.get(circuit_name, ["standard_circuit"])
    
    def analyze_circuit(self, hints: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Main analysis function with comprehensive error handling."""
        try:
            if not self.circuits:
                return self._no_match_response("No circuit data available")
            
            matches = self._match_circuit_by_hints(hints or {})
            return self._format_response(matches)
            
        except Exception as e:
            return self._no_match_response(f"Analysis error: {str(e)}")
    
    def _match_circuit_by_hints(self, hints: Dict[str, str]) -> List[Dict[str, Any]]:
        """Enhanced matching algorithm with fuzzy matching and multiple criteria."""
        matches = []
        
        for circuit_id, circuit_data in self.circuits.items():
            confidence = self._calculate_confidence(circuit_data, hints)
            if confidence > 0.1:  # Lower threshold for better coverage
                matches.append({
                    "circuit_id": circuit_id,
                    "data": circuit_data,
                    "confidence": confidence
                })
        
        return sorted(matches, key=lambda x: x["confidence"], reverse=True)
    
    def _calculate_confidence(self, circuit_data: Dict[str, Any], hints: Dict[str, str]) -> float:
        """Enhanced confidence calculation with multiple matching criteria."""
        confidence = 0.1  # Lower base confidence
        
        if not hints:
            return confidence
        
        # Country matching (highest weight)
        country_hint = hints.get("country", "").lower().strip()
        if country_hint and country_hint in circuit_data["country"].lower():
            confidence += 0.6
        
        # City/region matching
        city_hint = hints.get("city", "").lower().strip()
        if city_hint and city_hint in circuit_data["city_region"].lower():
            confidence += 0.4
        
        # Circuit name matching
        name_hint = hints.get("name", "").lower().strip()
        if name_hint:
            if name_hint in circuit_data["name"].lower():
                confidence += 0.7
            elif any(name_hint in alias for alias in circuit_data["aliases"]):
                confidence += 0.5
        
        # Feature matching
        feature_hint = hints.get("feature", "").lower().strip()
        if feature_hint and feature_hint in circuit_data["features"]:
            confidence += 0.3
        
        # Year matching
        year_hint = hints.get("year", "").strip()
        if year_hint and year_hint in circuit_data["years"]:
            confidence += 0.2
        
        # Grand Prix name matching
        gp_hint = hints.get("grand_prix", "").lower().strip()
        if gp_hint and gp_hint in circuit_data["grand_prix"].lower():
            confidence += 0.5
        
        return min(confidence, 1.0)
    
    def _format_response(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format response with enhanced error handling and validation."""
        try:
            if not matches:
                return self._no_match_response("No matching circuits found")
            
            primary = matches[0]
            
            # Validate primary match data
            if not primary.get("data"):
                return self._no_match_response("Invalid match data")
            
            response = {
                "primary_guess": {
                    "track_name": primary["data"]["name"],
                    "grand_prix_name": primary["data"]["grand_prix"],
                    "country": primary["data"]["country"],
                    "city_or_region": primary["data"]["city_region"],
                    "layout_or_years": "Current layout",
                    "f1_usage": primary["data"]["f1_usage"]
                },
                "confidence_score": round(primary["confidence"], 3),
                "confidence_label": self._get_confidence_label(primary["confidence"]),
                "alternatives": [],
                "reasoning": self._generate_reasoning(primary, matches),
                "notes": f"Analysis based on CSV data from F1 circuits 2023-2025. Total circuits in database: {len(self.circuits)}"
            }
            
            # Add alternatives with validation
            for match in matches[1:4]:
                if match.get("data"):
                    response["alternatives"].append({
                        "track_name": match["data"]["name"],
                        "country": match["data"]["country"],
                        "confidence": round(match["confidence"], 3),
                        "reason": f"Features: {', '.join(match['data']['features'][:2])}"
                    })
            
            return response
            
        except Exception as e:
            return self._no_match_response(f"Response formatting error: {str(e)}")
    
    def _generate_reasoning(self, primary_match: Dict[str, Any], all_matches: List[Dict[str, Any]]) -> str:
        """Generate detailed reasoning for the match."""
        confidence = primary_match["confidence"]
        circuit_name = primary_match["data"]["name"]
        
        if confidence >= 0.8:
            return f"High confidence match for {circuit_name} based on strong hint correlation."
        elif confidence >= 0.5:
            return f"Good match for {circuit_name} with moderate hint alignment."
        elif confidence >= 0.3:
            return f"Possible match for {circuit_name} with limited hint correlation."
        else:
            return f"Low confidence suggestion for {circuit_name}. Consider providing more specific hints."
    
    def _get_confidence_label(self, score: float) -> str:
        """Enhanced confidence labeling with more granular levels."""
        if score >= 0.8:
            return "very_high"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "very_low"
    
    def _no_match_response(self, reason: str) -> Dict[str, Any]:
        """Enhanced no-match response with helpful suggestions."""
        return {
            "primary_guess": None,
            "confidence_score": 0.0,
            "confidence_label": "no_confident_match_found",
            "alternatives": [],
            "reasoning": reason,
            "notes": "Try providing hints like: country, city, circuit name, or distinctive features.",
            "available_countries": list(set(circuit["country"] for circuit in self.circuits.values())),
            "total_circuits": len(self.circuits)
        }
    
    def get_all_circuits(self) -> Dict[str, Dict[str, Any]]:
        """Return all available circuits for reference."""
        return self.circuits.copy()
    
    def search_by_country(self, country: str) -> List[Dict[str, Any]]:
        """Search circuits by country with error handling."""
        try:
            country = country.lower().strip()
            results = []
            
            for circuit_data in self.circuits.values():
                if country in circuit_data["country"].lower():
                    results.append(circuit_data)
            
            return results
            
        except Exception as e:
            print(f"Error searching by country: {str(e)}")
            return []

def identify_circuit(hints: Optional[Dict[str, str]] = None) -> str:
    """Main function to identify F1 circuit with comprehensive error handling."""
    try:
        identifier = F1CircuitIdentifier()
        result = identifier.analyze_circuit(hints)
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        error_response = {
            "error": True,
            "message": f"System error: {str(e)}",
            "primary_guess": None,
            "confidence_score": 0.0,
            "confidence_label": "error"
        }
        return json.dumps(error_response, indent=2)

def run_comprehensive_tests() -> None:
    """Run comprehensive tests to validate 99.9% accuracy."""
    test_cases = [
        ({"country": "Belgium"}, "Circuit de Spa-Francorchamps"),
        ({"country": "Monaco"}, "Circuit de Monaco"),
        ({"country": "United Kingdom"}, "Silverstone Circuit"),
        ({"country": "Italy", "city": "Monza"}, "Autodromo Nazionale Monza"),
        ({"country": "Japan"}, "Suzuka International Racing Course"),
        ({"country": "Brazil"}, "Autódromo José Carlos Pace"),
        ({"country": "United States", "city": "Austin"}, "Circuit of the Americas"),
        ({"country": "Austria"}, "Red Bull Ring"),
        ({"name": "spa"}, "Circuit de Spa-Francorchamps"),
        ({"grand_prix": "Monaco Grand Prix"}, "Circuit de Monaco"),
        ({"feature": "eau_rouge"}, "Circuit de Spa-Francorchamps"),
        ({"year": "2023"}, None),  # Should return multiple matches
        ({}, None),  # No hints
        ({"country": "NonExistent"}, None),  # Invalid country
    ]
    
    passed = 0
    total = len(test_cases)
    
    print("Running comprehensive tests...")
    print("=" * 60)
    
    for i, (hints, expected) in enumerate(test_cases, 1):
        try:
            result_json = identify_circuit(hints)
            result = json.loads(result_json)
            
            if expected is None:
                # Test should handle gracefully
                if result.get("primary_guess") is None or result.get("confidence_score", 0) < 0.5:
                    passed += 1
                    status = "PASS"
                else:
                    status = "FAIL"
            else:
                # Test should match expected circuit
                if (result.get("primary_guess") and 
                    result["primary_guess"].get("track_name") == expected and
                    result.get("confidence_score", 0) >= 0.5):
                    passed += 1
                    status = "PASS"
                else:
                    status = "FAIL"
            
            print(f"Test {i:2d}: {status} - Hints: {hints}")
            if status == "FAIL":
                print(f"         Expected: {expected}")
                print(f"         Got: {result.get('primary_guess', {}).get('track_name', 'None')}")
                print(f"         Confidence: {result.get('confidence_score', 0)}")
            
        except Exception as e:
            print(f"Test {i:2d}: ERROR - {str(e)}")
    
    accuracy = (passed / total) * 100
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 99.9:
        print("✅ 99.9% accuracy target ACHIEVED!")
    else:
        print("❌ 99.9% accuracy target NOT met")

if __name__ == "__main__":
    # Run comprehensive tests
    run_comprehensive_tests()
    
    print("\n" + "=" * 60 + "\n")
    
    # Interactive examples
    print("Example usage:")
    print("\n1. Belgium hint:")
    result = identify_circuit({"country": "Belgium"})
    print(result)
    
    print("\n2. Monaco with city hint:")
    result = identify_circuit({"country": "Monaco", "city": "Monte Carlo"})
    print(result)