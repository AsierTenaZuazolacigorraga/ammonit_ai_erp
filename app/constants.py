import json
import logging

# Control flags
IS_EVALUATION = False
IS_EVALUATION_REVIEW = False
IS_EXAMS = True
IS_CORRECTIONS = True

# Inputs
ROOT_FOLDER = "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production"
STUDENTS_PDF_FOLDER = f"{ROOT_FOLDER}/students_pdf"
STUDENTS_PDF_FILE = f"{STUDENTS_PDF_FOLDER}/merged.pdf"
STUDENTS_PNG_FOLDER = f"{ROOT_FOLDER}/students_png"
PROFESSOR_PDF_FOLDER = f"{ROOT_FOLDER}/professor_pdf"
PROFESSOR_PDF_FILE = f"{PROFESSOR_PDF_FOLDER}/merged.pdf"
PROFESSOR_PNG_FOLDER = f"{ROOT_FOLDER}/professor_png"

# Outputs
CORRECTIONS_RESPONSE = f"{ROOT_FOLDER}/correction_response.pkl"
CORRECTIONS_RESPONSE_RAW = f"{ROOT_FOLDER}/correction_response.txt"
CORRECTIONS_REPORT_FILE = f"{ROOT_FOLDER}/correction_report.xlsx"
EVAL_RESPONSE = f"{ROOT_FOLDER}/eval_response.pkl"
EVAL_RESPONSE_RAW = f"{ROOT_FOLDER}/eval_response.txt"
EXAMS_RESPONSE = f"{ROOT_FOLDER}/exams_response.pkl"
EXAMS_RESPONSE_RAW = f"{ROOT_FOLDER}/exams_response.txt"

# Constants

EVALUATION_EXAMS_FOCUS = """
- En el ejercicio 1, podrás encontrar los huecos de "Cambios" y "Físicos". Aunque estén muy juntos, cada uno representa un hueco diferenciado. No los entiendas como un hueco de 2 palabras.
  Son 2 huecos diferentes de 1 palabra. Por lo tanto, a la hora de reportar, deja claro que son 2 respuestas diferentes. Lo mismo aplica para "Cambios" y "Químicos"
- En el ejercicio 3, sucede algo similar en el apartado e) con "Fusión" y "Ebullición", son 2 huecos. Puedes representarlos como 2 huecos e) distintos para seguir con la estructura de reporte
- Las respuestas pueden aparecer en euskera, castellano o ingles
- Las respuestas pueden contener fallos ortograficos, mantén la ortografía tal cual se muestra en el examen (sin realizar correcciones)
"""

EVALUATION_SYSTEM = f"""
Eres el asistente de un profesor. Tu tarea es analizar analizar el examen que se te entregue,
y devolver la información que se te pida.

El profesor, ha realizado estos pasos:
1. Ha impreso el cuerpo del examen (un .pdf con sus enunciados, instrucciones ...)
2. Ha resuelto los ejercicios sobre esos papeles impresos (escribiendo las respuestas a mano, con lápiz o bolígrafo)
3. Una vez terminado el examen, ha escaneado todos los papeles y ha generado unos archivos .pdf
4. Finalmente, ha convertido esos archivos .pdf a formato .png.

En cualquiera de las consultas que te realice el usuario:
a) En todos los pasos mencionados, utiliza técnicas de OCR o cualquier otra técnica avanzada
b) Realiza las transcripciones en formato texto
c) Si aparece cualquier fórmula matemática, o diagrama químico/físico, represéntalo en texto de manera adecuada
"""

LECTURE = '"Asignatura": Identifica el nombre de la asignatura'
PROFESSOR = '"Profesor": Identifica el nombre, apellidos, DNI ... del alumno que realizó el examen'
ID = '"Id": Identifica el id del ejercicio'
MAX_MARK = '"Puntuación Max": Identifica la puntuación maxima que pueda obtenerse en el ejercicio'
TYPE = '"Tipo": Identifica el tipo de ejercicio'

