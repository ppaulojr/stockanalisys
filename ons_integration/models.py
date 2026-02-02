"""
Data models for ONS API responses
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class EnergyData:
    """Representa dados de energia do ONS"""
    timestamp: datetime
    value: float
    unit: str
    source: Optional[str] = None
    region: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnergyData":
        """Cria instância a partir de um dicionário"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        
        return cls(
            timestamp=timestamp,
            value=float(data.get("value", 0)),
            unit=data.get("unit", "MW"),
            source=data.get("source"),
            region=data.get("region")
        )


@dataclass
class LoadData:
    """Representa dados de carga do sistema"""
    timestamp: datetime
    load_mw: float
    region: str
    verified: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LoadData":
        """Cria instância a partir de um dicionário"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        
        return cls(
            timestamp=timestamp,
            load_mw=float(data.get("load_mw", 0)),
            region=data.get("region", "SIN"),
            verified=data.get("verified", False)
        )


@dataclass
class GenerationData:
    """Representa dados de geração por fonte"""
    timestamp: datetime
    source_type: str  # hidro, termica, eolica, solar, nuclear
    generation_mw: float
    region: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationData":
        """Cria instância a partir de um dicionário"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        
        return cls(
            timestamp=timestamp,
            source_type=data.get("source_type", ""),
            generation_mw=float(data.get("generation_mw", 0)),
            region=data.get("region", "SIN")
        )
