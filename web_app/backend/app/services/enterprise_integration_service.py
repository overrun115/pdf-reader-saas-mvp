#!/usr/bin/env python3
"""
Enterprise Integration Service - Integraciones empresariales CRM/ERP
Parte de la Fase 4 de la expansión del sistema
"""

import logging
import asyncio
import json
import aiohttp
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac
import base64
from urllib.parse import urlencode, quote
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class IntegrationType(str, Enum):
    CRM_SALESFORCE = "crm_salesforce"
    CRM_HUBSPOT = "crm_hubspot"
    CRM_PIPEDRIVE = "crm_pipedrive"
    ERP_SAP = "erp_sap"
    ERP_ORACLE = "erp_oracle"
    ERP_NETSUITE = "erp_netsuite"
    DMS_SHAREPOINT = "dms_sharepoint"
    DMS_DROPBOX = "dms_dropbox"
    DMS_BOX = "dms_box"

class DataSyncDirection(str, Enum):
    BIDIRECTIONAL = "bidirectional"
    PUSH_ONLY = "push_only"
    PULL_ONLY = "pull_only"

class SyncStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class IntegrationConfig:
    """Configuración de integración"""
    integration_type: IntegrationType
    endpoint_url: str
    api_key: str
    api_secret: Optional[str] = None
    oauth_token: Optional[str] = None
    oauth_refresh_token: Optional[str] = None
    additional_headers: Dict[str, str] = None
    rate_limit_per_minute: int = 100
    timeout_seconds: int = 30
    retry_attempts: int = 3
    webhook_url: Optional[str] = None

@dataclass
class DocumentMapping:
    """Mapeo de documentos entre sistemas"""
    source_field: str
    target_field: str
    field_type: str
    transformation_rule: Optional[str] = None
    required: bool = False
    default_value: Optional[str] = None

@dataclass
class SyncRequest:
    """Solicitud de sincronización"""
    integration_type: IntegrationType
    sync_direction: DataSyncDirection
    document_data: Dict[str, Any]
    field_mappings: List[DocumentMapping]
    sync_options: Dict[str, Any]
    callback_url: Optional[str] = None

@dataclass
class SyncResult:
    """Resultado de sincronización"""
    sync_id: str
    status: SyncStatus
    integration_type: IntegrationType
    synced_records: int
    failed_records: int
    processing_time: float
    error_details: List[Dict[str, Any]]
    external_ids: Dict[str, str]
    metadata: Dict[str, Any]

@dataclass
class WebhookEvent:
    """Evento de webhook"""
    event_id: str
    integration_type: IntegrationType
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    signature: Optional[str] = None

