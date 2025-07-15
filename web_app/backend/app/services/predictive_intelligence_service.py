#!/usr/bin/env python3
"""
Predictive Intelligence Service - Capacidades predictivas y análisis avanzado
Parte de la Fase 3.3 de la expansión de inteligencia documental
"""

import logging
import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics
from collections import defaultdict, Counter
import pickle
import hashlib

# Machine Learning libraries
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    import pandas as pd
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Time series analysis
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

# Import existing services
from app.services.ai_intelligence_service import AIIntelligenceService, DocumentProfile
from app.services.workflow_automation_service import WorkflowAutomationService

logger = logging.getLogger(__name__)

class PredictionType(str, Enum):
    PROCESSING_TIME = "processing_time"
    QUALITY_SCORE = "quality_score"
    ERROR_PROBABILITY = "error_probability"
    OPTIMAL_WORKFLOW = "optimal_workflow"
    RESOURCE_USAGE = "resource_usage"
    USER_BEHAVIOR = "user_behavior"
    DOCUMENT_SIMILARITY = "document_similarity"
    CONVERSION_SUCCESS = "conversion_success"

class ModelType(str, Enum):
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    TIME_SERIES = "time_series"
    CLUSTERING = "clustering"
    ENSEMBLE = "ensemble"

@dataclass
class PredictionRequest:
    """Solicitud de predicción"""
    prediction_type: PredictionType
    document_features: Dict[str, Any]
    context: Dict[str, Any]
    confidence_threshold: float = 0.7

@dataclass
class PredictionResult:
    """Resultado de predicción"""
    prediction_type: PredictionType
    prediction: Union[float, str, Dict[str, Any]]
    confidence: float
    explanation: str
    factors: List[Dict[str, Any]]
    model_info: Dict[str, Any]
    processing_time: float
    recommendations: List[str]

@dataclass
class ModelMetrics:
    """Métricas de modelo"""
    model_id: str
    model_type: ModelType
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_samples: int
    last_trained: datetime
    feature_importance: Dict[str, float]

