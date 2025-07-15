#!/usr/bin/env python3
"""
Enterprise API Routes - APIs para integraciones y capacidades empresariales
Parte de la Fase 4 de la expansión del sistema
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks, Security
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
import tempfile
import os
from pathlib import Path
import asyncio
import json
from datetime import datetime, timedelta
import uuid

# Import enterprise services
from app.services.enterprise_integration_service import (
    EnterpriseIntegrationService, IntegrationConfig, IntegrationType, 
    SyncRequest, DataSyncDirection, DocumentMapping
)
from app.services.data_platform_service import (
    DataPlatformService, DataSource, DataSourceType, DataQuery, 
    DataPipeline, DataFormat, AggregationType, TimeGranularity
)
from app.services.ecosystem_connector_service import (
    EcosystemConnectorService, EcosystemConnection, EcosystemType,
    DataFlow, SyncMode, ConnectionStatus
)
from app.services.enterprise_security_service import (
    EnterpriseSecurityService, SecurityPolicy, SecurityLevel,
    AccessPermission, AccessLevel, ComplianceStandard, ThreatType
)

from app.api.dependencies import get_current_user
from app.models.schemas import UserResponse

# Pydantic models para requests/responses
from pydantic import BaseModel
from typing import Union

router = APIRouter(prefix="/api/enterprise")
security = HTTPBearer()

# Initialize enterprise services
integration_service = EnterpriseIntegrationService()
data_platform_service = DataPlatformService()
ecosystem_service = EcosystemConnectorService()
security_service = EnterpriseSecurityService()

# Schemas para las APIs

class IntegrationConfigRequest(BaseModel):
    integration_type: str
    endpoint_url: str
    api_key: str
    api_secret: Optional[str] = None
    oauth_token: Optional[str] = None
    additional_headers: Optional[Dict[str, str]] = None
    rate_limit_per_minute: int = 100

class SyncDocumentRequest(BaseModel):
    integration_id: str
    source_path: str
    target_path: str
    field_mappings: List[Dict[str, Any]]
    sync_direction: str = "push_only"
    sync_options: Dict[str, Any] = {}

class DataSourceRequest(BaseModel):
    source_type: str
    connection_string: str
    schema: Dict[str, Any]
    update_frequency: str
    metadata: Optional[Dict[str, Any]] = {}

class DataQueryRequest(BaseModel):
    query_type: str = "select"
    source_tables: List[str]
    filters: Optional[Dict[str, Any]] = {}
    aggregations: Optional[List[Dict[str, Any]]] = []
    time_range: Optional[List[str]] = None
    limit: int = 1000
    offset: int = 0

class EcosystemConnectionRequest(BaseModel):
    ecosystem_type: str
    connection_name: str
    credentials: Dict[str, str]
    configuration: Dict[str, Any]
    sync_mode: str = "manual"

class SecurityPolicyRequest(BaseModel):
    name: str
    description: str
    security_level: str
    rules: List[Dict[str, Any]]
    compliance_standards: List[str]

# Enterprise Integration Endpoints

@router.post("/integrations/register", response_model=Dict[str, Any])
async def register_integration(
    request: IntegrationConfigRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Registrar nueva integración empresarial"""
    try:
        integration_id = f"integration_{int(datetime.now().timestamp())}"
        
        config = IntegrationConfig(
            integration_type=IntegrationType(request.integration_type),
            endpoint_url=request.endpoint_url,
            api_key=request.api_key,
            api_secret=request.api_secret,
            oauth_token=request.oauth_token,
            additional_headers=request.additional_headers or {},
            rate_limit_per_minute=request.rate_limit_per_minute
        )
        
        success = await integration_service.register_integration(integration_id, config)
        
        if success:
            return {
                "integration_id": integration_id,
                "status": "registered",
                "integration_type": request.integration_type,
                "user_id": current_user.id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to register integration")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid integration type: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration registration failed: {str(e)}")

