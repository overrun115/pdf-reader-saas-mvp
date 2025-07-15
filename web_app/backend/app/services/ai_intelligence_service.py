#!/usr/bin/env python3
"""
AI Intelligence Service - IA avanzada para análisis de documentos
Parte de la Fase 3.2 de la expansión de inteligencia documental
"""

import logging
import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import re
import statistics
from collections import Counter, defaultdict
import hashlib

# Machine Learning and AI libraries
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.decomposition import PCA, LatentDirichletAllocation
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import IsolationForest
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

# NLP libraries
try:
    import spacy
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

# Import existing services
from app.services.advanced_ocr_nlp_service import AdvancedOCRNLPService
from app.services.layout_parser_service import LayoutParserService
from app.services.document_validation_service import DocumentValidationService
from app.services.word_intelligence_service import WordIntelligenceService
from app.services.excel_intelligence_service import ExcelIntelligenceService

logger = logging.getLogger(__name__)

class AnalysisType(str, Enum):
    CONTENT_INTELLIGENCE = "content_intelligence"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    DOCUMENT_CLASSIFICATION = "document_classification"
    SIMILARITY_ANALYSIS = "similarity_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    TREND_ANALYSIS = "trend_analysis"
    ENTITY_RELATIONSHIP = "entity_relationship"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"

class AIModelType(str, Enum):
    CLUSTERING = "clustering"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    TOPIC_MODELING = "topic_modeling"
    ANOMALY_DETECTION = "anomaly_detection"
    SIMILARITY = "similarity"

@dataclass
class AIAnalysisResult:
    """Resultado de análisis de IA"""
    analysis_type: AnalysisType
    confidence: float
    insights: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any]
    processing_time: float
    model_info: Dict[str, Any]

@dataclass
class ContentInsight:
    """Insight específico sobre contenido"""
    type: str
    description: str
    confidence: float
    evidence: List[str]
    impact: str  # high, medium, low
    actionable: bool

@dataclass
class DocumentProfile:
    """Perfil completo de documento"""
    document_id: str
    document_type: str
    content_features: Dict[str, Any]
    structural_features: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    semantic_features: Dict[str, Any]
    fingerprint: str

