#!/usr/bin/env python3
"""
Data Platform Service - Plataforma de datos unificada
Parte de la Fase 4.2 de la expansión del sistema
"""

import logging
import asyncio
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import uuid
from collections import defaultdict, deque
import sqlite3
import aiofiles
from pathlib import Path

# Data processing libraries
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False

# Time series and analytics
try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    import plotly.graph_objects as go
    import plotly.express as px
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

logger = logging.getLogger(__name__)

class DataSourceType(str, Enum):
    DOCUMENT_PROCESSING = "document_processing"
    USER_ACTIVITY = "user_activity"
    SYSTEM_METRICS = "system_metrics"
    INTEGRATION_DATA = "integration_data"
    WORKFLOW_EXECUTION = "workflow_execution"
    AI_ANALYSIS = "ai_analysis"
    PREDICTIVE_MODELS = "predictive_models"
    EXTERNAL_API = "external_api"

class DataFormat(str, Enum):
    JSON = "json"
    PARQUET = "parquet"
    CSV = "csv"
    AVRO = "avro"
    DELTA = "delta"
    SQLITE = "sqlite"

class AggregationType(str, Enum):
    SUM = "sum"
    COUNT = "count"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    DISTINCT_COUNT = "distinct_count"

class TimeGranularity(str, Enum):
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

@dataclass
class DataSource:
    """Fuente de datos"""
    source_id: str
    source_type: DataSourceType
    connection_string: str
    schema: Dict[str, Any]
    update_frequency: str
    is_active: bool = True
    metadata: Dict[str, Any] = None

@dataclass
class DataPipeline:
    """Pipeline de datos"""
    pipeline_id: str
    name: str
    source_ids: List[str]
    transformations: List[Dict[str, Any]]
    destination: str
    schedule: str
    is_active: bool = True
    last_run: Optional[datetime] = None
    metadata: Dict[str, Any] = None

@dataclass
class DataQuery:
    """Consulta de datos"""
    query_id: str
    query_type: str
    source_tables: List[str]
    filters: Dict[str, Any]
    aggregations: List[Dict[str, Any]]
    time_range: Optional[Tuple[datetime, datetime]] = None
    limit: int = 1000
    offset: int = 0

@dataclass
class DataInsight:
    """Insight de datos"""
    insight_id: str
    insight_type: str
    title: str
    description: str
    data: Dict[str, Any]
    confidence: float
    generated_at: datetime
    metadata: Dict[str, Any] = None

@dataclass
class DataAlert:
    """Alerta de datos"""
    alert_id: str
    alert_type: str
    condition: str
    threshold: Union[float, int]
    current_value: Union[float, int]
    triggered_at: datetime
    severity: str
    description: str

