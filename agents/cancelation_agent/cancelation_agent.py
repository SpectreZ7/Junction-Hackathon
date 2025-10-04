# Uber Data Intelligence Agent - CSV Version

import pandas as pd
from datetime import datetime
import json
from typing import Dict
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

CITY = "New York"
HOURS_AHEAD = 12

# Chemins des fichiers CSV
CANCELLATION_CSV_PATH = "cancellation_data.csv"
SURGE_CSV_PATH = "surge_data.csv"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0.4
MAX_TOKENS = 1500

# Thresholds
HIGH_CANCELLATION_THRESHOLD = 15  # percent
LOW_CANCELLATION_THRESHOLD = 5    # percent
HIGH_SURGE_THRESHOLD = 1.5
MINIMUM_JOBS_THRESHOLD = 50

# ============================================================================
# CSV Data Loader
# ============================================================================

class UberDataLoader:
    """Charge les données Uber depuis des fichiers CSV"""
    
    def __init__(self, cancellation_path: str, surge_path: str):
        self.cancellation_path = cancellation_path
        self.surge_path = surge_path
    
    def load_cancellation_data(self) -> pd.DataFrame:
        """
        Charge les données d'annulation depuis un CSV
        
        Format attendu du CSV:
        city_id, hexagon_id9, job_count, cancellation_rate_pct
        """
        try:
            # Lecture avec options de parsing plus flexibles
            df = pd.read_csv(
                self.cancellation_path,
                encoding='utf-8',
                sep=',',
                quotechar='"',
                escapechar='\\',
                on_bad_lines='warn',  # Affiche un warning au lieu de crasher
                engine='python'  # Parser Python plus tolérant
            )
            
            # Validation des colonnes requises
            required_columns = ['city_id', 'hexagon_id9', 'job_count', 'cancellation_rate_pct']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Colonnes manquantes dans {self.cancellation_path}: {missing_columns}")
            
            # Nettoyage: supprimer les lignes avec des valeurs manquantes critiques
            df = df.dropna(subset=['hexagon_id9', 'cancellation_rate_pct'])
            
            print(f"✓ Données d'annulation chargées: {len(df)} zones")
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Fichier non trouvé: {self.cancellation_path}")
        except Exception as e:
            print(f"\n⚠️  Erreur de parsing du CSV. Tentative avec des options alternatives...")
            try:
                # Tentative avec séparateur alternatif
                df = pd.read_csv(
                    self.cancellation_path,
                    encoding='utf-8',
                    sep=None,  # Détection automatique du séparateur
                    engine='python',
                    on_bad_lines='skip'  # Ignore les lignes problématiques
                )
                print(f"✓ Données chargées avec détection automatique du séparateur")
                return df
            except:
                raise Exception(f"Erreur lors du chargement de {self.cancellation_path}: {str(e)}")
    
    def load_surge_data(self) -> pd.DataFrame:
        """
        Charge les données de surge depuis un CSV
        
        Format attendu du CSV:
        city_id, hour, surge_multiplier
        """
        try:
            # Lecture avec options de parsing plus flexibles
            df = pd.read_csv(
                self.surge_path,
                encoding='utf-8',
                sep=',',
                quotechar='"',
                escapechar='\\',
                on_bad_lines='warn',
                engine='python'
            )
            
            # Validation des colonnes requises
            required_columns = ['city_id', 'hour', 'surge_multiplier']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Colonnes manquantes dans {self.surge_path}: {missing_columns}")
            
            # Nettoyage
            df = df.dropna(subset=['surge_multiplier', 'hour'])
            
            print(f"✓ Données de surge chargées: {len(df)} entrées")
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Fichier non trouvé: {self.surge_path}")
        except Exception as e:
            print(f"\n⚠️  Erreur de parsing du CSV. Tentative avec des options alternatives...")
            try:
                df = pd.read_csv(
                    self.surge_path,
                    encoding='utf-8',
                    sep=None,
                    engine='python',
                    on_bad_lines='skip'
                )
                print(f"✓ Données chargées avec détection automatique du séparateur")
                return df
            except:
                raise Exception(f"Erreur lors du chargement de {self.surge_path}: {str(e)}")


