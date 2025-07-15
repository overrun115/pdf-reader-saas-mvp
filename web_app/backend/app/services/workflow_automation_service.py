#!/usr/bin/env python3
"""
Workflow Automation Service - Motor de workflows inteligentes
Parte de la Fase 3 de la expansión de inteligencia documental
"""

import logging
import asyncio
import uuid
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
import time

# Importar servicios de inteligencia existentes
from app.services.advanced_ocr_nlp_service import AdvancedOCRNLPService
from app.services.layout_parser_service import LayoutParserService
from app.services.document_validation_service import DocumentValidationService
from app.services.word_intelligence_service import WordIntelligenceService
from app.services.excel_intelligence_service import ExcelIntelligenceService
from app.services.universal_converter_service import UniversalConverterService

logger = logging.getLogger(__name__)

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskType(str, Enum):
    OCR_ANALYSIS = "ocr_analysis"
    LAYOUT_ANALYSIS = "layout_analysis"
    VALIDATION = "validation"
    WORD_ANALYSIS = "word_analysis"
    EXCEL_ANALYSIS = "excel_analysis"
    DOCUMENT_CONVERSION = "document_conversion"
    CUSTOM_PROCESSING = "custom_processing"
    CONDITION_CHECK = "condition_check"
    DATA_TRANSFORMATION = "data_transformation"

class TriggerType(str, Enum):
    MANUAL = "manual"
    FILE_UPLOAD = "file_upload"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    COMPLETION = "completion"  # Triggered when another workflow completes