EVALUATION_USER = f"""
Te comparto los archivos .png, sigue estos pasos:
1. Procesa todos los contenidos que aparecen en la imagen
2. Presta especial atención, e identifica con precisión, a aquellos contenidos que se mencionan en la "estructura de reporte" que se muestra al final de este mensaje
3. Prepara el reporte
4. Devuelve el reporte

La estructura de reporte ha de ser esta:

<Profesor>
{PROFESSOR}
<\Profesor>

<Asignatura>
{LECTURE}
<\Asignatura>

<Ejercicios>
Itera sobre los ejercicios presentes en el examen, y para cada uno incluye estos campos:

<Id>
{ID}
<\Id>

<Puntuación Max>
{MAX_MARK}
<\Puntuación Max>

<Tipo>
{TYPE}
<\Tipo>

<Enunciado>
Extrae con precisión los contenidos presentados en el enunciado:
    - El enunciado es el texto que pertenece al .pdf originario del examen, escrito a máquina
<\Enunciado>

<Criterios>
Identifica los criterios de evaluación que aplica el profesor y también el desglose de puntuación del ejercicio (con máxima granularidad y detalle): 
    - Puedes partir de las respuestas y/o las anotaciones del profesor, deducir como ha de realizarse la corrección, y transcribir esa información
    - La idea es que puedas explicar a alguien cómo se corregirá el ejercicio
<\Criterios>

<Respuestas>
Extrae con precisión las respuestas proporcionadas por el profesor:  
    - Las respuestas son las que aparecerán escritas a mano (por lo tanto, no incluyas contenidos del enunciado o escritos a máquina aquí, solamente contenidos manuscritos)
    - Las respuestas del ejercicio pueden estar dispersas en distintas partes, por lo que busca en todo el examen
    - Las respuestas pueden estar estructuradas siguiendo patrones como 1, 2, 3, ... a), b), c), ..., identifica esa estructura y utilízala en la transcripción
    - Ten especial cuidado con estos puntos:
{EVALUATION_EXAMS_FOCUS}
<\Respuestas>

<\Ejercicios>
"""

EXAMS_SYSTEM = f"""
Eres el asistente de un profesor. Tu tarea es analizar analizar los exámenes que se te entreguen,
y devolver la información que se te pida.

El profesor, ha realizado estos pasos:
1. Ha impreso el cuerpo del examen (un .pdf con sus enunciados, instrucciones ...)
2. Ha entregado los papeles impresos al alumno
3. Ha dejado que el alumno resuelva los ejercicios sobre esos papeles impresos (escribiendo las respuestas a mano, con lápiz o bolígrafo)
4. Una vez terminado el examen, ha escaneado todos los papeles y ha generado unos archivos .pdf
5. Finalmente, ha convertido esos archivos .pdf a formato .png.

En cualquiera de las consultas que te realice el usuario:
a) En todos los pasos mencionados, utiliza técnicas de OCR o cualquier otra técnica avanzada
b) Realiza las transcripciones en formato texto
c) Si aparece cualquier fórmula matemática, o diagrama químico/físico, represéntalo en texto de manera adecuada
"""

STUDENT = '"Estudiante": Identifica el nombre del alumno que realizó el examen'
ID = '"Id": Identifica el id del ejercicio'

EXAMS_USER = f"""
Te comparto los archivos .png, sigue estos pasos:
1. Procesa todos los contenidos que aparecen en la imagen
2. Presta especial atención, e identifica con precisión, a aquellos contenidos que se mencionan en la "estructura de reporte" que se muestra al final de este mensaje
3. Prepara el reporte
4. Devuelve el reporte

La estructura de reporte ha de ser esta:

<Estudiante>
{STUDENT}
<\Estudiante>

<Ejercicios>
Itera sobre los ejercicios presentes en el examen, y para cada uno incluye estos campos:

<Id>
{ID}
<\Id>

<Respuestas>
Extrae con precisión las respuestas proporcionadas por el alumno:  
    - Las respuestas son las que aparecerán escritas a mano (por lo tanto, no incluyas contenidos del enunciado o escritos a máquina aquí, solamente contenidos manuscritos)
    - Las respuestas del ejercicio pueden estar dispersas en distintas partes, por lo que busca en todo el examen
    - Las respuestas pueden estar estructuradas siguiendo patrones como 1, 2, 3, ... a), b), c), ..., identifica esa estructura y utilízala en la transcripción
    - Si el alumno no ha respondido a parte o totalidad de una pregunta, representa esa ausencia de respuesta como "____"
    - Ten especial cuidado con estos puntos:
{EVALUATION_EXAMS_FOCUS}
<\Respuestas>

<\Ejercicios>
"""

CORRECTIONS_SYSTEM = f"""
Eres el asistente de un profesor. Tu tarea es analizar corregir los exámenes de los alumnos,
basándote en la información que se muestra en un examen base que ha elaborado el profesor
(donde podrás consultar las respuestas esperadas, las puntuaciones máximas posibles, los criterios de evaluación y el desglose de puntuación).

El profesor, ha realizado estos pasos:
1. Ha impreso el cuerpo del examen (un .pdf con sus enunciados, instrucciones ...)
2. Ha resuelto los ejercicios sobre esos papeles impresos (escribiendo las respuestas a mano, con lápiz o bolígrafo)
3. Una vez terminado el examen, ha escaneado todos los papeles y ha generado unos archivos .pdf
4. Ha convertido esos archivos .pdf a formato .png.
5. Finalmente, ha transcrito esos .png a text mediante uso de LLMs

El profesor, también ha realizado estos pasos:
1. Ha impreso el cuerpo del examen (un .pdf con sus enunciados, instrucciones ...)
2. Ha entregado los papeles impresos al alumno
3. Ha dejado que el alumno resuelva los ejercicios sobre esos papeles impresos (escribiendo las respuestas a mano, con lápiz o bolígrafo)
4. Una vez terminado el examen, ha escaneado todos los papeles y ha generado unos archivos .pdf
5. Ha convertido esos archivos .pdf a formato .png.
6. Finalmente, ha transcrito esos .png a text mediante uso de LLMs
"""

