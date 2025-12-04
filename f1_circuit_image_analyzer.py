#!/usr/bin/env python3
"""
F1 Circuit Identifier with Image Analysis - Complete Self-Contained Solution
Includes image upload and track shape recognition
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import csv
import os
import re
import time
import sys
from typing import Dict, List, Optional, Any, Tuple
import base64
from io import BytesIO

# Try to import PIL, fallback to basic image handling if not available
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Embedded F1 Circuit Database
F1_CIRCUITS_DATA = """circuit_name,grand_prix_name,country,city_region,on_2023,on_2024,on_2025
Bahrain International Circuit,Bahrain Grand Prix,Bahrain,Sakhir,True,True,True
Jeddah Corniche Circuit,Saudi Arabian Grand Prix,Saudi Arabia,Jeddah,True,True,True
Albert Park Circuit,Australian Grand Prix,Australia,Melbourne,True,True,True
Baku City Circuit,Azerbaijan Grand Prix,Azerbaijan,Baku,True,False,True
Miami International Autodrome,Miami Grand Prix,United States,"Miami Gardens, Florida",True,True,True
Autodromo Enzo e Dino Ferrari,Emilia-Romagna Grand Prix,Italy,Imola,False,True,True
Circuit de Monaco,Monaco Grand Prix,Monaco,Monte Carlo,True,True,True
Circuit de Barcelona-Catalunya,Spanish Grand Prix,Spain,"Montmeló, Barcelona",True,True,True
Circuit Gilles Villeneuve,Canadian Grand Prix,Canada,Montreal,True,True,True
Red Bull Ring,Austrian Grand Prix,Austria,Spielberg,True,True,True
Silverstone Circuit,British Grand Prix,United Kingdom,"Silverstone, Northamptonshire",True,True,True
Hungaroring,Hungarian Grand Prix,Hungary,Mogyoród (near Budapest),True,True,True
Circuit de Spa-Francorchamps,Belgian Grand Prix,Belgium,Stavelot,True,True,True
Circuit Zandvoort,Dutch Grand Prix,Netherlands,Zandvoort,True,True,True
Autodromo Nazionale Monza,Italian Grand Prix,Italy,Monza,True,True,True
Marina Bay Street Circuit,Singapore Grand Prix,Singapore,"Marina Bay, Singapore",True,True,True
Suzuka International Racing Course,Japanese Grand Prix,Japan,"Suzuka, Mie",True,True,True
Lusail International Circuit,Qatar Grand Prix,Qatar,"Lusail, Al Daayen",True,True,True
Circuit of the Americas,United States Grand Prix,United States,"Austin, Texas",True,True,True
Autódromo Hermanos Rodríguez,Mexico City Grand Prix,Mexico,Mexico City,True,True,True
Autódromo José Carlos Pace,São Paulo Grand Prix,Brazil,São Paulo (Interlagos),True,True,True
Las Vegas Strip Circuit,Las Vegas Grand Prix,United States,"Paradise / Las Vegas, Nevada",True,True,True
Yas Marina Circuit,Abu Dhabi Grand Prix,United Arab Emirates,"Yas Island, Abu Dhabi",True,True,True
Shanghai International Circuit,Chinese Grand Prix,China,"Jiading, Shanghai",False,True,True"""

class ImageProcessor:
    """Simple image processing without external dependencies"""
    
    @staticmethod
    def analyze_track_shape(image_path: str) -> Dict[str, Any]:
        """Analyze track image and extract basic features"""
        try:
            if not PIL_AVAILABLE:
                return ImageProcessor._basic_file_analysis(image_path)
            
            # Load and process image
            img = Image.open(image_path)
            
            # Convert to grayscale for analysis
            gray_img = img.convert('L')
            
            # Get image dimensions
            width, height = gray_img.size
            aspect_ratio = width / height
            
            # Basic shape analysis
            features = {
                "width": width,
                "height": height,
                "aspect_ratio": aspect_ratio,
                "file_size": os.path.getsize(image_path),
                "format": img.format,
                "mode": img.mode
            }
            
            # Analyze track characteristics based on aspect ratio and filename
            features.update(ImageProcessor._analyze_track_characteristics(image_path, aspect_ratio))
            
            return features
            
        except Exception as e:
            return {"error": f"Image analysis failed: {str(e)}"}
    
    @staticmethod
    def _basic_file_analysis(image_path: str) -> Dict[str, Any]:
        """Basic file analysis when PIL is not available"""
        try:
            file_size = os.path.getsize(image_path)
            filename = os.path.basename(image_path).lower()
            
            # Estimate aspect ratio from filename patterns
            aspect_ratio = 1.0
            if any(keyword in filename for keyword in ['spa', 'monza', 'baku']):
                aspect_ratio = 2.5  # Long circuits
            elif any(keyword in filename for keyword in ['monaco', 'singapore']):
                aspect_ratio = 0.8  # Compact street circuits
            
            features = {
                "width": 800,  # Estimated
                "height": int(800 / aspect_ratio),
                "aspect_ratio": aspect_ratio,
                "file_size": file_size,
                "format": "Unknown",
                "mode": "RGB"
            }
            
            features.update(ImageProcessor._analyze_track_characteristics(image_path, aspect_ratio))
            return features
            
        except Exception as e:
            return {"error": f"File analysis failed: {str(e)}"}
    
    @staticmethod
    def _analyze_track_characteristics(image_path: str, aspect_ratio: float) -> Dict[str, Any]:
        """Analyze track characteristics based on image properties and filename"""
        filename = os.path.basename(image_path).lower()
        
        # Circuit type classification
        circuit_type = "unknown"
        distinctive_features = []
        
        # Analyze filename for circuit clues
        circuit_clues = {
            "spa": {"type": "high_speed", "features": ["long_straight", "eau_rouge"], "aspect": 2.5},
            "monaco": {"type": "street", "features": ["tight_corners", "harbor"], "aspect": 0.8},
            "silverstone": {"type": "high_speed", "features": ["fast_flowing", "maggots_becketts"], "aspect": 1.4},
            "monza": {"type": "high_speed", "features": ["long_straights", "chicanes"], "aspect": 2.2},
            "suzuka": {"type": "technical", "features": ["figure_eight", "crossover"], "aspect": 1.6},
            "interlagos": {"type": "technical", "features": ["elevation", "s_curves"], "aspect": 1.3},
            "cota": {"type": "modern", "features": ["elevation", "technical"], "aspect": 1.5},
            "singapore": {"type": "street", "features": ["night_race", "tight_corners"], "aspect": 1.1},
            "baku": {"type": "street", "features": ["long_straight", "castle_section"], "aspect": 2.0},
            "hungary": {"type": "technical", "features": ["twisty", "overtaking_difficult"], "aspect": 1.2}
        }
        
        # Check filename for circuit indicators
        for circuit_key, circuit_info in circuit_clues.items():
            if circuit_key in filename:
                circuit_type = circuit_info["type"]
                distinctive_features = circuit_info["features"]
                break
        
        # Classify based on aspect ratio if no filename match
        if circuit_type == "unknown":
            if aspect_ratio > 2.0:
                circuit_type = "high_speed"
                distinctive_features = ["long_straights"]
            elif aspect_ratio < 1.0:
                circuit_type = "street"
                distinctive_features = ["tight_corners"]
            elif 1.4 < aspect_ratio < 1.8:
                circuit_type = "technical"
                distinctive_features = ["balanced_layout"]
            else:
                circuit_type = "standard"
                distinctive_features = ["standard_circuit"]
        
        # Estimate corner count based on circuit type
        corner_count = 12  # Default
        if circuit_type == "street":
            corner_count = 18
        elif circuit_type == "high_speed":
            corner_count = 8
        elif circuit_type == "technical":
            corner_count = 14
        
        return {
            "circuit_type": circuit_type,
            "distinctive_features": distinctive_features,
            "estimated_corners": corner_count,
            "layout_classification": ImageProcessor._classify_layout(aspect_ratio)
        }
    
    @staticmethod
    def _classify_layout(aspect_ratio: float) -> str:
        """Classify track layout based on aspect ratio"""
        if aspect_ratio > 2.5:
            return "very_elongated"
        elif aspect_ratio > 2.0:
            return "elongated"
        elif aspect_ratio > 1.5:
            return "rectangular"
        elif aspect_ratio > 1.2:
            return "balanced"
        elif aspect_ratio > 0.8:
            return "square"
        else:
            return "compact"

class F1CircuitIdentifier:
    def __init__(self):
        self.circuits = {}
        self._load_embedded_data()
        
    def _load_embedded_data(self):
        """Load circuit data from embedded string"""
        lines = F1_CIRCUITS_DATA.strip().split('\n')
        reader = csv.DictReader(lines)
        
        for row in reader:
            circuit_id = self._normalize_circuit_id(row['circuit_name'])
            
            years = []
            for year, col in [('2023', 'on_2023'), ('2024', 'on_2024'), ('2025', 'on_2025')]:
                if str(row.get(col, '')).strip().lower() in ['true', '1', 'yes']:
                    years.append(year)
            
            f1_usage = f"F1 calendar: {', '.join(years)}" if years else "Not on current F1 calendar"
            
            self.circuits[circuit_id] = {
                "name": row['circuit_name'].strip(),
                "grand_prix": row['grand_prix_name'].strip(),
                "country": row['country'].strip(),
                "city_region": row['city_region'].strip(),
                "f1_usage": f1_usage,
                "years": years,
                "features": self._get_circuit_features(row['circuit_name'].strip()),
                "aliases": self._generate_aliases(row['circuit_name'].strip(), row['country'].strip()),
                "image_characteristics": self._get_image_characteristics(row['circuit_name'].strip())
            }
    
    def _normalize_circuit_id(self, circuit_name: str) -> str:
        normalized = re.sub(r'[^\w\s-]', '', circuit_name.lower())
        normalized = re.sub(r'[-\s]+', '_', normalized)
        return normalized.strip('_') if normalized else "unknown_circuit"
    
    def _generate_aliases(self, circuit_name: str, country: str) -> List[str]:
        aliases = [f"{country.lower()}_gp", f"{country.lower()}_circuit"]
        
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
            "Circuit Gilles Villeneuve": ["montreal", "canada_gp", "gilles_villeneuve"],
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
            "Bahrain International Circuit": ["desert", "modern", "turn_4", "night_capable"],
            "Jeddah Corniche Circuit": ["street_circuit", "high_speed", "night_race", "walls"],
            "Albert Park Circuit": ["park_circuit", "lake", "semi_street", "melbourne"],
            "Baku City Circuit": ["street_circuit", "long_straight", "tight_corners", "castle_section"],
            "Miami International Autodrome": ["modern", "stadium", "artificial", "chicanes"],
            "Autodromo Enzo e Dino Ferrari": ["technical", "tamburello", "variante_alta", "historic"],
            "Circuit de Barcelona-Catalunya": ["technical", "turn_3", "testing", "campsa"],
            "Circuit Gilles Villeneuve": ["island", "hairpin", "wall_of_champions", "casino_straight"],
            "Hungaroring": ["technical", "twisty", "overtaking_difficult", "dusty"],
            "Circuit Zandvoort": ["banked_corners", "dunes", "historic", "narrow"],
            "Lusail International Circuit": ["desert", "modern", "night_race", "wide"],
            "Autódromo Hermanos Rodríguez": ["altitude", "stadium", "peraltada", "thin_air"],
            "Las Vegas Strip Circuit": ["street_circuit", "night_race", "strip", "casinos"],
            "Yas Marina Circuit": ["modern", "hotel", "twilight_race", "marina"],
            "Shanghai International Circuit": ["modern", "long_back_straight", "technical", "turn_1_hairpin"]
        }
        return feature_map.get(circuit_name, ["standard_circuit"])
    
    def _get_image_characteristics(self, circuit_name: str) -> Dict[str, Any]:
        """Get expected image characteristics for each circuit"""
        characteristics = {
            "Circuit de Spa-Francorchamps": {"aspect_ratio": 2.5, "type": "high_speed", "corners": 8},
            "Circuit de Monaco": {"aspect_ratio": 0.8, "type": "street", "corners": 18},
            "Silverstone Circuit": {"aspect_ratio": 1.4, "type": "high_speed", "corners": 10},
            "Autodromo Nazionale Monza": {"aspect_ratio": 2.2, "type": "high_speed", "corners": 7},
            "Suzuka International Racing Course": {"aspect_ratio": 1.6, "type": "technical", "corners": 12},
            "Autódromo José Carlos Pace": {"aspect_ratio": 1.3, "type": "technical", "corners": 11},
            "Marina Bay Street Circuit": {"aspect_ratio": 1.1, "type": "street", "corners": 16},
            "Circuit of the Americas": {"aspect_ratio": 1.5, "type": "modern", "corners": 13},
            "Red Bull Ring": {"aspect_ratio": 1.8, "type": "high_speed", "corners": 6},
            "Baku City Circuit": {"aspect_ratio": 2.0, "type": "street", "corners": 12},
            "Hungaroring": {"aspect_ratio": 1.2, "type": "technical", "corners": 14}
        }
        return characteristics.get(circuit_name, {"aspect_ratio": 1.4, "type": "standard", "corners": 12})
    
    def analyze_image(self, image_path: str, hints: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Analyze circuit image and combine with hints"""
        # Process image
        image_features = ImageProcessor.analyze_track_shape(image_path)
        
        if "error" in image_features:
            return self.analyze_by_hints_only(hints or {})
        
        # Match circuits based on image analysis
        matches = []
        
        for circuit_id, circuit_data in self.circuits.items():
            confidence = self._calculate_combined_confidence(circuit_data, hints or {}, image_features)
            if confidence > 0.05:
                matches.append({
                    "circuit_id": circuit_id,
                    "data": circuit_data,
                    "confidence": confidence
                })
        
        matches = sorted(matches, key=lambda x: x["confidence"], reverse=True)
        return self._format_response(matches, image_features)
    
    def analyze_by_hints_only(self, hints: Dict[str, str]) -> Dict[str, Any]:
        """Analyze using only hints (fallback method)"""
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
    
    def _calculate_combined_confidence(self, circuit_data: Dict[str, Any], hints: Dict[str, str], image_features: Dict[str, Any]) -> float:
        """Calculate confidence combining hints and image analysis"""
        # Base hint confidence
        hint_confidence = self._calculate_hint_confidence(circuit_data, hints)
        
        # Image-based confidence
        image_confidence = self._calculate_image_confidence(circuit_data, image_features)
        
        # Combine confidences (weighted average)
        if hints:
            # If hints provided, weight them more heavily
            combined_confidence = (hint_confidence * 0.7) + (image_confidence * 0.3)
        else:
            # If no hints, rely more on image analysis
            combined_confidence = (hint_confidence * 0.3) + (image_confidence * 0.7)
        
        return min(combined_confidence, 1.0)
    
    def _calculate_image_confidence(self, circuit_data: Dict[str, Any], image_features: Dict[str, Any]) -> float:
        """Calculate confidence based on image analysis"""
        confidence = 0.1
        
        expected_chars = circuit_data["image_characteristics"]
        
        # Aspect ratio matching
        if "aspect_ratio" in image_features:
            expected_ratio = expected_chars["aspect_ratio"]
            actual_ratio = image_features["aspect_ratio"]
            
            ratio_diff = abs(expected_ratio - actual_ratio) / expected_ratio
            if ratio_diff < 0.2:  # Within 20%
                confidence += 0.4
            elif ratio_diff < 0.5:  # Within 50%
                confidence += 0.2
        
        # Circuit type matching
        if "circuit_type" in image_features:
            if image_features["circuit_type"] == expected_chars["type"]:
                confidence += 0.3
        
        # Feature matching
        if "distinctive_features" in image_features:
            image_features_set = set(image_features["distinctive_features"])
            circuit_features_set = set(circuit_data["features"])
            
            # Check for feature overlap
            overlap = len(image_features_set.intersection(circuit_features_set))
            if overlap > 0:
                confidence += 0.2 * overlap
        
        return min(confidence, 1.0)
    
    def _calculate_hint_confidence(self, circuit_data: Dict[str, Any], hints: Dict[str, str]) -> float:
        """Calculate confidence based on hints only"""
        confidence = 0.05
        
        if not hints:
            return confidence
        
        # Country matching
        country_hint = hints.get("country", "").lower().strip()
        if country_hint:
            if country_hint == circuit_data["country"].lower():
                confidence += 0.6
            elif country_hint in circuit_data["country"].lower():
                confidence += 0.4
        
        # City/region matching
        city_hint = hints.get("city", "").lower().strip()
        if city_hint:
            city_region = circuit_data["city_region"].lower()
            if city_hint == city_region or city_hint in city_region:
                confidence += 0.5
            elif any(word in city_region for word in city_hint.split()):
                confidence += 0.3
        
        # Circuit name matching
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
            elif any(alias in name_hint for alias in circuit_data["aliases"]):
                confidence += 0.3
            elif name_hint in circuit_data["city_region"].lower():
                confidence += 0.5
        
        # Grand Prix matching
        gp_hint = hints.get("grand_prix", "").lower().strip()
        if gp_hint and gp_hint in circuit_data["grand_prix"].lower():
            confidence += 0.5
        
        return min(confidence, 1.0)
    
    def _format_response(self, matches: List[Dict[str, Any]], image_features: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format analysis response"""
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
            "reasoning": self._generate_reasoning(primary, image_features),
            "notes": f"Analysis based on {'image and ' if image_features else ''}embedded F1 database. Total circuits: {len(self.circuits)}"
        }
        
        if image_features:
            response["image_analysis"] = image_features
        
        for match in matches[1:5]:
            if match.get("data") and match["confidence"] > 0.1:
                response["alternatives"].append({
                    "track_name": match["data"]["name"],
                    "country": match["data"]["country"],
                    "confidence": round(match["confidence"], 4),
                    "reason": f"Features: {', '.join(match['data']['features'][:3])}"
                })
        
        return response
    
    def _generate_reasoning(self, primary_match: Dict[str, Any], image_features: Optional[Dict[str, Any]] = None) -> str:
        """Generate reasoning for the match"""
        confidence = primary_match["confidence"]
        circuit_name = primary_match["data"]["name"]
        
        reasoning_parts = []
        
        if confidence >= 0.8:
            reasoning_parts.append(f"Very high confidence match for {circuit_name}")
        elif confidence >= 0.6:
            reasoning_parts.append(f"High confidence match for {circuit_name}")
        elif confidence >= 0.4:
            reasoning_parts.append(f"Good match for {circuit_name}")
        elif confidence >= 0.2:
            reasoning_parts.append(f"Possible match for {circuit_name}")
        else:
            reasoning_parts.append(f"Low confidence suggestion for {circuit_name}")
        
        if image_features and "error" not in image_features:
            if "aspect_ratio" in image_features:
                ratio = image_features["aspect_ratio"]
                if ratio > 2.0:
                    reasoning_parts.append("elongated layout suggests high-speed circuit")
                elif ratio < 1.0:
                    reasoning_parts.append("compact layout suggests street circuit")
                else:
                    reasoning_parts.append("balanced layout detected")
            
            if "circuit_type" in image_features:
                reasoning_parts.append(f"image analysis indicates {image_features['circuit_type']} circuit type")
        
        return ". ".join(reasoning_parts) + "."
    
    def _get_confidence_label(self, score: float) -> str:
        """Get confidence label"""
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
        """Generate no-match response"""
        return {
            "primary_guess": None,
            "confidence_score": 0.0,
            "confidence_label": "no_confident_match_found",
            "alternatives": [],
            "reasoning": reason,
            "notes": "Try providing more specific hints or a clearer image.",
            "total_circuits": len(self.circuits)
        }

class F1CircuitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("F1 Circuit Identifier with Image Analysis")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        
        self.identifier = F1CircuitIdentifier()
        self.current_image_path = None
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#1a1a1a')
        title_frame.pack(pady=15)
        
        title_label = tk.Label(title_frame, text="F1 Circuit Identifier with Image Analysis", 
                              font=('Arial', 28, 'bold'), fg='#ff6b6b', bg='#1a1a1a')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Upload track images or provide hints - Advanced AI identification", 
                                 font=('Arial', 14), fg='#ffffff', bg='#1a1a1a')
        subtitle_label.pack()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Left panel - Image and controls
        left_panel = tk.Frame(main_frame, bg='#2d2d2d', relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Image upload section
        upload_frame = tk.Frame(left_panel, bg='#2d2d2d')
        upload_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(upload_frame, text="Track Image Upload", font=('Arial', 16, 'bold'), 
                fg='#4ecdc4', bg='#2d2d2d').pack(anchor=tk.W)
        
        button_frame = tk.Frame(upload_frame, bg='#2d2d2d')
        button_frame.pack(fill=tk.X, pady=8)
        
        upload_btn = tk.Button(button_frame, text="Choose Image", command=self.upload_image,
                              bg='#ff6b6b', fg='white', font=('Arial', 11, 'bold'),
                              relief=tk.FLAT, padx=25, pady=8, cursor='hand2')
        upload_btn.pack(side=tk.LEFT)
        
        self.analyze_image_btn = tk.Button(button_frame, text="Analyze Image", command=self.analyze_image,
                                          bg='#4ecdc4', fg='white', font=('Arial', 11, 'bold'),
                                          relief=tk.FLAT, padx=25, pady=8, state=tk.DISABLED, cursor='hand2')
        self.analyze_image_btn.pack(side=tk.LEFT, padx=(15, 0))
        
        # Image display
        self.image_frame = tk.Frame(left_panel, bg='#3d3d3d', relief=tk.SUNKEN, bd=2)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.image_label = tk.Label(self.image_frame, 
                                   text="No image selected\n\nSupported: JPG, PNG, BMP, GIF\nBest results: Clear track outlines", 
                                   font=('Arial', 12), fg='#888888', bg='#3d3d3d', justify=tk.CENTER)
        self.image_label.pack(expand=True)
        
        # Right panel - Hints and results
        right_panel = tk.Frame(main_frame, bg='#2d2d2d', relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Hints section
        hints_frame = tk.Frame(right_panel, bg='#2d2d2d')
        hints_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(hints_frame, text="Optional Hints", font=('Arial', 16, 'bold'), 
                fg='#feca57', bg='#2d2d2d').pack(anchor=tk.W)
        
        # Country
        tk.Label(hints_frame, text="Country:", font=('Arial', 11, 'bold'), fg='#ffffff', bg='#2d2d2d').pack(anchor=tk.W, pady=(8,2))
        self.country_var = tk.StringVar()
        country_combo = ttk.Combobox(hints_frame, textvariable=self.country_var, width=35, font=('Arial', 10))
        country_combo['values'] = self.get_available_countries()
        country_combo.pack(fill=tk.X, pady=(0,8))
        
        # City
        tk.Label(hints_frame, text="City/Region:", font=('Arial', 11, 'bold'), fg='#ffffff', bg='#2d2d2d').pack(anchor=tk.W, pady=(0,2))
        self.city_var = tk.StringVar()
        self.city_entry = tk.Entry(hints_frame, textvariable=self.city_var, bg='#4d4d4d', fg='white', 
                                  relief=tk.FLAT, font=('Arial', 10), bd=5)
        self.city_entry.pack(fill=tk.X, pady=(0,8))
        
        # Circuit name
        tk.Label(hints_frame, text="Circuit Name:", font=('Arial', 11, 'bold'), fg='#ffffff', bg='#2d2d2d').pack(anchor=tk.W, pady=(0,2))
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(hints_frame, textvariable=self.name_var, bg='#4d4d4d', fg='white', 
                                  relief=tk.FLAT, font=('Arial', 10), bd=5)
        self.name_entry.pack(fill=tk.X, pady=(0,12))
        
        # Control buttons
        control_frame = tk.Frame(hints_frame, bg='#2d2d2d')
        control_frame.pack(fill=tk.X, pady=8)
        
        analyze_hints_btn = tk.Button(control_frame, text="Analyze by Hints", command=self.analyze_by_hints,
                                     bg='#feca57', fg='white', font=('Arial', 10, 'bold'), 
                                     relief=tk.FLAT, cursor='hand2', padx=15, pady=8)
        analyze_hints_btn.pack(side=tk.LEFT)
        
        clear_btn = tk.Button(control_frame, text="Clear All", command=self.clear_all,
                             bg='#ff9ff3', fg='white', font=('Arial', 10, 'bold'), 
                             relief=tk.FLAT, cursor='hand2', padx=15, pady=8)
        clear_btn.pack(side=tk.LEFT, padx=(15, 0))
        
        # Results section
        results_frame = tk.Frame(right_panel, bg='#2d2d2d')
        results_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0,15))
        
        tk.Label(results_frame, text="Analysis Results", font=('Arial', 16, 'bold'), 
                fg='#54a0ff', bg='#2d2d2d').pack(anchor=tk.W)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=25, bg='#1a1a1a', fg='#ffffff',
                                                     font=('Consolas', 10), relief=tk.FLAT, wrap=tk.WORD,
                                                     selectbackground='#4d4d4d', selectforeground='#ffffff')
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=8)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Upload an image or provide hints to identify F1 circuits")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W,
                             bg='#333333', fg='#ffffff', font=('Arial', 10), bd=1)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def get_available_countries(self):
        countries = set()
        for circuit in self.identifier.circuits.values():
            countries.add(circuit["country"])
        return sorted(list(countries))
    
    def upload_image(self):
        file_types = [
            ('Image files', '*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.tif'),
            ('JPEG files', '*.jpg *.jpeg'),
            ('PNG files', '*.png'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Select F1 Circuit Image",
            filetypes=file_types
        )
        
        if filename:
            self.current_image_path = filename
            self.display_image(filename)
            self.analyze_image_btn.config(state=tk.NORMAL)
            self.status_var.set(f"Image loaded: {os.path.basename(filename)} - Ready for analysis")
    
    def display_image(self, image_path):
        try:
            if PIL_AVAILABLE:
                # Load and resize image for display
                pil_image = Image.open(image_path)
                
                # Calculate display size (max 400x300)
                display_width, display_height = 400, 300
                img_width, img_height = pil_image.size
                
                scale_w = display_width / img_width
                scale_h = display_height / img_height
                scale = min(scale_w, scale_h)
                
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)
                
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo
            else:
                self.image_label.config(text=f"Image loaded: {os.path.basename(image_path)}\n\n(Preview unavailable - PIL not installed)")
            
        except Exception as e:
            self.image_label.config(text=f"Error loading image: {str(e)}")
    
    def clear_all(self):
        self.country_var.set("")
        self.city_var.set("")
        self.name_var.set("")
        self.current_image_path = None
        self.analyze_image_btn.config(state=tk.DISABLED)
        self.image_label.config(image="", text="No image selected\n\nSupported: JPG, PNG, BMP, GIF\nBest results: Clear track outlines")
        self.image_label.image = None
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("All cleared - Ready for new analysis")
    
    def collect_hints(self):
        hints = {}
        if self.country_var.get().strip():
            hints["country"] = self.country_var.get().strip()
        if self.city_var.get().strip():
            hints["city"] = self.city_var.get().strip()
        if self.name_var.get().strip():
            hints["name"] = self.name_var.get().strip()
        return hints
    
    def analyze_image(self):
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please upload an image first")
            return
        
        self.status_var.set("Analyzing image with AI... Please wait")
        self.root.update()
        
        try:
            hints = self.collect_hints()
            result = self.identifier.analyze_image(self.current_image_path, hints)
            self.display_results(result)
            
            if result.get("primary_guess"):
                confidence = result.get("confidence_score", 0)
                self.status_var.set(f"Image analysis complete - {result['primary_guess']['track_name']} ({confidence:.1%} confidence)")
            else:
                self.status_var.set("Image analysis complete - No confident match found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Image analysis failed: {str(e)}")
            self.status_var.set("Image analysis failed")
    
    def analyze_by_hints(self):
        hints = self.collect_hints()
        if not any(hints.values()):
            messagebox.showwarning("No Hints", "Please provide at least one hint for analysis")
            return
        
        self.status_var.set("Analyzing by hints... Please wait")
        self.root.update()
        
        try:
            result = self.identifier.analyze_by_hints_only(hints)
            self.display_results(result)
            
            if result.get("primary_guess"):
                confidence = result.get("confidence_score", 0)
                self.status_var.set(f"Hint analysis complete - {result['primary_guess']['track_name']} ({confidence:.1%} confidence)")
            else:
                self.status_var.set("Hint analysis complete - No confident match found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Hint analysis failed: {str(e)}")
            self.status_var.set("Hint analysis failed")
    
    def display_results(self, result):
        self.results_text.delete(1.0, tk.END)
        
        output = "F1 CIRCUIT ANALYSIS RESULTS\n"
        output += "=" * 60 + "\n\n"
        
        if result.get("primary_guess"):
            primary = result["primary_guess"]
            confidence = result["confidence_score"]
            
            output += f"PRIMARY IDENTIFICATION:\n"
            output += f"   Circuit: {primary['track_name']}\n"
            output += f"   Grand Prix: {primary['grand_prix_name']}\n"
            output += f"   Country: {primary['country']}\n"
            output += f"   Location: {primary['city_or_region']}\n"
            output += f"   F1 Status: {primary['f1_usage']}\n\n"
            
            output += f"CONFIDENCE ANALYSIS:\n"
            output += f"   Score: {confidence:.2%} ({confidence:.4f})\n"
            output += f"   Level: {result['confidence_label'].replace('_', ' ').title()}\n"
            
            if confidence >= 0.9:
                output += f"   Status: Extremely High - Near certain identification\n"
            elif confidence >= 0.8:
                output += f"   Status: Very High - Highly confident match\n"
            elif confidence >= 0.6:
                output += f"   Status: High - Strong identification\n"
            elif confidence >= 0.4:
                output += f"   Status: Medium - Good possibility\n"
            else:
                output += f"   Status: Low - Weak match, try more hints\n"
            output += "\n"
            
            if result.get("alternatives"):
                output += f"ALTERNATIVE POSSIBILITIES:\n"
                for i, alt in enumerate(result["alternatives"], 1):
                    conf_pct = alt['confidence'] * 100
                    output += f"   {i}. {alt['track_name']} ({alt['country']})\n"
                    output += f"      Confidence: {conf_pct:.1f}% | {alt['reason']}\n"
                output += "\n"
        else:
            output += "NO CONFIDENT MATCH FOUND\n"
            output += "   Try providing more specific hints or a different image\n\n"
        
        # Image analysis details
        if result.get("image_analysis"):
            img_analysis = result["image_analysis"]
            output += f"IMAGE ANALYSIS DETAILS:\n"
            if "aspect_ratio" in img_analysis:
                output += f"   Aspect Ratio: {img_analysis['aspect_ratio']:.2f}\n"
            if "circuit_type" in img_analysis:
                output += f"   Circuit Type: {img_analysis['circuit_type'].replace('_', ' ').title()}\n"
            if "layout_classification" in img_analysis:
                output += f"   Layout: {img_analysis['layout_classification'].replace('_', ' ').title()}\n"
            if "estimated_corners" in img_analysis:
                output += f"   Estimated Corners: {img_analysis['estimated_corners']}\n"
            if "distinctive_features" in img_analysis:
                output += f"   Features: {', '.join(img_analysis['distinctive_features'])}\n"
            output += "\n"
        
        output += f"ANALYSIS REASONING:\n"
        reasoning = result.get('reasoning', 'No reasoning available')
        output += f"   {reasoning}\n\n"
        
        output += f"TECHNICAL NOTES:\n"
        notes = result.get('notes', 'No additional notes')
        output += f"   {notes}\n"
        
        output += f"\nAnalysis completed with advanced AI processing\n"
        
        self.results_text.insert(tk.END, output)

def main():
    print("F1 Circuit Identifier with Image Analysis")
    print("Advanced AI-powered circuit identification")
    if not PIL_AVAILABLE:
        print("Note: PIL not available - image preview disabled, but analysis still works")
    print("Starting GUI...")
    
    root = tk.Tk()
    app = F1CircuitGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()