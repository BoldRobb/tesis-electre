import pandas as pd
import numpy as np
import tempfile
import re
import os
import ctypes
import platform
from contextlib import contextmanager
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Tuple
from contextlib import contextmanager
from app.core.config import settings

from app.models import Alternativa, Criterio, Evaluacion, Escenario

def cargar_dll_electre():
    """
    Carga la librería ELECTRE III de forma compatible con Windows y Linux.
    
    Returns:
        ctypes.CDLL: Instancia de la librería cargada
    """
    if platform.system() == 'Windows':
        # En Windows, añadir el directorio de DLLs al path de búsqueda
        os.add_dll_directory(settings.DEBUGGER_PATH)
    
    # Cargar la librería (.dll en Windows, .so en Linux)
    dll = ctypes.CDLL(settings.DLL_PATH)
    return dll

def interpretar_resultado_flujo_neto(resultado):
    # Ejemplo: ":A1:1;:B2:0;:C3:-1;"
    pares = re.findall(r":([^:;]+):([-\d\.]+);", resultado)
    # Ordenar por valor de flujo neto (mayor es mejor)
    ranking = sorted(pares, key=lambda x: float(x[1]), reverse=True)
    return [alt for alt, val in ranking]

def interpretar_resultado_destilacion(resultado):
    # Ejemplo: "A1:0;B2:1;C3:2;"
    pares = re.findall(r"([^:;]+):(\d+);", resultado)
    # Ordenar por ranking (menor es mejor)
    ranking = sorted(pares, key=lambda x: int(x[1]))
    return [alt for alt, val in ranking]

def crear_csv_electre3(alternativas_matriz, criterios_nombres, pesos, preferencia, 
                       indiferencia, veto, direccion, nombre_archivo="electre3.csv"):
    """
    Crea un archivo CSV con el formato requerido para ELECTRE III
    
    Parámetros:
    - alternativas_matriz: matriz numpy o lista de listas con los valores de las alternativas
    - criterios_nombres: lista con los nombres de los criterios (columnas)
    - pesos: lista con los pesos de cada criterio (W)
    - preferencia: lista con los umbrales de preferencia para cada criterio (P)
    - indiferencia: lista con los umbrales de indiferencia para cada criterio (I/Q)
    - veto: lista con los umbrales de veto para cada criterio (V)
    - direccion: lista con la dirección de cada criterio (1=maximizar, 0=minimizar) (D)
    - nombre_archivo: nombre del archivo CSV a generar
    
    Retorna:
    - DataFrame con la estructura creada
    """
    
    # Convertir matriz de alternativas a numpy array si no lo es
    if not isinstance(alternativas_matriz, np.ndarray):
        alternativas_matriz = np.array(alternativas_matriz)
    
    # Verificar que las dimensiones coincidan
    num_alternativas, num_criterios = alternativas_matriz.shape
    
    if len(criterios_nombres) != num_criterios:
        raise ValueError("El número de criterios no coincide con las columnas de la matriz")
    
    # Verificar que todos los parámetros tengan la longitud correcta
    parametros = [pesos, preferencia, indiferencia, veto, direccion]
    nombres_param = ['pesos', 'preferencia', 'indiferencia', 'veto', 'direccion']
    
    for param, nombre in zip(parametros, nombres_param):
        if len(param) != num_criterios:
            raise ValueError(f"La longitud de {nombre} ({len(param)}) no coincide con el número de criterios ({num_criterios})")
    
    # Crear el DataFrame
    # Primero la fila de encabezados (nombres de criterios)
    data = []
    
    # Generar nombres de alternativas (A1, A2, A3, etc. o usar nombres personalizados)
    nombres_alternativas = [f"A{i+1}" for i in range(num_alternativas)]
    
    # Agregar filas de alternativas
    for i, nombre_alt in enumerate(nombres_alternativas):
        fila = [nombre_alt] + list(alternativas_matriz[i])
        data.append(fila)
    
    # Agregar fila de pesos (W)
    data.append(['W'] + list(pesos))
    
    # Agregar fila de preferencia (P)
    data.append(['P'] + list(preferencia))
    
    # Agregar fila de indiferencia (I)
    data.append(['I'] + list(indiferencia))
    
    # Agregar fila de veto (V)
    data.append(['V'] + list(veto))
    
    # Agregar fila de dirección (D)
    data.append(['D'] + list(direccion))
    
    # Crear DataFrame
    columnas = ['-'] + criterios_nombres
    df = pd.DataFrame(data, columns=columnas)
    
    # Guardar como CSV con separador de punto y coma
    df.to_csv(nombre_archivo, sep=';', index=False)
    
    print(f"Archivo {nombre_archivo} creado exitosamente")
    print("\nEstructura del archivo:")
    print(df.to_string(index=False))
    
    return df

def crear_csv_electre3_personalizado(alternativas_dict, criterios_nombres, pesos, 
                                   preferencia, indiferencia, veto, direccion, 
                                   nombres_alternativas=None, nombre_archivo="electre3.csv"):
    """
    Versión alternativa que acepta un diccionario de alternativas
    
    Parámetros:
    - alternativas_dict: diccionario donde las claves son nombres de alternativas 
                        y los valores son listas con los valores para cada criterio
    - nombres_alternativas: lista opcional con nombres personalizados para las alternativas
    - resto de parámetros igual que la función anterior
    """
    
    if nombres_alternativas is None:
        nombres_alternativas = list(alternativas_dict.keys())
    
    # Convertir diccionario a matriz
    alternativas_matriz = []
    for nombre in nombres_alternativas:
        if nombre in alternativas_dict:
            alternativas_matriz.append(alternativas_dict[nombre])
        else:
            raise ValueError(f"Alternativa '{nombre}' no encontrada en el diccionario")
    
    return crear_csv_electre3(alternativas_matriz, criterios_nombres, pesos, 
                             preferencia, indiferencia, veto, direccion, nombre_archivo)