class PredictiveIntelligenceService:
    """
    Servicio de inteligencia predictiva para análisis avanzado y predicciones
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI service for feature extraction
        self.ai_service = AIIntelligenceService()
        
        # Predictive models storage
        self.models: Dict[str, Any] = {}
        self.model_metrics: Dict[str, ModelMetrics] = {}
        self.feature_scalers: Dict[str, Any] = {}
        self.label_encoders: Dict[str, Any] = {}
        
        # Training data
        self.training_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Model configurations
        self.model_configs = {
            PredictionType.PROCESSING_TIME: {
                "model_type": ModelType.REGRESSION,
                "algorithm": "gradient_boosting",
                "features": ["word_count", "page_count", "file_size", "complex_tables", "form_elements"],
                "target": "processing_time"
            },
            PredictionType.QUALITY_SCORE: {
                "model_type": ModelType.REGRESSION,
                "algorithm": "random_forest",
                "features": ["text_validity", "confidence_score", "flesch_reading_ease", "entity_count"],
                "target": "quality_score"
            },
            PredictionType.ERROR_PROBABILITY: {
                "model_type": ModelType.CLASSIFICATION,
                "algorithm": "logistic_regression",
                "features": ["file_size", "special_char_density", "text_validity", "avg_confidence"],
                "target": "has_error"
            },
            PredictionType.OPTIMAL_WORKFLOW: {
                "model_type": ModelType.CLASSIFICATION,
                "algorithm": "random_forest",
                "features": ["document_type", "content_patterns", "complexity_score", "user_preferences"],
                "target": "optimal_workflow_id"
            },
            PredictionType.CONVERSION_SUCCESS: {
                "model_type": ModelType.CLASSIFICATION,
                "algorithm": "gradient_boosting",
                "features": ["source_format", "target_format", "file_size", "quality_score", "complexity"],
                "target": "conversion_success"
            }
        }
        
        # Performance tracking
        self.prediction_history: List[Dict[str, Any]] = []
        self.model_performance: Dict[str, List[float]] = defaultdict(list)
        
        # Prediction cache
        self.prediction_cache: Dict[str, PredictionResult] = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Initialize base models if possible
        if SKLEARN_AVAILABLE:
            self._initialize_base_models()
    
    def _initialize_base_models(self):
        """
        Inicializar modelos base con configuraciones por defecto
        """
        try:
            for prediction_type, config in self.model_configs.items():
                model_id = f"{prediction_type.value}_model"
                
                if config["model_type"] == ModelType.REGRESSION:
                    if config["algorithm"] == "gradient_boosting":
                        self.models[model_id] = GradientBoostingRegressor(
                            n_estimators=100,
                            learning_rate=0.1,
                            max_depth=3,
                            random_state=42
                        )
                    else:
                        self.models[model_id] = RandomForestRegressor(
                            n_estimators=100,
                            random_state=42
                        )
                
                elif config["model_type"] == ModelType.CLASSIFICATION:
                    if config["algorithm"] == "logistic_regression":
                        self.models[model_id] = LogisticRegression(random_state=42)
                    else:
                        self.models[model_id] = RandomForestClassifier(
                            n_estimators=100,
                            random_state=42
                        )
                
                # Initialize scaler
                self.feature_scalers[model_id] = StandardScaler()
                
                # Initialize label encoder for classification
                if config["model_type"] == ModelType.CLASSIFICATION:
                    self.label_encoders[model_id] = LabelEncoder()
                
                self.logger.info(f"Initialized model for {prediction_type.value}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize base models: {e}")
    
    async def predict(self, request: PredictionRequest) -> PredictionResult:
        """
        Realizar predicción basada en la solicitud
        """
        start_time = datetime.now()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.prediction_cache:
                cached_result = self.prediction_cache[cache_key]
                # Check if cache is still valid
                if (datetime.now() - start_time).total_seconds() < self.cache_ttl:
                    return cached_result
            
            prediction_type = request.prediction_type
            
            # Route to specific prediction function
            if prediction_type == PredictionType.PROCESSING_TIME:
                result = await self._predict_processing_time(request)
            elif prediction_type == PredictionType.QUALITY_SCORE:
                result = await self._predict_quality_score(request)
            elif prediction_type == PredictionType.ERROR_PROBABILITY:
                result = await self._predict_error_probability(request)
            elif prediction_type == PredictionType.OPTIMAL_WORKFLOW:
                result = await self._predict_optimal_workflow(request)
            elif prediction_type == PredictionType.RESOURCE_USAGE:
                result = await self._predict_resource_usage(request)
            elif prediction_type == PredictionType.USER_BEHAVIOR:
                result = await self._predict_user_behavior(request)
            elif prediction_type == PredictionType.DOCUMENT_SIMILARITY:
                result = await self._predict_document_similarity(request)
            elif prediction_type == PredictionType.CONVERSION_SUCCESS:
                result = await self._predict_conversion_success(request)
            else:
                raise ValueError(f"Unsupported prediction type: {prediction_type}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            # Cache result
            self.prediction_cache[cache_key] = result
            
            # Log prediction for performance tracking
            self._log_prediction(request, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            raise
    
    async def _predict_processing_time(self, request: PredictionRequest) -> PredictionResult:
        """
        Predecir tiempo de procesamiento
        """
        try:
            features = request.document_features
            model_id = f"{PredictionType.PROCESSING_TIME.value}_model"
            
            # Extract relevant features
            feature_vector = self._extract_features(features, self.model_configs[PredictionType.PROCESSING_TIME]["features"])
            
            if model_id in self.models and self._is_model_trained(model_id):
                # Use trained model
                scaled_features = self.feature_scalers[model_id].transform([feature_vector])
                prediction = self.models[model_id].predict(scaled_features)[0]
                confidence = self._calculate_prediction_confidence(model_id, scaled_features)
            else:
                # Use heuristic approach
                prediction = self._heuristic_processing_time(features)
                confidence = 0.6
            
            # Generate explanation
            factors = self._identify_time_factors(features)
            explanation = f"Estimated processing time: {prediction:.1f} seconds"
            
            recommendations = []
            if prediction > 60:
                recommendations.append("Consider breaking document into smaller parts")
            if features.get("file_size", 0) > 10000000:  # 10MB
                recommendations.append("Large file detected - ensure sufficient system resources")
            
            return PredictionResult(
                prediction_type=PredictionType.PROCESSING_TIME,
                prediction=round(prediction, 1),
                confidence=confidence,
                explanation=explanation,
                factors=factors,
                model_info={"model_id": model_id, "type": "regression"},
                processing_time=0,  # Set later
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Processing time prediction failed: {e}")
            raise
    
    async def _predict_quality_score(self, request: PredictionRequest) -> PredictionResult:
        """
        Predecir puntuación de calidad
        """
        try:
            features = request.document_features
            model_id = f"{PredictionType.QUALITY_SCORE.value}_model"
            
            feature_vector = self._extract_features(features, self.model_configs[PredictionType.QUALITY_SCORE]["features"])
            
            if model_id in self.models and self._is_model_trained(model_id):
                scaled_features = self.feature_scalers[model_id].transform([feature_vector])
                prediction = self.models[model_id].predict(scaled_features)[0]
                confidence = self._calculate_prediction_confidence(model_id, scaled_features)
            else:
                prediction = self._heuristic_quality_score(features)
                confidence = 0.6
            
            # Ensure score is between 0 and 1
            prediction = max(0, min(1, prediction))
            
            factors = self._identify_quality_factors(features)
            
            quality_level = "excellent" if prediction > 0.8 else "good" if prediction > 0.6 else "fair" if prediction > 0.4 else "poor"
            explanation = f"Predicted quality score: {prediction:.2f} ({quality_level})"
            
            recommendations = []
            if prediction < 0.6:
                recommendations.append("Document may require manual review")
                recommendations.append("Consider using enhanced processing options")
            
            return PredictionResult(
                prediction_type=PredictionType.QUALITY_SCORE,
                prediction=round(prediction, 2),
                confidence=confidence,
                explanation=explanation,
                factors=factors,
                model_info={"model_id": model_id, "type": "regression"},
                processing_time=0,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Quality score prediction failed: {e}")
            raise
    
    async def _predict_error_probability(self, request: PredictionRequest) -> PredictionResult:
        """
        Predecir probabilidad de error en el procesamiento
        """
        try:
            features = request.document_features
            model_id = f"{PredictionType.ERROR_PROBABILITY.value}_model"
            
            feature_vector = self._extract_features(features, self.model_configs[PredictionType.ERROR_PROBABILITY]["features"])
            
            if model_id in self.models and self._is_model_trained(model_id):
                scaled_features = self.feature_scalers[model_id].transform([feature_vector])
                prediction_proba = self.models[model_id].predict_proba(scaled_features)[0]
                prediction = prediction_proba[1] if len(prediction_proba) > 1 else prediction_proba[0]  # Probability of error
                confidence = max(prediction_proba)
            else:
                prediction = self._heuristic_error_probability(features)
                confidence = 0.6
            
            factors = self._identify_error_factors(features)
            
            risk_level = "high" if prediction > 0.7 else "medium" if prediction > 0.4 else "low"
            explanation = f"Error probability: {prediction:.2f} ({risk_level} risk)"
            
            recommendations = []
            if prediction > 0.5:
                recommendations.append("High error probability - consider manual review")
                recommendations.append("Use multiple processing engines for validation")
            if prediction > 0.3:
                recommendations.append("Enable error monitoring and alerting")
            
            return PredictionResult(
                prediction_type=PredictionType.ERROR_PROBABILITY,
                prediction=round(prediction, 2),
                confidence=confidence,
                explanation=explanation,
                factors=factors,
                model_info={"model_id": model_id, "type": "classification"},
                processing_time=0,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error probability prediction failed: {e}")
            raise
    
    async def _predict_optimal_workflow(self, request: PredictionRequest) -> PredictionResult:
        """
        Predecir el workflow óptimo para un documento
        """
        try:
            features = request.document_features
            context = request.context
            
            # Análisis basado en características del documento
            document_type = features.get("document_type", "unknown")
            content_patterns = features.get("content_patterns", {})
            complexity_score = features.get("complexity_score", 0)
            
            # Workflows predefinidos basados en patrones
            workflow_recommendations = {}
            
            # Workflow para documentos financieros
            if content_patterns.get("financial", 0) > 5:
                workflow_recommendations["financial_analysis"] = 0.9
                
            # Workflow para documentos legales
            if content_patterns.get("legal", 0) > 5:
                workflow_recommendations["legal_review"] = 0.85
                
            # Workflow para documentos técnicos
            if content_patterns.get("technical", 0) > 5:
                workflow_recommendations["technical_processing"] = 0.8
                
            # Workflow basado en complejidad
            if complexity_score > 0.7:
                workflow_recommendations["comprehensive_analysis"] = 0.75
            elif complexity_score < 0.3:
                workflow_recommendations["quick_processing"] = 0.8
            else:
                workflow_recommendations["standard_processing"] = 0.7
            
            # Workflow basado en tipo de documento
            type_workflows = {
                "pdf": "pdf_complete_analysis",
                "word": "word_intelligence_analysis", 
                "excel": "excel_data_analysis"
            }
            
            if document_type in type_workflows:
                workflow_recommendations[type_workflows[document_type]] = 0.8
            
            # Seleccionar mejor workflow
            if workflow_recommendations:
                optimal_workflow = max(workflow_recommendations.items(), key=lambda x: x[1])
                prediction = optimal_workflow[0]
                confidence = optimal_workflow[1]
            else:
                prediction = "standard_processing"
                confidence = 0.5
            
            factors = [
                {
                    "factor": "Document Type",
                    "value": document_type,
                    "impact": "high"
                },
                {
                    "factor": "Content Patterns",
                    "value": content_patterns,
                    "impact": "medium"
                },
                {
                    "factor": "Complexity Score",
                    "value": complexity_score,
                    "impact": "medium"
                }
            ]
            
            explanation = f"Recommended workflow: {prediction} (confidence: {confidence:.2f})"
            
            recommendations = [
                f"Use {prediction} workflow for optimal results",
                "Monitor processing performance and adjust if needed"
            ]
            
            if confidence < 0.7:
                recommendations.append("Consider custom workflow configuration")
            
            return PredictionResult(
                prediction_type=PredictionType.OPTIMAL_WORKFLOW,
                prediction=prediction,
                confidence=confidence,
                explanation=explanation,
                factors=factors,
                model_info={"type": "rule_based", "workflows_available": list(workflow_recommendations.keys())},
                processing_time=0,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Optimal workflow prediction failed: {e}")
            raise
    
    async def _predict_resource_usage(self, request: PredictionRequest) -> PredictionResult:
        """
        Predecir uso de recursos
        """
        try:
            features = request.document_features
            
            # Predicción basada en características del archivo
            file_size = features.get("file_size", 0)
            page_count = features.get("page_count", 1)
            word_count = features.get("word_count", 0)
            complex_tables = features.get("complex_tables", 0)
            
            # Estimación de CPU (en CPU-segundos)
            cpu_usage = (
                file_size / 1000000 * 2 +  # 2 CPU-sec per MB
                page_count * 1.5 +          # 1.5 CPU-sec per page
                word_count / 1000 * 0.5 +   # 0.5 CPU-sec per 1000 words
                complex_tables * 3          # 3 CPU-sec per complex table
            )
            
            # Estimación de memoria (en MB)
            memory_usage = (
                file_size / 1000000 * 50 +  # 50MB per MB of file
                page_count * 10 +            # 10MB per page
                complex_tables * 20          # 20MB per complex table
            )
            
            # Estimación de almacenamiento temporal (en MB)
            storage_usage = file_size / 1000000 * 2  # 2x file size for temp storage
            
            prediction = {
                "cpu_seconds": round(cpu_usage, 1),
                "memory_mb": round(memory_usage, 1),
                "storage_mb": round(storage_usage, 1),
                "estimated_cost": round(cpu_usage * 0.01, 3)  # $0.01 per CPU-second
            }
            
            confidence = 0.8
            
            factors = [
                {"factor": "File Size", "value": f"{file_size/1000000:.1f}MB", "impact": "high"},
                {"factor": "Page Count", "value": page_count, "impact": "medium"},
                {"factor": "Complex Tables", "value": complex_tables, "impact": "medium"}
            ]
            
            explanation = f"Estimated resources: {prediction['cpu_seconds']}s CPU, {prediction['memory_mb']:.0f}MB RAM"
            
            recommendations = []
            if prediction["memory_mb"] > 1000:
                recommendations.append("High memory usage expected - ensure sufficient RAM")
            if prediction["cpu_seconds"] > 30:
                recommendations.append("Long processing time expected - consider background processing")
            
            return PredictionResult(
                prediction_type=PredictionType.RESOURCE_USAGE,
                prediction=prediction,
                confidence=confidence,
                explanation=explanation,
                factors=factors,
                model_info={"type": "heuristic", "based_on": "file_characteristics"},
                processing_time=0,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Resource usage prediction failed: {e}")
            raise
    
    async def _predict_user_behavior(self, request: PredictionRequest) -> PredictionResult:
        """
        Predecir comportamiento del usuario
        """
        try:
            features = request.document_features
            context = request.context
            
            # Análisis de patrones de comportamiento
            user_id = context.get("user_id")
            document_type = features.get("document_type")
            file_size = features.get("file_size", 0)
            
            # Predicciones basadas en patrones históricos
            predictions = {
                "will_download": 0.7,  # Probabilidad de descarga
                "will_share": 0.3,     # Probabilidad de compartir
                "will_reprocess": 0.2, # Probabilidad de reprocesar
                "satisfaction_score": 0.8  # Puntuación de satisfacción esperada
            }
            
            # Ajustar basándose en características del documento
            if document_type == "pdf" and file_size > 5000000:  # PDF grande
                predictions["will_download"] *= 1.2
                predictions["will_reprocess"] *= 0.8
            
            if document_type in ["word", "excel"]:
                predictions["will_share"] *= 1.5
            
            confidence = 0.6  # Baja confianza sin datos históricos suficientes
            
            factors = [
                {"factor": "Document Type", "value": document_type, "impact": "medium"},
                {"factor": "File Size", "value": f"{file_size/1000000:.1f}MB", "impact": "low"},
                {"factor": "Historical Data", "value": "Limited", "impact": "high"}
            ]
            
            explanation = f"User behavior predictions based on document characteristics"
            
            recommendations = [
                "Collect more user interaction data for better predictions",
                "Implement user feedback mechanisms",
                "Track download and sharing patterns"
            ]
            
            return PredictionResult(
                prediction_type=PredictionType.USER_BEHAVIOR,
                prediction=predictions,
                confidence=confidence,
                explanation=explanation,
                factors=factors,
                model_info={"type": "heuristic", "data_source": "limited"},
                processing_time=0,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"User behavior prediction failed: {e}")
            raise
    
    async def _predict_document_similarity(self, request: PredictionRequest) -> PredictionResult:
        """
        Predecir similitud con otros documentos
        """
        try:
            features = request.document_features
            
            # Crear perfil simplificado del documento
            document_profile = {
                "word_count": features.get("word_count", 0),
                "page_count": features.get("page_count", 0),
                "content_patterns": features.get("content_patterns", {}),
                "document_type": features.get("document_type", "unknown")
            }
            
            # Buscar documentos similares en perfiles existentes
            similar_documents = []
            
            for doc_id, profile in self.ai_service.document_profiles.items():
                similarity_score = self._calculate_simple_similarity(document_profile, profile)
                if similarity_score > 0.5:
                    similar_documents.append({
                        "document_id": doc_id,
                        "similarity_score": similarity_score
                    })
            
            similar_documents.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            prediction = {
                "similar_documents_count": len(similar_documents),
                "top_similarities": similar_documents[:5],
                "average_similarity": np.mean([d["similarity_score"] for d in similar_documents]) if similar_documents else 0,
                "is_unique": len(similar_documents) == 0
            }
            
            confidence = 0.8 if len(self.ai_service.document_profiles) > 10 else 0.5
            
            factors = [
                {"factor": "Corpus Size", "value": len(self.ai_service.document_profiles), "impact": "high"},
                {"factor": "Document Features", "value": len(document_profile), "impact": "medium"}
            ]
            
            explanation = f"Found {len(similar_documents)} similar documents in corpus"
            
            recommendations = []
            if prediction["is_unique"]:
                recommendations.append("Document appears unique - may require custom processing")
            elif len(similar_documents) > 5:
                recommendations.append("Document follows common pattern - use template-based processing")
            
            return PredictionResult(
                prediction_type=PredictionType.DOCUMENT_SIMILARITY,
                prediction=prediction,
                confidence=confidence,
                explanation=explanation,
                factors=factors,
                model_info={"type": "similarity_analysis", "corpus_size": len(self.ai_service.document_profiles)},
                processing_time=0,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Document similarity prediction failed: {e}")
            raise
    
    async def _predict_conversion_success(self, request: PredictionRequest) -> PredictionResult:
        """
        Predecir éxito de conversión entre formatos
        """
        try:
            features = request.document_features
            context = request.context
            
            source_format = context.get("source_format", "pdf")
            target_format = context.get("target_format", "word")
            file_size = features.get("file_size", 0)
            quality_score = features.get("quality_score", 0.8)
            complexity = features.get("complexity_score", 0.5)
            
            # Matriz de éxito por tipo de conversión
            conversion_success_rates = {
                ("pdf", "word"): 0.85,
                ("pdf", "excel"): 0.65,
                ("word", "pdf"): 0.95,
                ("word", "excel"): 0.70,
                ("excel", "word"): 0.75,
                ("excel", "pdf"): 0.90,
                ("html", "pdf"): 0.92,
                ("txt", "word"): 0.98
            }
            
            base_success_rate = conversion_success_rates.get((source_format, target_format), 0.7)
            
            # Ajustar basándose en características del documento
            adjusted_rate = base_success_rate
            
            # Penalizar archivos muy grandes
            if file_size > 50000000:  # 50MB
                adjusted_rate *= 0.8
            elif file_size > 100000000:  # 100MB
                adjusted_rate *= 0.6
            
            # Ajustar por calidad
            if quality_score < 0.5:
                adjusted_rate *= 0.7
            elif quality_score > 0.9:
                adjusted_rate *= 1.1
            
            # Ajustar por complejidad
            if complexity > 0.8:
                adjusted_rate *= 0.8
            elif complexity < 0.3:
                adjusted_rate *= 1.05
            
            # Mantener entre 0 y 1
            prediction = min(1.0, max(0.0, adjusted_rate))
            confidence = 0.8
            
            factors = [
                {"factor": "Conversion Type", "value": f"{source_format} → {target_format}", "impact": "high"},
                {"factor": "File Size", "value": f"{file_size/1000000:.1f}MB", "impact": "medium"},
                {"factor": "Quality Score", "value": quality_score, "impact": "medium"},
                {"factor": "Complexity", "value": complexity, "impact": "medium"}
            ]
            
            success_level = "high" if prediction > 0.8 else "medium" if prediction > 0.6 else "low"
            explanation = f"Conversion success probability: {prediction:.2f} ({success_level})"
            
            recommendations = []
            if prediction < 0.7:
                recommendations.append("Low success probability - consider alternative formats")
                recommendations.append("Enable enhanced conversion options")
            if file_size > 50000000:
                recommendations.append("Large file detected - consider splitting before conversion")
            
            return PredictionResult(
                prediction_type=PredictionType.CONVERSION_SUCCESS,
                prediction=round(prediction, 2),
                confidence=confidence,
                explanation=explanation,
                factors=factors,
                model_info={"type": "heuristic", "conversion_matrix": True},
                processing_time=0,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Conversion success prediction failed: {e}")
            raise
    
    def _extract_features(self, features: Dict[str, Any], feature_names: List[str]) -> List[float]:
        """
        Extraer vector de características numéricas
        """
        try:
            feature_vector = []
            
            for feature_name in feature_names:
                if feature_name in features:
                    value = features[feature_name]
                    
                    if isinstance(value, (int, float)):
                        feature_vector.append(float(value))
                    elif isinstance(value, dict):
                        # Para características complejas, usar suma de valores
                        feature_vector.append(float(sum(value.values()) if value else 0))
                    elif isinstance(value, str):
                        # Para strings, usar hash normalizado
                        feature_vector.append(float(hash(value) % 1000) / 1000)
                    else:
                        feature_vector.append(0.0)
                else:
                    feature_vector.append(0.0)
            
            return feature_vector
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            return [0.0] * len(feature_names)
    
    def _heuristic_processing_time(self, features: Dict[str, Any]) -> float:
        """
        Estimación heurística del tiempo de procesamiento
        """
        try:
            base_time = 5.0  # 5 segundos base
            
            # Tiempo basado en tamaño de archivo
            file_size = features.get("file_size", 0)
            time_from_size = file_size / 1000000 * 2  # 2 segundos por MB
            
            # Tiempo basado en páginas
            page_count = features.get("page_count", 1)
            time_from_pages = page_count * 1.5  # 1.5 segundos por página
            
            # Tiempo basado en complejidad
            tables = features.get("complex_tables", 0)
            forms = features.get("form_elements", 0)
            time_from_complexity = (tables * 2) + (forms * 1.5)
            
            total_time = base_time + time_from_size + time_from_pages + time_from_complexity
            
            return max(total_time, 1.0)  # Mínimo 1 segundo
            
        except Exception as e:
            return 30.0  # Default fallback
    
    def _heuristic_quality_score(self, features: Dict[str, Any]) -> float:
        """
        Estimación heurística de la puntuación de calidad
        """
        try:
            base_score = 0.7
            
            # Ajustar por confianza de extracción
            confidence = features.get("confidence_score", 0.8)
            score = base_score * confidence
            
            # Ajustar por validez del texto
            text_validity = features.get("text_validity", 1.0)
            score *= text_validity
            
            # Penalizar por caracteres especiales
            special_char_density = features.get("special_char_density", 0)
            score *= (1 - min(special_char_density * 2, 0.5))
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            return 0.5  # Default fallback
    
    def _heuristic_error_probability(self, features: Dict[str, Any]) -> float:
        """
        Estimación heurística de la probabilidad de error
        """
        try:
            error_prob = 0.1  # Base 10% error probability
            
            # Aumentar por baja calidad
            text_validity = features.get("text_validity", 1.0)
            if text_validity < 0.5:
                error_prob += 0.4
            elif text_validity < 0.8:
                error_prob += 0.2
            
            # Aumentar por archivo muy grande
            file_size = features.get("file_size", 0)
            if file_size > 50000000:  # 50MB
                error_prob += 0.2
            
            # Aumentar por alta densidad de caracteres especiales
            special_char_density = features.get("special_char_density", 0)
            error_prob += min(special_char_density * 2, 0.3)
            
            return max(0.0, min(1.0, error_prob))
            
        except Exception as e:
            return 0.3  # Default fallback
    
    def _identify_time_factors(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identificar factores que afectan el tiempo de procesamiento
        """
        factors = []
        
        file_size = features.get("file_size", 0)
        if file_size > 10000000:  # 10MB
            factors.append({
                "factor": "Large File Size",
                "value": f"{file_size/1000000:.1f}MB",
                "impact": "high",
                "effect": "increases processing time"
            })
        
        page_count = features.get("page_count", 0)
        if page_count > 20:
            factors.append({
                "factor": "High Page Count",
                "value": page_count,
                "impact": "medium",
                "effect": "increases processing time"
            })
        
        tables = features.get("complex_tables", 0)
        if tables > 5:
            factors.append({
                "factor": "Complex Tables",
                "value": tables,
                "impact": "medium",
                "effect": "increases processing time"
            })
        
        return factors
    
    def _identify_quality_factors(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identificar factores que afectan la calidad
        """
        factors = []
        
        confidence = features.get("confidence_score", 0.8)
        if confidence < 0.7:
            factors.append({
                "factor": "Low OCR Confidence",
                "value": confidence,
                "impact": "high",
                "effect": "decreases quality"
            })
        
        text_validity = features.get("text_validity", 1.0)
        if text_validity < 0.8:
            factors.append({
                "factor": "Text Validity Issues",
                "value": text_validity,
                "impact": "high",
                "effect": "decreases quality"
            })
        
        flesch_score = features.get("flesch_reading_ease", 50)
        if flesch_score > 0:
            factors.append({
                "factor": "Readability Score",
                "value": flesch_score,
                "impact": "medium",
                "effect": "affects text quality assessment"
            })
        
        return factors
    
    def _identify_error_factors(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identificar factores que aumentan la probabilidad de error
        """
        factors = []
        
        special_char_density = features.get("special_char_density", 0)
        if special_char_density > 0.05:
            factors.append({
                "factor": "High Special Character Density",
                "value": special_char_density,
                "impact": "high",
                "effect": "increases error probability"
            })
        
        file_size = features.get("file_size", 0)
        if file_size > 50000000:  # 50MB
            factors.append({
                "factor": "Very Large File",
                "value": f"{file_size/1000000:.1f}MB",
                "impact": "medium",
                "effect": "increases error probability"
            })
        
        return factors
    
    def _calculate_simple_similarity(self, profile1: Dict[str, Any], profile2) -> float:
        """
        Calcular similitud simple entre documentos
        """
        try:
            if hasattr(profile2, 'content_features'):
                # DocumentProfile object
                features2 = {
                    "word_count": profile2.content_features.get("word_count", 0),
                    "page_count": profile2.structural_features.get("page_count", 0),
                    "content_patterns": profile2.content_features.get("content_patterns", {}),
                    "document_type": profile2.document_type
                }
            else:
                # Dictionary
                features2 = profile2
            
            similarity_scores = []
            
            # Similitud de tipo de documento
            if profile1.get("document_type") == features2.get("document_type"):
                similarity_scores.append(0.3)
            
            # Similitud de tamaño
            size1 = profile1.get("word_count", 0)
            size2 = features2.get("word_count", 0)
            if size1 > 0 and size2 > 0:
                size_sim = min(size1, size2) / max(size1, size2)
                similarity_scores.append(size_sim * 0.3)
            
            # Similitud de patrones
            patterns1 = profile1.get("content_patterns", {})
            patterns2 = features2.get("content_patterns", {})
            if patterns1 or patterns2:
                pattern_sim = self._pattern_similarity_simple(patterns1, patterns2)
                similarity_scores.append(pattern_sim * 0.4)
            
            return sum(similarity_scores) if similarity_scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def _pattern_similarity_simple(self, patterns1: Dict[str, int], patterns2: Dict[str, int]) -> float:
        """
        Calcular similitud de patrones simplificada
        """
        try:
            if not patterns1 and not patterns2:
                return 1.0
            if not patterns1 or not patterns2:
                return 0.0
            
            all_keys = set(patterns1.keys()) | set(patterns2.keys())
            if not all_keys:
                return 1.0
            
            matches = 0
            for key in all_keys:
                val1 = patterns1.get(key, 0)
                val2 = patterns2.get(key, 0)
                if val1 > 0 and val2 > 0:
                    matches += 1
            
            return matches / len(all_keys)
            
        except Exception as e:
            return 0.0
    
    def _is_model_trained(self, model_id: str) -> bool:
        """
        Verificar si un modelo está entrenado
        """
        return (model_id in self.models and 
                hasattr(self.models[model_id], 'coef_') or 
                hasattr(self.models[model_id], 'feature_importances_'))
    
    def _calculate_prediction_confidence(self, model_id: str, features) -> float:
        """
        Calcular confianza de la predicción
        """
        try:
            if model_id not in self.model_metrics:
                return 0.7  # Default confidence
            
            metrics = self.model_metrics[model_id]
            return min(0.95, metrics.accuracy * 1.1)  # Boost slightly but cap at 0.95
            
        except Exception as e:
            return 0.7
    
    def _generate_cache_key(self, request: PredictionRequest) -> str:
        """
        Generar clave de caché para la solicitud
        """
        try:
            key_data = {
                "prediction_type": request.prediction_type.value,
                "features_hash": hash(str(sorted(request.document_features.items()))),
                "context_hash": hash(str(sorted(request.context.items())))
            }
            
            return hashlib.md5(str(key_data).encode()).hexdigest()
            
        except Exception as e:
            return str(hash(str(request)))
    
    def _log_prediction(self, request: PredictionRequest, result: PredictionResult):
        """
        Registrar predicción para seguimiento de rendimiento
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "prediction_type": request.prediction_type.value,
                "confidence": result.confidence,
                "processing_time": result.processing_time
            }
            
            self.prediction_history.append(log_entry)
            
            # Mantener solo las últimas 1000 predicciones
            if len(self.prediction_history) > 1000:
                self.prediction_history = self.prediction_history[-1000:]
                
        except Exception as e:
            self.logger.error(f"Failed to log prediction: {e}")
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del servicio predictivo
        """
        try:
            recent_predictions = len([p for p in self.prediction_history 
                                    if datetime.fromisoformat(p["timestamp"]) > datetime.now() - timedelta(hours=24)])
            
            avg_confidence = 0
            if self.prediction_history:
                avg_confidence = np.mean([p["confidence"] for p in self.prediction_history])
            
            return {
                "service_status": "operational",
                "sklearn_available": SKLEARN_AVAILABLE,
                "statsmodels_available": STATSMODELS_AVAILABLE,
                "models_loaded": len(self.models),
                "trained_models": len(self.model_metrics),
                "prediction_cache_size": len(self.prediction_cache),
                "recent_predictions_24h": recent_predictions,
                "total_predictions": len(self.prediction_history),
                "average_confidence": round(avg_confidence, 3),
                "supported_prediction_types": [pt.value for pt in PredictionType],
                "model_types_available": [mt.value for mt in ModelType]
            }
            
        except Exception as e:
            return {"error": str(e), "service_status": "error"}
    
    async def batch_predict(self, requests: List[PredictionRequest]) -> List[PredictionResult]:
        """
        Realizar predicciones en lote
        """
        try:
            results = []
            for request in requests:
                try:
                    result = await self.predict(request)
                    results.append(result)
                except Exception as e:
                    # Create error result
                    error_result = PredictionResult(
                        prediction_type=request.prediction_type,
                        prediction=None,
                        confidence=0.0,
                        explanation=f"Prediction failed: {str(e)}",
                        factors=[],
                        model_info={"error": str(e)},
                        processing_time=0.0,
                        recommendations=["Check input data and try again"]
                    )
                    results.append(error_result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Batch prediction failed: {e}")
            raise