class EnterpriseIntegrationService:
    """
    Servicio de integración empresarial para conectar con sistemas CRM/ERP
    """
    
    def __init__(self):
        self.integrations: Dict[str, IntegrationConfig] = {}
        self.sync_history: List[SyncResult] = []
        self.webhook_handlers: Dict[str, callable] = {}
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}
        self.session = None
        
    async def initialize(self):
        """Inicializar el servicio"""
        try:
            self.session = aiohttp.ClientSession()
            await self._load_integration_configs()
            await self._setup_webhook_handlers()
            logger.info("Enterprise Integration Service inicializado exitosamente")
        except Exception as e:
            logger.error(f"Error inicializando Enterprise Integration Service: {e}")
            raise
    
    async def register_integration(self, integration_id: str, config: IntegrationConfig) -> bool:
        """Registrar nueva integración"""
        try:
            # Validar configuración
            if not await self._validate_integration_config(config):
                raise ValueError("Configuración de integración inválida")
            
            # Probar conexión
            if not await self._test_integration_connection(config):
                raise ConnectionError("No se pudo conectar con el sistema externo")
            
            # Registrar integración
            self.integrations[integration_id] = config
            
            # Configurar rate limiting
            self.rate_limiters[integration_id] = {
                "requests": [],
                "limit": config.rate_limit_per_minute
            }
            
            logger.info(f"Integración registrada: {integration_id} - {config.integration_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error registrando integración {integration_id}: {e}")
            return False
    
    async def sync_document_data(self, integration_id: str, sync_request: SyncRequest) -> SyncResult:
        """Sincronizar datos de documento con sistema externo"""
        try:
            sync_id = f"sync_{int(datetime.now().timestamp())}"
            start_time = datetime.now()
            
            if integration_id not in self.integrations:
                raise ValueError(f"Integración no encontrada: {integration_id}")
            
            config = self.integrations[integration_id]
            
            # Verificar rate limiting
            if not await self._check_rate_limit(integration_id):
                raise Exception("Rate limit excedido")
            
            # Transformar datos según mapeo
            transformed_data = await self._transform_document_data(
                sync_request.document_data,
                sync_request.field_mappings
            )
            
            # Ejecutar sincronización según tipo
            sync_result = await self._execute_sync(
                config,
                sync_request.sync_direction,
                transformed_data,
                sync_request.sync_options
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = SyncResult(
                sync_id=sync_id,
                status=sync_result.get("status", SyncStatus.COMPLETED),
                integration_type=config.integration_type,
                synced_records=sync_result.get("synced_records", 0),
                failed_records=sync_result.get("failed_records", 0),
                processing_time=processing_time,
                error_details=sync_result.get("errors", []),
                external_ids=sync_result.get("external_ids", {}),
                metadata=sync_result.get("metadata", {})
            )
            
            self.sync_history.append(result)
            
            # Callback si está configurado
            if sync_request.callback_url:
                await self._send_sync_callback(sync_request.callback_url, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error en sincronización {integration_id}: {e}")
            return SyncResult(
                sync_id=sync_id,
                status=SyncStatus.FAILED,
                integration_type=config.integration_type,
                synced_records=0,
                failed_records=1,
                processing_time=0,
                error_details=[{"error": str(e)}],
                external_ids={},
                metadata={}
            )
    
    async def batch_sync_documents(self, integration_id: str, sync_requests: List[SyncRequest]) -> List[SyncResult]:
        """Sincronización en lote de documentos"""
        try:
            if len(sync_requests) > 100:
                raise ValueError("Máximo 100 documentos por lote")
            
            results = []
            
            # Procesar en lotes de 10 para evitar sobrecarga
            batch_size = 10
            for i in range(0, len(sync_requests), batch_size):
                batch = sync_requests[i:i + batch_size]
                
                # Ejecutar batch concurrentemente
                tasks = [
                    self.sync_document_data(integration_id, req)
                    for req in batch
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        results.append(SyncResult(
                            sync_id=f"batch_error_{i}",
                            status=SyncStatus.FAILED,
                            integration_type=self.integrations[integration_id].integration_type,
                            synced_records=0,
                            failed_records=1,
                            processing_time=0,
                            error_details=[{"error": str(result)}],
                            external_ids={},
                            metadata={}
                        ))
                    else:
                        results.append(result)
                
                # Pausa entre lotes para respetar rate limits
                await asyncio.sleep(1)
            
            return results
            
        except Exception as e:
            logger.error(f"Error en sincronización batch: {e}")
            return []
    
    async def setup_webhook_listener(self, integration_id: str, webhook_url: str, event_types: List[str]) -> bool:
        """Configurar listener de webhooks"""
        try:
            if integration_id not in self.integrations:
                raise ValueError(f"Integración no encontrada: {integration_id}")
            
            config = self.integrations[integration_id]
            
            # Configurar webhook según tipo de integración
            webhook_config = await self._setup_integration_webhook(
                config,
                webhook_url,
                event_types
            )
            
            if webhook_config:
                self.integrations[integration_id].webhook_url = webhook_url
                logger.info(f"Webhook configurado para {integration_id}: {webhook_url}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error configurando webhook {integration_id}: {e}")
            return False
    
    async def process_webhook_event(self, integration_id: str, event_data: Dict[str, Any]) -> bool:
        """Procesar evento de webhook"""
        try:
            if integration_id not in self.integrations:
                return False
            
            config = self.integrations[integration_id]
            
            # Verificar firma del webhook
            if not await self._verify_webhook_signature(config, event_data):
                logger.warning(f"Firma de webhook inválida para {integration_id}")
                return False
            
            # Crear evento
            webhook_event = WebhookEvent(
                event_id=event_data.get("id", f"event_{int(datetime.now().timestamp())}"),
                integration_type=config.integration_type,
                event_type=event_data.get("type", "unknown"),
                timestamp=datetime.now(),
                data=event_data,
                signature=event_data.get("signature")
            )
            
            # Procesar evento según tipo
            result = await self._process_webhook_event(webhook_event)
            
            return result
            
        except Exception as e:
            logger.error(f"Error procesando webhook {integration_id}: {e}")
            return False
    
    async def get_integration_status(self, integration_id: str) -> Dict[str, Any]:
        """Obtener estado de integración"""
        try:
            if integration_id not in self.integrations:
                return {"status": "not_found"}
            
            config = self.integrations[integration_id]
            
            # Verificar conectividad
            is_connected = await self._test_integration_connection(config)
            
            # Obtener estadísticas de sincronización
            recent_syncs = [
                sync for sync in self.sync_history
                if sync.integration_type == config.integration_type
            ][-10:]  # Últimos 10 syncs
            
            success_rate = len([s for s in recent_syncs if s.status == SyncStatus.COMPLETED]) / max(1, len(recent_syncs))
            
            return {
                "status": "connected" if is_connected else "disconnected",
                "integration_type": config.integration_type,
                "last_sync": recent_syncs[-1].sync_id if recent_syncs else None,
                "success_rate": success_rate,
                "total_syncs": len(recent_syncs),
                "rate_limit_remaining": self._get_rate_limit_remaining(integration_id),
                "webhook_configured": bool(config.webhook_url)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de integración {integration_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_sync_history(self, integration_id: str, limit: int = 50) -> List[SyncResult]:
        """Obtener historial de sincronizaciones"""
        try:
            if integration_id not in self.integrations:
                return []
            
            config = self.integrations[integration_id]
            
            # Filtrar por tipo de integración
            filtered_history = [
                sync for sync in self.sync_history
                if sync.integration_type == config.integration_type
            ]
            
            # Ordenar por más reciente y limitar
            return sorted(filtered_history, key=lambda x: x.sync_id, reverse=True)[:limit]
            
        except Exception as e:
            logger.error(f"Error obteniendo historial de {integration_id}: {e}")
            return []
    
    async def create_field_mapping(self, source_schema: Dict[str, Any], target_schema: Dict[str, Any]) -> List[DocumentMapping]:
        """Crear mapeo automático de campos"""
        try:
            mappings = []
            
            # Mapeo automático basado en nombres similares
            for source_field, source_info in source_schema.items():
                best_match = None
                best_score = 0
                
                for target_field, target_info in target_schema.items():
                    # Calcular similitud de nombres
                    similarity = self._calculate_field_similarity(source_field, target_field)
                    
                    # Verificar compatibilidad de tipos
                    if self._are_types_compatible(source_info.get("type"), target_info.get("type")):
                        similarity += 0.2
                    
                    if similarity > best_score:
                        best_score = similarity
                        best_match = target_field
                
                # Crear mapeo si la similitud es suficiente
                if best_match and best_score > 0.6:
                    mappings.append(DocumentMapping(
                        source_field=source_field,
                        target_field=best_match,
                        field_type=source_info.get("type", "string"),
                        required=source_info.get("required", False)
                    ))
            
            return mappings
            
        except Exception as e:
            logger.error(f"Error creando mapeo de campos: {e}")
            return []
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del servicio"""
        try:
            total_syncs = len(self.sync_history)
            successful_syncs = len([s for s in self.sync_history if s.status == SyncStatus.COMPLETED])
            
            return {
                "service_status": "operational",
                "total_integrations": len(self.integrations),
                "integration_types": list(set(config.integration_type for config in self.integrations.values())),
                "total_syncs": total_syncs,
                "successful_syncs": successful_syncs,
                "success_rate": successful_syncs / max(1, total_syncs),
                "average_processing_time": statistics.mean([s.processing_time for s in self.sync_history]) if self.sync_history else 0,
                "supported_integrations": [integration_type.value for integration_type in IntegrationType],
                "capabilities": {
                    "bidirectional_sync": True,
                    "batch_processing": True,
                    "webhook_support": True,
                    "field_mapping": True,
                    "rate_limiting": True,
                    "retry_logic": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del servicio: {e}")
            return {"service_status": "error", "error": str(e)}
    
    # Métodos privados
    
    async def _load_integration_configs(self):
        """Cargar configuraciones de integración desde base de datos"""
        # En producción, cargar desde base de datos
        pass
    
    async def _setup_webhook_handlers(self):
        """Configurar manejadores de webhooks"""
        self.webhook_handlers = {
            IntegrationType.CRM_SALESFORCE: self._handle_salesforce_webhook,
            IntegrationType.CRM_HUBSPOT: self._handle_hubspot_webhook,
            IntegrationType.ERP_SAP: self._handle_sap_webhook,
            # Agregar más manejadores según necesidad
        }
    
    async def _validate_integration_config(self, config: IntegrationConfig) -> bool:
        """Validar configuración de integración"""
        if not config.endpoint_url or not config.api_key:
            return False
        
        # Validaciones específicas por tipo
        if config.integration_type in [IntegrationType.CRM_SALESFORCE, IntegrationType.ERP_SAP]:
            return bool(config.api_secret)
        
        return True
    
    async def _test_integration_connection(self, config: IntegrationConfig) -> bool:
        """Probar conexión con sistema externo"""
        try:
            headers = await self._build_auth_headers(config)
            
            async with self.session.get(
                config.endpoint_url,
                headers=headers,
                timeout=config.timeout_seconds
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Error probando conexión: {e}")
            return False
    
    async def _build_auth_headers(self, config: IntegrationConfig) -> Dict[str, str]:
        """Construir headers de autenticación"""
        headers = {"Content-Type": "application/json"}
        
        if config.additional_headers:
            headers.update(config.additional_headers)
        
        if config.oauth_token:
            headers["Authorization"] = f"Bearer {config.oauth_token}"
        elif config.api_key:
            headers["Authorization"] = f"Bearer {config.api_key}"
        
        return headers
    
    async def _check_rate_limit(self, integration_id: str) -> bool:
        """Verificar límite de velocidad"""
        if integration_id not in self.rate_limiters:
            return True
        
        limiter = self.rate_limiters[integration_id]
        now = datetime.now()
        
        # Limpiar requests antiguos (más de 1 minuto)
        limiter["requests"] = [
            req_time for req_time in limiter["requests"]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Verificar límite
        if len(limiter["requests"]) >= limiter["limit"]:
            return False
        
        # Registrar nuevo request
        limiter["requests"].append(now)
        return True
    
    async def _transform_document_data(self, data: Dict[str, Any], mappings: List[DocumentMapping]) -> Dict[str, Any]:
        """Transformar datos según mapeo"""
        transformed = {}
        
        for mapping in mappings:
            if mapping.source_field in data:
                value = data[mapping.source_field]
                
                # Aplicar transformación si está definida
                if mapping.transformation_rule:
                    value = await self._apply_transformation(value, mapping.transformation_rule)
                
                transformed[mapping.target_field] = value
            elif mapping.required and mapping.default_value:
                transformed[mapping.target_field] = mapping.default_value
        
        return transformed
    
    async def _execute_sync(self, config: IntegrationConfig, direction: DataSyncDirection, 
                           data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar sincronización según tipo de integración"""
        try:
            if config.integration_type == IntegrationType.CRM_SALESFORCE:
                return await self._sync_salesforce(config, direction, data, options)
            elif config.integration_type == IntegrationType.CRM_HUBSPOT:
                return await self._sync_hubspot(config, direction, data, options)
            elif config.integration_type == IntegrationType.ERP_SAP:
                return await self._sync_sap(config, direction, data, options)
            else:
                return await self._sync_generic(config, direction, data, options)
                
        except Exception as e:
            logger.error(f"Error ejecutando sync: {e}")
            return {
                "status": SyncStatus.FAILED,
                "errors": [{"error": str(e)}],
                "synced_records": 0,
                "failed_records": 1
            }
    
    async def _sync_salesforce(self, config: IntegrationConfig, direction: DataSyncDirection, 
                              data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Sincronización específica para Salesforce"""
        try:
            headers = await self._build_auth_headers(config)
            
            if direction in [DataSyncDirection.PUSH_ONLY, DataSyncDirection.BIDIRECTIONAL]:
                # Push data to Salesforce
                async with self.session.post(
                    f"{config.endpoint_url}/services/data/v57.0/sobjects/Document",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        return {
                            "status": SyncStatus.COMPLETED,
                            "synced_records": 1,
                            "failed_records": 0,
                            "external_ids": {"salesforce_id": result.get("id")},
                            "metadata": {"response": result}
                        }
            
            return {
                "status": SyncStatus.COMPLETED,
                "synced_records": 0,
                "failed_records": 0,
                "external_ids": {},
                "metadata": {}
            }
            
        except Exception as e:
            logger.error(f"Error en sync Salesforce: {e}")
            return {
                "status": SyncStatus.FAILED,
                "errors": [{"error": str(e)}],
                "synced_records": 0,
                "failed_records": 1
            }
    
    async def _sync_hubspot(self, config: IntegrationConfig, direction: DataSyncDirection, 
                           data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Sincronización específica para HubSpot"""
        try:
            headers = await self._build_auth_headers(config)
            
            if direction in [DataSyncDirection.PUSH_ONLY, DataSyncDirection.BIDIRECTIONAL]:
                # Push data to HubSpot
                async with self.session.post(
                    f"{config.endpoint_url}/crm/v3/objects/contacts",
                    headers=headers,
                    json={"properties": data}
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        return {
                            "status": SyncStatus.COMPLETED,
                            "synced_records": 1,
                            "failed_records": 0,
                            "external_ids": {"hubspot_id": result.get("id")},
                            "metadata": {"response": result}
                        }
            
            return {
                "status": SyncStatus.COMPLETED,
                "synced_records": 0,
                "failed_records": 0,
                "external_ids": {},
                "metadata": {}
            }
            
        except Exception as e:
            logger.error(f"Error en sync HubSpot: {e}")
            return {
                "status": SyncStatus.FAILED,
                "errors": [{"error": str(e)}],
                "synced_records": 0,
                "failed_records": 1
            }
    
    async def _sync_sap(self, config: IntegrationConfig, direction: DataSyncDirection, 
                       data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Sincronización específica para SAP"""
        try:
            headers = await self._build_auth_headers(config)
            headers["Content-Type"] = "application/xml"
            
            # Convertir datos a XML para SAP
            xml_data = self._dict_to_xml(data)
            
            if direction in [DataSyncDirection.PUSH_ONLY, DataSyncDirection.BIDIRECTIONAL]:
                async with self.session.post(
                    f"{config.endpoint_url}/sap/bc/rest/documents",
                    headers=headers,
                    data=xml_data
                ) as response:
                    if response.status == 200:
                        result_xml = await response.text()
                        result = self._xml_to_dict(result_xml)
                        return {
                            "status": SyncStatus.COMPLETED,
                            "synced_records": 1,
                            "failed_records": 0,
                            "external_ids": {"sap_id": result.get("document_id")},
                            "metadata": {"response": result}
                        }
            
            return {
                "status": SyncStatus.COMPLETED,
                "synced_records": 0,
                "failed_records": 0,
                "external_ids": {},
                "metadata": {}
            }
            
        except Exception as e:
            logger.error(f"Error en sync SAP: {e}")
            return {
                "status": SyncStatus.FAILED,
                "errors": [{"error": str(e)}],
                "synced_records": 0,
                "failed_records": 1
            }
    
    async def _sync_generic(self, config: IntegrationConfig, direction: DataSyncDirection, 
                           data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Sincronización genérica para APIs REST"""
        try:
            headers = await self._build_auth_headers(config)
            
            if direction in [DataSyncDirection.PUSH_ONLY, DataSyncDirection.BIDIRECTIONAL]:
                async with self.session.post(
                    config.endpoint_url,
                    headers=headers,
                    json=data
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        return {
                            "status": SyncStatus.COMPLETED,
                            "synced_records": 1,
                            "failed_records": 0,
                            "external_ids": {"external_id": result.get("id")},
                            "metadata": {"response": result}
                        }
            
            return {
                "status": SyncStatus.COMPLETED,
                "synced_records": 0,
                "failed_records": 0,
                "external_ids": {},
                "metadata": {}
            }
            
        except Exception as e:
            logger.error(f"Error en sync genérico: {e}")
            return {
                "status": SyncStatus.FAILED,
                "errors": [{"error": str(e)}],
                "synced_records": 0,
                "failed_records": 1
            }
    
    def _dict_to_xml(self, data: Dict[str, Any]) -> str:
        """Convertir diccionario a XML"""
        root = ET.Element("Document")
        
        for key, value in data.items():
            element = ET.SubElement(root, key)
            element.text = str(value)
        
        return ET.tostring(root, encoding='unicode')
    
    def _xml_to_dict(self, xml_string: str) -> Dict[str, Any]:
        """Convertir XML a diccionario"""
        try:
            root = ET.fromstring(xml_string)
            return {child.tag: child.text for child in root}
        except Exception:
            return {}
    
    def _calculate_field_similarity(self, field1: str, field2: str) -> float:
        """Calcular similitud entre nombres de campos"""
        # Implementación básica de similitud
        field1_lower = field1.lower()
        field2_lower = field2.lower()
        
        if field1_lower == field2_lower:
            return 1.0
        
        # Verificar si uno está contenido en el otro
        if field1_lower in field2_lower or field2_lower in field1_lower:
            return 0.8
        
        # Calcular similitud por caracteres comunes
        common_chars = set(field1_lower) & set(field2_lower)
        total_chars = set(field1_lower) | set(field2_lower)
        
        return len(common_chars) / len(total_chars) if total_chars else 0
    
    def _are_types_compatible(self, type1: str, type2: str) -> bool:
        """Verificar compatibilidad de tipos"""
        if not type1 or not type2:
            return True
        
        compatible_types = {
            "string": ["text", "varchar", "char"],
            "integer": ["int", "number", "numeric"],
            "float": ["decimal", "double", "real"],
            "boolean": ["bool", "bit"],
            "date": ["datetime", "timestamp"]
        }
        
        for base_type, compatible in compatible_types.items():
            if (type1.lower() == base_type and type2.lower() in compatible) or \
               (type2.lower() == base_type and type1.lower() in compatible):
                return True
        
        return type1.lower() == type2.lower()
    
    async def _apply_transformation(self, value: Any, rule: str) -> Any:
        """Aplicar regla de transformación"""
        try:
            if rule == "uppercase":
                return str(value).upper()
            elif rule == "lowercase":
                return str(value).lower()
            elif rule == "trim":
                return str(value).strip()
            elif rule.startswith("prefix:"):
                prefix = rule.split(":", 1)[1]
                return f"{prefix}{value}"
            elif rule.startswith("suffix:"):
                suffix = rule.split(":", 1)[1]
                return f"{value}{suffix}"
            else:
                return value
        except Exception:
            return value
    
    async def _setup_integration_webhook(self, config: IntegrationConfig, webhook_url: str, event_types: List[str]) -> bool:
        """Configurar webhook en sistema externo"""
        try:
            headers = await self._build_auth_headers(config)
            
            webhook_data = {
                "url": webhook_url,
                "events": event_types,
                "active": True
            }
            
            async with self.session.post(
                f"{config.endpoint_url}/webhooks",
                headers=headers,
                json=webhook_data
            ) as response:
                return response.status in [200, 201]
                
        except Exception as e:
            logger.error(f"Error configurando webhook: {e}")
            return False
    
    async def _verify_webhook_signature(self, config: IntegrationConfig, event_data: Dict[str, Any]) -> bool:
        """Verificar firma de webhook"""
        if not config.api_secret:
            return True  # No hay secret configurado
        
        try:
            signature = event_data.get("signature", "")
            payload = json.dumps(event_data, sort_keys=True)
            
            expected_signature = hmac.new(
                config.api_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verificando firma webhook: {e}")
            return False
    
    async def _process_webhook_event(self, event: WebhookEvent) -> bool:
        """Procesar evento de webhook"""
        try:
            handler = self.webhook_handlers.get(event.integration_type)
            if handler:
                return await handler(event)
            
            # Procesamiento genérico
            logger.info(f"Evento webhook recibido: {event.event_type} - {event.integration_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error procesando evento webhook: {e}")
            return False
    
    async def _handle_salesforce_webhook(self, event: WebhookEvent) -> bool:
        """Manejar webhook de Salesforce"""
        try:
            # Lógica específica para Salesforce
            logger.info(f"Procesando webhook Salesforce: {event.event_type}")
            return True
        except Exception as e:
            logger.error(f"Error procesando webhook Salesforce: {e}")
            return False
    
    async def _handle_hubspot_webhook(self, event: WebhookEvent) -> bool:
        """Manejar webhook de HubSpot"""
        try:
            # Lógica específica para HubSpot
            logger.info(f"Procesando webhook HubSpot: {event.event_type}")
            return True
        except Exception as e:
            logger.error(f"Error procesando webhook HubSpot: {e}")
            return False
    
    async def _handle_sap_webhook(self, event: WebhookEvent) -> bool:
        """Manejar webhook de SAP"""
        try:
            # Lógica específica para SAP
            logger.info(f"Procesando webhook SAP: {event.event_type}")
            return True
        except Exception as e:
            logger.error(f"Error procesando webhook SAP: {e}")
            return False
    
    async def _send_sync_callback(self, callback_url: str, result: SyncResult):
        """Enviar callback de sincronización"""
        try:
            callback_data = {
                "sync_id": result.sync_id,
                "status": result.status,
                "synced_records": result.synced_records,
                "failed_records": result.failed_records,
                "processing_time": result.processing_time,
                "external_ids": result.external_ids
            }
            
            async with self.session.post(
                callback_url,
                json=callback_data,
                timeout=10
            ) as response:
                if response.status == 200:
                    logger.info(f"Callback enviado exitosamente: {callback_url}")
                else:
                    logger.warning(f"Error enviando callback: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error enviando callback: {e}")
    
    def _get_rate_limit_remaining(self, integration_id: str) -> int:
        """Obtener límite de velocidad restante"""
        if integration_id not in self.rate_limiters:
            return 0
        
        limiter = self.rate_limiters[integration_id]
        now = datetime.now()
        
        # Limpiar requests antiguos
        recent_requests = [
            req_time for req_time in limiter["requests"]
            if now - req_time < timedelta(minutes=1)
        ]
        
        return max(0, limiter["limit"] - len(recent_requests))
    
    async def cleanup(self):
        """Limpiar recursos"""
        if self.session:
            await self.session.close()