@dataclass
class WorkflowTask:
    """Individual task within a workflow"""
    id: str
    name: str
    task_type: TaskType
    parameters: Dict[str, Any]
    dependencies: List[str]  # Task IDs that must complete before this task
    conditions: Optional[Dict[str, Any]] = None  # Conditions for task execution
    timeout: Optional[int] = None  # Timeout in seconds
    retry_count: int = 0
    max_retries: int = 3
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class WorkflowDefinition:
    """Definition of a complete workflow"""
    id: str
    name: str
    description: str
    tasks: List[WorkflowTask]
    triggers: List[Dict[str, Any]]
    global_parameters: Dict[str, Any]
    created_by: str
    is_active: bool = True
    max_concurrent_executions: int = 1
    retention_days: int = 30
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class WorkflowExecution:
    """Instance of a running workflow"""
    id: str
    workflow_id: str
    status: WorkflowStatus
    triggered_by: TriggerType
    trigger_data: Dict[str, Any]
    context: Dict[str, Any]
    current_task: Optional[str] = None
    progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class WorkflowAutomationService:
    """
    Servicio de automatización de workflows inteligentes
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize intelligence services
        self.ocr_service = AdvancedOCRNLPService()
        self.layout_service = LayoutParserService()
        self.validation_service = DocumentValidationService()
        self.word_service = WordIntelligenceService()
        self.excel_service = ExcelIntelligenceService()
        self.converter_service = UniversalConverterService()
        
        # Workflow storage (in production, this would be a database)
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.active_executions: Dict[str, asyncio.Task] = {}
        
        # Scheduling and execution management
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.scheduler_running = False
        self.scheduler_task = None
        
        # Task registry - maps task types to execution functions
        self.task_registry: Dict[TaskType, Callable] = {
            TaskType.OCR_ANALYSIS: self._execute_ocr_analysis,
            TaskType.LAYOUT_ANALYSIS: self._execute_layout_analysis,
            TaskType.VALIDATION: self._execute_validation,
            TaskType.WORD_ANALYSIS: self._execute_word_analysis,
            TaskType.EXCEL_ANALYSIS: self._execute_excel_analysis,
            TaskType.DOCUMENT_CONVERSION: self._execute_document_conversion,
            TaskType.CONDITION_CHECK: self._execute_condition_check,
            TaskType.DATA_TRANSFORMATION: self._execute_data_transformation,
        }
    
    async def create_workflow(self, workflow_definition: Dict[str, Any]) -> WorkflowDefinition:
        """
        Crear una nueva definición de workflow
        """
        try:
            workflow_id = str(uuid.uuid4())
            
            # Convertir tasks a objetos WorkflowTask
            tasks = []
            for task_data in workflow_definition.get("tasks", []):
                task = WorkflowTask(
                    id=task_data.get("id", str(uuid.uuid4())),
                    name=task_data["name"],
                    task_type=TaskType(task_data["task_type"]),
                    parameters=task_data.get("parameters", {}),
                    dependencies=task_data.get("dependencies", []),
                    conditions=task_data.get("conditions"),
                    timeout=task_data.get("timeout"),
                    max_retries=task_data.get("max_retries", 3)
                )
                tasks.append(task)
            
            workflow = WorkflowDefinition(
                id=workflow_id,
                name=workflow_definition["name"],
                description=workflow_definition.get("description", ""),
                tasks=tasks,
                triggers=workflow_definition.get("triggers", []),
                global_parameters=workflow_definition.get("global_parameters", {}),
                created_by=workflow_definition.get("created_by", "system"),
                is_active=workflow_definition.get("is_active", True),
                max_concurrent_executions=workflow_definition.get("max_concurrent_executions", 1),
                retention_days=workflow_definition.get("retention_days", 30),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Validar workflow
            validation_result = await self._validate_workflow(workflow)
            if not validation_result["valid"]:
                raise Exception(f"Invalid workflow: {validation_result['errors']}")
            
            # Almacenar workflow
            self.workflows[workflow_id] = workflow
            
            self.logger.info(f"Created workflow: {workflow.name} ({workflow_id})")
            return workflow
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow: {e}")
            raise
    
    async def execute_workflow(
        self, 
        workflow_id: str, 
        trigger_type: TriggerType = TriggerType.MANUAL,
        trigger_data: Dict[str, Any] = None,
        context: Dict[str, Any] = None
    ) -> WorkflowExecution:
        """
        Ejecutar un workflow
        """
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflows[workflow_id]
            
            if not workflow.is_active:
                raise ValueError(f"Workflow {workflow_id} is not active")
            
            # Verificar límite de ejecuciones concurrentes
            active_count = len([
                exec for exec in self.executions.values() 
                if exec.workflow_id == workflow_id and exec.status == WorkflowStatus.RUNNING
            ])
            
            if active_count >= workflow.max_concurrent_executions:
                raise ValueError(f"Maximum concurrent executions ({workflow.max_concurrent_executions}) reached for workflow {workflow_id}")
            
            # Crear ejecución
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                triggered_by=trigger_type,
                trigger_data=trigger_data or {},
                context=context or {},
                started_at=datetime.now()
            )
            
            self.executions[execution_id] = execution
            
            # Iniciar ejecución asíncrona
            task = asyncio.create_task(self._run_workflow_execution(execution_id))
            self.active_executions[execution_id] = task
            
            self.logger.info(f"Started workflow execution: {execution_id} for workflow {workflow_id}")
            return execution
            
        except Exception as e:
            self.logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            raise
    
    async def _run_workflow_execution(self, execution_id: str):
        """
        Ejecutar workflow de forma asíncrona
        """
        try:
            execution = self.executions[execution_id]
            workflow = self.workflows[execution.workflow_id]
            
            execution.status = WorkflowStatus.RUNNING
            
            # Crear copia de las tareas para esta ejecución
            tasks = {task.id: WorkflowTask(**asdict(task)) for task in workflow.tasks}
            
            # Ejecutar tareas según dependencias
            completed_tasks = set()
            total_tasks = len(tasks)
            
            while len(completed_tasks) < total_tasks:
                # Encontrar tareas que pueden ejecutarse (dependencias cumplidas)
                ready_tasks = []
                for task_id, task in tasks.items():
                    if (task.status == WorkflowStatus.PENDING and 
                        all(dep in completed_tasks for dep in task.dependencies)):
                        ready_tasks.append(task_id)
                
                if not ready_tasks:
                    # No hay tareas listas - verificar si hay tareas en ejecución
                    running_tasks = [t for t in tasks.values() if t.status == WorkflowStatus.RUNNING]
                    if not running_tasks:
                        # Deadlock - algunas tareas no pueden ejecutarse
                        pending_tasks = [t for t in tasks.values() if t.status == WorkflowStatus.PENDING]
                        raise Exception(f"Workflow deadlock: {len(pending_tasks)} tasks cannot be executed")
                    
                    # Esperar a que termine alguna tarea
                    await asyncio.sleep(1)
                    continue
                
                # Ejecutar tareas listas en paralelo
                task_futures = []
                for task_id in ready_tasks:
                    task = tasks[task_id]
                    future = asyncio.create_task(self._execute_task(task, execution.context))
                    task_futures.append((task_id, future))
                
                # Esperar a que terminen las tareas
                for task_id, future in task_futures:
                    try:
                        result = await future
                        task = tasks[task_id]
                        task.status = WorkflowStatus.COMPLETED
                        task.result = result
                        task.completed_at = datetime.now()
                        completed_tasks.add(task_id)
                        
                        # Actualizar contexto con resultado
                        execution.context[f"task_{task_id}_result"] = result
                        
                    except Exception as e:
                        task = tasks[task_id]
                        task.error = str(e)
                        
                        # Intentar retry si es posible
                        if task.retry_count < task.max_retries:
                            task.retry_count += 1
                            task.status = WorkflowStatus.PENDING
                            self.logger.warning(f"Task {task_id} failed, retrying ({task.retry_count}/{task.max_retries}): {e}")
                        else:
                            task.status = WorkflowStatus.FAILED
                            completed_tasks.add(task_id)
                            self.logger.error(f"Task {task_id} failed permanently: {e}")
                            
                            # Si la tarea es crítica, fallar todo el workflow
                            if task.parameters.get("critical", False):
                                execution.status = WorkflowStatus.FAILED
                                execution.error = f"Critical task {task_id} failed: {e}"
                                execution.completed_at = datetime.now()
                                return
                
                # Actualizar progreso
                execution.progress = len(completed_tasks) / total_tasks
            
            # Verificar si hay tareas fallidas
            failed_tasks = [t for t in tasks.values() if t.status == WorkflowStatus.FAILED]
            if failed_tasks:
                execution.status = WorkflowStatus.FAILED
                execution.error = f"{len(failed_tasks)} tasks failed"
            else:
                execution.status = WorkflowStatus.COMPLETED
                # Compilar resultados finales
                execution.result = {
                    "tasks_completed": len(completed_tasks),
                    "task_results": {task_id: task.result for task_id, task in tasks.items() if task.result},
                    "execution_time": (datetime.now() - execution.started_at).total_seconds()
                }
            
            execution.completed_at = datetime.now()
            execution.progress = 1.0
            
            self.logger.info(f"Workflow execution {execution_id} completed with status: {execution.status}")
            
        except Exception as e:
            execution = self.executions[execution_id]
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.now()
            self.logger.error(f"Workflow execution {execution_id} failed: {e}")
        
        finally:
            # Limpiar ejecución activa
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def _execute_task(self, task: WorkflowTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecutar una tarea individual
        """
        try:
            task.status = WorkflowStatus.RUNNING
            task.started_at = datetime.now()
            
            # Verificar condiciones
            if task.conditions and not await self._check_conditions(task.conditions, context):
                return {"skipped": True, "reason": "Conditions not met"}
            
            # Ejecutar tarea según tipo
            if task.task_type in self.task_registry:
                executor_func = self.task_registry[task.task_type]
                result = await executor_func(task.parameters, context)
                return result
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
                
        except Exception as e:
            task.status = WorkflowStatus.FAILED
            task.error = str(e)
            raise
    
    async def _check_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Verificar condiciones para ejecución de tarea
        """
        try:
            condition_type = conditions.get("type", "and")
            rules = conditions.get("rules", [])
            
            results = []
            for rule in rules:
                field = rule.get("field")
                operator = rule.get("operator")
                value = rule.get("value")
                
                # Obtener valor del contexto
                field_value = context.get(field)
                
                # Evaluar condición
                if operator == "equals":
                    results.append(field_value == value)
                elif operator == "not_equals":
                    results.append(field_value != value)
                elif operator == "greater_than":
                    results.append(float(field_value or 0) > float(value))
                elif operator == "less_than":
                    results.append(float(field_value or 0) < float(value))
                elif operator == "contains":
                    results.append(value in str(field_value or ""))
                elif operator == "exists":
                    results.append(field_value is not None)
                else:
                    results.append(True)  # Unknown operator - assume true
            
            # Combinar resultados
            if condition_type == "and":
                return all(results)
            elif condition_type == "or":
                return any(results)
            else:
                return all(results)  # Default to AND
                
        except Exception as e:
            self.logger.warning(f"Error checking conditions: {e}")
            return True  # Default to true on error
    
    # Task execution methods
    async def _execute_ocr_analysis(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar análisis OCR"""
        file_path = parameters.get("file_path") or context.get("file_path")
        page_num = parameters.get("page_num", 0)
        enhance_quality = parameters.get("enhance_quality", True)
        
        if not file_path:
            raise ValueError("file_path is required for OCR analysis")
        
        result = await self.ocr_service.process_pdf_page(file_path, page_num, enhance_quality)
        return {"ocr_result": result}
    
    async def _execute_layout_analysis(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar análisis de layout"""
        file_path = parameters.get("file_path") or context.get("file_path")
        enhanced_mode = parameters.get("enhanced_mode", True)
        
        if not file_path:
            raise ValueError("file_path is required for layout analysis")
        
        if enhanced_mode:
            result = await self.layout_service.enhanced_analyze_document_layout(file_path)
        else:
            result = await self.layout_service.analyze_document_layout(file_path)
        
        return {"layout_result": result}
    
    async def _execute_validation(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar validación de datos"""
        elements = parameters.get("elements") or context.get("elements")
        document_type = parameters.get("document_type")
        
        if not elements:
            raise ValueError("elements are required for validation")
        
        validation_results = await self.validation_service.validate_document_elements(elements, document_type)
        return {"validation_results": validation_results}
    
    async def _execute_word_analysis(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar análisis de documento Word"""
        file_path = parameters.get("file_path") or context.get("file_path")
        
        if not file_path:
            raise ValueError("file_path is required for Word analysis")
        
        result = await self.word_service.analyze_word_document(file_path)
        return {"word_analysis": result}
    
    async def _execute_excel_analysis(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar análisis de archivo Excel"""
        file_path = parameters.get("file_path") or context.get("file_path")
        
        if not file_path:
            raise ValueError("file_path is required for Excel analysis")
        
        result = await self.excel_service.analyze_excel_file(file_path)
        return {"excel_analysis": result}
    
    async def _execute_document_conversion(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar conversión de documento"""
        source_file = parameters.get("source_file") or context.get("file_path")
        target_format = parameters.get("target_format")
        output_file = parameters.get("output_file")
        options = parameters.get("options", {})
        
        if not all([source_file, target_format, output_file]):
            raise ValueError("source_file, target_format, and output_file are required for conversion")
        
        result = await self.converter_service.convert_document(source_file, target_format, output_file, options)
        return {"conversion_result": result}
    
    async def _execute_condition_check(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar verificación de condiciones"""
        conditions = parameters.get("conditions", {})
        result = await self._check_conditions(conditions, context)
        return {"condition_met": result}
    
    async def _execute_data_transformation(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar transformación de datos"""
        transformations = parameters.get("transformations", [])
        data = parameters.get("data") or context
        
        result = data.copy()
        
        for transform in transformations:
            transform_type = transform.get("type")
            source_field = transform.get("source")
            target_field = transform.get("target")
            
            if transform_type == "copy":
                result[target_field] = result.get(source_field)
            elif transform_type == "rename":
                result[target_field] = result.pop(source_field, None)
            elif transform_type == "format":
                format_str = transform.get("format", "{value}")
                value = result.get(source_field)
                result[target_field] = format_str.format(value=value)
        
        return {"transformed_data": result}
    
    async def _validate_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """
        Validar definición de workflow
        """
        errors = []
        
        # Verificar que hay al menos una tarea
        if not workflow.tasks:
            errors.append("Workflow must have at least one task")
        
        # Verificar IDs únicos de tareas
        task_ids = [task.id for task in workflow.tasks]
        if len(task_ids) != len(set(task_ids)):
            errors.append("Task IDs must be unique")
        
        # Verificar dependencias válidas
        for task in workflow.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    errors.append(f"Task {task.id} has invalid dependency: {dep}")
        
        # Verificar que no hay dependencias circulares
        if self._has_circular_dependencies(workflow.tasks):
            errors.append("Workflow has circular dependencies")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _has_circular_dependencies(self, tasks: List[WorkflowTask]) -> bool:
        """
        Verificar dependencias circulares usando DFS
        """
        visited = set()
        rec_stack = set()
        
        def visit(task_id: str) -> bool:
            if task_id in rec_stack:
                return True  # Ciclo detectado
            if task_id in visited:
                return False
            
            visited.add(task_id)
            rec_stack.add(task_id)
            
            # Encontrar tarea
            task = next((t for t in tasks if t.id == task_id), None)
            if task:
                for dep in task.dependencies:
                    if visit(dep):
                        return True
            
            rec_stack.remove(task_id)
            return False
        
        for task in tasks:
            if task.id not in visited:
                if visit(task.id):
                    return True
        
        return False
    
    # Management and monitoring methods
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Obtener estado de ejecución de workflow
        """
        if execution_id not in self.executions:
            raise ValueError(f"Execution {execution_id} not found")
        
        execution = self.executions[execution_id]
        return {
            "execution_id": execution.id,
            "workflow_id": execution.workflow_id,
            "status": execution.status,
            "progress": execution.progress,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "current_task": execution.current_task,
            "error": execution.error,
            "result": execution.result
        }
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """
        Cancelar ejecución de workflow
        """
        try:
            if execution_id in self.active_executions:
                task = self.active_executions[execution_id]
                task.cancel()
                
                execution = self.executions[execution_id]
                execution.status = WorkflowStatus.CANCELLED
                execution.completed_at = datetime.now()
                
                del self.active_executions[execution_id]
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error cancelling workflow {execution_id}: {e}")
            return False
    
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """
        Listar todos los workflows
        """
        return [
            {
                "id": wf.id,
                "name": wf.name,
                "description": wf.description,
                "is_active": wf.is_active,
                "task_count": len(wf.tasks),
                "created_at": wf.created_at.isoformat() if wf.created_at else None,
                "updated_at": wf.updated_at.isoformat() if wf.updated_at else None
            }
            for wf in self.workflows.values()
        ]
    
    async def get_workflow_executions(self, workflow_id: str = None) -> List[Dict[str, Any]]:
        """
        Obtener ejecuciones de workflows
        """
        executions = self.executions.values()
        if workflow_id:
            executions = [e for e in executions if e.workflow_id == workflow_id]
        
        return [
            {
                "execution_id": exec.id,
                "workflow_id": exec.workflow_id,
                "status": exec.status,
                "progress": exec.progress,
                "triggered_by": exec.triggered_by,
                "started_at": exec.started_at.isoformat() if exec.started_at else None,
                "completed_at": exec.completed_at.isoformat() if exec.completed_at else None,
                "error": exec.error
            }
            for exec in executions
        ]
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del servicio
        """
        total_workflows = len(self.workflows)
        active_workflows = len([wf for wf in self.workflows.values() if wf.is_active])
        total_executions = len(self.executions)
        active_executions = len(self.active_executions)
        
        # Estadísticas de estado
        status_counts = {}
        for execution in self.executions.values():
            status = execution.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "service_status": "operational",
            "workflows": {
                "total": total_workflows,
                "active": active_workflows
            },
            "executions": {
                "total": total_executions,
                "active": active_executions,
                "by_status": status_counts
            },
            "supported_task_types": [task_type.value for task_type in TaskType],
            "supported_trigger_types": [trigger.value for trigger in TriggerType]
        }
    
    async def create_preset_workflows(self) -> List[WorkflowDefinition]:
        """
        Crear workflows predefinidos comunes
        """
        preset_workflows = [
            # Workflow 1: Análisis completo de PDF
            {
                "name": "Complete PDF Analysis",
                "description": "Comprehensive analysis of PDF documents with OCR, layout, and validation",
                "tasks": [
                    {
                        "id": "ocr_task",
                        "name": "OCR Analysis",
                        "task_type": "ocr_analysis",
                        "parameters": {"enhance_quality": True},
                        "dependencies": []
                    },
                    {
                        "id": "layout_task",
                        "name": "Layout Analysis",
                        "task_type": "layout_analysis",
                        "parameters": {"enhanced_mode": True},
                        "dependencies": []
                    },
                    {
                        "id": "validation_task",
                        "name": "Data Validation",
                        "task_type": "validation",
                        "parameters": {"document_type": "pdf"},
                        "dependencies": ["ocr_task"]
                    }
                ],
                "triggers": [{"type": "file_upload", "filter": {"extension": ".pdf"}}],
                "global_parameters": {},
                "created_by": "system"
            },
            
            # Workflow 2: Conversión automática PDF a Word
            {
                "name": "PDF to Word Conversion",
                "description": "Automatic conversion of PDF to Word with quality optimization",
                "tasks": [
                    {
                        "id": "convert_task",
                        "name": "Convert to Word",
                        "task_type": "document_conversion",
                        "parameters": {
                            "target_format": "word",
                            "options": {"preserve_layout": True}
                        },
                        "dependencies": []
                    }
                ],
                "triggers": [{"type": "file_upload", "filter": {"extension": ".pdf"}}],
                "global_parameters": {},
                "created_by": "system"
            },
            
            # Workflow 3: Análisis de calidad de documentos
            {
                "name": "Document Quality Analysis",
                "description": "Multi-format document quality assessment and recommendations",
                "tasks": [
                    {
                        "id": "quality_check",
                        "name": "Quality Assessment",
                        "task_type": "condition_check",
                        "parameters": {
                            "conditions": {
                                "type": "and",
                                "rules": [
                                    {"field": "file_size", "operator": "less_than", "value": "50000000"}
                                ]
                            }
                        },
                        "dependencies": []
                    },
                    {
                        "id": "word_analysis",
                        "name": "Word Analysis",
                        "task_type": "word_analysis",
                        "parameters": {},
                        "dependencies": ["quality_check"],
                        "conditions": {
                            "type": "and",
                            "rules": [
                                {"field": "file_extension", "operator": "contains", "value": "doc"}
                            ]
                        }
                    },
                    {
                        "id": "excel_analysis",
                        "name": "Excel Analysis", 
                        "task_type": "excel_analysis",
                        "parameters": {},
                        "dependencies": ["quality_check"],
                        "conditions": {
                            "type": "and",
                            "rules": [
                                {"field": "file_extension", "operator": "contains", "value": "xls"}
                            ]
                        }
                    }
                ],
                "triggers": [{"type": "manual"}],
                "global_parameters": {},
                "created_by": "system"
            }
        ]
        
        created_workflows = []
        for preset in preset_workflows:
            try:
                workflow = await self.create_workflow(preset)
                created_workflows.append(workflow)
                self.logger.info(f"Created preset workflow: {workflow.name}")
            except Exception as e:
                self.logger.error(f"Failed to create preset workflow {preset['name']}: {e}")
        
        return created_workflows