class UberDataAgentConfig:
    def __init__(self, city: str, hours_ahead: int):
        self.groq_api_key = GROQ_API_KEY
        self.groq_model = GROQ_MODEL
        self.city = city
        self.hours_ahead = hours_ahead
        self.temperature = TEMPERATURE
        self.max_tokens = MAX_TOKENS
        
        self.system_prompt = """You are an AI agent specialized in analyzing Uber operational data.
You identify zones with high earnings potential and low cancellation rates.
Respond ONLY in valid JSON."""


config = UberDataAgentConfig(city=CITY, hours_ahead=HOURS_AHEAD)


class UberDataIntelligenceAgent:
    def __init__(self, config: UberDataAgentConfig, data_loader: UberDataLoader):
        self.config = config
        self.agent_id = f"uber_data_agent_{config.city.lower().replace(' ', '_')}"
        self.groq_client = Groq(api_key=config.groq_api_key)
        self.data_loader = data_loader
    
    def get_recommendation(self) -> Dict:
        """Main entry point"""
        
        # Charger les données depuis les CSV
        print("Chargement des données...")
        cancellation_df = self.data_loader.load_cancellation_data()
        surge_df = self.data_loader.load_surge_data()
        
        return self.analyze_with_ai(cancellation_df, surge_df)
    
    def analyze_with_ai(self, cancellation_df: pd.DataFrame, surge_df: pd.DataFrame) -> Dict:
        """Analyse les données avec Groq AI"""
        
        now = datetime.now()
        
        # Préparation de l'analyse par zone
        zones_analysis = []
        
        for _, zone in cancellation_df.iterrows():
            zone_id = str(zone['hexagon_id9'])  # Utiliser directement l'ID de la zone
            
            # Obtenir les données de surge pour les prochaines heures (toutes zones confondues car pas de hexagon_id9 dans surge)
            upcoming_hours = [(now.hour + i) % 24 for i in range(1, 7)]
            zone_surge = surge_df[surge_df['hour'].isin(upcoming_hours)]
            
            # Calculer la moyenne de surge pour les prochaines heures
            avg_surge = zone_surge['surge_multiplier'].mean() if len(zone_surge) > 0 else 1.0
            max_surge = zone_surge['surge_multiplier'].max() if len(zone_surge) > 0 else 1.0
            
            # Calcul du score de zone
            cancellation_penalty = zone['cancellation_rate_pct'] / 100
            surge_bonus = avg_surge
            score = (surge_bonus * 100) * (1 - cancellation_penalty)
            
            # Classification de la qualité
            if zone['cancellation_rate_pct'] < LOW_CANCELLATION_THRESHOLD and avg_surge > HIGH_SURGE_THRESHOLD:
                quality = "excellent"
            elif zone['cancellation_rate_pct'] < HIGH_CANCELLATION_THRESHOLD and avg_surge > 1.2:
                quality = "good"
            elif zone['cancellation_rate_pct'] > HIGH_CANCELLATION_THRESHOLD:
                quality = "poor"
            else:
                quality = "average"
            
            zones_analysis.append({
                'zone_id': zone_id,  # Code de zone au lieu de nom
                'cancellation_rate': float(zone['cancellation_rate_pct']),
                'avg_surge_next_6h': round(float(avg_surge), 2),
                'max_surge_next_6h': round(float(max_surge), 2),
                'job_count': int(zone['job_count']),
                'quality': quality,
                'score': round(float(score), 2)
            })
        
        # Tri par score
        zones_analysis.sort(key=lambda x: x['score'], reverse=True)
        
        # Obtenir les pics de surge
        now_hour = now.hour
        next_hours = [(now_hour + i) % 24 for i in range(1, self.config.hours_ahead)]
        upcoming_surge = surge_df[surge_df['hour'].isin(next_hours)]
        
        surge_peaks = upcoming_surge.groupby('hour').agg({
            'surge_multiplier': 'mean'
        }).reset_index()
        
        surge_peaks = surge_peaks[surge_peaks['surge_multiplier'] > 1.5].sort_values('surge_multiplier', ascending=False)
        
        surge_times = []
        for _, row in surge_peaks.head(5).iterrows():
            surge_times.append({
                'hour': int(row['hour']),
                'avg_surge': round(float(row['surge_multiplier']), 2)
            })
        
        # Préparation du prompt pour l'IA
        user_prompt = f"""Analyze Uber data for {self.config.city}:

TOP ZONES (by score):
{json.dumps(zones_analysis[:10], indent=2)}

HIGH SURGE HOURS:
{json.dumps(surge_times, indent=2)}

Identify ALL optimal zones and time windows. Use ONLY zone_id codes (do NOT create zone names). Provide MULTIPLE recommendations ranked by priority. Respond in JSON:
{{
    "peaks_identified": [
        {{
            "time_window": "17:00-19:00",
            "zone_id": "88283082a9fffff",
            "avg_surge": 2.5,
            "cancellation_rate": 12.5,
            "priority": "high",
            "reasoning": "High surge with acceptable cancellation"
        }},
        {{
            "time_window": "08:00-10:00",
            "zone_id": "88283082bbfffff",
            "avg_surge": 2.2,
            "cancellation_rate": 8.5,
            "priority": "high",
            "reasoning": "Morning rush with low cancellation"
        }},
        {{
            "time_window": "12:00-14:00",
            "zone_id": "88283082ccfffff",
            "avg_surge": 1.8,
            "cancellation_rate": 10.0,
            "priority": "medium",
            "reasoning": "Lunch time decent surge"
        }}
    ],
    "zones_to_avoid": [
        {{
            "zone_id": "88283082ddfffff",
            "reason": "High cancellation rate (20%)",
            "cancellation_rate": 20.0
        }},
        {{
            "zone_id": "88283082eeffffff",
            "reason": "Low surge and high cancellation",
            "cancellation_rate": 18.5
        }}
    ],
    "top_recommendations": [
        {{
            "rank": 1,
            "action": "go",
            "target_zone_id": "88283082a9fffff",
            "target_time": "17:00-19:00",
            "reasoning": "Best surge + low cancellation combination",
            "expected_revenue_multiplier": 2.5,
            "confidence": 0.90
        }},
        {{
            "rank": 2,
            "action": "go",
            "target_zone_id": "88283082bbfffff",
            "target_time": "08:00-10:00",
            "reasoning": "Second best option with morning rush",
            "expected_revenue_multiplier": 2.2,
            "confidence": 0.85
        }},
        {{
            "rank": 3,
            "action": "consider",
            "target_zone_id": "88283082ccfffff",
            "target_time": "12:00-14:00",
            "reasoning": "Good backup option during lunch hours",
            "expected_revenue_multiplier": 1.8,
            "confidence": 0.75
        }}
    ],
    "analysis": "Comprehensive summary of data insights covering all opportunities"
}}

CRITICAL: Use ONLY the zone_id codes from the data provided. Do NOT invent zone names. Reference zones by their hexagon_id9 codes ONLY."""

        try:
            print("Analyse des données avec l'IA...")
            chat_completion = self.groq_client.chat.completions.create(
                model=self.config.groq_model,
                messages=[
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            ai_response = chat_completion.choices[0].message.content
            
            # Parser le JSON
            cleaned = ai_response.strip()
            if cleaned.startswith('```'):
                lines = cleaned.split('\n')
                cleaned = '\n'.join([l for l in lines if not l.strip().startswith('```')])
            
            json_start = cleaned.find('{')
            json_end = cleaned.rfind('}') + 1
            ai_analysis = json.loads(cleaned[json_start:json_end])
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat(),
                'city': self.config.city,
                'zones_analyzed': len(zones_analysis),
                'ai_analysis': ai_analysis,
                'raw_data': {
                    'top_zones': zones_analysis[:5],
                    'surge_peaks': surge_times
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'zones_analyzed': len(zones_analysis),
                'raw_data': {
                    'top_zones': zones_analysis[:5],
                    'surge_peaks': surge_times
                }
            }


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    # Initialiser le chargeur de données
    data_loader = UberDataLoader(
        cancellation_path=CANCELLATION_CSV_PATH,
        surge_path=SURGE_CSV_PATH
    )
    
    # Créer l'agent
    agent = UberDataIntelligenceAgent(config=config, data_loader=data_loader)
    
    # Obtenir la recommandation
    result = agent.get_recommendation()
    
    # Afficher le résultat
    print("\n" + "="*80)
    print("RÉSULTAT DE L'ANALYSE")
    print("="*80)
    print(json.dumps(result, indent=2, ensure_ascii=False))