class AIIntelligenceService:
    """
    Servicio de IA avanzada para análisis inteligente de documentos
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize existing services
        self.ocr_service = AdvancedOCRNLPService()
        self.layout_service = LayoutParserService()
        self.validation_service = DocumentValidationService()
        self.word_service = WordIntelligenceService()
        self.excel_service = ExcelIntelligenceService()
        
        # Initialize NLP
        self.nlp = None
        if NLP_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.logger.warning("spaCy English model not available")
        
        # AI Models cache
        self.trained_models: Dict[str, Any] = {}
        self.document_profiles: Dict[str, DocumentProfile] = {}
        
        # Feature extractors
        self.tfidf_vectorizer = None
        if SKLEARN_AVAILABLE:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
        
        # Document corpus for training
        self.document_corpus: List[Dict[str, Any]] = []
        
        # Analysis patterns
        self.content_patterns = {
            'financial': [
                r'\$[\d,]+\.?\d*', r'revenue', r'profit', r'expense', r'budget',
                r'quarterly', r'annual', r'fiscal', r'balance sheet', r'income statement'
            ],
            'legal': [
                r'whereas', r'therefore', r'party', r'agreement', r'contract',
                r'liability', r'indemnify', r'breach', r'governing law', r'jurisdiction'
            ],
            'technical': [
                r'algorithm', r'implementation', r'specification', r'architecture',
                r'protocol', r'interface', r'API', r'framework', r'methodology'
            ],
            'academic': [
                r'abstract', r'methodology', r'conclusion', r'references',
                r'hypothesis', r'literature review', r'research', r'study', r'analysis'
            ],
            'medical': [
                r'patient', r'diagnosis', r'treatment', r'symptoms', r'medication',
                r'clinical', r'medical history', r'prescription', r'dosage'
            ]
        }
    
    async def analyze_document_intelligence(
        self,
        document_data: Dict[str, Any],
        analysis_types: List[AnalysisType] = None
    ) -> Dict[str, AIAnalysisResult]:
        """
        Análisis completo de inteligencia de documento
        """
        start_time = datetime.now()
        
        try:
            if not analysis_types:
                analysis_types = [
                    AnalysisType.CONTENT_INTELLIGENCE,
                    AnalysisType.DOCUMENT_CLASSIFICATION,
                    AnalysisType.SEMANTIC_ANALYSIS
                ]
            
            results = {}
            
            # Crear perfil del documento
            document_profile = await self._create_document_profile(document_data)
            
            # Ejecutar análisis solicitados
            for analysis_type in analysis_types:
                try:
                    if analysis_type == AnalysisType.CONTENT_INTELLIGENCE:
                        result = await self._analyze_content_intelligence(document_profile)
                    elif analysis_type == AnalysisType.SEMANTIC_ANALYSIS:
                        result = await self._analyze_semantic_content(document_profile)
                    elif analysis_type == AnalysisType.DOCUMENT_CLASSIFICATION:
                        result = await self._classify_document(document_profile)
                    elif analysis_type == AnalysisType.SIMILARITY_ANALYSIS:
                        result = await self._analyze_similarity(document_profile)
                    elif analysis_type == AnalysisType.ANOMALY_DETECTION:
                        result = await self._detect_anomalies(document_profile)
                    elif analysis_type == AnalysisType.TREND_ANALYSIS:
                        result = await self._analyze_trends(document_profile)
                    elif analysis_type == AnalysisType.ENTITY_RELATIONSHIP:
                        result = await self._analyze_entity_relationships(document_profile)
                    else:
                        continue
                    
                    results[analysis_type.value] = result
                    
                except Exception as e:
                    self.logger.error(f"Failed to run {analysis_type.value}: {e}")
                    continue
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Generar insights consolidados
            consolidated_insights = await self._consolidate_insights(results)
            
            return {
                "analysis_results": results,
                "consolidated_insights": consolidated_insights,
                "document_profile": document_profile,
                "processing_time": processing_time,
                "capabilities_used": self._get_ai_capabilities()
            }
            
        except Exception as e:
            self.logger.error(f"AI Intelligence analysis failed: {e}")
            raise
    
    async def _create_document_profile(self, document_data: Dict[str, Any]) -> DocumentProfile:
        """
        Crear perfil completo del documento
        """
        try:
            document_id = document_data.get("id", str(hash(str(document_data))))
            document_type = document_data.get("type", "unknown")
            
            # Extraer texto para análisis
            text_content = self._extract_text_content(document_data)
            
            # Features de contenido
            content_features = await self._extract_content_features(text_content)
            
            # Features estructurales
            structural_features = await self._extract_structural_features(document_data)
            
            # Métricas de calidad
            quality_metrics = await self._calculate_quality_metrics(document_data, text_content)
            
            # Features semánticos
            semantic_features = await self._extract_semantic_features(text_content)
            
            # Generar fingerprint
            fingerprint = self._generate_document_fingerprint(content_features, structural_features)
            
            profile = DocumentProfile(
                document_id=document_id,
                document_type=document_type,
                content_features=content_features,
                structural_features=structural_features,
                quality_metrics=quality_metrics,
                semantic_features=semantic_features,
                fingerprint=fingerprint
            )
            
            # Cache del perfil
            self.document_profiles[document_id] = profile
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to create document profile: {e}")
            raise
    
    def _extract_text_content(self, document_data: Dict[str, Any]) -> str:
        """
        Extraer contenido de texto del documento
        """
        text_parts = []
        
        # Extraer de diferentes fuentes según el tipo de análisis
        if "extracted_text" in document_data:
            text_parts.append(document_data["extracted_text"])
        
        if "analysis_results" in document_data:
            results = document_data["analysis_results"]
            
            # Texto de análisis OCR
            if "ocr_analysis" in results:
                ocr_data = results["ocr_analysis"]
                if "text_elements" in ocr_data:
                    for element in ocr_data["text_elements"]:
                        if "text" in element:
                            text_parts.append(element["text"])
            
            # Texto de análisis de Word
            if "word_intelligence" in results:
                word_data = results["word_intelligence"]
                if "plain_text" in word_data.get("analysis_results", {}).get("content", {}):
                    text_parts.append(word_data["analysis_results"]["content"]["plain_text"])
        
        return " ".join(text_parts).strip()
    
    async def _extract_content_features(self, text: str) -> Dict[str, Any]:
        """
        Extraer características del contenido
        """
        try:
            features = {}
            
            if not text:
                return features
            
            # Estadísticas básicas
            features["char_count"] = len(text)
            features["word_count"] = len(text.split())
            features["sentence_count"] = len(re.split(r'[.!?]+', text))
            features["paragraph_count"] = len(text.split('\n\n'))
            
            # Características lingüísticas
            if features["word_count"] > 0:
                features["avg_word_length"] = sum(len(word) for word in text.split()) / features["word_count"]
                features["avg_sentence_length"] = features["word_count"] / max(features["sentence_count"], 1)
            
            # Métricas de legibilidad
            if NLP_AVAILABLE and features["word_count"] > 10:
                try:
                    features["flesch_reading_ease"] = flesch_reading_ease(text)
                    features["flesch_kincaid_grade"] = flesch_kincaid_grade(text)
                except:
                    features["flesch_reading_ease"] = 0
                    features["flesch_kincaid_grade"] = 0
            
            # Patrones de contenido
            features["content_patterns"] = {}
            for pattern_type, patterns in self.content_patterns.items():
                count = 0
                for pattern in patterns:
                    count += len(re.findall(pattern, text, re.IGNORECASE))
                features["content_patterns"][pattern_type] = count
            
            # Diversidad léxica
            words = text.lower().split()
            if words:
                features["lexical_diversity"] = len(set(words)) / len(words)
                features["most_common_words"] = dict(Counter(words).most_common(10))
            
            # Densidad de números y fechas
            numbers = re.findall(r'\d+', text)
            dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
            features["numeric_density"] = len(numbers) / max(features["word_count"], 1)
            features["date_density"] = len(dates) / max(features["word_count"], 1)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract content features: {e}")
            return {}
    
    async def _extract_structural_features(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extraer características estructurales del documento
        """
        try:
            features = {}
            
            # Información básica del documento
            if "metadata" in document_data:
                metadata = document_data["metadata"]
                features["page_count"] = metadata.get("page_count", 0)
                features["file_size"] = metadata.get("file_size", 0)
            
            # Análisis de estructura
            if "document_structure" in document_data:
                structure = document_data["document_structure"]
                if "pages" in structure:
                    pages = structure["pages"]
                    features["pages_analyzed"] = len(pages)
                    
                    # Contar elementos por tipo
                    element_counts = defaultdict(int)
                    for page in pages:
                        if "elements" in page:
                            for element in page["elements"]:
                                element_type = element.get("type", "unknown")
                                element_counts[element_type] += 1
                    
                    features["element_distribution"] = dict(element_counts)
            
            # Análisis de layout si está disponible
            if "analysis_results" in document_data:
                results = document_data["analysis_results"]
                
                if "layout_analysis" in results:
                    layout_data = results["layout_analysis"]
                    if "pages" in layout_data:
                        features["complex_tables"] = 0
                        features["form_elements"] = 0
                        features["graphic_elements"] = 0
                        
                        for page in layout_data["pages"]:
                            features["complex_tables"] += len(page.get("complex_tables", []))
                            features["form_elements"] += len(page.get("form_elements", []))
                            features["graphic_elements"] += len(page.get("graphic_elements", []))
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract structural features: {e}")
            return {}
    
    async def _calculate_quality_metrics(self, document_data: Dict[str, Any], text: str) -> Dict[str, Any]:
        """
        Calcular métricas de calidad del documento
        """
        try:
            metrics = {}
            
            # Calidad de OCR/extracción
            if "confidence_score" in document_data:
                metrics["extraction_confidence"] = document_data["confidence_score"]
            
            # Completitud del texto
            if text:
                # Ratio de caracteres válidos
                valid_chars = sum(1 for c in text if c.isalnum() or c.isspace() or c in '.,!?;:()[]{}"-')
                metrics["text_validity"] = valid_chars / max(len(text), 1)
                
                # Densidad de caracteres especiales problemáticos
                special_chars = sum(1 for c in text if ord(c) > 127 and not c.isalnum())
                metrics["special_char_density"] = special_chars / max(len(text), 1)
            
            # Consistencia estructural
            if "analysis_results" in document_data:
                results = document_data["analysis_results"]
                
                # Calidad de Word si está disponible
                if "word_intelligence" in results:
                    word_data = results["word_intelligence"]
                    if "quality_assessment" in word_data.get("analysis_results", {}):
                        quality_data = word_data["analysis_results"]["quality_assessment"]
                        metrics["word_quality"] = quality_data.get("quality_scores", {})
                
                # Calidad de Excel si está disponible
                if "excel_intelligence" in results:
                    excel_data = results["excel_intelligence"]
                    if "quality_analysis" in excel_data.get("analysis_results", {}):
                        quality_data = excel_data["analysis_results"]["quality_analysis"]
                        metrics["excel_quality"] = quality_data.get("data_quality_score", 0)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to calculate quality metrics: {e}")
            return {}
    
    async def _extract_semantic_features(self, text: str) -> Dict[str, Any]:
        """
        Extraer características semánticas usando NLP
        """
        try:
            features = {}
            
            if not text or not self.nlp:
                return features
            
            # Procesar texto con spaCy
            doc = self.nlp(text[:10000])  # Limitar para rendimiento
            
            # Entidades nombradas
            entities = {}
            for ent in doc.ents:
                label = ent.label_
                entities[label] = entities.get(label, 0) + 1
            features["named_entities"] = entities
            
            # Análisis de sentimientos básico (polaridad)
            positive_words = ["good", "excellent", "positive", "success", "improve", "benefit"]
            negative_words = ["bad", "poor", "negative", "fail", "problem", "issue"]
            
            text_lower = text.lower()
            pos_count = sum(text_lower.count(word) for word in positive_words)
            neg_count = sum(text_lower.count(word) for word in negative_words)
            
            total_sentiment_words = pos_count + neg_count
            if total_sentiment_words > 0:
                features["sentiment_polarity"] = (pos_count - neg_count) / total_sentiment_words
            else:
                features["sentiment_polarity"] = 0
            
            # Complejidad sintáctica
            features["avg_dependency_depth"] = np.mean([len(list(token.ancestors)) for token in doc])
            
            # Tipos de palabra predominantes
            pos_counts = {}
            for token in doc:
                if not token.is_stop and not token.is_punct:
                    pos = token.pos_
                    pos_counts[pos] = pos_counts.get(pos, 0) + 1
            features["pos_distribution"] = pos_counts
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract semantic features: {e}")
            return {}
    
    def _generate_document_fingerprint(
        self, 
        content_features: Dict[str, Any], 
        structural_features: Dict[str, Any]
    ) -> str:
        """
        Generar huella digital del documento
        """
        try:
            # Combinar características clave para fingerprint
            key_features = {
                "word_count": content_features.get("word_count", 0),
                "page_count": structural_features.get("page_count", 0),
                "element_distribution": structural_features.get("element_distribution", {}),
                "content_patterns": content_features.get("content_patterns", {}),
                "lexical_diversity": content_features.get("lexical_diversity", 0)
            }
            
            # Crear hash
            fingerprint_string = json.dumps(key_features, sort_keys=True)
            return hashlib.md5(fingerprint_string.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Failed to generate document fingerprint: {e}")
            return "unknown"
    
    async def _analyze_content_intelligence(self, profile: DocumentProfile) -> AIAnalysisResult:
        """
        Análisis de inteligencia de contenido
        """
        start_time = datetime.now()
        
        try:
            insights = []
            recommendations = []
            
            # Análisis de características de contenido
            content_features = profile.content_features
            
            # Insight sobre longitud del documento
            word_count = content_features.get("word_count", 0)
            if word_count > 0:
                if word_count < 100:
                    insights.append(ContentInsight(
                        type="document_length",
                        description="Document is very short, may lack comprehensive information",
                        confidence=0.8,
                        evidence=[f"Only {word_count} words"],
                        impact="medium",
                        actionable=True
                    ))
                    recommendations.append("Consider expanding content for better analysis coverage")
                elif word_count > 10000:
                    insights.append(ContentInsight(
                        type="document_length",
                        description="Document is very comprehensive and detailed",
                        confidence=0.9,
                        evidence=[f"{word_count} words provide extensive coverage"],
                        impact="low",
                        actionable=False
                    ))
            
            # Análisis de legibilidad
            flesch_score = content_features.get("flesch_reading_ease", 50)
            if flesch_score < 30:
                insights.append(ContentInsight(
                    type="readability",
                    description="Document has very difficult readability level",
                    confidence=0.85,
                    evidence=[f"Flesch Reading Ease: {flesch_score}"],
                    impact="high",
                    actionable=True
                ))
                recommendations.append("Consider simplifying language and sentence structure")
            elif flesch_score > 80:
                insights.append(ContentInsight(
                    type="readability",
                    description="Document is very easy to read",
                    confidence=0.85,
                    evidence=[f"Flesch Reading Ease: {flesch_score}"],
                    impact="low",
                    actionable=False
                ))
            
            # Análisis de patrones de contenido
            content_patterns = content_features.get("content_patterns", {})
            dominant_pattern = max(content_patterns.items(), key=lambda x: x[1]) if content_patterns else None
            
            if dominant_pattern and dominant_pattern[1] > 5:
                insights.append(ContentInsight(
                    type="content_classification",
                    description=f"Document shows strong {dominant_pattern[0]} characteristics",
                    confidence=min(0.9, dominant_pattern[1] / 20),
                    evidence=[f"{dominant_pattern[1]} {dominant_pattern[0]} pattern matches"],
                    impact="medium",
                    actionable=True
                ))
                recommendations.append(f"Optimize processing pipeline for {dominant_pattern[0]} document type")
            
            # Análisis de diversidad léxica
            lexical_diversity = content_features.get("lexical_diversity", 0)
            if lexical_diversity < 0.3:
                insights.append(ContentInsight(
                    type="vocabulary",
                    description="Document has low vocabulary diversity, may be repetitive",
                    confidence=0.8,
                    evidence=[f"Lexical diversity: {lexical_diversity:.2f}"],
                    impact="medium",
                    actionable=True
                ))
                recommendations.append("Consider varying vocabulary for better engagement")
            
            # Análisis de densidad numérica
            numeric_density = content_features.get("numeric_density", 0)
            if numeric_density > 0.1:
                insights.append(ContentInsight(
                    type="data_content",
                    description="Document is highly data-driven with many numerical values",
                    confidence=0.9,
                    evidence=[f"Numeric density: {numeric_density:.2f}"],
                    impact="low",
                    actionable=True
                ))
                recommendations.append("Consider using data extraction and validation tools")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIAnalysisResult(
                analysis_type=AnalysisType.CONTENT_INTELLIGENCE,
                confidence=0.85,
                insights=[insight.__dict__ for insight in insights],
                recommendations=recommendations,
                metadata={
                    "features_analyzed": len(content_features),
                    "insights_generated": len(insights)
                },
                processing_time=processing_time,
                model_info={"type": "rule_based", "version": "1.0"}
            )
            
        except Exception as e:
            self.logger.error(f"Content intelligence analysis failed: {e}")
            raise
    
    async def _analyze_semantic_content(self, profile: DocumentProfile) -> AIAnalysisResult:
        """
        Análisis semántico del contenido
        """
        start_time = datetime.now()
        
        try:
            insights = []
            recommendations = []
            
            semantic_features = profile.semantic_features
            
            # Análisis de entidades nombradas
            entities = semantic_features.get("named_entities", {})
            if entities:
                total_entities = sum(entities.values())
                entity_diversity = len(entities) / max(total_entities, 1)
                
                insights.append(ContentInsight(
                    type="entity_analysis",
                    description=f"Document contains {total_entities} named entities across {len(entities)} categories",
                    confidence=0.9,
                    evidence=[f"Entity types: {list(entities.keys())}"],
                    impact="medium",
                    actionable=True
                ))
                
                if entity_diversity > 0.5:
                    recommendations.append("Rich entity content suitable for knowledge extraction")
                
                # Identificar tipo de entidad dominante
                if entities:
                    dominant_entity = max(entities.items(), key=lambda x: x[1])
                    if dominant_entity[1] > total_entities * 0.4:
                        insights.append(ContentInsight(
                            type="entity_focus",
                            description=f"Document focuses heavily on {dominant_entity[0]} entities",
                            confidence=0.8,
                            evidence=[f"{dominant_entity[1]} out of {total_entities} entities"],
                            impact="medium",
                            actionable=True
                        ))
            
            # Análisis de sentimiento
            sentiment = semantic_features.get("sentiment_polarity", 0)
            if abs(sentiment) > 0.3:
                sentiment_label = "positive" if sentiment > 0 else "negative"
                insights.append(ContentInsight(
                    type="sentiment",
                    description=f"Document has {sentiment_label} sentiment orientation",
                    confidence=min(0.9, abs(sentiment) * 2),
                    evidence=[f"Sentiment polarity: {sentiment:.2f}"],
                    impact="low",
                    actionable=False
                ))
            
            # Análisis de complejidad sintáctica
            complexity = semantic_features.get("avg_dependency_depth", 0)
            if complexity > 3:
                insights.append(ContentInsight(
                    type="syntactic_complexity",
                    description="Document has high syntactic complexity",
                    confidence=0.8,
                    evidence=[f"Average dependency depth: {complexity:.1f}"],
                    impact="medium",
                    actionable=True
                ))
                recommendations.append("Consider simplifying sentence structure for better comprehension")
            
            # Análisis de distribución de tipos de palabra
            pos_dist = semantic_features.get("pos_distribution", {})
            if pos_dist:
                total_pos = sum(pos_dist.values())
                noun_ratio = pos_dist.get("NOUN", 0) / max(total_pos, 1)
                verb_ratio = pos_dist.get("VERB", 0) / max(total_pos, 1)
                
                if noun_ratio > 0.4:
                    insights.append(ContentInsight(
                        type="linguistic_style",
                        description="Document is noun-heavy, indicating descriptive or technical content",
                        confidence=0.8,
                        evidence=[f"Noun ratio: {noun_ratio:.2f}"],
                        impact="low",
                        actionable=True
                    ))
                
                if verb_ratio > 0.2:
                    insights.append(ContentInsight(
                        type="linguistic_style",
                        description="Document is action-oriented with many verbs",
                        confidence=0.8,
                        evidence=[f"Verb ratio: {verb_ratio:.2f}"],
                        impact="low",
                        actionable=False
                    ))
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIAnalysisResult(
                analysis_type=AnalysisType.SEMANTIC_ANALYSIS,
                confidence=0.8,
                insights=[insight.__dict__ for insight in insights],
                recommendations=recommendations,
                metadata={
                    "entities_found": len(entities),
                    "semantic_features": len(semantic_features)
                },
                processing_time=processing_time,
                model_info={"type": "nlp_based", "library": "spaCy" if NLP_AVAILABLE else "basic"}
            )
            
        except Exception as e:
            self.logger.error(f"Semantic analysis failed: {e}")
            raise
    
    async def _classify_document(self, profile: DocumentProfile) -> AIAnalysisResult:
        """
        Clasificación automática del documento
        """
        start_time = datetime.now()
        
        try:
            insights = []
            recommendations = []
            
            # Clasificación basada en patrones de contenido
            content_patterns = profile.content_features.get("content_patterns", {})
            structural_features = profile.structural_features
            
            # Calcular scores para cada categoría
            classification_scores = {}
            
            for category, count in content_patterns.items():
                if count > 0:
                    # Score basado en frecuencia de patrones
                    pattern_score = min(1.0, count / 10)
                    
                    # Ajustar por características estructurales
                    if category == "financial" and structural_features.get("complex_tables", 0) > 0:
                        pattern_score *= 1.2
                    elif category == "technical" and structural_features.get("graphic_elements", 0) > 0:
                        pattern_score *= 1.1
                    elif category == "legal" and profile.content_features.get("avg_sentence_length", 0) > 25:
                        pattern_score *= 1.1
                    
                    classification_scores[category] = min(1.0, pattern_score)
            
            # Determinar clasificación principal
            if classification_scores:
                primary_category = max(classification_scores.items(), key=lambda x: x[1])
                confidence = primary_category[1]
                
                insights.append(ContentInsight(
                    type="document_classification",
                    description=f"Document classified as {primary_category[0]} type",
                    confidence=confidence,
                    evidence=[f"Classification score: {confidence:.2f}"],
                    impact="high",
                    actionable=True
                ))
                
                # Recomendaciones específicas por tipo
                category_recommendations = {
                    "financial": [
                        "Use financial data extraction tools",
                        "Implement numerical validation",
                        "Consider automated financial analysis"
                    ],
                    "legal": [
                        "Apply legal document templates",
                        "Use contract analysis tools",
                        "Implement compliance checking"
                    ],
                    "technical": [
                        "Enable technical terminology recognition",
                        "Use code/formula extraction",
                        "Apply technical document formatting"
                    ],
                    "academic": [
                        "Use citation extraction",
                        "Apply academic formatting standards",
                        "Enable reference validation"
                    ],
                    "medical": [
                        "Apply medical terminology validation",
                        "Use patient data protection",
                        "Enable medical code recognition"
                    ]
                }
                
                if primary_category[0] in category_recommendations:
                    recommendations.extend(category_recommendations[primary_category[0]])
            
            # Clasificación por estructura
            page_count = structural_features.get("page_count", 0)
            tables = structural_features.get("complex_tables", 0)
            forms = structural_features.get("form_elements", 0)
            
            if forms > 5:
                insights.append(ContentInsight(
                    type="structural_classification",
                    description="Document appears to be a form or application",
                    confidence=0.9,
                    evidence=[f"{forms} form elements detected"],
                    impact="high",
                    actionable=True
                ))
                recommendations.append("Use form processing and field extraction tools")
            
            if tables > 3 and page_count < 10:
                insights.append(ContentInsight(
                    type="structural_classification",
                    description="Document is table-heavy, likely a report or data sheet",
                    confidence=0.8,
                    evidence=[f"{tables} tables in {page_count} pages"],
                    impact="medium",
                    actionable=True
                ))
                recommendations.append("Focus on table extraction and data analysis")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIAnalysisResult(
                analysis_type=AnalysisType.DOCUMENT_CLASSIFICATION,
                confidence=max(classification_scores.values()) if classification_scores else 0.5,
                insights=[insight.__dict__ for insight in insights],
                recommendations=recommendations,
                metadata={
                    "classification_scores": classification_scores,
                    "categories_detected": len(classification_scores)
                },
                processing_time=processing_time,
                model_info={"type": "pattern_based", "categories": list(self.content_patterns.keys())}
            )
            
        except Exception as e:
            self.logger.error(f"Document classification failed: {e}")
            raise
    
    async def _analyze_similarity(self, profile: DocumentProfile) -> AIAnalysisResult:
        """
        Análisis de similitud con otros documentos
        """
        start_time = datetime.now()
        
        try:
            insights = []
            recommendations = []
            
            if not SKLEARN_AVAILABLE:
                return AIAnalysisResult(
                    analysis_type=AnalysisType.SIMILARITY_ANALYSIS,
                    confidence=0.0,
                    insights=[],
                    recommendations=["Install scikit-learn for similarity analysis"],
                    metadata={"error": "scikit-learn not available"},
                    processing_time=0,
                    model_info={"type": "unavailable"}
                )
            
            # Buscar documentos similares en el corpus
            similar_documents = []
            current_fingerprint = profile.fingerprint
            
            for doc_id, other_profile in self.document_profiles.items():
                if doc_id != profile.document_id:
                    # Calcular similitud basada en características
                    similarity_score = self._calculate_document_similarity(profile, other_profile)
                    
                    if similarity_score > 0.7:
                        similar_documents.append({
                            "document_id": doc_id,
                            "similarity_score": similarity_score,
                            "document_type": other_profile.document_type
                        })
            
            # Ordenar por similitud
            similar_documents.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            if similar_documents:
                top_similar = similar_documents[0]
                insights.append(ContentInsight(
                    type="document_similarity",
                    description=f"Found {len(similar_documents)} similar documents",
                    confidence=0.8,
                    evidence=[f"Top similarity: {top_similar['similarity_score']:.2f} with {top_similar['document_id']}"],
                    impact="medium",
                    actionable=True
                ))
                
                recommendations.append("Consider using templates or workflows from similar documents")
                
                if len(similar_documents) > 5:
                    recommendations.append("Document appears to follow a common pattern - enable batch processing")
            
            # Análisis de duplicados potenciales
            exact_matches = [doc for doc in similar_documents if doc["similarity_score"] > 0.95]
            if exact_matches:
                insights.append(ContentInsight(
                    type="duplicate_detection",
                    description=f"Found {len(exact_matches)} potential duplicate documents",
                    confidence=0.9,
                    evidence=[f"Similarity scores > 0.95"],
                    impact="high",
                    actionable=True
                ))
                recommendations.append("Review for duplicate content and consider deduplication")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIAnalysisResult(
                analysis_type=AnalysisType.SIMILARITY_ANALYSIS,
                confidence=0.8,
                insights=[insight.__dict__ for insight in insights],
                recommendations=recommendations,
                metadata={
                    "similar_documents_found": len(similar_documents),
                    "corpus_size": len(self.document_profiles),
                    "top_similarities": similar_documents[:3]
                },
                processing_time=processing_time,
                model_info={"type": "feature_similarity", "algorithm": "cosine_similarity"}
            )
            
        except Exception as e:
            self.logger.error(f"Similarity analysis failed: {e}")
            raise
    
    def _calculate_document_similarity(self, profile1: DocumentProfile, profile2: DocumentProfile) -> float:
        """
        Calcular similitud entre dos documentos
        """
        try:
            similarity_scores = []
            
            # Similitud de características de contenido
            content_sim = self._feature_similarity(
                profile1.content_features, 
                profile2.content_features,
                ["word_count", "lexical_diversity", "numeric_density"]
            )
            similarity_scores.append(content_sim * 0.4)
            
            # Similitud estructural
            structural_sim = self._feature_similarity(
                profile1.structural_features,
                profile2.structural_features,
                ["page_count", "complex_tables", "form_elements"]
            )
            similarity_scores.append(structural_sim * 0.3)
            
            # Similitud de patrones de contenido
            patterns1 = profile1.content_features.get("content_patterns", {})
            patterns2 = profile2.content_features.get("content_patterns", {})
            pattern_sim = self._pattern_similarity(patterns1, patterns2)
            similarity_scores.append(pattern_sim * 0.3)
            
            return sum(similarity_scores)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate document similarity: {e}")
            return 0.0
    
    def _feature_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any], key_features: List[str]) -> float:
        """
        Calcular similitud basada en características específicas
        """
        try:
            similarities = []
            
            for feature in key_features:
                val1 = features1.get(feature, 0)
                val2 = features2.get(feature, 0)
                
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    if val1 == val2 == 0:
                        similarities.append(1.0)
                    else:
                        max_val = max(val1, val2)
                        min_val = min(val1, val2)
                        similarities.append(min_val / max(max_val, 1))
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            self.logger.error(f"Failed to calculate feature similarity: {e}")
            return 0.0
    
    def _pattern_similarity(self, patterns1: Dict[str, int], patterns2: Dict[str, int]) -> float:
        """
        Calcular similitud de patrones de contenido
        """
        try:
            if not patterns1 and not patterns2:
                return 1.0
            
            if not patterns1 or not patterns2:
                return 0.0
            
            # Vector de patrones
            all_patterns = set(patterns1.keys()) | set(patterns2.keys())
            
            vec1 = [patterns1.get(pattern, 0) for pattern in all_patterns]
            vec2 = [patterns2.get(pattern, 0) for pattern in all_patterns]
            
            # Similitud coseno
            if SKLEARN_AVAILABLE:
                vec1 = np.array(vec1).reshape(1, -1)
                vec2 = np.array(vec2).reshape(1, -1)
                return cosine_similarity(vec1, vec2)[0][0]
            else:
                # Similitud coseno manual
                dot_product = sum(a * b for a, b in zip(vec1, vec2))
                norm1 = sum(a * a for a in vec1) ** 0.5
                norm2 = sum(b * b for b in vec2) ** 0.5
                
                if norm1 == 0 or norm2 == 0:
                    return 0.0
                
                return dot_product / (norm1 * norm2)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate pattern similarity: {e}")
            return 0.0
    
    async def _detect_anomalies(self, profile: DocumentProfile) -> AIAnalysisResult:
        """
        Detección de anomalías en el documento
        """
        start_time = datetime.now()
        
        try:
            insights = []
            recommendations = []
            
            content_features = profile.content_features
            structural_features = profile.structural_features
            quality_metrics = profile.quality_metrics
            
            # Anomalías de contenido
            word_count = content_features.get("word_count", 0)
            char_count = content_features.get("char_count", 0)
            
            # Ratio anómalo de caracteres por palabra
            if word_count > 0:
                avg_word_length = char_count / word_count
                if avg_word_length > 15:
                    insights.append(ContentInsight(
                        type="content_anomaly",
                        description="Unusually long average word length detected",
                        confidence=0.8,
                        evidence=[f"Average word length: {avg_word_length:.1f} characters"],
                        impact="medium",
                        actionable=True
                    ))
                    recommendations.append("Check for OCR errors or encoding issues")
                elif avg_word_length < 2:
                    insights.append(ContentInsight(
                        type="content_anomaly",
                        description="Unusually short average word length detected",
                        confidence=0.8,
                        evidence=[f"Average word length: {avg_word_length:.1f} characters"],
                        impact="medium",
                        actionable=True
                    ))
                    recommendations.append("Document may contain fragmented text or poor OCR quality")
            
            # Anomalías estructurales
            page_count = structural_features.get("page_count", 0)
            file_size = structural_features.get("file_size", 0)
            
            if page_count > 0 and file_size > 0:
                size_per_page = file_size / page_count
                if size_per_page > 5000000:  # >5MB per page
                    insights.append(ContentInsight(
                        type="structural_anomaly",
                        description="Unusually large file size per page",
                        confidence=0.9,
                        evidence=[f"{size_per_page/1000000:.1f}MB per page"],
                        impact="high",
                        actionable=True
                    ))
                    recommendations.append("Document may contain high-resolution images or embedded objects")
            
            # Anomalías de calidad
            text_validity = quality_metrics.get("text_validity", 1.0)
            if text_validity < 0.7:
                insights.append(ContentInsight(
                    type="quality_anomaly",
                    description="Low text validity score indicates extraction issues",
                    confidence=0.9,
                    evidence=[f"Text validity: {text_validity:.2f}"],
                    impact="high",
                    actionable=True
                ))
                recommendations.append("Review text extraction process and consider alternative OCR settings")
            
            special_char_density = quality_metrics.get("special_char_density", 0)
            if special_char_density > 0.1:
                insights.append(ContentInsight(
                    type="quality_anomaly",
                    description="High density of special characters detected",
                    confidence=0.8,
                    evidence=[f"Special character density: {special_char_density:.2f}"],
                    impact="medium",
                    actionable=True
                ))
                recommendations.append("Check for encoding issues or corrupted text")
            
            # Anomalías semánticas
            semantic_features = profile.semantic_features
            sentiment = semantic_features.get("sentiment_polarity", 0)
            if abs(sentiment) > 0.8:
                insights.append(ContentInsight(
                    type="semantic_anomaly",
                    description="Extreme sentiment polarity detected",
                    confidence=0.7,
                    evidence=[f"Sentiment polarity: {sentiment:.2f}"],
                    impact="low",
                    actionable=False
                ))
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIAnalysisResult(
                analysis_type=AnalysisType.ANOMALY_DETECTION,
                confidence=0.8,
                insights=[insight.__dict__ for insight in insights],
                recommendations=recommendations,
                metadata={
                    "anomalies_detected": len(insights),
                    "categories_checked": ["content", "structural", "quality", "semantic"]
                },
                processing_time=processing_time,
                model_info={"type": "rule_based_anomaly", "thresholds": "adaptive"}
            )
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            raise
    
    async def _analyze_trends(self, profile: DocumentProfile) -> AIAnalysisResult:
        """
        Análisis de tendencias temporales (requiere corpus histórico)
        """
        start_time = datetime.now()
        
        try:
            insights = []
            recommendations = []
            
            # Para análisis de tendencias necesitamos datos históricos
            if len(self.document_profiles) < 5:
                insights.append(ContentInsight(
                    type="trend_analysis",
                    description="Insufficient historical data for trend analysis",
                    confidence=0.9,
                    evidence=[f"Only {len(self.document_profiles)} documents in corpus"],
                    impact="low",
                    actionable=True
                ))
                recommendations.append("Process more documents to enable trend analysis")
            else:
                # Análisis básico de tendencias basado en documentos existentes
                doc_types = [p.document_type for p in self.document_profiles.values()]
                type_counts = Counter(doc_types)
                
                if type_counts:
                    most_common_type = type_counts.most_common(1)[0]
                    insights.append(ContentInsight(
                        type="document_trend",
                        description=f"Most common document type: {most_common_type[0]}",
                        confidence=0.8,
                        evidence=[f"{most_common_type[1]} out of {len(doc_types)} documents"],
                        impact="medium",
                        actionable=True
                    ))
                    
                    if most_common_type[1] > len(doc_types) * 0.6:
                        recommendations.append(f"Consider optimizing workflow for {most_common_type[0]} documents")
                
                # Análisis de complejidad temporal
                complexity_scores = []
                for p in self.document_profiles.values():
                    word_count = p.content_features.get("word_count", 0)
                    page_count = p.structural_features.get("page_count", 1)
                    complexity = word_count / page_count if page_count > 0 else 0
                    complexity_scores.append(complexity)
                
                if len(complexity_scores) > 1:
                    avg_complexity = np.mean(complexity_scores)
                    current_complexity = profile.content_features.get("word_count", 0) / max(profile.structural_features.get("page_count", 1), 1)
                    
                    if current_complexity > avg_complexity * 1.5:
                        insights.append(ContentInsight(
                            type="complexity_trend",
                            description="Document is significantly more complex than average",
                            confidence=0.8,
                            evidence=[f"Complexity: {current_complexity:.0f} vs avg {avg_complexity:.0f}"],
                            impact="medium",
                            actionable=True
                        ))
                        recommendations.append("Consider extended processing time for complex documents")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIAnalysisResult(
                analysis_type=AnalysisType.TREND_ANALYSIS,
                confidence=0.7,
                insights=[insight.__dict__ for insight in insights],
                recommendations=recommendations,
                metadata={
                    "corpus_size": len(self.document_profiles),
                    "analysis_scope": "basic_trends"
                },
                processing_time=processing_time,
                model_info={"type": "statistical_trends", "requires_history": True}
            )
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            raise
    
    async def _analyze_entity_relationships(self, profile: DocumentProfile) -> AIAnalysisResult:
        """
        Análisis de relaciones entre entidades
        """
        start_time = datetime.now()
        
        try:
            insights = []
            recommendations = []
            
            semantic_features = profile.semantic_features
            entities = semantic_features.get("named_entities", {})
            
            if not entities:
                insights.append(ContentInsight(
                    type="entity_relationship",
                    description="No named entities found for relationship analysis",
                    confidence=0.9,
                    evidence=["Zero named entities detected"],
                    impact="low",
                    actionable=True
                ))
                recommendations.append("Consider using entity extraction tools or manual annotation")
            else:
                # Análisis de diversidad de entidades
                total_entities = sum(entities.values())
                entity_types = len(entities)
                entity_diversity = entity_types / max(total_entities, 1)
                
                if entity_diversity > 0.5:
                    insights.append(ContentInsight(
                        type="entity_diversity",
                        description="High entity type diversity indicates rich content",
                        confidence=0.8,
                        evidence=[f"{entity_types} types among {total_entities} entities"],
                        impact="medium",
                        actionable=True
                    ))
                    recommendations.append("Leverage entity extraction for knowledge graph construction")
                
                # Identificar entidades dominantes
                if entities:
                    dominant_entities = [(k, v) for k, v in entities.items() if v > total_entities * 0.3]
                    
                    for entity_type, count in dominant_entities:
                        insights.append(ContentInsight(
                            type="entity_focus",
                            description=f"Document heavily features {entity_type} entities",
                            confidence=0.9,
                            evidence=[f"{count} {entity_type} entities ({count/total_entities:.1%})"],
                            impact="medium",
                            actionable=True
                        ))
                        
                        # Recomendaciones específicas por tipo de entidad
                        entity_recommendations = {
                            "PERSON": "Consider privacy protection and name normalization",
                            "ORG": "Enable organization relationship mapping",
                            "GPE": "Use geographic analysis tools",
                            "MONEY": "Apply financial data extraction",
                            "DATE": "Enable temporal analysis features"
                        }
                        
                        if entity_type in entity_recommendations:
                            recommendations.append(entity_recommendations[entity_type])
                
                # Análisis de co-ocurrencia (simplificado)
                if len(entities) > 2:
                    insights.append(ContentInsight(
                        type="entity_relationships",
                        description="Multiple entity types suggest complex relationships",
                        confidence=0.7,
                        evidence=[f"Co-occurrence of {len(entities)} entity types"],
                        impact="medium",
                        actionable=True
                    ))
                    recommendations.append("Consider relationship extraction and network analysis")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIAnalysisResult(
                analysis_type=AnalysisType.ENTITY_RELATIONSHIP,
                confidence=0.8,
                insights=[insight.__dict__ for insight in insights],
                recommendations=recommendations,
                metadata={
                    "entities_found": entities,
                    "total_entities": sum(entities.values()) if entities else 0,
                    "entity_types": len(entities)
                },
                processing_time=processing_time,
                model_info={"type": "entity_analysis", "nlp_library": "spaCy" if NLP_AVAILABLE else "basic"}
            )
            
        except Exception as e:
            self.logger.error(f"Entity relationship analysis failed: {e}")
            raise
    
    async def _consolidate_insights(self, results: Dict[str, AIAnalysisResult]) -> Dict[str, Any]:
        """
        Consolidar insights de múltiples análisis
        """
        try:
            all_insights = []
            all_recommendations = []
            high_impact_insights = []
            
            for analysis_type, result in results.items():
                all_insights.extend(result.insights)
                all_recommendations.extend(result.recommendations)
                
                # Filtrar insights de alto impacto
                for insight in result.insights:
                    if insight.get("impact") == "high" and insight.get("confidence", 0) > 0.8:
                        high_impact_insights.append(insight)
            
            # Calcular métricas consolidadas
            avg_confidence = np.mean([result.confidence for result in results.values()])
            total_processing_time = sum([result.processing_time for result in results.values()])
            
            # Insights prioritarios
            actionable_insights = [i for i in all_insights if i.get("actionable", False)]
            
            # Recomendaciones únicas
            unique_recommendations = list(set(all_recommendations))
            
            return {
                "summary": {
                    "total_insights": len(all_insights),
                    "high_impact_insights": len(high_impact_insights),
                    "actionable_insights": len(actionable_insights),
                    "total_recommendations": len(unique_recommendations),
                    "average_confidence": round(avg_confidence, 3),
                    "total_processing_time": round(total_processing_time, 2)
                },
                "priority_insights": high_impact_insights[:5],  # Top 5
                "key_recommendations": unique_recommendations[:10],  # Top 10
                "analysis_coverage": list(results.keys()),
                "overall_quality": self._calculate_overall_quality(all_insights)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to consolidate insights: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_quality(self, insights: List[Dict[str, Any]]) -> str:
        """
        Calcular calidad general basada en insights
        """
        try:
            if not insights:
                return "unknown"
            
            high_impact = sum(1 for i in insights if i.get("impact") == "high")
            medium_impact = sum(1 for i in insights if i.get("impact") == "medium")
            
            total_insights = len(insights)
            
            if high_impact > total_insights * 0.3:
                return "needs_attention"
            elif medium_impact > total_insights * 0.5:
                return "good"
            else:
                return "excellent"
                
        except Exception as e:
            return "unknown"
    
    def _get_ai_capabilities(self) -> Dict[str, bool]:
        """
        Obtener capacidades de IA disponibles
        """
        return {
            "sklearn_available": SKLEARN_AVAILABLE,
            "spacy_available": NLP_AVAILABLE,
            "networkx_available": NETWORKX_AVAILABLE,
            "content_intelligence": True,
            "semantic_analysis": NLP_AVAILABLE,
            "document_classification": True,
            "similarity_analysis": SKLEARN_AVAILABLE,
            "anomaly_detection": True,
            "trend_analysis": True,
            "entity_relationships": NLP_AVAILABLE,
            "machine_learning": SKLEARN_AVAILABLE,
            "natural_language_processing": NLP_AVAILABLE
        }
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del servicio de IA
        """
        try:
            return {
                "service_status": "operational",
                "ai_capabilities": self._get_ai_capabilities(),
                "document_profiles": len(self.document_profiles),
                "trained_models": len(self.trained_models),
                "supported_analysis_types": [at.value for at in AnalysisType],
                "corpus_size": len(self.document_corpus),
                "dependencies": {
                    "scikit_learn": SKLEARN_AVAILABLE,
                    "spacy": NLP_AVAILABLE,
                    "networkx": NETWORKX_AVAILABLE
                }
            }
            
        except Exception as e:
            return {"error": str(e), "service_status": "error"}