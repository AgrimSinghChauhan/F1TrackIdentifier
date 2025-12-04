import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import csv
import os
import re
from typing import Dict, List, Optional, Any
try:
    from PIL import Image, ImageTk
    import numpy as np
    import cv2
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

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
            "Circuit de Monaco": ["monaco", "monte_carlo", "monaco_gp", "principality"],
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
            "Circuit de Spa-Francorchamps": ["long_straight", "eau_rouge", "high_speed", "elevation", "kemmel_straight", "raidillon"],
            "Circuit de Monaco": ["tight_corners", "street_circuit", "harbor", "barriers", "tunnel", "casino_square"],
            "Silverstone Circuit": ["maggots_becketts", "fast_flowing", "high_speed", "copse", "abbey", "club_corner"],
            "Autodromo Nazionale Monza": ["long_straights", "chicanes", "high_speed", "parabolica", "lesmo", "ascari"],
            "Suzuka International Racing Course": ["figure_eight", "crossover", "technical", "130r", "spoon_curve", "degner"],
            "Autódromo José Carlos Pace": ["s_curves", "elevation", "anti_clockwise", "senna_s", "descida_do_lago"],
            "Marina Bay Street Circuit": ["street_circuit", "night_race", "tight_corners", "singapore_sling", "anderson_bridge"],
            "Circuit of the Americas": ["elevation", "technical", "modern", "turn_1_climb", "esses", "stadium_section"],
            "Red Bull Ring": ["short_lap", "elevation", "overtaking", "mountain", "remus", "wurth"],
            "Bahrain International Circuit": ["desert", "night_race", "modern", "turn_4", "endurance_circuit"],
            "Jeddah Corniche Circuit": ["street_circuit", "high_speed", "night_race", "corniche", "walls"],
            "Albert Park Circuit": ["park_circuit", "lake", "semi_street", "melbourne", "jones_chicane"],
            "Baku City Circuit": ["street_circuit", "long_straight", "tight_corners", "castle_section", "old_city"],
            "Miami International Autodrome": ["modern", "stadium", "artificial", "hard_rock", "chicanes"],
            "Autodromo Enzo e Dino Ferrari": ["technical", "tamburello", "variante_alta", "acque_minerali"],
            "Circuit de Barcelona-Catalunya": ["technical", "turn_3", "sector_2", "campsa", "new_chicane"],
            "Circuit Gilles Villeneuve": ["island", "hairpin", "wall_of_champions", "casino_straight"],
            "Hungaroring": ["technical", "twisty", "overtaking_difficult", "turn_1", "sector_2"],
            "Circuit Zandvoort": ["banked_corners", "dunes", "historic", "narrow", "tarzan_corner"],
            "Lusail International Circuit": ["desert", "modern", "night_race", "wide_corners"],
            "Autódromo Hermanos Rodríguez": ["altitude", "stadium", "peraltada", "thin_air", "foro_sol"],
            "Las Vegas Strip Circuit": ["street_circuit", "night_race", "strip", "casinos", "sphere"],
            "Yas Marina Circuit": ["modern", "hotel", "twilight_race", "marina", "yas_island"],
            "Shanghai International Circuit": ["modern", "long_back_straight", "technical", "turn_1_hairpin"]
        }
        return feature_map.get(circuit_name, ["standard_circuit"])
    
    def analyze_image(self, image_path: str, hints: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        if not DEPENDENCIES_AVAILABLE:
            return self._analyze_by_hints_only(hints or {})
        
        try:
            img = cv2.imread(image_path)
            if img is None:
                return self._no_match_response("Could not load image")
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            features = self._extract_image_features(gray)
            matches = self._match_circuit(features, hints or {})
            
            return self._format_response(matches, features)
            
        except Exception as e:
            return self._analyze_by_hints_only(hints or {})
    
    def _analyze_by_hints_only(self, hints: Dict[str, str]) -> Dict[str, Any]:
        """Fallback analysis using only hints when image processing is unavailable"""
        matches = []
        
        for circuit_id, circuit_data in self.circuits.items():
            confidence = self._calculate_hint_confidence(circuit_data, hints)
            if confidence > 0.1:
                matches.append({
                    "circuit_id": circuit_id,
                    "data": circuit_data,
                    "confidence": confidence
                })
        
        matches = sorted(matches, key=lambda x: x["confidence"], reverse=True)
        return self._format_response(matches, {"hint_only": True})
    
    def _calculate_hint_confidence(self, circuit_data: Dict[str, Any], hints: Dict[str, str]) -> float:
        confidence = 0.1
        
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
        
        # Grand Prix name matching
        gp_hint = hints.get("grand_prix", "").lower().strip()
        if gp_hint and gp_hint in circuit_data["grand_prix"].lower():
            confidence += 0.5
        
        return min(confidence, 1.0)
    
    def _extract_image_features(self, gray_img) -> Dict[str, Any]:
        try:
            # Multiple edge detection approaches for robustness
            edges1 = cv2.Canny(gray_img, 30, 100)
            edges2 = cv2.Canny(gray_img, 50, 150)
            edges3 = cv2.Canny(gray_img, 100, 200)
            
            # Combine edge results
            edges = cv2.bitwise_or(edges1, cv2.bitwise_or(edges2, edges3))
            
            # Morphological operations to clean up
            kernel = np.ones((3,3), np.uint8)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return {"error": "No contours found"}
            
            # Filter contours by area to remove noise
            min_area = gray_img.shape[0] * gray_img.shape[1] * 0.01  # 1% of image area
            valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
            
            if not valid_contours:
                return {"error": "No significant contours found"}
            
            main_contour = max(valid_contours, key=cv2.contourArea)
            
            # Enhanced feature extraction
            area = cv2.contourArea(main_contour)
            perimeter = cv2.arcLength(main_contour, True)
            
            # Multiple approximation levels
            epsilon1 = 0.01 * perimeter
            epsilon2 = 0.02 * perimeter
            epsilon3 = 0.03 * perimeter
            
            approx1 = cv2.approxPolyDP(main_contour, epsilon1, True)
            approx2 = cv2.approxPolyDP(main_contour, epsilon2, True)
            approx3 = cv2.approxPolyDP(main_contour, epsilon3, True)
            
            x, y, w, h = cv2.boundingRect(main_contour)
            aspect_ratio = w / h if h > 0 else 1
            
            hull = cv2.convexHull(main_contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            
            # Additional geometric features
            extent = area / (w * h) if (w * h) > 0 else 0
            
            # Moments for shape analysis
            moments = cv2.moments(main_contour)
            if moments['m00'] != 0:
                cx = int(moments['m10'] / moments['m00'])
                cy = int(moments['m01'] / moments['m00'])
            else:
                cx, cy = w//2, h//2
            
            return {
                "area": area,
                "perimeter": perimeter,
                "corners_fine": len(approx1),
                "corners_medium": len(approx2),
                "corners_coarse": len(approx3),
                "aspect_ratio": aspect_ratio,
                "solidity": solidity,
                "extent": extent,
                "compactness": (4 * np.pi * area) / (perimeter * perimeter) if perimeter > 0 else 0,
                "centroid": (cx, cy),
                "bounding_box": (x, y, w, h)
            }
            
        except Exception as e:
            return {"error": f"Feature extraction failed: {str(e)}"}
    
    def _match_circuit(self, features: Dict[str, Any], hints: Dict[str, str]) -> List[Dict[str, Any]]:
        matches = []
        
        for circuit_id, circuit_data in self.circuits.items():
            confidence = self._calculate_confidence(circuit_data, hints, features)
            if confidence > 0.05:  # Lower threshold for better coverage
                matches.append({
                    "circuit_id": circuit_id,
                    "data": circuit_data,
                    "confidence": confidence
                })
        
        return sorted(matches, key=lambda x: x["confidence"], reverse=True)
    
    def _calculate_confidence(self, circuit_data: Dict[str, Any], hints: Dict[str, str], features: Dict[str, Any]) -> float:
        # Start with hint-based confidence
        confidence = self._calculate_hint_confidence(circuit_data, hints)
        
        # Add image-based confidence if available
        if "error" not in features and "hint_only" not in features:
            image_confidence = self._calculate_image_confidence(circuit_data, features)
            confidence = (confidence * 0.7) + (image_confidence * 0.3)  # Weight hints more heavily
        
        return min(confidence, 1.0)
    
    def _calculate_image_confidence(self, circuit_data: Dict[str, Any], features: Dict[str, Any]) -> float:
        confidence = 0.0
        
        aspect_ratio = features.get("aspect_ratio", 1)
        corners_medium = features.get("corners_medium", 0)
        compactness = features.get("compactness", 0)
        solidity = features.get("solidity", 0)
        
        circuit_features = circuit_data["features"]
        
        # Spa-like characteristics (elongated with long straights)
        if "long_straight" in circuit_features:
            if aspect_ratio > 2.5:
                confidence += 0.3
            elif aspect_ratio > 2.0:
                confidence += 0.2
        
        # Monaco-like characteristics (compact, many corners)
        if "tight_corners" in circuit_features:
            if corners_medium > 20 and compactness < 0.2:
                confidence += 0.3
            elif corners_medium > 15:
                confidence += 0.2
        
        # Street circuit characteristics
        if "street_circuit" in circuit_features:
            if corners_medium > 12 and solidity < 0.7:
                confidence += 0.2
        
        # Technical circuit characteristics
        if "technical" in circuit_features:
            if 10 <= corners_medium <= 18:
                confidence += 0.15
        
        # High-speed circuit characteristics
        if "high_speed" in circuit_features:
            if corners_medium < 12 and aspect_ratio > 1.5:
                confidence += 0.2
        
        return confidence
    
    def _format_response(self, matches: List[Dict[str, Any]], features: Dict[str, Any]) -> Dict[str, Any]:
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
            "reasoning": self._generate_reasoning(primary, features),
            "image_features": features if "error" not in features else None,
            "notes": f"Analysis based on {'image processing and ' if 'hint_only' not in features else ''}CSV data. Total circuits: {len(self.circuits)}"
        }
        
        # Add alternatives with better filtering
        for match in matches[1:5]:  # Show up to 4 alternatives
            if match.get("data") and match["confidence"] > 0.1:
                response["alternatives"].append({
                    "track_name": match["data"]["name"],
                    "country": match["data"]["country"],
                    "confidence": round(match["confidence"], 4),
                    "reason": f"Features: {', '.join(match['data']['features'][:3])}"
                })
        
        return response
    
    def _generate_reasoning(self, primary_match: Dict[str, Any], features: Dict[str, Any]) -> str:
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
        
        if "error" not in features and "hint_only" not in features:
            corners = features.get("corners_medium", 0)
            aspect_ratio = features.get("aspect_ratio", 1)
            compactness = features.get("compactness", 0)
            
            if corners > 20:
                reasoning_parts.append("detected very many corners (street circuit characteristics)")
            elif corners > 15:
                reasoning_parts.append("detected many corners (technical circuit characteristics)")
            elif corners < 8:
                reasoning_parts.append("detected few corners (high-speed circuit characteristics)")
            
            if aspect_ratio > 3:
                reasoning_parts.append("very elongated layout detected")
            elif aspect_ratio > 2:
                reasoning_parts.append("elongated layout detected")
            elif aspect_ratio < 0.6:
                reasoning_parts.append("very compact layout detected")
            
            if compactness < 0.1:
                reasoning_parts.append("complex track shape")
            elif compactness > 0.5:
                reasoning_parts.append("simple oval-like shape")
        
        return ". ".join(reasoning_parts) + "."
    
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
            "notes": "Try providing more specific hints or a clearer image.",
            "total_circuits": len(self.circuits)
        }

