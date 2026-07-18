import subprocess
import json
import pytest
from pathlib import Path

# Cargar los esquemas Pydantic desde los scripts
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
from search_symbol import SearchResponse
from extractor import ExtractorResponse

PROJECT_ROOT = Path(__file__).parent.parent

def run_command(command: list) -> str:
    """Ejecuta un comando CLI y captura stdout."""
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout, result.stderr, result.returncode

def extract_json_from_output(stdout: str) -> dict:
    """Extrae el JSON válido ignorando logs de tvdatafeed."""
    for line in stdout.strip().split('\n'):
        if line.startswith('{'):
            return json.loads(line)
    raise ValueError(f"No se encontró un JSON válido en la salida: {stdout}")

class TestSmokeCLI:
    
    def test_search_symbol_happy_path(self):
        """Evalúa que search_symbol retorne un JSON válido de Pydantic."""
        cmd = [sys.executable, "scripts/search_symbol.py", "--symbol", "AAPL", "--json"]
        stdout, stderr, code = run_command(cmd)
        assert code == 0, f"Script falló: {stderr}"
        
        data = extract_json_from_output(stdout)
        
        # Validar contrato pydantic
        response = SearchResponse(**data)
        assert response.status == "success"
        assert len(response.results) > 0
        assert any(r.symbol == "AAPL" for r in response.results)

    def test_search_symbol_security_injection(self):
        """Evalúa que el Guardrail de Seguridad intercepte comandos inyectados."""
        cmd = [sys.executable, "scripts/search_symbol.py", "--symbol", "AAPL;rm -rf /", "--json"]
        stdout, stderr, code = run_command(cmd)
        assert code == 1, "La validación de seguridad debería abortar con código 1"
        
        data = extract_json_from_output(stdout)
        response = SearchResponse(**data)
        assert response.status == "error"
        assert "Error de Seguridad" in response.error_message or "Símbolo inválido" in response.error_message

    def test_extractor_happy_path(self):
        """Evalúa que el extractor devuelva el output estructurado correcto."""
        cmd = [sys.executable, "scripts/extractor.py", "--symbol", "AAPL", "--exchange", "NASDAQ", "--bars", "5", "--json"]
        stdout, stderr, code = run_command(cmd)
        assert code == 0, f"Script falló: {stderr}"
        
        data = extract_json_from_output(stdout)
        
        # Validar contrato pydantic
        response = ExtractorResponse(**data)
        assert response.status == "success"
        assert len(response.files) > 0
        assert response.files[0].symbol == "AAPL"
        assert response.files[0].exchange == "NASDAQ"
        assert response.files[0].rows > 0

    def test_extractor_security_injection(self):
        """Evalúa que el extractor frene inyecciones."""
        cmd = [sys.executable, "scripts/extractor.py", "--symbol", "TSLA", "--exchange", "NASDAQ&echo hacked", "--bars", "5", "--json"]
        stdout, stderr, code = run_command(cmd)
        assert code == 1, "La validación de seguridad debería abortar con código 1"
        
        data = extract_json_from_output(stdout)
        response = ExtractorResponse(**data)
        assert response.status == "error"
        assert "Error de Seguridad" in response.error_message