@contextmanager
def csv_temporal_electre3(alternativas_matriz, criterios_nombres, pesos, 
                         preferencia, indiferencia, veto, direccion, 
                         nombres_alternativas=None):
    """
    Context manager que crea un archivo CSV temporal para ELECTRE III
    y lo elimina automáticamente al finalizar
    
    Uso:
    with csv_temporal_electre3(datos...) as archivo_csv:
        # Usar archivo_csv con la DLL
        resultado = llamar_dll(archivo_csv)
    # El archivo se elimina automáticamente aquí
    """
    
    # Crear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    archivo_temporal = temp_file.name
    temp_file.close()
    
    try:
        # Crear el CSV usando la función existente
        df = crear_csv_electre3(alternativas_matriz, criterios_nombres, pesos, 
                               preferencia, indiferencia, veto, direccion, 
                               archivo_temporal)
        
        # Si se proporcionan nombres personalizados, actualizarlos
        if nombres_alternativas:
            for i, nombre in enumerate(nombres_alternativas):
                if i < len(df) - 5:  # No modificar las últimas 5 filas (W,P,I,V,D)
                    df.iloc[i, 0] = nombre
                # Guardar con nombres actualizados y agregar ';' al final de cada fila
            df.to_csv(archivo_temporal, index=False)
            # Añadir ';' al final de cada línea del archivo
            with open(archivo_temporal, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(archivo_temporal, 'w', encoding='utf-8') as f:
                for line in lines:
                    line = line.rstrip('\n')
                    if not line.endswith(';'):
                        line += ';'
                    f.write(line + '\n')
        
        print(f"Archivo temporal creado: {archivo_temporal}")
        yield archivo_temporal
        
    finally:
        # Eliminar archivo temporal
        try:
            os.unlink(archivo_temporal)
            print(f"Archivo temporal eliminado: {archivo_temporal}")
        except OSError:
            print(f"No se pudo eliminar el archivo temporal: {archivo_temporal}")

def ejecutar_electre3_con_dll(dll_path, alternativas_matriz, criterios_nombres, 
                             pesos, preferencia, indiferencia, veto, direccion,
                             nombres_alternativas=None, lambda_corte=-1):
    """
    Ejecuta ELECTRE III usando una DLL de C++
    
    Parámetros:
    - dll_path: ruta al archivo DLL
    - lambda_corte: valor de corte lambda para la matriz T
    - resto de parámetros: igual que crear_csv_electre3
    
    Retorna:
    - Resultado del análisis ELECTRE III
    """
    
    try:
        # Cargar la DLL
        dll = ctypes.CDLL(dll_path)
        
        # Configurar tipos de argumentos y retorno (ajustar según tu DLL)
        # Ejemplo: función que toma archivo CSV y lambda, retorna puntero a resultado
        dll.ejecutar_electre3.argtypes = [ctypes.c_char_p, ctypes.c_double]
        dll.ejecutar_electre3.restype = ctypes.c_char_p  # o el tipo que corresponda
        
        # Usar archivo temporal
        with csv_temporal_electre3(alternativas_matriz, criterios_nombres, pesos,
                                  preferencia, indiferencia, veto, direccion,
                                  nombres_alternativas) as archivo_csv:
            
            print(f"Ejecutando ELECTRE III con λ = {lambda_corte}")
            
            # Llamar a la función DLL
            resultado = dll.ejecutar_electre3(
                archivo_csv.encode('utf-8'),  # Convertir string a bytes
                ctypes.c_double(lambda_corte)
            )
            
            # Procesar resultado (ajustar según el tipo de retorno de tu DLL)
            if resultado:
                resultado_str = resultado.decode('utf-8')
                print("Resultado ELECTRE III:")
                print(resultado_str)
                return resultado_str
            else:
                print("La DLL no retornó resultado")
                return None
                
    except Exception as e:
        print(f"Error al ejecutar ELECTRE III con DLL: {e}")
        return None

def ejemplo_uso_con_dll():
    """
    Ejemplo de uso completo con archivo temporal y DLL
    """
    print("=== EJEMPLO DE USO CON DLL ===")
    
    # Datos de ejemplo (hoteles)
    hoteles_matriz = [
        [1600, 300, 2, 3, 4, 5],  # hotel1
        [1700, 400, 2, 2, 4, 5],  # hotel2
        [1700, 550, 4, 0, 3, 3],  # hotel3
        [2000, 350, 3, 2, 4, 2],  # hotel4
        [1200, 110, 1, 0, 1, 1],  # hotel5
        [110, 1300, 1, 1, 3, 4],  # hotel6
    ]
    
    criterios_hoteles = ['DC', 'DD', 'SEQ', 'RE', 'ST', 'SER']
    pesos_hoteles = [0.2, 0.3, 0.1, 0.1, 0.1, 0.2]
    preferencia_hoteles = [700, 300, 1, 1, 2, 3]
    indiferencia_hoteles = [200, 100, 0, 0, 1, 1]
    veto_hoteles = [1000, 1000, 3, 3, 3, 4]
    direccion_hoteles = [0, 0, 1, 1, 1, 1]
    nombres_hoteles = ['hotel1', 'hotel2', 'hotel3', 'hotel4', 'hotel5', 'hotel6']
    
    # Opción 1: Usar context manager directamente
    print("\n--- Opción 1: Context Manager ---")
    with csv_temporal_electre3(hoteles_matriz, criterios_hoteles, pesos_hoteles,
                              preferencia_hoteles, indiferencia_hoteles,
                              veto_hoteles, direccion_hoteles, nombres_hoteles) as csv_file:
        
        print(f"Archivo temporal disponible: {csv_file}")
        # Aquí llamarías a tu DLL
        # resultado = tu_dll.procesar_electre3(csv_file, lambda_corte=0.67)
        print("Simulando procesamiento con DLL...")
        
        # Verificar que el archivo existe y tiene contenido
        if os.path.exists(csv_file):
            with open(csv_file, 'r') as f:
                contenido = f.read()
                print(f"Archivo tiene {len(contenido)} caracteres")
        
    print("Archivo temporal eliminado automáticamente")
    
    # Opción 2: Usar función wrapper (descomenta si tienes una DLL)
    print("\n--- Opción 2: Función Wrapper ---")
    # dll_path = "ruta/a/tu/electre3.dll"  # Cambia por la ruta real
    # resultado = ejecutar_electre3_con_dll(dll_path, hoteles_matriz, criterios_hoteles,
    #                                      pesos_hoteles, preferencia_hoteles,
    #                                      indiferencia_hoteles, veto_hoteles,
    #                                      direccion_hoteles, nombres_hoteles, 0.67)
    print("Función wrapper lista para usar cuando tengas la DLL")

def analisis_sensibilidad_lambda(dll_path, alternativas_matriz, criterios_nombres,
                                pesos, preferencia, indiferencia, veto, direccion,
                                nombres_alternativas=None, lambdas=[0.6, 0.67, 0.75]):
    """
    Realiza análisis de sensibilidad con diferentes valores de lambda
    """
    resultados = {}
    
    for lambda_val in lambdas:
        print(f"\n--- Analizando con λ = {lambda_val} ---")
        resultado = ejecutar_electre3_con_dll(dll_path, alternativas_matriz, criterios_nombres,
                                            pesos, preferencia, indiferencia, veto, direccion,
                                            nombres_alternativas, lambda_val)
        if resultado:
            resultados[lambda_val] = resultado
    
    return resultados

def obtener_datos_escenario_para_electre(db: Session, escenario_id: int) -> Dict:
    """
    Obtiene todos los datos necesarios de un escenario para ejecutar ELECTRE III
    
    Args:
        db: Sesión de SQLAlchemy
        escenario_id: ID del escenario a analizar
    
    Returns:
        Dict con los datos estructurados para ELECTRE III
    """
    
    # Obtener alternativas del escenario
    alternativas = db.query(Alternativa).filter(
        Alternativa.escenario_id == escenario_id
    ).all()
    
    # Obtener criterios del escenario
    criterios = db.query(Criterio).filter(
        Criterio.escenario_id == escenario_id
    ).all()
    
    # Obtener evaluaciones del escenario
    evaluaciones = db.query(Evaluacion).filter(
        Evaluacion.escenario_id == escenario_id
    ).all()
    
    if not alternativas or not criterios or not evaluaciones:
        raise ValueError(f"No se encontraron datos suficientes para el escenario {escenario_id}")
    
    #Obtener corte del escenario si no, colocar -1
    corte = db.query(Escenario).filter(Escenario.id == escenario_id).first().corte
    if corte is None:
        corte = -1

    # Crear diccionario de evaluaciones para acceso rápido
    eval_dict = {}
    for eval in evaluaciones:
        key = (eval.alternativa_id, eval.criterio_id)
        eval_dict[key] = eval.value
    
    # Construir matriz de decisión
    matriz_decision = []
    nombres_alternativas = []
    
    for alternativa in alternativas:
        fila = []
        nombres_alternativas.append(alternativa.name)
        
        for criterio in criterios:
            key = (alternativa.id, criterio.id)
            if key in eval_dict:
                fila.append(eval_dict[key])
            else:
                raise ValueError(f"Falta evaluación para alternativa {alternativa.name} y criterio {criterio.name}")
        
        matriz_decision.append(fila)
    
    # Extraer información de criterios
    nombres_criterios = [criterio.name for criterio in criterios]
    pesos = [criterio.weight for criterio in criterios]
    
    # Umbrales ELECTRE III (usar valores por defecto si no están definidos)
    preferencia = []
    indiferencia = []
    veto = []
    direccion = []
    
    for criterio in criterios:
        # Umbral de preferencia
        if criterio.preference_threshold is not None:
            preferencia.append(criterio.preference_threshold)
        else:
            # Valor por defecto: 10% del rango de valores para este criterio
            valores_criterio = [eval_dict[(alt.id, criterio.id)] for alt in alternativas]
            rango = max(valores_criterio) - min(valores_criterio)
            preferencia.append(rango * 0.1)
        
        # Umbral de indiferencia
        if criterio.indifference_threshold is not None:
            indiferencia.append(criterio.indifference_threshold)
        else:
            # Valor por defecto: 5% del rango
            valores_criterio = [eval_dict[(alt.id, criterio.id)] for alt in alternativas]
            rango = max(valores_criterio) - min(valores_criterio)
            indiferencia.append(rango * 0.05)
        
        # Umbral de veto
        if criterio.veto_threshold is not None:
            veto.append(criterio.veto_threshold)
        else:
            # Valor por defecto: 50% del rango
            valores_criterio = [eval_dict[(alt.id, criterio.id)] for alt in alternativas]
            rango = max(valores_criterio) - min(valores_criterio)
            veto.append(rango * 0.5)
        
        # Dirección (1 para beneficio, 0 para costo)
        direccion.append(1 if criterio.is_benefit else 0)
    
    return {
        'matriz_decision': np.array(matriz_decision),
        'nombres_alternativas': nombres_alternativas,
        'nombres_criterios': nombres_criterios,
        'pesos': pesos,
        'preferencia': preferencia,
        'indiferencia': indiferencia,
        'veto': veto,
        'direccion': direccion,
        'alternativas_obj': alternativas,
        'criterios_obj': criterios,
        'corte' : corte
    }

def crear_csv_electre3_desde_bd(db: Session, escenario_id: int, 
                               nombre_archivo: str = "electre3_bd.csv") -> pd.DataFrame:
    """
    Crea un archivo CSV para ELECTRE III directamente desde la base de datos
    
    Args:
        db: Sesión de SQLAlchemy
        escenario_id: ID del escenario
        nombre_archivo: Nombre del archivo CSV a crear
    
    Returns:
        DataFrame con la estructura ELECTRE III
    """
    
    # Obtener datos del escenario
    datos = obtener_datos_escenario_para_electre(db, escenario_id)
    
    # Usar la función existente para crear el CSV
    from app.utils.electreIII import crear_csv_electre3
    
    df = crear_csv_electre3(
        alternativas_matriz=datos['matriz_decision'],
        criterios_nombres=datos['nombres_criterios'],
        pesos=datos['pesos'],
        preferencia=datos['preferencia'],
        indiferencia=datos['indiferencia'],
        veto=datos['veto'],
        direccion=datos['direccion'],
        nombre_archivo=nombre_archivo
    )
    
    # Actualizar nombres de alternativas en el DataFrame
    for i, nombre in enumerate(datos['nombres_alternativas']):
        if i < len(df) - 5:  # No modificar las últimas 5 filas (W,P,I,V,D)
            df.iloc[i, 0] = nombre

    # Guardar con nombres actualizados y agregar ';' al final de cada fila
    df.to_csv(nombre_archivo, index=False)
    # Añadir ';' al final de cada línea del archivo
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        for line in lines:
            line = line.rstrip('\n')
            if not line.endswith(';'):
                line += ';'
            f.write(line + '\n')
    
    return df

@contextmanager
def csv_temporal_electre3_desde_bd(db: Session, escenario_id: int):
    """
    Context manager que crea un archivo CSV temporal para ELECTRE III desde la BD
    y lo elimina automáticamente al finalizar
    
    Args:
        db: Sesión de SQLAlchemy
        escenario_id: ID del escenario
    
    Yields:
        str: Ruta del archivo CSV temporal
    """
    
    # Crear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    archivo_temporal = temp_file.name
    temp_file.close()
    
    try:
        # Crear el CSV desde la base de datos
        df = crear_csv_electre3_desde_bd(db, escenario_id, archivo_temporal)
        
        print(f"Archivo temporal creado desde BD: {archivo_temporal}")
        print(f"Escenario ID: {escenario_id}")
        print(f"Dimensiones: {df.shape}")
        
        yield archivo_temporal
        
    finally:
        # Eliminar archivo temporal
        try:
            os.unlink(archivo_temporal)
            print(f"Archivo temporal eliminado: {archivo_temporal}")
        except OSError:
            print(f"No se pudo eliminar el archivo temporal: {archivo_temporal}")

def ejecutar_electre3_desde_bd_flujo_neto(db: Session, escenario_id: int) -> Optional[str]:
    """
    Ejecuta ELECTRE III usando datos directamente de la base de datos
    
    Args:
        db: Sesión de SQLAlchemy
        escenario_id: ID del escenario
        dll_path: Ruta a la DLL de ELECTRE III
        lambda_corte: Valor de corte lambda
        Usando el flujo Neto
    Returns:
        Resultado del análisis ELECTRE III o None si hay error
    """
    try:
        import ctypes
        
        # Cargar la DLL (compatible Windows/Linux)
        dll = cargar_dll_electre()

        dll.ElectreIIIExplotarFlujoNeto.argtypes = [ctypes.c_long, ctypes.c_long, ctypes.c_double, ctypes.c_char_p]
        dll.ElectreIIIExplotarFlujoNeto.restype = ctypes.c_char_p
        # Obtener datos del escenario para contar alternativas y criterios
        datos = obtener_datos_escenario_para_electre(db, escenario_id)
        num_alternativas = len(datos['nombres_alternativas'])
        num_criterios = len(datos['nombres_criterios'])
        print(f"Escenario {escenario_id} tiene {num_alternativas} alternativas y {num_criterios} criterios")
        # Usar archivo temporal desde la BD
        with csv_temporal_electre3_desde_bd(db, escenario_id) as archivo_csv:
            
            print(f"Ejecutando ELECTRE III para escenario {escenario_id} con λ = {datos['corte']}")
            # Leer el contenido del archivo CSV y reemplazar saltos de línea por ':'
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                csv_content = f.read().replace('\n', ':')

            # Llamar a la función DLL pasando la cadena en vez del archivo
            resultado = dll.ElectreIIIExplotarFlujoNeto(
                ctypes.c_long(num_alternativas),
                ctypes.c_long(num_criterios),
                ctypes.c_double(datos['corte']),
                csv_content.encode('utf-8')
            )

            
            if resultado:
                resultado_str = resultado.decode('utf-8')
                print("Resultado ELECTRE III:")
                print(resultado_str)
                resultado_alternativas = interpretar_resultado_flujo_neto(resultado_str)
                print("Alternativas ordenadas por ELECTRE III:")
                print(resultado_alternativas)

                return resultado_alternativas
            else:
                print("La DLL no retornó resultado")
                return None
                
    except Exception as e:
        print(f"Error al ejecutar ELECTRE III desde BD: {e}")
        return None


def ejecutar_electre3_desde_bd_destilacion(db: Session, escenario_id: int,
                              ) -> Optional[str]:
    """
    Ejecuta ELECTRE III usando datos directamente de la base de datos
    
    Args:
        db: Sesión de SQLAlchemy
        escenario_id: ID del escenario
        dll_path: Ruta a la DLL de ELECTRE III
        lambda_corte: Valor de corte lambda
        Usando el flujo Neto
    Returns:
        Resultado del análisis ELECTRE III o None si hay error
    """
    try:
        import ctypes
        
        # Cargar la DLL (compatible Windows/Linux)
        dll = cargar_dll_electre()

        dll.ElectreIIIExplotarDestilacion.argtypes = [ctypes.c_long, ctypes.c_long, ctypes.c_double, ctypes.c_char_p]
        dll.ElectreIIIExplotarDestilacion.restype = ctypes.c_char_p
        # Obtener datos del escenario para contar alternativas y criterios
        datos = obtener_datos_escenario_para_electre(db, escenario_id)
        num_alternativas = len(datos['nombres_alternativas'])
        num_criterios = len(datos['nombres_criterios'])
        print(f"Escenario {escenario_id} tiene {num_alternativas} alternativas y {num_criterios} criterios")
        # Usar archivo temporal desde la BD
        with csv_temporal_electre3_desde_bd(db, escenario_id) as archivo_csv:
            
            print(f"Ejecutando ELECTRE III para escenario {escenario_id} con λ = {datos['corte']}")
            # Leer el contenido del archivo CSV y reemplazar saltos de línea por ':'
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                csv_content = f.read().replace('\n', ':')
            print("CSV que se enviará a la DLL:")
            print(csv_content)
            print("num_alternativas:", num_alternativas)
            print("num_criterios:", num_criterios)
            # Llamar a la función DLL pasando la cadena en vez del archivo
            resultado = dll.ElectreIIIExplotarDestilacion(
                ctypes.c_long(num_alternativas),
                ctypes.c_long(num_criterios),
                ctypes.c_double(datos['corte']),
                csv_content.encode('utf-8')
            )

            
            if resultado:
                resultado_str = resultado.decode('utf-8')
                print("Resultado ELECTRE III:")
                print(resultado_str)
                # Interpretar el resultado
                resultado_alternativas = interpretar_resultado_destilacion(resultado_str)
                print("Alternativas ordenadas por ELECTRE III:")
                print(resultado_alternativas)

                return resultado_alternativas
            else:
                print("La DLL no retornó resultado")
                return None
                
    except Exception as e:
        print(f"Error al ejecutar ELECTRE III desde BD: {e}")
        return None
def analizar_consistencia_datos(db: Session, escenario_id: int) -> Dict:
    """
    Analiza la consistencia de los datos antes de ejecutar ELECTRE III
    
    Args:
        db: Sesión de SQLAlchemy
        escenario_id: ID del escenario
    
    Returns:
        Dict con información sobre la consistencia de los datos
    """
    
    try:
        datos = obtener_datos_escenario_para_electre(db, escenario_id)
        
        # Verificaciones básicas
        num_alternativas = len(datos['nombres_alternativas'])
        num_criterios = len(datos['nombres_criterios'])
        
        # Verificar matriz de decisión
        matriz = datos['matriz_decision']
        
        # Estadísticas por criterio
        stats_criterios = {}
        for i, nombre_criterio in enumerate(datos['nombres_criterios']):
            columna = matriz[:, i]
            stats_criterios[nombre_criterio] = {
                'min': float(np.min(columna)),
                'max': float(np.max(columna)),
                'mean': float(np.mean(columna)),
                'std': float(np.std(columna)),
                'rango': float(np.max(columna) - np.min(columna))
            }
        
        # Verificar umbrales
        umbrales_info = {}
        for i, nombre_criterio in enumerate(datos['nombres_criterios']):
            umbrales_info[nombre_criterio] = {
                'peso': datos['pesos'][i],
                'preferencia': datos['preferencia'][i],
                'indiferencia': datos['indiferencia'][i],
                'veto': datos['veto'][i],
                'direccion': 'beneficio' if datos['direccion'][i] == 1 else 'costo',
                'umbral_coherente': datos['indiferencia'][i] <= datos['preferencia'][i] <= datos['veto'][i]
            }
        
        return {
            'num_alternativas': num_alternativas,
            'num_criterios': num_criterios,
            'dimensiones_matriz': matriz.shape,
            'stats_criterios': stats_criterios,
            'umbrales_info': umbrales_info,
            'datos_completos': True,
            'suma_pesos': sum(datos['pesos'])
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'datos_completos': False
        }

def generar_reporte_escenario(db: Session, escenario_id: int) -> str:

    """
    Genera un reporte detallado del escenario para ELECTRE III
    
    Args:
        db: Sesión de SQLAlchemy
        escenario_id: ID del escenario
    
    Returns:
        String con el reporte formateado
    """
    
    consistencia = analizar_consistencia_datos(db, escenario_id)
    
    if not consistencia['datos_completos']:
        return f"ERROR: {consistencia['error']}"
    
    reporte = []
    reporte.append("=" * 60)
    reporte.append(f"REPORTE ESCENARIO {escenario_id} - ELECTRE III")
    reporte.append("=" * 60)
    
    reporte.append(f"\nDIMENSIONES:")
    reporte.append(f"  • Alternativas: {consistencia['num_alternativas']}")
    reporte.append(f"  • Criterios: {consistencia['num_criterios']}")
    reporte.append(f"  • Suma de pesos: {consistencia['suma_pesos']:.3f}")
    
    reporte.append(f"\nESTADÍSTICAS POR CRITERIO:")
    for criterio, stats in consistencia['stats_criterios'].items():
        reporte.append(f"  {criterio}:")
        reporte.append(f"    - Rango: [{stats['min']:.2f}, {stats['max']:.2f}]")
        reporte.append(f"    - Media: {stats['mean']:.2f} ± {stats['std']:.2f}")
    
    reporte.append(f"\nUMBRALES ELECTRE III:")
    for criterio, info in consistencia['umbrales_info'].items():
        coherente = "✓" if info['umbral_coherente'] else "✗"
        reporte.append(f"  {criterio} ({info['direccion']}) {coherente}:")
        reporte.append(f"    - Peso: {info['peso']:.3f}")
        reporte.append(f"    - Indiferencia: {info['indiferencia']:.2f}")
        reporte.append(f"    - Preferencia: {info['preferencia']:.2f}")
        reporte.append(f"    - Veto: {info['veto']:.2f}")
    
    return "\n".join(reporte)

def ejecutar_electre3_desde_argumentos_flujo_neto(
    alternativas_matriz,
    criterios_nombres,
    pesos,
    preferencia,
    indiferencia,
    veto,
    direccion,
    lambda_corte,
    nombres_alternativas=None
) -> Optional[str]:
    """
    Ejecuta ELECTRE III usando la DLL, recibiendo todos los datos como argumentos.

    Args:
        alternativas_matriz: matriz de alternativas (lista de listas o np.ndarray)
        criterios_nombres: lista de nombres de criterios
        pesos: lista de pesos
        preferencia: lista de umbrales de preferencia
        indiferencia: lista de umbrales de indiferencia
        veto: lista de umbrales de veto
        direccion: lista de dirección (1=beneficio, 0=costo)
        lambda_corte: valor de corte lambda
        nombres_alternativas: lista de nombres de alternativas (opcional)

    Returns:
        Resultado del análisis ELECTRE III o None si hay error
    """
    try:
        import ctypes
        import os

        # Cargar la DLL (compatible Windows/Linux)
        dll = cargar_dll_electre()

        dll.ElectreIIIExplotarFlujoNeto.argtypes = [
            ctypes.c_long, ctypes.c_long, ctypes.c_double, ctypes.c_char_p
        ]
        dll.ElectreIIIExplotarFlujoNeto.restype = ctypes.c_char_p

        num_alternativas = len(alternativas_matriz)
        num_criterios = len(criterios_nombres)
        
        # Crear archivo CSV temporal con los datos recibidos
        with csv_temporal_electre3(
            alternativas_matriz, criterios_nombres, pesos,
            preferencia, indiferencia, veto, direccion, nombres_alternativas
        ) as archivo_csv:

            # Leer el contenido del archivo CSV y reemplazar saltos de línea por ':'
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                csv_content = f.read().replace('\n', ':')

            print("CSV que se enviará a la DLL:")
            print(csv_content)
            print("num_alternativas:", num_alternativas)
            print("num_criterios:", num_criterios)
            # Llamar a la función DLL pasando la cadena en vez del archivo
            resultado = dll.ElectreIIIExplotarFlujoNeto(
                ctypes.c_long(num_alternativas),
                ctypes.c_long(num_criterios),
                ctypes.c_double(lambda_corte),
                csv_content.encode('utf-8')
            )

            if resultado:
                resultado_str = resultado.decode('utf-8')
                resultado_alternativas = interpretar_resultado_flujo_neto(resultado_str)
                print("Alternativas ordenadas por ELECTRE III:")
                print(resultado_alternativas)

                return resultado_alternativas
            else:
                print("La DLL no retornó resultado")
                return None

    except Exception as e:
        print(f"Error al ejecutar ELECTRE III desde argumentos: {e}")
        return None
    
def ejecutar_electre3_desde_argumentos_destilacion(
    alternativas_matriz,
    criterios_nombres,
    pesos,
    preferencia,
    indiferencia,
    veto,
    direccion,
    lambda_corte,
    nombres_alternativas=None
) -> Optional[str]:
    """
    Ejecuta ELECTRE III usando la DLL, recibiendo todos los datos como argumentos.

    Args:
        alternativas_matriz: matriz de alternativas (lista de listas o np.ndarray)
        criterios_nombres: lista de nombres de criterios
        pesos: lista de pesos
        preferencia: lista de umbrales de preferencia
        indiferencia: lista de umbrales de indiferencia
        veto: lista de umbrales de veto
        direccion: lista de dirección (1=beneficio, 0=costo)
        lambda_corte: valor de corte lambda
        nombres_alternativas: lista de nombres de alternativas (opcional)

    Returns:
        Resultado del análisis ELECTRE III o None si hay error
    """
    try:
        import ctypes
        import os

        # Cargar la DLL (compatible Windows/Linux)
        dll = cargar_dll_electre()

        dll.ElectreIIIExplotarDestilacion.argtypes = [
            ctypes.c_long, ctypes.c_long, ctypes.c_double, ctypes.c_char_p
        ]
        dll.ElectreIIIExplotarDestilacion.restype = ctypes.c_char_p

        num_alternativas = len(alternativas_matriz)
        num_criterios = len(criterios_nombres)
        print (f"Ejecutando ELECTRE III con {num_alternativas} alternativas y {num_criterios} criterios")

        # Crear archivo CSV temporal con los datos recibidos
        with csv_temporal_electre3(
            alternativas_matriz, criterios_nombres, pesos,
            preferencia, indiferencia, veto, direccion, nombres_alternativas
        ) as archivo_csv:

            # Leer el contenido del archivo CSV y reemplazar saltos de línea por ':'
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                csv_content = f.read().replace('\n', ':')
            print("CSV que se enviará a la DLL:")
            print(csv_content)
            print("num_alternativas:", num_alternativas)
            print("num_criterios:", num_criterios)
            # Llamar a la función DLL pasando la cadena en vez del archivo
            resultado = dll.ElectreIIIExplotarDestilacion(
                ctypes.c_long(num_alternativas),
                ctypes.c_long(num_criterios),
                ctypes.c_double(lambda_corte),
                csv_content.encode('utf-8')
            )

            if resultado:
                resultado_str = resultado.decode('utf-8')
                resultado_alternativas = interpretar_resultado_destilacion(resultado_str)
                print("Alternativas ordenadas por ELECTRE III:")
                print(resultado_alternativas)

                return resultado_alternativas
            else:
                print("La DLL no retornó resultado")
                return None

    except Exception as e:
        print(f"Error al ejecutar ELECTRE III desde argumentos: {e}")
        return None

def ejecutar_electre3_desde_csv_destilacion(ruta_csv: str, lambda_corte: float = -1) -> Optional[str]:
    """
    Ejecuta ELECTRE III método de destilación leyendo directamente un archivo CSV.

    Args:
        ruta_csv: Ruta al archivo CSV con formato ELECTRE III
        lambda_corte: Valor de corte lambda (por defecto -1)

    Returns:
        Lista de alternativas ordenadas según destilación o None si hay error
    """
    try:
        import ctypes
        import os

        # Leer el archivo CSV con el formato correcto (separador de comas, punto y coma al final)
        # Primero leer líneas manualmente para procesarlas correctamente
        with open(ruta_csv, 'r', encoding='utf-8') as f:
            lineas = [linea.strip().rstrip(';') for linea in f.readlines() if linea.strip()]
        
        # Parsear cada línea dividiendo por comas
        matriz_datos = []
        for linea in lineas:
            if linea:
                valores = [val.strip() for val in linea.split(',')]
                matriz_datos.append(valores)
        
        # Convertir a numpy array para facilitar el manejo
        matriz = np.array(matriz_datos, dtype=object)
        
        # Identificar filas especiales (W, P, I, Q, V, D)
        filas_especiales = {}
        indices_alternativas = []
        
        for i, fila in enumerate(matriz):
            primera_col = str(fila[0]).strip()
            if primera_col in ['W', 'P', 'I', 'Q', 'V', 'D']:
                filas_especiales[primera_col] = i
            elif primera_col != '-':  # Ignorar la fila de encabezado
                indices_alternativas.append(i)
        
        # Extraer datos
        num_alternativas = len(indices_alternativas)
        num_criterios = len(matriz[0]) - 1  # -1 porque la primera columna son nombres
        
        # Nombres de alternativas
        nombres_alternativas = [str(matriz[i][0]).strip() for i in indices_alternativas]
        
        # Nombres de criterios (de la primera fila con encabezado '-')
        fila_encabezado = None
        for i, fila in enumerate(matriz):
            if str(fila[0]).strip() == '-':
                fila_encabezado = i
                break
        
        if fila_encabezado is not None and len(matriz[fila_encabezado]) > 1:
            criterios_nombres = [str(matriz[fila_encabezado][j]).strip() for j in range(1, len(matriz[fila_encabezado]))]
        else:
            criterios_nombres = [f"C{j}" for j in range(num_criterios)]
        
        # Matriz de alternativas
        alternativas_matriz = []
        for i in indices_alternativas:
            fila_valores = []
            for j in range(1, num_criterios + 1):
                valor = matriz[i][j]
                # Convertir a float, manejando posibles NaN
                try:
                    fila_valores.append(float(valor))
                except (ValueError, TypeError):
                    fila_valores.append(0.0)
            alternativas_matriz.append(fila_valores)
        
        # Extraer parámetros de filas especiales
        def extraer_fila_parametros(letra):
            if letra in filas_especiales:
                idx = filas_especiales[letra]
                parametros = []
                for j in range(1, num_criterios + 1):
                    try:
                        parametros.append(float(matriz[idx][j]))
                    except (ValueError, TypeError, IndexError):
                        parametros.append(0.0)
                return parametros
            else:
                return [0.0] * num_criterios
        
        pesos = extraer_fila_parametros('W')
        preferencia = extraer_fila_parametros('P')
        # Intentar 'I' primero, luego 'Q' si no existe
        indiferencia = extraer_fila_parametros('I') if 'I' in filas_especiales else extraer_fila_parametros('Q')
        veto = extraer_fila_parametros('V')
        direccion = extraer_fila_parametros('D')
        
        # Convertir direcciones a enteros
        direccion = [int(d) for d in direccion]
        
        print(f"CSV procesado: {num_alternativas} alternativas, {num_criterios} criterios")
        print(f"Alternativas: {nombres_alternativas}")
        print(f"Criterios: {criterios_nombres}")
        
        # Cargar la DLL (compatible Windows/Linux)
        dll = cargar_dll_electre()

        dll.ElectreIIIExplotarDestilacion.argtypes = [
            ctypes.c_long, ctypes.c_long, ctypes.c_double, ctypes.c_char_p
        ]
        dll.ElectreIIIExplotarDestilacion.restype = ctypes.c_char_p

        # Crear archivo CSV temporal con formato correcto
        with csv_temporal_electre3(
            alternativas_matriz, criterios_nombres, pesos,
            preferencia, indiferencia, veto, direccion, nombres_alternativas
        ) as archivo_csv:

            # Leer el contenido del archivo CSV y reemplazar saltos de línea por ':'
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                csv_content = f.read().replace('\n', ':')

        # Ejecutar FUERA del context manager para evitar que se elimine el archivo antes de tiempo
        print(f"Ejecutando ELECTRE III Destilación con λ = {lambda_corte}")
        print(f"Contenido CSV a enviar: {csv_content[:200]}...")  # Mostrar primeros 200 caracteres
        
        # Llamar a la función DLL
        resultado = dll.ElectreIIIExplotarDestilacion(
            ctypes.c_long(num_alternativas),
            ctypes.c_long(num_criterios),
            ctypes.c_double(lambda_corte),
            csv_content.encode('utf-8')
        )

        if resultado:
            resultado_str = resultado.decode('utf-8')
            print("Resultado ELECTRE III (Destilación):")
            print(resultado_str)
            resultado_alternativas = interpretar_resultado_destilacion(resultado_str)
            print("Alternativas ordenadas por Destilación:")
            for idx, alt in enumerate(resultado_alternativas, 1):
                print(f"  {idx}. {alt}")

            return resultado_alternativas
        else:
            print("La DLL no retornó resultado")
            return None

    except Exception as e:
        print(f"Error al ejecutar ELECTRE III desde CSV (Destilación): {e}")
        import traceback
        traceback.print_exc()
        return None

def ejecutar_electre3_desde_csv_flujo_neto(ruta_csv: str, lambda_corte: float = -1) -> Optional[str]:
    """
    Ejecuta ELECTRE III método de flujo neto leyendo directamente un archivo CSV.

    Args:
        ruta_csv: Ruta al archivo CSV con formato ELECTRE III
        lambda_corte: Valor de corte lambda (por defecto -1)

    Returns:
        Lista de alternativas ordenadas según flujo neto o None si hay error
    """
    try:
        import ctypes
        import os

        # Leer el archivo CSV con el formato correcto (separador de comas, punto y coma al final)
        # Primero leer líneas manualmente para procesarlas correctamente
        with open(ruta_csv, 'r', encoding='utf-8') as f:
            lineas = [linea.strip().rstrip(';') for linea in f.readlines() if linea.strip()]
        
        # Parsear cada línea dividiendo por comas
        matriz_datos = []
        for linea in lineas:
            if linea:
                valores = [val.strip() for val in linea.split(',')]
                matriz_datos.append(valores)
        
        # Convertir a numpy array para facilitar el manejo
        matriz = np.array(matriz_datos, dtype=object)
        
        # Identificar filas especiales (W, P, I, Q, V, D)
        filas_especiales = {}
        indices_alternativas = []
        
        for i, fila in enumerate(matriz):
            primera_col = str(fila[0]).strip()
            if primera_col in ['W', 'P', 'I', 'Q', 'V', 'D']:
                filas_especiales[primera_col] = i
            elif primera_col != '-':  # Ignorar la fila de encabezado
                indices_alternativas.append(i)
        
        # Extraer datos
        num_alternativas = len(indices_alternativas)
        num_criterios = len(matriz[0]) - 1  # -1 porque la primera columna son nombres
        
        # Nombres de alternativas
        nombres_alternativas = [str(matriz[i][0]).strip() for i in indices_alternativas]
        
        # Nombres de criterios (de la primera fila con encabezado '-')
        fila_encabezado = None
        for i, fila in enumerate(matriz):
            if str(fila[0]).strip() == '-':
                fila_encabezado = i
                break
        
        if fila_encabezado is not None and len(matriz[fila_encabezado]) > 1:
            criterios_nombres = [str(matriz[fila_encabezado][j]).strip() for j in range(1, len(matriz[fila_encabezado]))]
        else:
            criterios_nombres = [f"C{j}" for j in range(num_criterios)]
        
        # Matriz de alternativas
        alternativas_matriz = []
        for i in indices_alternativas:
            fila_valores = []
            for j in range(1, num_criterios + 1):
                valor = matriz[i][j]
                # Convertir a float, manejando posibles NaN
                try:
                    fila_valores.append(float(valor))
                except (ValueError, TypeError):
                    fila_valores.append(0.0)
            alternativas_matriz.append(fila_valores)
        
        # Extraer parámetros de filas especiales
        def extraer_fila_parametros(letra):
            if letra in filas_especiales:
                idx = filas_especiales[letra]
                parametros = []
                for j in range(1, num_criterios + 1):
                    try:
                        parametros.append(float(matriz[idx][j]))
                    except (ValueError, TypeError, IndexError):
                        parametros.append(0.0)
                return parametros
            else:
                return [0.0] * num_criterios
        
        pesos = extraer_fila_parametros('W')
        preferencia = extraer_fila_parametros('P')
        # Intentar 'I' primero, luego 'Q' si no existe
        indiferencia = extraer_fila_parametros('I') if 'I' in filas_especiales else extraer_fila_parametros('Q')
        veto = extraer_fila_parametros('V')
        direccion = extraer_fila_parametros('D')
        
        # Convertir direcciones a enteros
        direccion = [int(d) for d in direccion]
        
        print(f"CSV procesado: {num_alternativas} alternativas, {num_criterios} criterios")
        print(f"Alternativas: {nombres_alternativas}")
        print(f"Criterios: {criterios_nombres}")
        
        # Cargar la DLL (compatible Windows/Linux)
        dll = cargar_dll_electre()

        dll.ElectreIIIExplotarFlujoNeto.argtypes = [
            ctypes.c_long, ctypes.c_long, ctypes.c_double, ctypes.c_char_p
        ]
        dll.ElectreIIIExplotarFlujoNeto.restype = ctypes.c_char_p

        # Crear archivo CSV temporal con formato correcto
        with csv_temporal_electre3(
            alternativas_matriz, criterios_nombres, pesos,
            preferencia, indiferencia, veto, direccion, nombres_alternativas
        ) as archivo_csv:

            # Leer el contenido del archivo CSV y reemplazar saltos de línea por ':'
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                csv_content = f.read().replace('\n', ':')

        # Ejecutar FUERA del context manager para evitar que se elimine el archivo antes de tiempo
        print(f"Ejecutando ELECTRE III Flujo Neto con λ = {lambda_corte}")
        print(f"Contenido CSV a enviar: {csv_content[:200]}...")  # Mostrar primeros 200 caracteres
        
        # Llamar a la función DLL
        resultado = dll.ElectreIIIExplotarFlujoNeto(
            ctypes.c_long(num_alternativas),
            ctypes.c_long(num_criterios),
            ctypes.c_double(lambda_corte),
            csv_content.encode('utf-8')
        )

        if resultado:
            resultado_str = resultado.decode('utf-8')
            print("Resultado ELECTRE III (Flujo Neto):")
            print(resultado_str)
            resultado_alternativas = interpretar_resultado_flujo_neto(resultado_str)
            print("Alternativas ordenadas por Flujo Neto:")
            for idx, alt in enumerate(resultado_alternativas, 1):
                print(f"  {idx}. {alt}")

            return resultado_alternativas
        else:
            print("La DLL no retornó resultado")
            return None

    except Exception as e:
        print(f"Error al ejecutar ELECTRE III desde CSV (Flujo Neto): {e}")
        import traceback
        traceback.print_exc()
        return None