CORRECTIONS_FOCUS = """
- Las respuestas pueden aparecer en euskera, castellano o ingles. Las respuestas en distintos idiomas se considerarán válidas si están bien
- Las respuestas pueden contener fallos ortograficos. Al tratarse de un examen de ciencias, no se puntuarán negativamente los fallos ortográficos
"""

LONG_JUST = """"Corrección Detallada": Corrige el ejercicio de manera detallada:
    - Identifica con precisión las respuestas del alumno
    - Identifica con precisión todas las respuestas del profesor
    - Compara ambas respuestas, y con detalle, corrígelas acorde a los criterios de evaluación y desglose de puntuación
    - Calcula/prepara una puntuación para el ejercicio. Presta vital atención (asegúrate de realizar bien esta tarea), porque la nota del alumno dependerá de el y es muy importante
    - Elabora un reporte donde detallas la corrección"""
SHORT_JUST = """"Corrección Resumida": Resume la corrección detallada en una simple frase, la cual se usará más adelante para generar un reporte resumido"""
MARK = """"Puntuación": Nota que le asignas al alumno después de la corrección correspondiente. Aquí, reporta solamente la nota (sin ningún texto adicional)"""

CORRECTIONS_USER = f"""
Te comparto los archivos los textos transcritos, tanto del examen base del profesor, como el examen del alumno. Sigue estos pasos:
1. Procesa todos los contenidos que se te compartan
2. Corrige el examen del alumno. Para ello, presta especial atención, e identifica con precisión aquellos conetidos que se mencionan en la "estructura de reporte" que se muestra al final de este mensaje
3. Prepara el reporte
4. Devuelve el reporte

<Examen del profesor>
{{PROFESSOR_EXAM}}
<\Examen del profesor>

<Examen del alumno>
{{STUDENT_EXAM}}
<\Examen del alumno>

La estructura de reporte ha de ser esta:

<Ejercicios>
Itera sobre los ejercicios presentes en el examen, y para cada uno incluye estos campos:

<Id>
{ID}
<\Id>

<Corrección Detallada>
{LONG_JUST}
    - Ten especial cuidado con estos puntos:
{CORRECTIONS_FOCUS}
<\Corrección Detallada>

<Corrección Resuminda>
{SHORT_JUST}
<\Corrección Resuminda>

<Puntuación>
{MARK}
<\Puntuación>

<\Ejercicios>
"""

STRUCTURER_SYSTEM = """
Eres un extractor y formateador de texto. Tienes que seguir estos pasos:
1. Leer el texto base que proporciona el usuario
2. Leer el esquema json que proporciona el usuario
3. Extraer del texto base aquellos campos que aparezcan en el esquema json. Los campos que no aparezcan, déjalos vacíos
4. Responder con el esquema json bien rellenado
Evita a toda costa excepciones en la petición.
"""

STRUCTURER_USER = """
Este es el texto base: \n\n{base_text}\n\nEste es el esquema json que se retrae mediante BaseModel.model_json_schema()\n {base_json_schema}"
"""

# Cost data is given in this magnitudes
# - input [$ / 1M input tokens]
# - input_cached [$ / 1M input tokens]
# - output [$ / 1M input tokens]
COSTS = {
    "gpt-4o": {
        "input": 2.50,
        "input_cached": 1.25,
        "output": 10.00,
    },
    "llama-3.2-90b-text-preview": {
        "input": 0,
        "output": 0,
    },
    "claude-3-5-sonnet-20241022": {
        "input": 3,
        "output": 15,
    },
}

# System things
LOGGER_NAME = "logger"
LOGGER_FOLDER = "/home/atena/my_projects/proff_ai/app/logs/"
LOGGER_FILE = "app.log"
LOGGER_MAX_BYTES = 5 * 1024 * 1024
LOGGER_BACKUP_COUNT = 5
LOGGER_LEVEL = logging.INFO
LOGGER_DATE_FMT = "%Y-%m-%d %H:%M:%S"
LOGGER_LINE_FMT = "%(asctime)s - %(levelname)s - %(message)s"
LOGGER_FORMATTER = logging.Formatter(LOGGER_LINE_FMT, LOGGER_DATE_FMT)
