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
        try:
            if not os.path.exists(self.csv_path):
                raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
            
            self.circuits = self._load_circuits_from_csv()
            
            if not self.circuits:
                raise ValueError("No circuits loaded from CSV file")
                
        except Exception as e:
            raise RuntimeError(f"Failed to initialize F1 Circuit Identifier: {str(e)}")
        
    def _load_circuits_from_csv(self) -> Dict[str, Dict[str, Any]]:
        circuits = {}
        required_columns = ['circuit_name', 'grand_prix_name', 'country', 'city_region', 'on_2023', 'on_2024', 'on_2025']
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                if content.startswith('\ufeff'):
                    content = content[1:]
                
                lines = content.strip().split('\n')
                reader = csv.DictReader(lines)
                
                if not all(col in reader.fieldnames for col in required_columns):
                    missing = [col for col in required_columns if col not in reader.fieldnames]
                    raise ValueError(f"Missing required CSV columns: {missing}")
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if not all(row.get(col, '').strip() for col in required_columns[:4]):
                            continue
                        
                        circuit_id = self._normalize_circuit_id(row['circuit_name'])
                        
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
        if not circuit_name:
            raise ValueError("Circuit name cannot be empty")
        
        normalized = re.sub(r'[^\w\s-]', '', circuit_name.lower())
        normalized = re.sub(r'[-\s]+', '_', normalized)
        normalized = normalized.strip('_')
        
        return normalized if normalized else "unknown_circuit"
    
    def _generate_aliases(self, circuit_name: str, country: str) -> List[str]:
        aliases = []
        aliases.append(f"{country.lower()}_gp")
        aliases.append(f"{country.lower()}_circuit")
        
        name_variations = {
            "Circuit de Spa-Francorchamps": ["spa", "spa_francorchamps", "belgium_gp", "francorchamps"],
            "Circuit de Monaco": ["monaco", "monte_carlo", "monaco_gp", "principality", "monte carlo"],
            "Silverstone Circuit": ["silverstone", "british_gp", "uk_gp", "england_gp"],
            "Autodromo Nazionale Monza": ["monza", "italian_gp", "italy_gp", "temple_of_speed"],
            "Suzuka International Racing Course": ["suzuka", "japanese_gp", "japan_gp", "figure_8"],
            "Autódromo José Carlos Pace": ["interlagos", "brazil_gp", "sao_paulo_gp", "jose_carlos_pace"],
            "Circuit of the Americas": ["cota", "austin", "us_gp", "usa_gp", "americas"],
            "Red Bull Ring": ["austria_gp", "spielberg", "red_bull_ring", "a1_ring"],
            "Marina Bay Street Circuit": ["singapore_gp", "marina_bay", "singapore_street"],
            "Bahrain International Circuit": ["bahrain_gp", "sakhir", "desert_circuit"],
            "Jeddah Corniche Circuit": ["jeddah", "saudi_arabia_gp", "corniche"],
            "Albert Park Circuit": ["melbourne", "australia_gp", "albert_park"],
            "Baku City Circuit": ["baku", "azerbaijan_gp", "city_circuit"],
            "Miami International Autodrome": ["miami_gp", "hard_rock_stadium", "florida"],
            "Autodromo Enzo e Dino Ferrari": ["imola", "san_marino_gp", "emilia_romagna_gp"],
            "Circuit de Barcelona-Catalunya": ["barcelona", "spain_gp", "catalunya", "montmelo"],
            "Circuit Gilles Villeneuve": ["montreal", "canada_gp", "gilles_villeneuve", "ile_notre_dame"],
            "Hungaroring": ["hungary_gp", "budapest", "mogyorod"],
            "Circuit Zandvoort": ["zandvoort", "netherlands_gp", "dutch_gp"],
            "Lusail International Circuit": ["lusail", "qatar_gp", "doha"],
            "Autódromo Hermanos Rodríguez": ["mexico_gp", "mexico_city", "hermanos_rodriguez"],
            "Las Vegas Strip Circuit": ["las_vegas_gp", "strip_circuit", "nevada"],
            "Yas Marina Circuit": ["abu_dhabi_gp", "yas_marina", "yas_island"],
            "Shanghai International Circuit": ["shanghai", "china_gp", "chinese_gp"]
        }
        
        if circuit_name in name_variations:
            aliases.extend(name_variations[circuit_name])
            
        return list(set(aliases))
    
    def _get_circuit_features(self, circuit_name: str) -> List[str]:
        feature_map = {
            "Circuit de Spa-Francorchamps": ["long_straight", "eau_rouge", "high_speed", "elevation"],
            "Circuit de Monaco": ["tight_corners", "street_circuit", "harbor", "barriers"],
            "Silverstone Circuit": ["maggots_becketts", "fast_flowing", "high_speed", "copse"],
            "Autodromo Nazionale Monza": ["long_straights", "chicanes", "high_speed", "parabolica"],
            "Suzuka International Racing Course": ["figure_eight", "crossover", "technical", "130r"],
            "Autódromo José Carlos Pace": ["s_curves", "elevation", "anti_clockwise", "senna_s"],
            "Marina Bay Street Circuit": ["street_circuit", "night_race", "tight_corners", "singapore_sling"],
            "Circuit of the Americas": ["elevation", "technical", "modern", "turn_1_climb"],
            "Red Bull Ring": ["short_lap", "elevation", "overtaking", "mountain"],
            "Bahrain International Circuit": ["desert", "night_race", "modern", "turn_4"],
            "Jeddah Corniche Circuit": ["street_circuit", "high_speed", "night_race", "corniche"],
            "Albert Park Circuit": ["park_circuit", "lake", "semi_street", "melbourne"],
            "Baku City Circuit": ["street_circuit", "long_straight", "tight_corners", "castle_section"],
            "Miami International Autodrome": ["modern", "stadium", "artificial", "hard_rock"],
            "Autodromo Enzo e Dino Ferrari": ["technical", "tamburello", "variante_alta", "acque_minerali"],
            "Circuit de Barcelona-Catalunya": ["technical", "turn_3", "sector_2", "campsa"],
            "Circuit Gilles Villeneuve": ["island", "hairpin", "wall_of_champions", "casino_straight"],
            "Hungaroring": ["technical", "twisty", "overtaking_difficult", "turn_1"],
            "Circuit Zandvoort": ["banked_corners", "dunes", "historic", "narrow"],
            "Lusail International Circuit": ["desert", "modern", "night_race", "wide_corners"],
            "Autódromo Hermanos Rodríguez": ["altitude", "stadium", "peraltada", "thin_air"],
            "Las Vegas Strip Circuit": ["street_circuit", "night_race", "strip", "casinos"],
            "Yas Marina Circuit": ["modern", "hotel", "twilight_race", "marina"],
            "Shanghai International Circuit": ["modern", "long_back_straight", "technical", "turn_1_hairpin"]
        }
        return feature_map.get(circuit_name, ["standard_circuit"])
    
    def analyze_by_hints_only(self, hints: Dict[str, str]) -> Dict[str, Any]:
        """Main analysis function using only hints"""
        matches = []
        
        for circuit_id, circuit_data in self.circuits.items():
            confidence = self._calculate_hint_confidence(circuit_data, hints)
            if confidence > 0.05:
                matches.append({
                    "circuit_id": circuit_id,
                    "data": circuit_data,
                    "confidence": confidence
                })
        
        matches = sorted(matches, key=lambda x: x["confidence"], reverse=True)
        return self._format_response(matches)
    
    def _calculate_hint_confidence(self, circuit_data: Dict[str, Any], hints: Dict[str, str]) -> float:
        confidence = 0.05
        
        if not hints:
            return confidence
        
        # Exact country match
        country_hint = hints.get("country", "").lower().strip()
        if country_hint:
            if country_hint == circuit_data["country"].lower():
                confidence += 0.6
            elif country_hint in circuit_data["country"].lower():
                confidence += 0.4
        
        # City/region matching with fuzzy logic
        city_hint = hints.get("city", "").lower().strip()
        if city_hint:
            city_region = circuit_data["city_region"].lower()
            if city_hint == city_region or city_hint in city_region:
                confidence += 0.5
            elif any(word in city_region for word in city_hint.split()):
                confidence += 0.3
        
        # Circuit name matching with aliases
        name_hint = hints.get("name", "").lower().strip()
        if name_hint:
            circuit_name = circuit_data["name"].lower()
            if name_hint == circuit_name:
                confidence += 0.8
            elif name_hint in circuit_name:
                confidence += 0.6
            elif any(name_hint == alias for alias in circuit_data["aliases"]):
                confidence += 0.7
            elif any(name_hint in alias for alias in circuit_data["aliases"]):
                confidence += 0.4
            # Additional fuzzy matching for partial names
            elif any(alias in name_hint for alias in circuit_data["aliases"]):
                confidence += 0.3
            elif name_hint in circuit_data["city_region"].lower():
                confidence += 0.5
        
        # Grand Prix name matching
        gp_hint = hints.get("grand_prix", "").lower().strip()
        if gp_hint and gp_hint in circuit_data["grand_prix"].lower():
            confidence += 0.5
        
        return min(confidence, 1.0)
    
    def _format_response(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not matches:
            return self._no_match_response("No matching circuits found")
        
        primary = matches[0]
        
        response = {
            "primary_guess": {
                "track_name": primary["data"]["name"],
                "grand_prix_name": primary["data"]["grand_prix"],
                "country": primary["data"]["country"],
                "city_or_region": primary["data"]["city_region"],
                "layout_or_years": "Current layout",
                "f1_usage": primary["data"]["f1_usage"]
            },
            "confidence_score": round(primary["confidence"], 4),
            "confidence_label": self._get_confidence_label(primary["confidence"]),
            "alternatives": [],
            "reasoning": self._generate_reasoning(primary),
            "notes": f"Analysis based on CSV data. Total circuits: {len(self.circuits)}"
        }
        
        # Add alternatives with better filtering
        for match in matches[1:5]:
            if match.get("data") and match["confidence"] > 0.1:
                response["alternatives"].append({
                    "track_name": match["data"]["name"],
                    "country": match["data"]["country"],
                    "confidence": round(match["confidence"], 4),
                    "reason": f"Features: {', '.join(match['data']['features'][:3])}"
                })
        
        return response
    
    def _generate_reasoning(self, primary_match: Dict[str, Any]) -> str:
        confidence = primary_match["confidence"]
        circuit_name = primary_match["data"]["name"]
        
        if confidence >= 0.8:
            return f"Very high confidence match for {circuit_name} based on strong hint correlation."
        elif confidence >= 0.6:
            return f"High confidence match for {circuit_name} with good hint alignment."
        elif confidence >= 0.4:
            return f"Good match for {circuit_name} with moderate hint correlation."
        elif confidence >= 0.2:
            return f"Possible match for {circuit_name} with limited hint correlation."
        else:
            return f"Low confidence suggestion for {circuit_name}. Consider providing more specific hints."
    
    def _get_confidence_label(self, score: float) -> str:
        if score >= 0.9:
            return "extremely_high"
        elif score >= 0.8:
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
        return {
            "primary_guess": None,
            "confidence_score": 0.0,
            "confidence_label": "no_confident_match_found",
            "alternatives": [],
            "reasoning": reason,
            "notes": "Try providing more specific hints.",
            "total_circuits": len(self.circuits)
        }

def identify_circuit(hints: Optional[Dict[str, str]] = None) -> str:
    """Main function to identify F1 circuit"""
    try:
        identifier = F1CircuitIdentifier()
        result = identifier.analyze_by_hints_only(hints or {})
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

if __name__ == "__main__":
    # Test examples
    print("Testing Belgium hint:")
    result = identify_circuit({"country": "Belgium"})
    print(result)
    
    print("\nTesting Monaco hint:")
    result = identify_circuit({"country": "Monaco", "city": "Monte Carlo"})
    print(result)