@router.post("/integrations/{integration_id}/sync", response_model=Dict[str, Any])
async def sync_documents(
    integration_id: str,
    request: SyncDocumentRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Sincronizar documentos con sistema externo"""
    try:
        # Crear mapeos de documentos
        field_mappings = []
        for mapping_data in request.field_mappings:
            mapping = DocumentMapping(
                source_field=mapping_data["source_field"],
                target_field=mapping_data["target_field"],
                field_type=mapping_data.get("field_type", "string"),
                transformation_rule=mapping_data.get("transformation_rule"),
                required=mapping_data.get("required", False)
            )
            field_mappings.append(mapping)
        
        sync_request = SyncRequest(
            integration_type=IntegrationType(request.integration_id.split('_')[0]),  # Inferir del ID
            sync_direction=DataSyncDirection(request.sync_direction),
            document_data={
                "source_path": request.source_path,
                "target_path": request.target_path
            },
            field_mappings=field_mappings,
            sync_options=request.sync_options
        )
        
        result = await integration_service.sync_document_data(integration_id, sync_request)
        
        return {
            "sync_id": result.sync_id,
            "status": result.status,
            "integration_type": result.integration_type,
            "records_processed": result.synced_records,
            "processing_time": result.processing_time,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document sync failed: {str(e)}")

@router.get("/integrations", response_model=Dict[str, Any])
async def list_integrations(
    current_user: UserResponse = Depends(get_current_user)
):
    """Listar integraciones disponibles"""
    try:
        integrations = []
        
        # En producción, obtener de base de datos filtrado por usuario
        # Por ahora, obtener estadísticas del servicio
        stats = await integration_service.get_service_stats()
        
        return {
            "integrations": integrations,
            "service_stats": stats,
            "supported_types": [integration_type.value for integration_type in IntegrationType],
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list integrations: {str(e)}")

@router.get("/integrations/{integration_id}/status", response_model=Dict[str, Any])
async def get_integration_status(
    integration_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Obtener estado de integración"""
    try:
        status = await integration_service.get_integration_status(integration_id)
        
        return {
            "integration_id": integration_id,
            "status": status,
            "user_id": current_user.id,
            "checked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get integration status: {str(e)}")

# Data Platform Endpoints

@router.post("/data/sources/register", response_model=Dict[str, Any])
async def register_data_source(
    request: DataSourceRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Registrar nueva fuente de datos"""
    try:
        source_id = f"source_{int(datetime.now().timestamp())}"
        
        data_source = DataSource(
            source_id=source_id,
            source_type=DataSourceType(request.source_type),
            connection_string=request.connection_string,
            schema=request.schema,
            update_frequency=request.update_frequency,
            metadata=request.metadata
        )
        
        success = await data_platform_service.register_data_source(data_source)
        
        if success:
            return {
                "source_id": source_id,
                "status": "registered",
                "source_type": request.source_type,
                "user_id": current_user.id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to register data source")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid source type: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data source registration failed: {str(e)}")

@router.post("/data/query", response_model=Dict[str, Any])
async def execute_data_query(
    request: DataQueryRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Ejecutar consulta de datos"""
    try:
        query_id = f"query_{int(datetime.now().timestamp())}"
        
        # Parsear time_range si se proporciona
        time_range = None
        if request.time_range and len(request.time_range) == 2:
            time_range = (
                datetime.fromisoformat(request.time_range[0]),
                datetime.fromisoformat(request.time_range[1])
            )
        
        data_query = DataQuery(
            query_id=query_id,
            query_type=request.query_type,
            source_tables=request.source_tables,
            filters=request.filters or {},
            aggregations=request.aggregations or [],
            time_range=time_range,
            limit=request.limit,
            offset=request.offset
        )
        
        result = await data_platform_service.execute_query(data_query)
        
        return {
            "query_id": query_id,
            "result": result,
            "user_id": current_user.id,
            "executed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

@router.post("/data/insights/generate", response_model=Dict[str, Any])
async def generate_data_insights(
    source_ids: List[str],
    insight_types: List[str],
    current_user: UserResponse = Depends(get_current_user)
):
    """Generar insights de datos"""
    try:
        insights = await data_platform_service.generate_insights(source_ids, insight_types)
        
        return {
            "insights_generated": len(insights),
            "insights": [
                {
                    "insight_id": insight.insight_id,
                    "insight_type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "data": insight.data
                }
                for insight in insights
            ],
            "user_id": current_user.id,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")

@router.post("/data/dashboard/create", response_model=Dict[str, Any])
async def create_data_dashboard(
    dashboard_config: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user)
):
    """Crear dashboard de datos"""
    try:
        dashboard_config["dashboard_id"] = f"dashboard_{current_user.id}_{int(datetime.now().timestamp())}"
        
        dashboard = await data_platform_service.create_dashboard(dashboard_config)
        
        return {
            "dashboard": dashboard,
            "user_id": current_user.id,
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard creation failed: {str(e)}")

@router.get("/data/metrics/realtime", response_model=Dict[str, Any])
async def get_realtime_metrics(
    metric_names: List[str],
    current_user: UserResponse = Depends(get_current_user)
):
    """Obtener métricas en tiempo real"""
    try:
        metrics = await data_platform_service.get_real_time_metrics(metric_names)
        
        return {
            "metrics": metrics,
            "user_id": current_user.id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

# Ecosystem Connector Endpoints

@router.post("/ecosystem/connections/create", response_model=Dict[str, Any])
async def create_ecosystem_connection(
    request: EcosystemConnectionRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Crear conexión con ecosistema externo"""
    try:
        connection_id = f"connection_{int(datetime.now().timestamp())}"
        
        connection = EcosystemConnection(
            connection_id=connection_id,
            ecosystem_type=EcosystemType(request.ecosystem_type),
            connection_name=request.connection_name,
            credentials=request.credentials,
            configuration=request.configuration,
            sync_mode=SyncMode(request.sync_mode)
        )
        
        success = await ecosystem_service.create_connection(connection)
        
        if success:
            return {
                "connection_id": connection_id,
                "status": "created",
                "ecosystem_type": request.ecosystem_type,
                "user_id": current_user.id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create ecosystem connection")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid ecosystem type: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection creation failed: {str(e)}")

@router.post("/ecosystem/connections/{connection_id}/sync", response_model=Dict[str, Any])
async def sync_ecosystem_documents(
    connection_id: str,
    source_path: str,
    target_path: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Sincronizar documentos con ecosistema"""
    try:
        operation = await ecosystem_service.sync_documents(connection_id, source_path, target_path)
        
        return {
            "operation_id": operation.operation_id,
            "status": operation.status,
            "records_processed": operation.records_processed,
            "started_at": operation.started_at.isoformat(),
            "completed_at": operation.completed_at.isoformat() if operation.completed_at else None,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ecosystem sync failed: {str(e)}")

@router.get("/ecosystem/connections/{connection_id}/files", response_model=Dict[str, Any])
async def list_ecosystem_files(
    connection_id: str,
    path: str = "/",
    current_user: UserResponse = Depends(get_current_user)
):
    """Listar archivos en ecosistema"""
    try:
        files = await ecosystem_service.list_files(connection_id, path)
        
        return {
            "connection_id": connection_id,
            "path": path,
            "files": files,
            "file_count": len(files),
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@router.post("/ecosystem/connections/{connection_id}/download", response_model=Dict[str, Any])
async def download_ecosystem_file(
    connection_id: str,
    file_path: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Descargar archivo desde ecosistema"""
    try:
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        local_path = temp_file.name
        temp_file.close()
        
        success = await ecosystem_service.download_file(connection_id, file_path, local_path)
        
        if success:
            return {
                "connection_id": connection_id,
                "file_path": file_path,
                "local_path": local_path,
                "status": "downloaded",
                "user_id": current_user.id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to download file")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")

@router.get("/ecosystem/capabilities/{ecosystem_type}", response_model=Dict[str, Any])
async def get_ecosystem_capabilities(
    ecosystem_type: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Obtener capacidades del ecosistema"""
    try:
        capabilities = await ecosystem_service.get_ecosystem_capabilities(EcosystemType(ecosystem_type))
        
        return {
            "ecosystem_type": ecosystem_type,
            "capabilities": capabilities,
            "user_id": current_user.id,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid ecosystem type: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")

# Enterprise Security Endpoints

@router.post("/security/authenticate", response_model=Dict[str, Any])
async def enterprise_authenticate(
    username: str,
    password: str,
    ip_address: str,
    user_agent: str = "Unknown"
):
    """Autenticación empresarial avanzada"""
    try:
        result = await security_service.authenticate_user(username, password, ip_address, user_agent)
        
        return {
            "authentication": result,
            "authenticated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@router.post("/security/validate-session", response_model=Dict[str, Any])
async def validate_enterprise_session(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Validar sesión empresarial"""
    try:
        session_token = credentials.credentials
        # En producción, obtener IP del request
        ip_address = "127.0.0.1"  
        
        result = await security_service.validate_session(session_token, ip_address)
        
        return {
            "session_validation": result,
            "validated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session validation failed: {str(e)}")

@router.post("/security/policies/create", response_model=Dict[str, Any])
async def create_security_policy(
    request: SecurityPolicyRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Crear política de seguridad"""
    try:
        policy_id = f"policy_{int(datetime.now().timestamp())}"
        
        policy = SecurityPolicy(
            policy_id=policy_id,
            name=request.name,
            description=request.description,
            security_level=SecurityLevel(request.security_level),
            rules=request.rules,
            compliance_standards=[ComplianceStandard(std) for std in request.compliance_standards]
        )
        
        success = await security_service.create_security_policy(policy)
        
        if success:
            return {
                "policy_id": policy_id,
                "status": "created",
                "security_level": request.security_level,
                "user_id": current_user.id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create security policy")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid security level or compliance standard: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy creation failed: {str(e)}")

@router.post("/security/scan-threats", response_model=Dict[str, Any])
async def scan_security_threats(
    request_data: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user)
):
    """Escanear amenazas de seguridad"""
    try:
        # Agregar información del usuario al request
        request_data["user_id"] = current_user.id
        request_data["ip_address"] = request_data.get("ip_address", "127.0.0.1")
        
        scan_result = await security_service.scan_for_threats(request_data)
        
        return {
            "scan_result": scan_result,
            "user_id": current_user.id,
            "scanned_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Threat scan failed: {str(e)}")

@router.post("/security/encrypt", response_model=Dict[str, Any])
async def encrypt_enterprise_data(
    data: str,
    key_id: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Encriptar datos empresariales"""
    try:
        result = await security_service.encrypt_data(data, key_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "encryption_result": result,
            "user_id": current_user.id,
            "encrypted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")

@router.post("/security/decrypt", response_model=Dict[str, Any])
async def decrypt_enterprise_data(
    encrypted_data: str,
    key_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Desencriptar datos empresariales"""
    try:
        result = await security_service.decrypt_data(encrypted_data, key_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "decryption_result": result,
            "user_id": current_user.id,
            "decrypted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")

@router.get("/security/audit/report", response_model=Dict[str, Any])
async def generate_audit_report(
    start_date: str,
    end_date: str,
    user_id: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Generar reporte de auditoría"""
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        report = await security_service.generate_audit_report(start_dt, end_dt, user_id)
        
        return {
            "audit_report": report,
            "requested_by": current_user.id,
            "generated_at": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit report generation failed: {str(e)}")

@router.get("/security/compliance/{standard}", response_model=Dict[str, Any])
async def check_compliance_standard(
    standard: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Verificar cumplimiento de estándar"""
    try:
        compliance_result = await security_service.check_compliance(ComplianceStandard(standard))
        
        return {
            "compliance_check": compliance_result,
            "checked_by": current_user.id,
            "checked_at": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid compliance standard: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")

@router.get("/security/dashboard", response_model=Dict[str, Any])
async def get_security_dashboard(
    current_user: UserResponse = Depends(get_current_user)
):
    """Obtener dashboard de seguridad"""
    try:
        dashboard = await security_service.get_security_dashboard()
        
        return {
            "security_dashboard": dashboard,
            "user_id": current_user.id,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get security dashboard: {str(e)}")

# General Enterprise Endpoints

@router.get("/status", response_model=Dict[str, Any])
async def get_enterprise_status(
    current_user: UserResponse = Depends(get_current_user)
):
    """Obtener estado general de servicios empresariales"""
    try:
        # Obtener estadísticas de todos los servicios
        integration_stats = await integration_service.get_service_stats()
        data_platform_stats = await data_platform_service.get_service_stats()
        ecosystem_stats = await ecosystem_service.get_service_stats()
        security_stats = await security_service.get_service_stats()
        
        return {
            "enterprise_status": "operational",
            "services": {
                "enterprise_integration": integration_stats,
                "data_platform": data_platform_stats,
                "ecosystem_connector": ecosystem_stats,
                "enterprise_security": security_stats
            },
            "overall_health": {
                "services_operational": 4,
                "total_services": 4,
                "uptime_percentage": 100.0
            },
            "user_id": current_user.id,
            "checked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enterprise status: {str(e)}")

@router.get("/capabilities", response_model=Dict[str, Any])
async def get_enterprise_capabilities():
    """Obtener capacidades empresariales disponibles"""
    try:
        return {
            "enterprise_capabilities": {
                "integrations": {
                    "crm_systems": ["salesforce", "hubspot", "pipedrive"],
                    "erp_systems": ["sap", "oracle", "netsuite"],
                    "document_management": ["sharepoint", "box", "dropbox"]
                },
                "data_platform": {
                    "data_sources": ["document_processing", "user_activity", "system_metrics"],
                    "analytics": ["trend_analysis", "anomaly_detection", "correlation_analysis"],
                    "export_formats": ["csv", "json", "parquet"]
                },
                "ecosystem_connectors": {
                    "cloud_storage": ["aws_s3", "azure_blob", "gcp_storage"],
                    "productivity": ["google_workspace", "microsoft_365"],
                    "collaboration": ["slack", "teams", "notion"]
                },
                "security": {
                    "authentication": ["multi_factor", "sso", "oauth"],
                    "encryption": ["aes_256", "rsa", "fernet"],
                    "compliance": ["gdpr", "hipaa", "sox", "pci_dss", "iso_27001", "soc_2"]
                }
            },
            "api_version": "4.0.0",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")

# Initialize services on startup
@router.on_event("startup")
async def startup_enterprise_services():
    """Inicializar servicios empresariales al arrancar"""
    try:
        await integration_service.initialize()
        await data_platform_service.initialize()
        await ecosystem_service.initialize()
        await security_service.initialize()
        
        logger.info("Enterprise services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize enterprise services: {e}")
        # En producción, esto debería fallar el startup
        
# Cleanup on shutdown
@router.on_event("shutdown")
async def shutdown_enterprise_services():
    """Limpiar servicios empresariales al apagar"""
    try:
        if hasattr(ecosystem_service, 'cleanup'):
            await ecosystem_service.cleanup()
        logger.info("Enterprise services cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during enterprise services cleanup: {e}")

# Error handling middleware
@router.middleware("http")
async def enterprise_error_handler(request, call_next):
    """Middleware para manejo de errores empresariales"""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Enterprise service error: {str(e)}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Enterprise Service Error",
                "detail": str(e),
                "service": "enterprise",
                "timestamp": str(datetime.utcnow())
            }
        )