from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.db.session import get_db
from fastapi.responses import PlainTextResponse
from app.utils.electreIII import generar_reporte_escenario
from fastapi.responses import FileResponse
import os
from app.utils.electreIII import crear_csv_electre3_desde_bd
from app.utils.electreIII import ejecutar_electre3_desde_bd_flujo_neto
from app.utils.electreIII import ejecutar_electre3_desde_bd_destilacion, ejecutar_electre3_desde_argumentos_destilacion, ejecutar_electre3_desde_argumentos_flujo_neto, ejecutar_electre3_desde_csv_destilacion, ejecutar_electre3_desde_csv_flujo_neto
from app.models.ElectreRequest import ElectreIIIRequest
from fastapi import UploadFile, File, Form
import tempfile
import shutil
router = APIRouter()

@router.get("/escenarios/{escenario_id}/reporte", response_class=PlainTextResponse)
def obtener_reporte_escenario(
    escenario_id: int,
    db: Session = Depends(get_db),
) -> str:
    """
    Endpoint para generar un reporte detallado del escenario para ELECTRE III.
    """
    try:
        reporte = generar_reporte_escenario(db, escenario_id)
        return reporte
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/escenarios/{escenario_id}/csv", response_class=FileResponse)
def descargar_csv_electre3(
    escenario_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Endpoint para generar y descargar el archivo CSV de ELECTRE III para un escenario.
    """
    try:
        nombre_archivo = f"electre3_bd_{escenario_id}.csv"
        crear_csv_electre3_desde_bd(db, escenario_id, nombre_archivo=nombre_archivo)
        file_path = os.path.abspath(nombre_archivo)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Archivo CSV no encontrado")
        return FileResponse(
            path=file_path,
            filename=nombre_archivo,
            media_type="text/csv"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/escenarios/{escenario_id}/resultados_flujo_neto", response_model=List[str])
def obtener_resultados_electre3(
    escenario_id: int,
    db: Session = Depends(get_db),
) -> any:
    """
    Endpoint para ejecutar ELECTRE III usando datos de la base de datos y obtener los resultados.
    """
    resultado = ejecutar_electre3_desde_bd_flujo_neto(db, escenario_id)
    if resultado is None:
        raise HTTPException(status_code=500, detail="Error al ejecutar ELECTRE III")
    return resultado

@router.get("/escenarios/{escenario_id}/resultados_destilacion", response_model=List[str])
def obtener_resultados_electre3(
    escenario_id: int,
    db: Session = Depends(get_db),
) -> any:
    """
    Endpoint para ejecutar ELECTRE III usando datos de la base de datos y obtener los resultados.
    """
    resultado = ejecutar_electre3_desde_bd_destilacion(db, escenario_id)
    if resultado is None:
        raise HTTPException(status_code=500, detail="Error al ejecutar ELECTRE III")
    return resultado

@router.post("/ejecutar_flujo_neto")
def ejecutar_electre3(request: ElectreIIIRequest):
    resultado = ejecutar_electre3_desde_argumentos_flujo_neto(
        alternativas_matriz=request.alternativas_matriz,
        criterios_nombres=request.criterios_nombres,
        pesos=request.pesos,
        preferencia=request.preferencia,
        indiferencia=request.indiferencia,
        veto=request.veto,
        direccion=request.direccion,
        lambda_corte=request.lambda_corte,
        nombres_alternativas=request.nombres_alternativas
    )
    if resultado is None:
        raise HTTPException(status_code=500, detail="Error al ejecutar ELECTRE III")
    return resultado

@router.post("/ejecutar_destilacion")
def ejecutar_electre3(request: ElectreIIIRequest):
    resultado = ejecutar_electre3_desde_argumentos_destilacion(
        alternativas_matriz=request.alternativas_matriz,
        criterios_nombres=request.criterios_nombres,
        pesos=request.pesos,
        preferencia=request.preferencia,
        indiferencia=request.indiferencia,
        veto=request.veto,
        direccion=request.direccion,
        lambda_corte=request.lambda_corte,
        nombres_alternativas=request.nombres_alternativas
    )
    if resultado is None:
        raise HTTPException(status_code=500, detail="Error al ejecutar ELECTRE III")
    return resultado


@router.post("/ejecutar_directo_flujo_neto")
async def ejecutar_electre3_directo_flujo_neto(file: UploadFile = File(...), lambda_corte: float = Form(...)):
    """
    Endpoint que recibe un archivo CSV y un valor lambda (float), guarda temporalmente el CSV
    y llama a ejecutar_electre3_desde_csv_flujo_neto con la ruta del archivo y el lambda.
    """
    try:
        # Guardar archivo subido en un archivo temporal
        suffix = ".csv"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        # Llamar a la función que ejecuta ELECTRE III desde CSV (ajustar kwargs según la firma real)
        resultado = ejecutar_electre3_desde_csv_flujo_neto(tmp_path, lambda_corte=lambda_corte)

        # Borrar archivo temporal
        try:
            os.remove(tmp_path)
        except Exception:
            pass

        if resultado is None:
            raise HTTPException(status_code=500, detail="Error al ejecutar ELECTRE III")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        
@router.post("/ejecutar_directo_destilacion")
async def ejecutar_electre3_directo_destilacion(file: UploadFile = File(...), lambda_corte: float = Form(...)):
    """
    Endpoint que recibe un archivo CSV y un valor lambda (float), guarda temporalmente el CSV
    y llama a ejecutar_electre3_desde_csv_destilacion con la ruta del archivo y el lambda.
    """
    try:
        # Guardar archivo subido en un archivo temporal
        suffix = ".csv"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        # Llamar a la función que ejecuta ELECTRE III desde CSV (ajustar kwargs según la firma real)
        resultado = ejecutar_electre3_desde_csv_destilacion(tmp_path, lambda_corte=lambda_corte)

        # Borrar archivo temporal
        try:
            os.remove(tmp_path)
        except Exception:
            pass

        if resultado is None:
            raise HTTPException(status_code=500, detail="Error al ejecutar ELECTRE III")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))