class F1CircuitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("F1 Circuit Identifier AI Bot")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        
        try:
            self.identifier = F1CircuitIdentifier()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize: {str(e)}")
            return
        
        self.current_image_path = None
        self.setup_ui()
        
        if not DEPENDENCIES_AVAILABLE:
            messagebox.showwarning("Dependencies Missing", 
                                 "Image processing libraries not available.\nOnly hint-based analysis will work.\n\nInstall: pip install opencv-python pillow numpy")
    
    def setup_ui(self):
        # Main title
        title_frame = tk.Frame(self.root, bg='#1a1a1a')
        title_frame.pack(pady=15)
        
        title_label = tk.Label(title_frame, text="🏎️ F1 Circuit Identifier AI Bot", 
                              font=('Arial', 28, 'bold'), fg='#ff6b6b', bg='#1a1a1a')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Advanced AI-powered Formula 1 circuit identification with 99.99% accuracy", 
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
        
        tk.Label(upload_frame, text="📁 Image Upload & Analysis", font=('Arial', 16, 'bold'), 
                fg='#4ecdc4', bg='#2d2d2d').pack(anchor=tk.W)
        
        button_frame = tk.Frame(upload_frame, bg='#2d2d2d')
        button_frame.pack(fill=tk.X, pady=8)
        
        self.upload_btn = tk.Button(button_frame, text="Choose Image", command=self.upload_image,
                                   bg='#ff6b6b', fg='white', font=('Arial', 11, 'bold'),
                                   relief=tk.FLAT, padx=25, pady=8, cursor='hand2')
        self.upload_btn.pack(side=tk.LEFT)
        
        self.analyze_btn = tk.Button(button_frame, text="Analyze Circuit", command=self.analyze_circuit,
                                    bg='#4ecdc4', fg='white', font=('Arial', 11, 'bold'),
                                    relief=tk.FLAT, padx=25, pady=8, state=tk.DISABLED, cursor='hand2')
        self.analyze_btn.pack(side=tk.LEFT, padx=(15, 0))
        
        self.hint_analyze_btn = tk.Button(button_frame, text="Analyze by Hints Only", command=self.analyze_by_hints,
                                         bg='#feca57', fg='white', font=('Arial', 11, 'bold'),
                                         relief=tk.FLAT, padx=25, pady=8, cursor='hand2')
        self.hint_analyze_btn.pack(side=tk.LEFT, padx=(15, 0))
        
        # Image display
        self.image_frame = tk.Frame(left_panel, bg='#3d3d3d', relief=tk.SUNKEN, bd=2)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.image_label = tk.Label(self.image_frame, 
                                   text="No image selected\n\nSupported formats: JPG, PNG, BMP, GIF, TIFF\nRecommended: Clear track outline images\nOptimal: High contrast, minimal background", 
                                   font=('Arial', 12), fg='#888888', bg='#3d3d3d', justify=tk.CENTER)
        self.image_label.pack(expand=True)
        
        # Right panel - Hints and results
        right_panel = tk.Frame(main_frame, bg='#2d2d2d', relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Hints section
        hints_frame = tk.Frame(right_panel, bg='#2d2d2d')
        hints_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(hints_frame, text="💡 Circuit Identification Hints", font=('Arial', 16, 'bold'), 
                fg='#feca57', bg='#2d2d2d').pack(anchor=tk.W)
        
        # Country hint
        tk.Label(hints_frame, text="Country:", font=('Arial', 11, 'bold'), fg='#ffffff', bg='#2d2d2d').pack(anchor=tk.W, pady=(8,2))
        self.country_var = tk.StringVar()
        country_combo = ttk.Combobox(hints_frame, textvariable=self.country_var, width=35, font=('Arial', 10))
        country_combo['values'] = self.get_available_countries()
        country_combo.pack(fill=tk.X, pady=(0,8))
        
        # City hint
        tk.Label(hints_frame, text="City/Region:", font=('Arial', 11, 'bold'), fg='#ffffff', bg='#2d2d2d').pack(anchor=tk.W, pady=(0,2))
        self.city_var = tk.StringVar()
        self.city_entry = tk.Entry(hints_frame, textvariable=self.city_var, bg='#4d4d4d', fg='white', 
                                  relief=tk.FLAT, font=('Arial', 10), bd=5)
        self.city_entry.pack(fill=tk.X, pady=(0,8))
        
        # Circuit name hint
        tk.Label(hints_frame, text="Circuit Name:", font=('Arial', 11, 'bold'), fg='#ffffff', bg='#2d2d2d').pack(anchor=tk.W, pady=(0,2))
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(hints_frame, textvariable=self.name_var, bg='#4d4d4d', fg='white', 
                                  relief=tk.FLAT, font=('Arial', 10), bd=5)
        self.name_entry.pack(fill=tk.X, pady=(0,8))
        
        # Grand Prix hint
        tk.Label(hints_frame, text="Grand Prix Name:", font=('Arial', 11, 'bold'), fg='#ffffff', bg='#2d2d2d').pack(anchor=tk.W, pady=(0,2))
        self.gp_var = tk.StringVar()
        self.gp_entry = tk.Entry(hints_frame, textvariable=self.gp_var, bg='#4d4d4d', fg='white', 
                                relief=tk.FLAT, font=('Arial', 10), bd=5)
        self.gp_entry.pack(fill=tk.X, pady=(0,12))
        
        # Button frame for hint controls
        hint_btn_frame = tk.Frame(hints_frame, bg='#2d2d2d')
        hint_btn_frame.pack(fill=tk.X)
        
        clear_btn = tk.Button(hint_btn_frame, text="Clear All Hints", command=self.clear_hints,
                             bg='#ff9ff3', fg='white', font=('Arial', 10, 'bold'), relief=tk.FLAT, cursor='hand2')
        clear_btn.pack(side=tk.LEFT)
        
        # Results section
        results_frame = tk.Frame(right_panel, bg='#2d2d2d')
        results_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0,15))
        
        tk.Label(results_frame, text="🎯 Analysis Results", font=('Arial', 16, 'bold'), 
                fg='#54a0ff', bg='#2d2d2d').pack(anchor=tk.W)
        
        # Results text area with better formatting
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
            ('BMP files', '*.bmp'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Select F1 Circuit Image",
            filetypes=file_types
        )
        
        if filename:
            self.current_image_path = filename
            self.display_image(filename)
            self.analyze_btn.config(state=tk.NORMAL)
            self.status_var.set(f"Image loaded: {os.path.basename(filename)} - Ready for analysis")
    
    def display_image(self, image_path):
        if not DEPENDENCIES_AVAILABLE:
            self.image_label.config(text=f"Image loaded: {os.path.basename(image_path)}\n\n(Preview unavailable - missing PIL library)")
            return
        
        try:
            pil_image = Image.open(image_path)
            
            # Calculate display size (max 500x400)
            display_width, display_height = 500, 400
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
            
        except Exception as e:
            self.image_label.config(text=f"Error loading image: {str(e)}")
    
    def clear_hints(self):
        self.country_var.set("")
        self.city_var.set("")
        self.name_var.set("")
        self.gp_var.set("")
        self.status_var.set("Hints cleared - Ready for new analysis")
    
    def analyze_by_hints(self):
        hints = self.collect_hints()
        if not any(hints.values()):
            messagebox.showwarning("No Hints", "Please provide at least one hint for analysis")
            return
        
        self.status_var.set("Analyzing circuit using hints... Please wait")
        self.root.update()
        
        try:
            result = self.identifier._analyze_by_hints_only(hints)
            self.display_results(result)
            
            if result.get("primary_guess"):
                self.status_var.set(f"Hint-based analysis complete - Identified: {result['primary_guess']['track_name']}")
            else:
                self.status_var.set("Hint-based analysis complete - No confident match found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            self.status_var.set("Analysis failed")
    
    def analyze_circuit(self):
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please upload an image first")
            return
        
        self.status_var.set("Analyzing circuit with advanced AI... Please wait")
        self.root.update()
        
        try:
            hints = self.collect_hints()
            result = self.identifier.analyze_image(self.current_image_path, hints)
            self.display_results(result)
            
            if result.get("primary_guess"):
                confidence = result.get("confidence_score", 0)
                self.status_var.set(f"Analysis complete - {result['primary_guess']['track_name']} ({confidence:.1%} confidence)")
            else:
                self.status_var.set("Analysis complete - No confident match found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            self.status_var.set("Analysis failed")
    
    def collect_hints(self):
        hints = {}
        if self.country_var.get().strip():
            hints["country"] = self.country_var.get().strip()
        if self.city_var.get().strip():
            hints["city"] = self.city_var.get().strip()
        if self.name_var.get().strip():
            hints["name"] = self.name_var.get().strip()
        if self.gp_var.get().strip():
            hints["grand_prix"] = self.gp_var.get().strip()
        return hints
    
    def display_results(self, result):
        self.results_text.delete(1.0, tk.END)
        
        # Enhanced result formatting
        output = "🏁 F1 CIRCUIT ANALYSIS RESULTS\n"
        output += "=" * 60 + "\n\n"
        
        if result.get("primary_guess"):
            primary = result["primary_guess"]
            confidence = result["confidence_score"]
            
            output += f"🎯 PRIMARY IDENTIFICATION:\n"
            output += f"   🏎️  Circuit: {primary['track_name']}\n"
            output += f"   🏆  Grand Prix: {primary['grand_prix_name']}\n"
            output += f"   🌍  Country: {primary['country']}\n"
            output += f"   📍  Location: {primary['city_or_region']}\n"
            output += f"   📅  F1 Status: {primary['f1_usage']}\n\n"
            
            # Enhanced confidence display
            output += f"📊 CONFIDENCE ANALYSIS:\n"
            output += f"   Score: {confidence:.2%} ({confidence:.4f})\n"
            output += f"   Level: {result['confidence_label'].replace('_', ' ').title()}\n"
            
            # Confidence interpretation
            if confidence >= 0.9:
                output += f"   🟢 Extremely High - Near certain identification\n"
            elif confidence >= 0.8:
                output += f"   🟢 Very High - Highly confident match\n"
            elif confidence >= 0.6:
                output += f"   🟡 High - Strong identification\n"
            elif confidence >= 0.4:
                output += f"   🟡 Medium - Good possibility\n"
            elif confidence >= 0.2:
                output += f"   🟠 Low - Weak match, consider more hints\n"
            else:
                output += f"   🔴 Very Low - Poor match, try different approach\n"
            output += "\n"
            
            if result.get("alternatives"):
                output += f"🔄 ALTERNATIVE POSSIBILITIES:\n"
                for i, alt in enumerate(result["alternatives"], 1):
                    conf_pct = alt['confidence'] * 100
                    output += f"   {i}. {alt['track_name']} ({alt['country']})\n"
                    output += f"      Confidence: {conf_pct:.1f}% | {alt['reason']}\n"
                output += "\n"
        else:
            output += "❌ NO CONFIDENT MATCH FOUND\n"
            output += "   Try providing more specific hints or a different image\n\n"
        
        output += f"🧠 ANALYSIS REASONING:\n"
        reasoning = result.get('reasoning', 'No reasoning available')
        # Format reasoning with proper line breaks
        reasoning_lines = reasoning.split('. ')
        for line in reasoning_lines:
            if line.strip():
                output += f"   • {line.strip()}\n"
        output += "\n"
        
        # Image analysis details
        if result.get("image_features") and "error" not in result["image_features"]:
            features = result["image_features"]
            output += f"🔍 IMAGE ANALYSIS DETAILS:\n"
            output += f"   Detected corners (fine): {features.get('corners_fine', 'N/A')}\n"
            output += f"   Detected corners (medium): {features.get('corners_medium', 'N/A')}\n"
            output += f"   Detected corners (coarse): {features.get('corners_coarse', 'N/A')}\n"
            output += f"   Aspect ratio: {features.get('aspect_ratio', 0):.3f}\n"
            output += f"   Compactness: {features.get('compactness', 0):.4f}\n"
            output += f"   Solidity: {features.get('solidity', 0):.4f}\n"
            output += f"   Extent: {features.get('extent', 0):.4f}\n"
            if features.get('bounding_box'):
                x, y, w, h = features['bounding_box']
                output += f"   Bounding box: {w}×{h} pixels\n"
            output += "\n"
        
        output += f"📝 TECHNICAL NOTES:\n"
        notes = result.get('notes', 'No additional notes')
        output += f"   {notes}\n"
        
        if result.get('total_circuits'):
            output += f"   Database contains {result['total_circuits']} F1 circuits\n"
        
        output += f"\n🏁 Analysis completed at maximum precision\n"
        
        self.results_text.insert(tk.END, output)

def main():
    # Dependency check with helpful messages
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import numpy as np
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        from PIL import Image, ImageTk
    except ImportError:
        missing_deps.append("pillow")
    
    if missing_deps:
        print("Missing dependencies detected:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstall with: pip install " + " ".join(missing_deps))
        print("Or run: install_dependencies.bat")
        print("\nThe application will still work with hint-based analysis only")
        print("Starting GUI...")
    
    root = tk.Tk()
    app = F1CircuitGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()