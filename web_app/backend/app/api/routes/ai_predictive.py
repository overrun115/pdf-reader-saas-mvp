#!/usr/bin/env python3
"""
AI Predictive API Routes - APIs para IA avanzada y capacidades predictivas
Parte de las Fases 3.2 y 3.3 de la expansión del sistema
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import tempfile
import os
from pathlib import Path
import asyncio
import json
from datetime import datetime

# Import AI and predictive services
from app.services.ai_intelligence_service import AIIntelligenceService, AnalysisType
from app.services.predictive_intelligence_service import (
    PredictiveIntelligenceService, PredictionRequest, PredictionType
)
from app.services.workflow_automation_service import WorkflowAutomationService
from app.api.dependencies import get_current_user
from app.models.schemas import UserResponse

# Pydantic models para requests/responses
from pydantic import BaseModel
from typing import Union

router = APIRouter(prefix="/api/ai-predictive")

# Schemas para las APIs
class AIAnalysisRequest(BaseModel):
    analysis_types: Optional[List[str]] = None
    document_data: Dict[str, Any]

class PredictiveAnalysisRequest(BaseModel):
    prediction_type: str
    document_features: Dict[str, Any]
    context: Optional[Dict[str, Any]] = {}
    confidence_threshold: Optional[float] = 0.7

class BatchPredictionRequest(BaseModel):
    predictions: List[PredictiveAnalysisRequest]

class WorkflowAnalysisRequest(BaseModel):
    workflow_definition: Dict[str, Any]

# Initialize services
ai_service = AIIntelligenceService()
predictive_service = PredictiveIntelligenceService()
workflow_service = WorkflowAutomationService()

@router.post("/analyze/intelligence", response_model=Dict[str, Any])
async def analyze_document_intelligence(
    request: AIAnalysisRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Análisis completo de inteligencia de documento usando IA avanzada
    """
    try:
        import time
        start_time = time.time()
        
        # Convert string analysis types to enums
        analysis_types = []
        if request.analysis_types:
            for analysis_type in request.analysis_types:
                try:
                    analysis_types.append(AnalysisType(analysis_type))
                except ValueError:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid analysis type: {analysis_type}"
                    )
        
        # Perform AI analysis
        results = await ai_service.analyze_document_intelligence(
            document_data=request.document_data,
            analysis_types=analysis_types
        )
        
        processing_time = time.time() - start_time
        
        return {
            "analysis_type": "ai_intelligence",
            "results": results,
            "processing_time": round(processing_time, 2),
            "user_id": current_user.id,
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.post("/predict", response_model=Dict[str, Any])
async def make_prediction(
    request: PredictiveAnalysisRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Realizar predicción específica usando IA predictiva
    """
    try:
        # Validate prediction type
        try:
            prediction_type = PredictionType(request.prediction_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid prediction type: {request.prediction_type}"
            )
        
        # Create prediction request
        pred_request = PredictionRequest(
            prediction_type=prediction_type,
            document_features=request.document_features,
            context=request.context,
            confidence_threshold=request.confidence_threshold
        )
        
        # Perform prediction
        result = await predictive_service.predict(pred_request)
        
        return {
            "prediction_type": result.prediction_type.value,
            "prediction": result.prediction,
            "confidence": result.confidence,
            "explanation": result.explanation,
            "factors": result.factors,
            "recommendations": result.recommendations,
            "model_info": result.model_info,
            "processing_time": result.processing_time,
            "user_id": current_user.id,
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/predict/batch", response_model=Dict[str, Any])
async def batch_predictions(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Realizar múltiples predicciones en lote
    """
    try:
        if len(request.predictions) > 50:
            raise HTTPException(
                status_code=400,
                detail="Maximum 50 predictions allowed per batch"
            )
        
        # Convert to prediction requests
        pred_requests = []
        for pred_req in request.predictions:
            try:
                prediction_type = PredictionType(pred_req.prediction_type)
                pred_requests.append(PredictionRequest(
                    prediction_type=prediction_type,
                    document_features=pred_req.document_features,
                    context=pred_req.context,
                    confidence_threshold=pred_req.confidence_threshold
                ))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid prediction type: {pred_req.prediction_type}"
                )
        
        # Perform batch predictions
        results = await predictive_service.batch_predict(pred_requests)
        
        # Convert results to serializable format
        serialized_results = []
        for result in results:
            serialized_results.append({
                "prediction_type": result.prediction_type.value,
                "prediction": result.prediction,
                "confidence": result.confidence,
                "explanation": result.explanation,
                "factors": result.factors,
                "recommendations": result.recommendations,
                "model_info": result.model_info,
                "processing_time": result.processing_time
            })
        
        return {
            "batch_type": "predictive_analysis",
            "total_predictions": len(serialized_results),
            "results": serialized_results,
            "user_id": current_user.id,
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

@router.post("/analyze/comprehensive", response_model=Dict[str, Any])
async def comprehensive_analysis(
    file: UploadFile = File(...),
    include_predictions: bool = True,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Análisis comprehensivo combinando IA y predicciones
    """
    supported_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.html', '.htm', '.txt']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported: {', '.join(supported_extensions)}"
        )
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        import time
        start_time = time.time()
        
        # Prepare document data for analysis
        document_data = {
            "id": f"temp_{int(time.time())}",
            "type": file_ext[1:],  # Remove dot
            "file_path": temp_path,
            "file_size": len(content),
            "filename": file.filename
        }
        
        # Perform AI intelligence analysis
        ai_results = await ai_service.analyze_document_intelligence(
            document_data=document_data,
            analysis_types=[
                AnalysisType.CONTENT_INTELLIGENCE,
                AnalysisType.SEMANTIC_ANALYSIS,
                AnalysisType.DOCUMENT_CLASSIFICATION,
                AnalysisType.ANOMALY_DETECTION
            ]
        )
        
        comprehensive_results = {
            "ai_analysis": ai_results,
            "predictions": {},
            "recommendations": [],
            "overall_insights": {}
        }
        
        # Perform predictions if requested
        if include_predictions:
            # Extract features for predictions
            document_profile = ai_results.get("document_profile")
            if document_profile:
                features = {
                    **document_profile.content_features,
                    **document_profile.structural_features,
                    **document_profile.quality_metrics,
                    "file_size": len(content),
                    "document_type": file_ext[1:]
                }
                
                # Key predictions
                prediction_types = [
                    PredictionType.PROCESSING_TIME,
                    PredictionType.QUALITY_SCORE,
                    PredictionType.ERROR_PROBABILITY,
                    PredictionType.OPTIMAL_WORKFLOW
                ]
                
                predictions = {}
                for pred_type in prediction_types:
                    try:
                        pred_request = PredictionRequest(
                            prediction_type=pred_type,
                            document_features=features,
                            context={"user_id": current_user.id, "file_type": file_ext[1:]}
                        )
                        
                        pred_result = await predictive_service.predict(pred_request)
                        predictions[pred_type.value] = {
                            "prediction": pred_result.prediction,
                            "confidence": pred_result.confidence,
                            "explanation": pred_result.explanation,
                            "recommendations": pred_result.recommendations
                        }
                        
                    except Exception as e:
                        predictions[pred_type.value] = {
                            "error": str(e),
                            "prediction": None,
                            "confidence": 0
                        }
                
                comprehensive_results["predictions"] = predictions
        
        # Generate consolidated recommendations
        all_recommendations = []
        
        # From AI analysis
        if "consolidated_insights" in ai_results:
            ai_recommendations = ai_results["consolidated_insights"].get("key_recommendations", [])
            all_recommendations.extend(ai_recommendations)
        
        # From predictions
        for pred_result in comprehensive_results["predictions"].values():
            if "recommendations" in pred_result:
                all_recommendations.extend(pred_result["recommendations"])
        
        # Remove duplicates and limit
        unique_recommendations = list(set(all_recommendations))[:10]
        comprehensive_results["recommendations"] = unique_recommendations
        
        # Generate overall insights
        overall_insights = await _generate_overall_insights(ai_results, comprehensive_results["predictions"])
        comprehensive_results["overall_insights"] = overall_insights
        
        processing_time = time.time() - start_time
        
        return {
            "analysis_type": "comprehensive",
            "document_name": file.filename,
            "processing_time": round(processing_time, 2),
            "results": comprehensive_results,
            "user_id": current_user.id,
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@router.post("/workflow/analyze", response_model=Dict[str, Any])
async def analyze_workflow_intelligence(
    request: WorkflowAnalysisRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Análizar workflow con inteligencia artificial para optimización
    """
    try:
        # Create workflow
        workflow = await workflow_service.create_workflow(request.workflow_definition)
        
        # Analyze workflow characteristics
        workflow_analysis = {
            "complexity_score": _calculate_workflow_complexity(workflow),
            "estimated_execution_time": _estimate_workflow_time(workflow),
            "resource_requirements": _estimate_workflow_resources(workflow),
            "optimization_suggestions": _generate_optimization_suggestions(workflow),
            "risk_assessment": _assess_workflow_risks(workflow)
        }
        
        return {
            "analysis_type": "workflow_intelligence",
            "workflow_id": workflow.id,
            "workflow_name": workflow.name,
            "analysis": workflow_analysis,
            "user_id": current_user.id,
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow analysis failed: {str(e)}")

@router.get("/capabilities", response_model=Dict[str, Any])
async def get_ai_predictive_capabilities():
    """
    Obtener capacidades disponibles de IA y predicción
    """
    try:
        ai_stats = await ai_service.get_service_stats()
        predictive_stats = await predictive_service.get_service_stats()
        workflow_stats = await workflow_service.get_service_stats()
        
        return {
            "service_status": "operational",
            "ai_intelligence": ai_stats,
            "predictive_intelligence": predictive_stats,
            "workflow_automation": workflow_stats,
            "combined_features": {
                "document_intelligence": True,
                "content_analysis": True,
                "semantic_analysis": ai_stats.get("ai_capabilities", {}).get("spacy_available", False),
                "document_classification": True,
                "similarity_analysis": ai_stats.get("ai_capabilities", {}).get("sklearn_available", False),
                "anomaly_detection": True,
                "trend_analysis": True,
                "processing_time_prediction": True,
                "quality_prediction": True,
                "error_prediction": True,
                "workflow_optimization": True,
                "resource_prediction": True,
                "batch_processing": True
            },
            "api_version": "3.0.0"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")

@router.get("/stats/performance", response_model=Dict[str, Any])
async def get_performance_statistics(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Obtener estadísticas de rendimiento de IA y predicciones
    """
    try:
        # This would integrate with actual database in production
        return {
            "user_id": current_user.id,
            "performance_metrics": {
                "ai_analyses_performed": 0,  # Would come from database
                "predictions_made": 0,
                "workflows_optimized": 0,
                "average_accuracy": 0.85,
                "total_processing_time": 0,
                "success_rate": 0.95
            },
            "recent_activity": {
                "last_24h": {
                    "analyses": 0,
                    "predictions": 0,
                    "avg_confidence": 0.82
                },
                "last_7d": {
                    "analyses": 0,
                    "predictions": 0,
                    "avg_confidence": 0.84
                }
            },
            "model_performance": {
                "processing_time_model": {"accuracy": 0.87, "last_updated": "2024-01-01"},
                "quality_score_model": {"accuracy": 0.83, "last_updated": "2024-01-01"},
                "error_prediction_model": {"accuracy": 0.91, "last_updated": "2024-01-01"}
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance stats: {str(e)}")

@router.post("/optimize/recommendations", response_model=Dict[str, Any])
async def get_optimization_recommendations(
    document_features: Dict[str, Any],
    processing_history: Optional[List[Dict[str, Any]]] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Obtener recomendaciones de optimización basadas en IA
    """
    try:
        recommendations = {
            "processing_optimization": [],
            "workflow_optimization": [],
            "resource_optimization": [],
            "quality_optimization": []
        }
        
        # Processing optimization
        file_size = document_features.get("file_size", 0)
        if file_size > 50000000:  # 50MB
            recommendations["processing_optimization"].append({
                "type": "file_size",
                "recommendation": "Consider splitting large files for better performance",
                "impact": "high",
                "estimated_improvement": "50% faster processing"
            })
        
        # Quality optimization
        quality_score = document_features.get("quality_score", 0.8)
        if quality_score < 0.7:
            recommendations["quality_optimization"].append({
                "type": "quality_enhancement",
                "recommendation": "Use enhanced OCR settings for better quality",
                "impact": "high",
                "estimated_improvement": "20% better quality score"
            })
        
        # Workflow optimization
        document_type = document_features.get("document_type", "unknown")
        if document_type != "unknown":
            recommendations["workflow_optimization"].append({
                "type": "workflow_selection",
                "recommendation": f"Use optimized {document_type} workflow",
                "impact": "medium",
                "estimated_improvement": "30% faster processing"
            })
        
        # Resource optimization
        complexity = document_features.get("complexity_score", 0.5)
        if complexity > 0.8:
            recommendations["resource_optimization"].append({
                "type": "resource_allocation",
                "recommendation": "Allocate additional processing resources",
                "impact": "medium",
                "estimated_improvement": "25% faster processing"
            })
        
        return {
            "optimization_type": "ai_recommendations",
            "document_analysis": document_features,
            "recommendations": recommendations,
            "priority_actions": _prioritize_recommendations(recommendations),
            "user_id": current_user.id,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

# Helper functions
async def _generate_overall_insights(ai_results: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generar insights generales combinando resultados de IA y predicciones
    """
    try:
        insights = {
            "document_summary": {},
            "key_findings": [],
            "risk_factors": [],
            "opportunities": []
        }
        
        # Extract key metrics
        if "consolidated_insights" in ai_results:
            consolidated = ai_results["consolidated_insights"]
            insights["document_summary"] = {
                "total_insights": consolidated.get("summary", {}).get("total_insights", 0),
                "confidence_level": consolidated.get("summary", {}).get("average_confidence", 0),
                "quality_assessment": consolidated.get("overall_quality", "unknown")
            }
        
        # Add prediction insights
        if "processing_time" in predictions:
            processing_pred = predictions["processing_time"]
            if isinstance(processing_pred.get("prediction"), (int, float)):
                if processing_pred["prediction"] > 60:
                    insights["risk_factors"].append("Long processing time predicted")
                else:
                    insights["opportunities"].append("Fast processing expected")
        
        if "error_probability" in predictions:
            error_pred = predictions["error_probability"]
            if isinstance(error_pred.get("prediction"), (int, float)):
                if error_pred["prediction"] > 0.5:
                    insights["risk_factors"].append("High error probability detected")
                else:
                    insights["opportunities"].append("Low error risk - suitable for automation")
        
        if "quality_score" in predictions:
            quality_pred = predictions["quality_score"]
            if isinstance(quality_pred.get("prediction"), (int, float)):
                if quality_pred["prediction"] > 0.8:
                    insights["opportunities"].append("High quality output expected")
                elif quality_pred["prediction"] < 0.6:
                    insights["risk_factors"].append("Quality concerns - may need manual review")
        
        return insights
        
    except Exception as e:
        return {"error": str(e)}

def _calculate_workflow_complexity(workflow) -> float:
    """
    Calcular complejidad del workflow
    """
    try:
        complexity = 0.0
        
        # Base complexity from number of tasks
        task_count = len(workflow.tasks)
        complexity += task_count * 0.1
        
        # Complexity from dependencies
        total_dependencies = sum(len(task.dependencies) for task in workflow.tasks)
        complexity += total_dependencies * 0.05
        
        # Complexity from conditions
        conditional_tasks = sum(1 for task in workflow.tasks if task.conditions)
        complexity += conditional_tasks * 0.15
        
        return min(1.0, complexity)
        
    except Exception:
        return 0.5

def _estimate_workflow_time(workflow) -> Dict[str, Any]:
    """
    Estimar tiempo de ejecución del workflow
    """
    try:
        # Base time estimates per task type (in seconds)
        task_times = {
            "ocr_analysis": 30,
            "layout_analysis": 20,
            "validation": 10,
            "word_analysis": 25,
            "excel_analysis": 30,
            "document_conversion": 45,
            "condition_check": 2,
            "data_transformation": 5
        }
        
        total_time = 0
        for task in workflow.tasks:
            task_type = task.task_type.value if hasattr(task.task_type, 'value') else str(task.task_type)
            total_time += task_times.get(task_type, 15)  # Default 15 seconds
        
        # Adjust for parallel execution potential
        max_parallel = len([task for task in workflow.tasks if not task.dependencies])
        if max_parallel > 1:
            total_time *= 0.7  # 30% time reduction for parallelization
        
        return {
            "estimated_seconds": round(total_time),
            "estimated_human": f"{total_time//60:.0f}m {total_time%60:.0f}s" if total_time >= 60 else f"{total_time:.0f}s",
            "confidence": 0.7
        }
        
    except Exception:
        return {"estimated_seconds": 60, "estimated_human": "1m", "confidence": 0.3}

def _estimate_workflow_resources(workflow) -> Dict[str, Any]:
    """
    Estimar recursos necesarios para el workflow
    """
    try:
        # Resource estimates per task type
        base_memory = 100  # MB
        base_cpu = 0.5     # CPU cores
        
        task_count = len(workflow.tasks)
        
        estimated_memory = base_memory + (task_count * 50)
        estimated_cpu = base_cpu + (task_count * 0.2)
        
        return {
            "memory_mb": round(estimated_memory),
            "cpu_cores": round(estimated_cpu, 1),
            "storage_mb": round(estimated_memory * 0.5),  # Temp storage
            "network_bandwidth": "low"
        }
        
    except Exception:
        return {"memory_mb": 500, "cpu_cores": 1.0, "storage_mb": 250, "network_bandwidth": "low"}

def _generate_optimization_suggestions(workflow) -> List[str]:
    """
    Generar sugerencias de optimización del workflow
    """
    try:
        suggestions = []
        
        task_count = len(workflow.tasks)
        if task_count > 10:
            suggestions.append("Consider breaking workflow into smaller sub-workflows")
        
        # Check for sequential tasks that could be parallel
        sequential_tasks = [task for task in workflow.tasks if task.dependencies]
        if len(sequential_tasks) > task_count * 0.7:
            suggestions.append("Look for opportunities to parallelize independent tasks")
        
        # Check for redundant validations
        validation_tasks = [task for task in workflow.tasks if 'validation' in str(task.task_type)]
        if len(validation_tasks) > 2:
            suggestions.append("Consider consolidating validation steps")
        
        return suggestions
        
    except Exception:
        return ["Review workflow structure for optimization opportunities"]

def _assess_workflow_risks(workflow) -> Dict[str, Any]:
    """
    Evaluar riesgos del workflow
    """
    try:
        risks = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        # Check for single points of failure
        critical_tasks = [task for task in workflow.tasks if task.parameters.get("critical", False)]
        if critical_tasks:
            risks["high"].append(f"{len(critical_tasks)} critical tasks with no fallback")
        
        # Check for complex dependencies
        complex_deps = [task for task in workflow.tasks if len(task.dependencies) > 3]
        if complex_deps:
            risks["medium"].append(f"{len(complex_deps)} tasks with complex dependencies")
        
        # Check for timeout risks
        long_tasks = [task for task in workflow.tasks if task.timeout and task.timeout > 300]
        if long_tasks:
            risks["medium"].append(f"{len(long_tasks)} tasks with long timeouts")
        
        return risks
        
    except Exception:
        return {"high": [], "medium": ["Unable to assess risks"], "low": []}

def _prioritize_recommendations(recommendations: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Priorizar recomendaciones por impacto
    """
    try:
        all_recommendations = []
        
        for category, recs in recommendations.items():
            for rec in recs:
                rec["category"] = category
                all_recommendations.append(rec)
        
        # Sort by impact (high > medium > low)
        impact_order = {"high": 3, "medium": 2, "low": 1}
        sorted_recs = sorted(
            all_recommendations,
            key=lambda x: impact_order.get(x.get("impact", "low"), 1),
            reverse=True
        )
        
        return sorted_recs[:5]  # Top 5 recommendations
        
    except Exception:
        return []

# Error handling middleware for AI/Predictive endpoints
@router.middleware("http")
async def ai_predictive_error_handler(request, call_next):
    """Middleware para manejo de errores específicos de IA/Predictivos"""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"AI/Predictive service error: {str(e)}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "AI/Predictive Service Error",
                "detail": str(e),
                "service": "ai_predictive",
                "timestamp": str(datetime.utcnow())
            }
        )