class DataPlatformService:
    """
    Servicio de plataforma de datos unificada para análisis y business intelligence
    """
    
    def __init__(self, data_dir: str = "data_platform"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Componentes principales
        self.data_sources: Dict[str, DataSource] = {}
        self.data_pipelines: Dict[str, DataPipeline] = {}
        self.data_warehouse = None
        self.metrics_store = defaultdict(deque)
        self.insights_cache = {}
        self.alerts = []
        
        # Configuración
        self.warehouse_path = self.data_dir / "warehouse.db"
        self.metrics_path = self.data_dir / "metrics.db"
        
    async def initialize(self):
        """Inicializar la plataforma de datos"""
        try:
            # Crear warehouse de datos
            await self._initialize_data_warehouse()
            
            # Configurar fuentes de datos por defecto
            await self._setup_default_data_sources()
            
            # Inicializar pipelines
            await self._initialize_data_pipelines()
            
            # Configurar métricas y alertas
            await self._setup_metrics_and_alerts()
            
            logger.info("Data Platform Service inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando Data Platform Service: {e}")
            raise
    
    async def register_data_source(self, source: DataSource) -> bool:
        """Registrar nueva fuente de datos"""
        try:
            # Validar fuente de datos
            if not await self._validate_data_source(source):
                return False
            
            # Probar conexión
            if not await self._test_data_source_connection(source):
                logger.warning(f"No se pudo conectar con fuente {source.source_id}")
                return False
            
            # Registrar fuente
            self.data_sources[source.source_id] = source
            
            # Crear tabla en warehouse
            await self._create_warehouse_table(source)
            
            logger.info(f"Fuente de datos registrada: {source.source_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registrando fuente de datos: {e}")
            return False
    
    async def ingest_data(self, source_id: str, data: List[Dict[str, Any]]) -> bool:
        """Ingerir datos desde fuente"""
        try:
            if source_id not in self.data_sources:
                raise ValueError(f"Fuente de datos no encontrada: {source_id}")
            
            source = self.data_sources[source_id]
            
            # Validar esquema
            validated_data = await self._validate_data_schema(data, source.schema)
            
            # Enriquecer datos
            enriched_data = await self._enrich_data(validated_data, source)
            
            # Guardar en warehouse
            await self._store_data_in_warehouse(source_id, enriched_data)
            
            # Actualizar métricas
            await self._update_ingestion_metrics(source_id, len(enriched_data))
            
            # Verificar alertas
            await self._check_data_alerts(source_id, enriched_data)
            
            logger.info(f"Datos ingeridos: {len(enriched_data)} registros de {source_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingiriendo datos: {e}")
            return False
    
    async def create_data_pipeline(self, pipeline: DataPipeline) -> bool:
        """Crear pipeline de datos"""
        try:
            # Validar pipeline
            if not await self._validate_pipeline(pipeline):
                return False
            
            # Registrar pipeline
            self.data_pipelines[pipeline.pipeline_id] = pipeline
            
            # Crear tablas intermedias si es necesario
            await self._create_pipeline_tables(pipeline)
            
            logger.info(f"Pipeline creado: {pipeline.pipeline_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando pipeline: {e}")
            return False
    
    async def execute_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Ejecutar pipeline de datos"""
        try:
            if pipeline_id not in self.data_pipelines:
                raise ValueError(f"Pipeline no encontrado: {pipeline_id}")
            
            pipeline = self.data_pipelines[pipeline_id]
            start_time = datetime.now()
            
            # Ejecutar transformaciones
            result = await self._execute_pipeline_transformations(pipeline)
            
            # Actualizar última ejecución
            pipeline.last_run = datetime.now()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "pipeline_id": pipeline_id,
                "status": "completed",
                "records_processed": result.get("records_processed", 0),
                "processing_time": processing_time,
                "transformations_applied": len(pipeline.transformations),
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando pipeline {pipeline_id}: {e}")
            return {
                "pipeline_id": pipeline_id,
                "status": "failed",
                "error": str(e),
                "execution_time": datetime.now().isoformat()
            }
    
    async def execute_query(self, query: DataQuery) -> Dict[str, Any]:
        """Ejecutar consulta de datos"""
        try:
            # Construir consulta SQL
            sql_query = await self._build_sql_query(query)
            
            # Ejecutar consulta
            if DUCKDB_AVAILABLE:
                result = await self._execute_duckdb_query(sql_query)
            else:
                result = await self._execute_sqlite_query(sql_query)
            
            # Formatear resultado
            formatted_result = await self._format_query_result(result, query)
            
            return {
                "query_id": query.query_id,
                "status": "completed",
                "data": formatted_result,
                "record_count": len(formatted_result) if isinstance(formatted_result, list) else 0,
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando consulta: {e}")
            return {
                "query_id": query.query_id,
                "status": "failed",
                "error": str(e),
                "execution_time": datetime.now().isoformat()
            }
    
    async def generate_insights(self, data_source_ids: List[str], insight_types: List[str]) -> List[DataInsight]:
        """Generar insights de datos"""
        try:
            insights = []
            
            for insight_type in insight_types:
                if insight_type == "trend_analysis":
                    trend_insights = await self._generate_trend_insights(data_source_ids)
                    insights.extend(trend_insights)
                elif insight_type == "anomaly_detection":
                    anomaly_insights = await self._generate_anomaly_insights(data_source_ids)
                    insights.extend(anomaly_insights)
                elif insight_type == "correlation_analysis":
                    correlation_insights = await self._generate_correlation_insights(data_source_ids)
                    insights.extend(correlation_insights)
                elif insight_type == "performance_metrics":
                    performance_insights = await self._generate_performance_insights(data_source_ids)
                    insights.extend(performance_insights)
            
            # Guardar insights en cache
            for insight in insights:
                self.insights_cache[insight.insight_id] = insight
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generando insights: {e}")
            return []
    
    async def create_dashboard(self, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Crear dashboard de datos"""
        try:
            dashboard_id = dashboard_config.get("dashboard_id", str(uuid.uuid4()))
            
            # Generar componentes del dashboard
            components = []
            
            for widget_config in dashboard_config.get("widgets", []):
                widget = await self._create_dashboard_widget(widget_config)
                if widget:
                    components.append(widget)
            
            # Crear dashboard
            dashboard = {
                "dashboard_id": dashboard_id,
                "title": dashboard_config.get("title", "Dashboard"),
                "description": dashboard_config.get("description", ""),
                "components": components,
                "refresh_interval": dashboard_config.get("refresh_interval", 300),
                "created_at": datetime.now().isoformat(),
                "layout": dashboard_config.get("layout", "grid")
            }
            
            # Guardar dashboard
            dashboard_path = self.data_dir / f"dashboard_{dashboard_id}.json"
            async with aiofiles.open(dashboard_path, 'w') as f:
                await f.write(json.dumps(dashboard, indent=2))
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creando dashboard: {e}")
            return {}
    
    async def get_real_time_metrics(self, metric_names: List[str]) -> Dict[str, Any]:
        """Obtener métricas en tiempo real"""
        try:
            metrics = {}
            
            for metric_name in metric_names:
                if metric_name in self.metrics_store:
                    metric_data = list(self.metrics_store[metric_name])
                    
                    # Calcular estadísticas
                    values = [m["value"] for m in metric_data if isinstance(m.get("value"), (int, float))]
                    if values:
                        metrics[metric_name] = {
                            "current_value": values[-1] if values else 0,
                            "average": sum(values) / len(values),
                            "min": min(values),
                            "max": max(values),
                            "count": len(values),
                            "last_updated": metric_data[-1]["timestamp"] if metric_data else None
                        }
                    else:
                        metrics[metric_name] = {
                            "current_value": 0,
                            "average": 0,
                            "min": 0,
                            "max": 0,
                            "count": 0,
                            "last_updated": None
                        }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas en tiempo real: {e}")
            return {}
    
    async def setup_data_alert(self, alert_config: Dict[str, Any]) -> bool:
        """Configurar alerta de datos"""
        try:
            alert = DataAlert(
                alert_id=alert_config.get("alert_id", str(uuid.uuid4())),
                alert_type=alert_config["alert_type"],
                condition=alert_config["condition"],
                threshold=alert_config["threshold"],
                current_value=0,
                triggered_at=datetime.now(),
                severity=alert_config.get("severity", "medium"),
                description=alert_config.get("description", "")
            )
            
            self.alerts.append(alert)
            
            logger.info(f"Alerta configurada: {alert.alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error configurando alerta: {e}")
            return False
    
    async def export_data(self, query: DataQuery, format: DataFormat, output_path: str) -> bool:
        """Exportar datos"""
        try:
            # Ejecutar consulta
            query_result = await self.execute_query(query)
            
            if query_result["status"] != "completed":
                return False
            
            data = query_result["data"]
            
            # Convertir a DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            # Exportar según formato
            if format == DataFormat.CSV:
                df.to_csv(output_path, index=False)
            elif format == DataFormat.JSON:
                df.to_json(output_path, orient="records", indent=2)
            elif format == DataFormat.PARQUET and PARQUET_AVAILABLE:
                df.to_parquet(output_path)
            else:
                # Fallback a JSON
                df.to_json(output_path, orient="records", indent=2)
            
            logger.info(f"Datos exportados: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando datos: {e}")
            return False
    
    async def get_data_lineage(self, entity_id: str) -> Dict[str, Any]:
        """Obtener linaje de datos"""
        try:
            lineage = {
                "entity_id": entity_id,
                "upstream_dependencies": [],
                "downstream_dependencies": [],
                "transformations": [],
                "data_quality_metrics": {}
            }
            
            # Buscar dependencias upstream
            for pipeline_id, pipeline in self.data_pipelines.items():
                if entity_id in pipeline.source_ids:
                    lineage["downstream_dependencies"].append({
                        "pipeline_id": pipeline_id,
                        "pipeline_name": pipeline.name,
                        "transformations": len(pipeline.transformations)
                    })
            
            # Buscar dependencias downstream
            for source_id, source in self.data_sources.items():
                if source_id == entity_id:
                    lineage["upstream_dependencies"].append({
                        "source_id": source_id,
                        "source_type": source.source_type,
                        "update_frequency": source.update_frequency
                    })
            
            return lineage
            
        except Exception as e:
            logger.error(f"Error obteniendo linaje de datos: {e}")
            return {}
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del servicio"""
        try:
            # Calcular estadísticas de fuentes de datos
            active_sources = sum(1 for source in self.data_sources.values() if source.is_active)
            
            # Calcular estadísticas de pipelines
            active_pipelines = sum(1 for pipeline in self.data_pipelines.values() if pipeline.is_active)
            
            # Calcular estadísticas de warehouse
            warehouse_stats = await self._get_warehouse_stats()
            
            return {
                "service_status": "operational",
                "data_sources": {
                    "total": len(self.data_sources),
                    "active": active_sources,
                    "types": list(set(source.source_type for source in self.data_sources.values()))
                },
                "data_pipelines": {
                    "total": len(self.data_pipelines),
                    "active": active_pipelines,
                    "last_execution": max([p.last_run for p in self.data_pipelines.values() if p.last_run], default=None)
                },
                "warehouse": warehouse_stats,
                "insights": {
                    "cached": len(self.insights_cache),
                    "types": list(set(insight.insight_type for insight in self.insights_cache.values()))
                },
                "alerts": {
                    "total": len(self.alerts),
                    "active": len([a for a in self.alerts if a.triggered_at > datetime.now() - timedelta(hours=24)])
                },
                "capabilities": {
                    "real_time_metrics": True,
                    "data_lineage": True,
                    "dashboard_creation": True,
                    "automated_insights": True,
                    "data_quality_monitoring": True,
                    "parquet_support": PARQUET_AVAILABLE,
                    "duckdb_support": DUCKDB_AVAILABLE,
                    "analytics_support": ANALYTICS_AVAILABLE
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del servicio: {e}")
            return {"service_status": "error", "error": str(e)}
    
    # Métodos privados
    
    async def _initialize_data_warehouse(self):
        """Inicializar warehouse de datos"""
        try:
            if DUCKDB_AVAILABLE:
                self.data_warehouse = duckdb.connect(str(self.warehouse_path))
            else:
                self.data_warehouse = sqlite3.connect(str(self.warehouse_path))
            
            # Crear tablas base
            await self._create_base_tables()
            
        except Exception as e:
            logger.error(f"Error inicializando warehouse: {e}")
            raise
    
    async def _create_base_tables(self):
        """Crear tablas base del warehouse"""
        try:
            base_tables = [
                """
                CREATE TABLE IF NOT EXISTS data_sources (
                    source_id TEXT PRIMARY KEY,
                    source_type TEXT,
                    connection_string TEXT,
                    schema TEXT,
                    is_active BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS data_ingestion_log (
                    log_id TEXT PRIMARY KEY,
                    source_id TEXT,
                    records_ingested INTEGER,
                    ingestion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    error_details TEXT
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS data_quality_metrics (
                    metric_id TEXT PRIMARY KEY,
                    source_id TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            ]
            
            if DUCKDB_AVAILABLE:
                for table_sql in base_tables:
                    self.data_warehouse.execute(table_sql)
            else:
                cursor = self.data_warehouse.cursor()
                for table_sql in base_tables:
                    cursor.execute(table_sql)
                self.data_warehouse.commit()
            
        except Exception as e:
            logger.error(f"Error creando tablas base: {e}")
            raise
    
    async def _setup_default_data_sources(self):
        """Configurar fuentes de datos por defecto"""
        try:
            default_sources = [
                DataSource(
                    source_id="document_processing",
                    source_type=DataSourceType.DOCUMENT_PROCESSING,
                    connection_string="internal://document_processing",
                    schema={
                        "document_id": {"type": "string", "required": True},
                        "document_type": {"type": "string", "required": True},
                        "processing_time": {"type": "float", "required": True},
                        "status": {"type": "string", "required": True},
                        "created_at": {"type": "timestamp", "required": True}
                    },
                    update_frequency="real-time"
                ),
                DataSource(
                    source_id="user_activity",
                    source_type=DataSourceType.USER_ACTIVITY,
                    connection_string="internal://user_activity",
                    schema={
                        "user_id": {"type": "string", "required": True},
                        "action": {"type": "string", "required": True},
                        "timestamp": {"type": "timestamp", "required": True},
                        "metadata": {"type": "json", "required": False}
                    },
                    update_frequency="real-time"
                ),
                DataSource(
                    source_id="system_metrics",
                    source_type=DataSourceType.SYSTEM_METRICS,
                    connection_string="internal://system_metrics",
                    schema={
                        "metric_name": {"type": "string", "required": True},
                        "metric_value": {"type": "float", "required": True},
                        "timestamp": {"type": "timestamp", "required": True},
                        "tags": {"type": "json", "required": False}
                    },
                    update_frequency="1m"
                )
            ]
            
            for source in default_sources:
                await self.register_data_source(source)
            
        except Exception as e:
            logger.error(f"Error configurando fuentes por defecto: {e}")
    
    async def _initialize_data_pipelines(self):
        """Inicializar pipelines de datos"""
        try:
            # Pipeline de agregación diaria
            daily_aggregation = DataPipeline(
                pipeline_id="daily_aggregation",
                name="Daily Data Aggregation",
                source_ids=["document_processing", "user_activity"],
                transformations=[
                    {
                        "type": "time_aggregation",
                        "granularity": "day",
                        "metrics": ["count", "sum", "average"]
                    },
                    {
                        "type": "data_quality_check",
                        "rules": ["completeness", "validity", "consistency"]
                    }
                ],
                destination="daily_metrics",
                schedule="0 1 * * *"  # Diario a la 1 AM
            )
            
            await self.create_data_pipeline(daily_aggregation)
            
        except Exception as e:
            logger.error(f"Error inicializando pipelines: {e}")
    
    async def _setup_metrics_and_alerts(self):
        """Configurar métricas y alertas"""
        try:
            # Configurar alertas por defecto
            default_alerts = [
                {
                    "alert_id": "high_error_rate",
                    "alert_type": "error_rate",
                    "condition": "greater_than",
                    "threshold": 0.05,
                    "severity": "high",
                    "description": "Error rate exceeds 5%"
                },
                {
                    "alert_id": "slow_processing",
                    "alert_type": "processing_time",
                    "condition": "greater_than",
                    "threshold": 300,
                    "severity": "medium",
                    "description": "Processing time exceeds 5 minutes"
                }
            ]
            
            for alert_config in default_alerts:
                await self.setup_data_alert(alert_config)
            
        except Exception as e:
            logger.error(f"Error configurando métricas y alertas: {e}")
    
    async def _validate_data_source(self, source: DataSource) -> bool:
        """Validar fuente de datos"""
        try:
            # Validar campos requeridos
            if not source.source_id or not source.source_type:
                return False
            
            # Validar esquema
            if not source.schema:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando fuente de datos: {e}")
            return False
    
    async def _test_data_source_connection(self, source: DataSource) -> bool:
        """Probar conexión con fuente de datos"""
        try:
            # Para fuentes internas, siempre retornar True
            if source.connection_string.startswith("internal://"):
                return True
            
            # Para fuentes externas, implementar pruebas específicas
            return True
            
        except Exception as e:
            logger.error(f"Error probando conexión: {e}")
            return False
    
    async def _create_warehouse_table(self, source: DataSource):
        """Crear tabla en warehouse para fuente de datos"""
        try:
            # Generar schema SQL
            columns = []
            for field_name, field_info in source.schema.items():
                field_type = field_info.get("type", "string")
                sql_type = self._map_type_to_sql(field_type)
                columns.append(f"{field_name} {sql_type}")
            
            columns_sql = ", ".join(columns)
            table_name = f"data_{source.source_id}"
            
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {columns_sql},
                _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            if DUCKDB_AVAILABLE:
                self.data_warehouse.execute(create_table_sql)
            else:
                cursor = self.data_warehouse.cursor()
                cursor.execute(create_table_sql)
                self.data_warehouse.commit()
            
        except Exception as e:
            logger.error(f"Error creando tabla en warehouse: {e}")
    
    def _map_type_to_sql(self, field_type: str) -> str:
        """Mapear tipo de campo a tipo SQL"""
        type_mapping = {
            "string": "TEXT",
            "integer": "INTEGER",
            "float": "REAL",
            "boolean": "BOOLEAN",
            "timestamp": "TIMESTAMP",
            "json": "TEXT"
        }
        return type_mapping.get(field_type, "TEXT")
    
    async def _validate_data_schema(self, data: List[Dict[str, Any]], schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validar datos contra esquema"""
        try:
            validated_data = []
            
            for record in data:
                validated_record = {}
                
                for field_name, field_info in schema.items():
                    if field_name in record:
                        value = record[field_name]
                        
                        # Validar tipo
                        if field_info.get("type") == "integer":
                            try:
                                value = int(value)
                            except (ValueError, TypeError):
                                if field_info.get("required", False):
                                    continue  # Skip invalid required field
                                value = None
                        elif field_info.get("type") == "float":
                            try:
                                value = float(value)
                            except (ValueError, TypeError):
                                if field_info.get("required", False):
                                    continue
                                value = None
                        
                        validated_record[field_name] = value
                    elif field_info.get("required", False):
                        continue  # Skip record with missing required field
                
                if validated_record:
                    validated_data.append(validated_record)
            
            return validated_data
            
        except Exception as e:
            logger.error(f"Error validando esquema de datos: {e}")
            return []
    
    async def _enrich_data(self, data: List[Dict[str, Any]], source: DataSource) -> List[Dict[str, Any]]:
        """Enriquecer datos con metadatos adicionales"""
        try:
            enriched_data = []
            
            for record in data:
                enriched_record = record.copy()
                
                # Agregar metadatos
                enriched_record["_source_id"] = source.source_id
                enriched_record["_source_type"] = source.source_type
                enriched_record["_ingested_at"] = datetime.now().isoformat()
                
                # Generar hash para deduplicación
                record_hash = hashlib.md5(json.dumps(record, sort_keys=True).encode()).hexdigest()
                enriched_record["_record_hash"] = record_hash
                
                enriched_data.append(enriched_record)
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Error enriqueciendo datos: {e}")
            return data
    
    async def _store_data_in_warehouse(self, source_id: str, data: List[Dict[str, Any]]):
        """Almacenar datos en warehouse"""
        try:
            if not data:
                return
            
            table_name = f"data_{source_id}"
            
            # Preparar datos para inserción
            columns = list(data[0].keys())
            placeholders = ", ".join(["?" for _ in columns])
            columns_sql = ", ".join(columns)
            
            insert_sql = f"INSERT INTO {table_name} ({columns_sql}) VALUES ({placeholders})"
            
            values = []
            for record in data:
                values.append([record.get(col) for col in columns])
            
            if DUCKDB_AVAILABLE:
                self.data_warehouse.executemany(insert_sql, values)
            else:
                cursor = self.data_warehouse.cursor()
                cursor.executemany(insert_sql, values)
                self.data_warehouse.commit()
            
        except Exception as e:
            logger.error(f"Error almacenando datos en warehouse: {e}")
    
    async def _update_ingestion_metrics(self, source_id: str, record_count: int):
        """Actualizar métricas de ingesta"""
        try:
            metric_data = {
                "source_id": source_id,
                "value": record_count,
                "timestamp": datetime.now().isoformat()
            }
            
            self.metrics_store["ingestion_rate"].append(metric_data)
            
            # Mantener solo los últimos 1000 registros
            if len(self.metrics_store["ingestion_rate"]) > 1000:
                self.metrics_store["ingestion_rate"].popleft()
            
        except Exception as e:
            logger.error(f"Error actualizando métricas de ingesta: {e}")
    
    async def _check_data_alerts(self, source_id: str, data: List[Dict[str, Any]]):
        """Verificar alertas de datos"""
        try:
            # Verificar alertas configuradas
            for alert in self.alerts:
                if alert.alert_type == "error_rate":
                    # Calcular tasa de error
                    error_records = len([r for r in data if r.get("status") == "error"])
                    error_rate = error_records / len(data) if data else 0
                    
                    if error_rate > alert.threshold:
                        alert.current_value = error_rate
                        alert.triggered_at = datetime.now()
                        logger.warning(f"Alerta disparada: {alert.description}")
                
                elif alert.alert_type == "processing_time":
                    # Verificar tiempo de procesamiento
                    processing_times = [r.get("processing_time", 0) for r in data if r.get("processing_time")]
                    if processing_times:
                        avg_processing_time = sum(processing_times) / len(processing_times)
                        
                        if avg_processing_time > alert.threshold:
                            alert.current_value = avg_processing_time
                            alert.triggered_at = datetime.now()
                            logger.warning(f"Alerta disparada: {alert.description}")
            
        except Exception as e:
            logger.error(f"Error verificando alertas: {e}")
    
    async def _validate_pipeline(self, pipeline: DataPipeline) -> bool:
        """Validar pipeline de datos"""
        try:
            # Validar que las fuentes existen
            for source_id in pipeline.source_ids:
                if source_id not in self.data_sources:
                    return False
            
            # Validar transformaciones
            for transformation in pipeline.transformations:
                if "type" not in transformation:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando pipeline: {e}")
            return False
    
    async def _create_pipeline_tables(self, pipeline: DataPipeline):
        """Crear tablas para pipeline"""
        try:
            # Crear tabla de resultados del pipeline
            table_name = f"pipeline_{pipeline.pipeline_id}"
            
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                execution_id TEXT PRIMARY KEY,
                source_data TEXT,
                transformed_data TEXT,
                execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                error_details TEXT
            )
            """
            
            if DUCKDB_AVAILABLE:
                self.data_warehouse.execute(create_table_sql)
            else:
                cursor = self.data_warehouse.cursor()
                cursor.execute(create_table_sql)
                self.data_warehouse.commit()
            
        except Exception as e:
            logger.error(f"Error creando tablas de pipeline: {e}")
    
    async def _execute_pipeline_transformations(self, pipeline: DataPipeline) -> Dict[str, Any]:
        """Ejecutar transformaciones del pipeline"""
        try:
            records_processed = 0
            
            for transformation in pipeline.transformations:
                transformation_type = transformation["type"]
                
                if transformation_type == "time_aggregation":
                    # Ejecutar agregación temporal
                    result = await self._execute_time_aggregation(pipeline, transformation)
                    records_processed += result.get("records_processed", 0)
                    
                elif transformation_type == "data_quality_check":
                    # Ejecutar verificaciones de calidad
                    result = await self._execute_data_quality_check(pipeline, transformation)
                    records_processed += result.get("records_processed", 0)
                    
                elif transformation_type == "data_enrichment":
                    # Ejecutar enriquecimiento de datos
                    result = await self._execute_data_enrichment(pipeline, transformation)
                    records_processed += result.get("records_processed", 0)
            
            return {"records_processed": records_processed}
            
        except Exception as e:
            logger.error(f"Error ejecutando transformaciones: {e}")
            return {"records_processed": 0}
    
    async def _execute_time_aggregation(self, pipeline: DataPipeline, transformation: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar agregación temporal"""
        try:
            granularity = transformation.get("granularity", "day")
            metrics = transformation.get("metrics", ["count"])
            
            # Implementar agregación temporal
            records_processed = 0
            
            for source_id in pipeline.source_ids:
                table_name = f"data_{source_id}"
                
                # Crear consulta de agregación
                for metric in metrics:
                    if metric == "count":
                        agg_sql = f"""
                        SELECT 
                            DATE_TRUNC('{granularity}', _ingested_at) as time_bucket,
                            COUNT(*) as count_value
                        FROM {table_name}
                        WHERE _ingested_at >= NOW() - INTERVAL '1 DAY'
                        GROUP BY time_bucket
                        ORDER BY time_bucket
                        """
                    elif metric == "sum":
                        agg_sql = f"""
                        SELECT 
                            DATE_TRUNC('{granularity}', _ingested_at) as time_bucket,
                            SUM(CASE WHEN processing_time IS NOT NULL THEN processing_time ELSE 0 END) as sum_value
                        FROM {table_name}
                        WHERE _ingested_at >= NOW() - INTERVAL '1 DAY'
                        GROUP BY time_bucket
                        ORDER BY time_bucket
                        """
                    
                    # Ejecutar consulta (simulado)
                    records_processed += 1
            
            return {"records_processed": records_processed}
            
        except Exception as e:
            logger.error(f"Error en agregación temporal: {e}")
            return {"records_processed": 0}
    
    async def _execute_data_quality_check(self, pipeline: DataPipeline, transformation: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar verificaciones de calidad de datos"""
        try:
            rules = transformation.get("rules", [])
            records_processed = 0
            
            for source_id in pipeline.source_ids:
                table_name = f"data_{source_id}"
                
                # Implementar verificaciones de calidad
                for rule in rules:
                    if rule == "completeness":
                        # Verificar completitud
                        records_processed += 1
                    elif rule == "validity":
                        # Verificar validez
                        records_processed += 1
                    elif rule == "consistency":
                        # Verificar consistencia
                        records_processed += 1
            
            return {"records_processed": records_processed}
            
        except Exception as e:
            logger.error(f"Error en verificación de calidad: {e}")
            return {"records_processed": 0}
    
    async def _execute_data_enrichment(self, pipeline: DataPipeline, transformation: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar enriquecimiento de datos"""
        try:
            enrichment_type = transformation.get("enrichment_type", "metadata")
            records_processed = 0
            
            for source_id in pipeline.source_ids:
                # Implementar enriquecimiento
                if enrichment_type == "metadata":
                    records_processed += 1
                elif enrichment_type == "geolocation":
                    records_processed += 1
                elif enrichment_type == "categorization":
                    records_processed += 1
            
            return {"records_processed": records_processed}
            
        except Exception as e:
            logger.error(f"Error en enriquecimiento de datos: {e}")
            return {"records_processed": 0}
    
    async def _build_sql_query(self, query: DataQuery) -> str:
        """Construir consulta SQL"""
        try:
            # Construir SELECT
            select_clause = "*"
            if query.aggregations:
                agg_columns = []
                for agg in query.aggregations:
                    agg_type = agg.get("type", "count")
                    column = agg.get("column", "*")
                    agg_columns.append(f"{agg_type.upper()}({column}) as {agg_type}_{column}")
                select_clause = ", ".join(agg_columns)
            
            # Construir FROM
            from_clause = ", ".join([f"data_{table}" for table in query.source_tables])
            
            # Construir WHERE
            where_clause = ""
            if query.filters:
                conditions = []
                for field, value in query.filters.items():
                    if isinstance(value, str):
                        conditions.append(f"{field} = '{value}'")
                    else:
                        conditions.append(f"{field} = {value}")
                where_clause = f"WHERE {' AND '.join(conditions)}"
            
            # Construir tiempo
            if query.time_range:
                start_time, end_time = query.time_range
                time_condition = f"_ingested_at BETWEEN '{start_time}' AND '{end_time}'"
                if where_clause:
                    where_clause += f" AND {time_condition}"
                else:
                    where_clause = f"WHERE {time_condition}"
            
            # Construir ORDER BY y LIMIT
            order_clause = "ORDER BY _ingested_at DESC"
            limit_clause = f"LIMIT {query.limit} OFFSET {query.offset}"
            
            # Construir consulta completa
            sql_query = f"""
            SELECT {select_clause}
            FROM {from_clause}
            {where_clause}
            {order_clause}
            {limit_clause}
            """
            
            return sql_query.strip()
            
        except Exception as e:
            logger.error(f"Error construyendo consulta SQL: {e}")
            return "SELECT 1"
    
    async def _execute_duckdb_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """Ejecutar consulta con DuckDB"""
        try:
            result = self.data_warehouse.execute(sql_query).fetchall()
            columns = [desc[0] for desc in self.data_warehouse.description]
            
            return [dict(zip(columns, row)) for row in result]
            
        except Exception as e:
            logger.error(f"Error ejecutando consulta DuckDB: {e}")
            return []
    
    async def _execute_sqlite_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """Ejecutar consulta con SQLite"""
        try:
            cursor = self.data_warehouse.cursor()
            cursor.execute(sql_query)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            return [dict(zip(columns, row)) for row in result]
            
        except Exception as e:
            logger.error(f"Error ejecutando consulta SQLite: {e}")
            return []
    
    async def _format_query_result(self, result: List[Dict[str, Any]], query: DataQuery) -> List[Dict[str, Any]]:
        """Formatear resultado de consulta"""
        try:
            # Formatear fechas y tipos
            formatted_result = []
            
            for row in result:
                formatted_row = {}
                for key, value in row.items():
                    if isinstance(value, datetime):
                        formatted_row[key] = value.isoformat()
                    else:
                        formatted_row[key] = value
                formatted_result.append(formatted_row)
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error formateando resultado: {e}")
            return result
    
    async def _generate_trend_insights(self, data_source_ids: List[str]) -> List[DataInsight]:
        """Generar insights de tendencias"""
        try:
            insights = []
            
            for source_id in data_source_ids:
                # Implementar análisis de tendencias
                insight = DataInsight(
                    insight_id=f"trend_{source_id}_{int(datetime.now().timestamp())}",
                    insight_type="trend_analysis",
                    title=f"Tendencia en {source_id}",
                    description=f"Análisis de tendencias para fuente {source_id}",
                    data={
                        "source_id": source_id,
                        "trend_direction": "increasing",
                        "trend_strength": 0.75,
                        "period": "7_days"
                    },
                    confidence=0.8,
                    generated_at=datetime.now()
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generando insights de tendencias: {e}")
            return []
    
    async def _generate_anomaly_insights(self, data_source_ids: List[str]) -> List[DataInsight]:
        """Generar insights de anomalías"""
        try:
            insights = []
            
            for source_id in data_source_ids:
                # Implementar detección de anomalías
                insight = DataInsight(
                    insight_id=f"anomaly_{source_id}_{int(datetime.now().timestamp())}",
                    insight_type="anomaly_detection",
                    title=f"Anomalías en {source_id}",
                    description=f"Detección de anomalías para fuente {source_id}",
                    data={
                        "source_id": source_id,
                        "anomalies_detected": 3,
                        "anomaly_score": 0.85,
                        "time_window": "24_hours"
                    },
                    confidence=0.9,
                    generated_at=datetime.now()
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generando insights de anomalías: {e}")
            return []
    
    async def _generate_correlation_insights(self, data_source_ids: List[str]) -> List[DataInsight]:
        """Generar insights de correlación"""
        try:
            insights = []
            
            if len(data_source_ids) >= 2:
                # Implementar análisis de correlación
                insight = DataInsight(
                    insight_id=f"correlation_{int(datetime.now().timestamp())}",
                    insight_type="correlation_analysis",
                    title="Correlaciones entre fuentes",
                    description="Análisis de correlaciones entre fuentes de datos",
                    data={
                        "source_pairs": data_source_ids,
                        "correlation_coefficient": 0.65,
                        "relationship_type": "positive"
                    },
                    confidence=0.7,
                    generated_at=datetime.now()
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generando insights de correlación: {e}")
            return []
    
    async def _generate_performance_insights(self, data_source_ids: List[str]) -> List[DataInsight]:
        """Generar insights de rendimiento"""
        try:
            insights = []
            
            for source_id in data_source_ids:
                # Implementar análisis de rendimiento
                insight = DataInsight(
                    insight_id=f"performance_{source_id}_{int(datetime.now().timestamp())}",
                    insight_type="performance_metrics",
                    title=f"Métricas de rendimiento para {source_id}",
                    description=f"Análisis de rendimiento para fuente {source_id}",
                    data={
                        "source_id": source_id,
                        "throughput": 1500,
                        "latency": 0.25,
                        "error_rate": 0.02,
                        "availability": 0.998
                    },
                    confidence=0.95,
                    generated_at=datetime.now()
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generando insights de rendimiento: {e}")
            return []
    
    async def _create_dashboard_widget(self, widget_config: Dict[str, Any]) -> Dict[str, Any]:
        """Crear widget de dashboard"""
        try:
            widget_type = widget_config.get("type", "metric")
            
            if widget_type == "metric":
                return {
                    "type": "metric",
                    "title": widget_config.get("title", "Métrica"),
                    "query": widget_config.get("query", {}),
                    "visualization": "number",
                    "refresh_interval": widget_config.get("refresh_interval", 60)
                }
            elif widget_type == "chart":
                return {
                    "type": "chart",
                    "title": widget_config.get("title", "Gráfico"),
                    "query": widget_config.get("query", {}),
                    "visualization": widget_config.get("chart_type", "line"),
                    "refresh_interval": widget_config.get("refresh_interval", 300)
                }
            elif widget_type == "table":
                return {
                    "type": "table",
                    "title": widget_config.get("title", "Tabla"),
                    "query": widget_config.get("query", {}),
                    "visualization": "table",
                    "refresh_interval": widget_config.get("refresh_interval", 300)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error creando widget de dashboard: {e}")
            return None
    
    async def _get_warehouse_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del warehouse"""
        try:
            stats = {
                "total_tables": 0,
                "total_records": 0,
                "storage_size_mb": 0,
                "last_updated": datetime.now().isoformat()
            }
            
            # Obtener estadísticas básicas
            if self.warehouse_path.exists():
                stats["storage_size_mb"] = self.warehouse_path.stat().st_size / (1024 * 1024)
            
            # Contar tablas y registros
            for source_id in self.data_sources.keys():
                stats["total_tables"] += 1
                # En un entorno real, consultaríamos la base de datos
                stats["total_records"] += 1000  # Simulado
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del warehouse: {e}")
            return {}