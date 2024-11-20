def call_openai_and_groq(
    openai_client: OpenAI,
    groq_client: Groq,
    openai_system_message: str,
    openai_user_png_files: List[str],
    structuring_instructions: str,
    structuring_base_model: Union[Exam, ExamEval],
) -> Tuple[Union[Exam, ExamEval], str]:

    logging.info("Consulting openai ...")
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": openai_system_message,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{e}"},
                    }
                    for e in pngs_2_base64(openai_user_png_files)
                ],
            },
        ],
        temperature=0,
        max_tokens=2048,
        top_p=0,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"},
    )
    raw_response = response.choices[0].message.content

    logging.info("Consulting groq for structured output ...")
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.2-90b-text-preview",
            messages=[
                {
                    "role": "system",
                    "content": structuring_instructions.format(
                        json_schema=json.dumps(
                            structuring_base_model.model_json_schema(), indent=2
                        )
                    ),
                },
                {"role": "user", "content": raw_response},
            ],
            temperature=0,
            max_tokens=1024,
            top_p=0,
            stream=False,
            response_format={"type": "json_object"},
            stop=None,
        )
        response = structuring_base_model.model_validate(
            json.loads(completion.choices[0].message.content)
        )
    except Exception as e:
        logging.error(e)
        response = {}
    return (
        response,
        raw_response,
    )


# EVALUATOR_INSTRUCTIONS = f"""
# Eres el asistente de un profesor. Tu tarea es analizar un examen y reportar los criterios de evaluación que establece el profesor.
# El usuario puede realizarte 2 tipos de consultas.
# - "Consulta tipo A"
# 	1. El usuario te entregará un examen escaneado (en formato .png), resuelto a mano por el propio profesor
# 	2. Tu has de leer y guardar los contenidos
# 	3. Tu has de identificar y devolver:
# 		- {LECTURE}
# 		- {PROFESSOR}
# 		- {IDS}
# - "Consulta tipo B"
# 	1. El usuario te preguntará sobre un ejercicio en concreto
# 	2. Tu has de identificar, leer, entender y guardar las respuestas que da el profesor para ese ejercicio. Las respuestas aparecerán manuscritas a mano.
#        Las respuestas pueden presentarse en varios formatos (dependiendo del tipo de ejercicio): rellena el hueco, identifica la palabra correcta, formulas, diagramas...
#        Tómate tu tiempo en este paso, es muy importante
# 	3. Tu has devolver:
# 		- {MAX_MARK}
#         - Las respuestas concretas (lo hayas identificado en el paso 2.)
# 		- El criterio de evaluación
# 		- El desglose preciso de la puntuación
#         - No devuelvas texto o información que aparezca en el enunciado, céntrate solamente en los puntos que te he mencionado y que has de devolver
# """

# EVAL_CRITERIA_INSTRUCTIONS = f"""
# Eres el asistente de un profesor, y tu tarea es retraer de un examen elaborado por el propio profesor los criterios de evaluación. Luego, estos criterios de evaluación se utilizarán para poder corregir los exámenes de los alumnos.
# Sigue estos pasos:
# 1. Lee el examen y devuelve la siguiente información genérica:
# - {LECTURE}
# - {PROFESSOR}
# 2. Itera sobre cada ejercicio, y para cada uno sigue estos pasos:
# 	2.1. Lee el enunciado del ejercicio y devuelve esta información:
# 		- El identificador o número del ejercicio
# 		- Puntuación máxima que sea posible obtener en el ejercicio
# 	2.2. Lee con mucho detalle y detenimiento las respuestas que establece el profesor para el ejercicio. Devuelve esta información:
#         - La respuesta correcta (manuscrita por el profesor) al completo
# 		- El desglose de la puntuación
#         - El criterio de evaluación
# """


# CORRECTOR_INSTRUCTIONS = f"""
# Eres el asistente de un profesor. Tu tarea es corregir los exámenes de los alumnos.
# El usuario puede realizarte 3 tipos de consultas.
# - "Consulta tipo A"
#     1. El usuario te entregará texto extenso, el cual representa los criterios de evaluación del examen (incluyendo todos los ejercicios)
#     2. Tu has de leer y guardar los contenidos
# - "Consulta tipo B"
#     1. El usuario te entregará un examen escaneado (en formato .png), resuelto a mano por el alumno
#     2. Tu has de leer y guardar los contenidos
#     3. Tu has de identificar y devolver:
#         - {STUDENT}
# - "Consulta tipo C"
#     1. El usuario te preguntará sobre un ejercicio en concreto
#     2. Tu has de identificar los criterios de evaluación de ese ejercicio
#     3. Tu has de identificar, leer, entender y guardar las respuestas que da el alumno para ese ejercicio. Las respuestas aparecerán manuscritas a mano.
#        Las respuestas pueden presentarse en varios formatos (dependiendo del tipo de ejercicio): rellena el hueco, identifica la palabra correcta, formulas, diagramas...
#        Los criterios de evaluación pueden ayudarte a identificar el tipo de ejercicio y por lo tanto el tipo de respuesta.
#        Importante, podría ocurrir que el alumno no haya respondido a ciertas partes (o a la totalidad) del ejercicio. Si es así, tienes que identificar con precisión las partes que no tengan respuesta.
#        Usaremos toda la información que extraigamos en este paso para poder corregir el ejercicio. Tómate tu tiempo, es muy importante
#     4. Tu has de corregir las respuestas (identificadas en el paso 3.), siguiendo a raja-tabla los criterios de evaluación (indentificados en el paso 2.)
#     5. Tu has devolver:
#         - {CURR_MARK}
#         - {SHORT_CORRECTION}
#         - {LONG_CORRECTION}
#         - No devuelvas texto o información que aparezca en el enunciado, céntrate solamente en los puntos que te he mencionado y que has de devolver
# """

# CORRECTION_INSTRUCTIONS = f"""
# Eres el asistente de un profesor, y tu tarea es corregir los exámenes de los alumnos.
# Estos son los criterios de evaluación del examen, que ha definido el profesor, y que has de respetar a raja-tabla durante tu corrección:
# {{eval_criteria}}
# Sigue estos pasos:
# 1. Lee el examen que se te entregue, y devuelve:
# - {STUDENT}
# 2. Itera sobre cada ejercicio. Para cada uno sigue estos pasos:
#     2.1. Lee la respuesta del alumno. Identifica con extremo detalle la información. Tómate tu tiempo. Es importante tener claro que es lo que ha respondido el alumno. Si el alumno no proporciona respuestas, identifícalo también para que no cause confusión
#     2.2. Corrige la respuesta acorde a los criterios de evaluación
#     2.3. Devuelve la puntuación y una justificación de corrección
# """

LECTURE = "La asignatura"
PROFESSOR = "Nombre, apellidos, DNI ... del profesor"
IDS = "Cantidad de total de ejercicios"
MAX_MARK = "Puntuación máxima que sea posible obtener"

f"""
Eres el asistente de un profesor. Tu tarea es analizar analizar los exámenes que se te entreguen,
y devolver la información que se te pida.

El profesor, ha realizado estos pasos:
1. Ha impreso el cuerpo del examen (un .pdf con sus enunciados, instrucciones ...)
2. Ha resuelto los ejercicios sobre esos papeles impresos (escribiendo las respuestas a mano, con lápiz o bolígrafo)
3. Una vez terminado el examen, ha escaneado todos los papeles y ha generado unos archivos .pdf
4. Finalmente, ha convertido esos archivos .pdf a formato .png.

El profesor te compartirá esos archivos .png, y entonces sigue estos pasos:

1. Itera sobre cada ejercicio, y para cada uno sigue estos pasos:
    1.1. "Id": Identifica el id del ejercicio
    1.2. "Tipo": Identifica el tipo de ejercicio:
         - Rellena el hueco
         - Escribe una definición
         - Identifica la palabra correcta
         - Escribe un diagrama
         - ...
    1.3. "Max": Identifica la puntuación máxima que pueda obtenerse en el ejercicio
    1.4. "Enunciado": Identifica el enunciado y el texto originarios del examen (el texto que pertenece al .pdf originario del examen).
         Asegúrate de incluir solo el contenido que aparece escrito a máquina 
    1.5. "Respuestas": Identifica las respuestas proporcionadas por el profesor, que aparecerán escritas a mano (mediante lápiz o bolígrafo)
         Asegúrate de incluir solo el contenido que aparece manuscrito
    1.6. "Criterios": Entiende los criterios de evaluación y el desglose de puntuación del ejercicio, a partir de las anotaciones del profesor.
         Añade las explicaciones oportunas si es necesario.
         Realiza esta tarea con la máxima exactitud, precisión y detalle.
    1.7. Transcribe todo lo identificado

Notas:
a) En todos los pasos mencionados, utiliza técnicas de OCR o cualquier otra técnica avanzada
b) Realiza las transcripciones en formato markdown
c) La respuestas se dan cerca del mismo ejercicio (caso más común), pero también puede darse en otra página distinta (caso menos común)
"""

f"""
```markdown
### Ejercicio 1

- **Id**: 1
- **Tipo**: Rellena el hueco
- **Max**: 4,5 puntos
- **Enunciado**: 
  ```
  La naturaleza y el mundo están en continuo ________. Todos los días podemos ver un montón de cambios en la vida que nos rodea. No habría ________ si no existieran los cambios.

  Algunos de esos cambios sólo se producen en la forma, tamaño, volumen o en el aspecto exterior de las cosas, pero siguen siendo las mismas cosas, no cambia su naturaleza. A esos cambios se les llama ________ ________.

  Algunos ejemplos más son:
  a. El ________ de agua que se condensa en el espejo cuando te estás duchando.
  b. La ________ del cacao en la leche o el azúcar en el café.
  c. ________ una hoja de papel.
  d. ________ plastilina.

  Otros de los cambios que podemos ver cada día son los que implican la obtención de nuevas ________ a partir de unas dadas. A los cambios en los que al principio tenemos unas sustancias y después tenemos otras sustancias distintas se les llama ________ ________, son aquellos cambios en los que cambia la naturaleza de las cosas.

  Algunos ejemplos más de cambios químicos o reacciones químicas son:
  a. La ________ en nuestro estómago.
  b. ________ papel, madera...
  c. ________ la cena.
  d. Cuando se estropea algo de comida (________).
  ```
- **Respuestas**: 
  ```
  CAMBIO, VIDA, CAMBIOS FÍSICOS
  a. VAPOR
  b. DISOLUCIÓN
  c. TROCEAR
  d. MOLDEAR
  SUSTANCIAS, CAMBIOS QUÍMICOS
  a. DIGESTIÓN
  b. QUEMAR
  c. COCINAR
  d. PUTREFACCIÓN
  ```
- **Criterios**: 
  - Cada hueco correctamente rellenado vale 0,3 puntos.
  - Total de huecos: 15.

### Ejercicio 2

- **Id**: 2
- **Tipo**: Responde correctamente
- **Max**: 2,5 puntos
- **Enunciado**: 
  ```
  a. ¿Qué es una reacción química?
  b. ¿Cómo se representa una reacción química?
  ```
- **Respuestas**: 
  ```
  a. UNA REACCIÓN QUÍMICA ES EL PROCESO POR EL QUE UNAS SUSTANCIAS (REACTIVOS) SE TRANSFORMAN EN OTRAS DISTINTAS (PRODUCTO).
  b. SUSTANCIAS INICIALES (REACTIVOS) → SUSTANCIAS FINALES (PRODUCTO).
  ```
- **Criterios**: 
  - Cada respuesta correcta vale 1,25 puntos.

### Ejercicio 3

- **Id**: 3
- **Tipo**: Rellena correctamente
- **Max**: 1,6 puntos
- **Enunciado**: 
  ```
  ¿Cómo sé que hay un cambio químico? Hay múltiples opciones, entre otras encontramos las siguientes:
  a. Porque ha habido un cambio de ________.
  b. Porque se han producido burbujas de ________.
  c. Porque el aspecto ________ ha cambiado.
  d. Porque aparece un ________ (sólido en suspensión o al fondo del tubo).
  e. Porque ha cambiado el punto de ________ o ________.
  f. Porque ha cambiado su ________.
  g. Porque ha cambiado su ________.
  ```
- **Respuestas**: 
  ```
  a. COLOR
  b. GAS
  c. EXTERIOR
  d. PRECIPITADO
  e. FUSIÓN, EBULLICIÓN
  f. SOLUBILIDAD
  g. DENSIDAD
  ```
- **Criterios**: 
  - Cada hueco correctamente rellenado vale 0,2 puntos.
  - Total de huecos: 8.

### Ejercicio 4

- **Id**: 4
- **Tipo**: Identifica la reacción
- **Max**: 0,4 puntos
- **Enunciado**: 
  ```
  ¿Qué reacción representa la siguiente imagen?
  ```
- **Respuestas**: 
  ```
  SO₃ + H₂O → H₂SO₄
  ```
- **Criterios**: 
  - Cada parte de la ecuación correctamente identificada vale 0,1 puntos.

### Ejercicio 5

- **Id**: 5
- **Tipo**: Escribe una definición
- **Max**: 1 punto
- **Enunciado**: 
  ```
  ¿Qué es la ley de conservación de masa?
  ```
- **Respuestas**: 
  ```
  EN UNA REACCIÓN QUÍMICA LA MASA DE LOS REACTIVOS (SUSTANCIAS INICIALES) ES LA MISMA QUE LA MASA DE LOS PRODUCTOS (SUSTANCIAS FINALES). POR ELLO, PODEMOS DECIR QUE LA MASA SE CONSERVA EN UNA REACCIÓN QUÍMICA.
  ```
- **Criterios**: 
  - La definición completa y correcta vale 1 punto.
```
"""

f"""
Eres el asistente de un profesor. Tu tarea es analizar analizar los exámenes que se te entreguen,
y devolver la información que se te pida.

El profesor, ha realizado estos pasos:
1. Ha impreso el cuerpo del examen (un .pdf con sus enunciados, instrucciones ...)
2. Ha entregado los papeles impresos al alumno
3. Ha dejado que el alumno resuelva los ejercicios sobre esos papeles impresos (escribiendo las respuestas a mano, con lápiz o bolígrafo)
4. Una vez terminado el examen, ha escaneado todos los papeles y ha generado unos archivos .pdf
5. Finalmente, ha convertido esos archivos .pdf a formato .png.

Cuando el profesor te compartirá esos archivos .png, sigue estos pasos:

1. Lee los ejercicios. Itera sobre ellos, y para cada uno sigue estos pasos:
    1.1. "Id": Identifica el id del ejercicio
    1.2. "Tipo": Identifica el tipo de ejercicio:
         - Rellena el hueco
         - Escribe una definición
         - Identifica la palabra correcta
         - Escribe un diagrama
         - ...
    1.3. "Enunciado": Identifica el enunciado y el texto originarios del examen (el texto que pertenece al .pdf originario del examen).
         Asegúrate de incluir solo el contenido que aparece escrito a máquina 
    1.4. "Respuestas": Identifica las respuestas proporcionadas por el alumno:
         - Estas respuestas aparecerán escritas a mano (mediante lápiz o bolígrafo)
         - Si no hay respuestas escritas a mano (mediante lápiz o bolígrafo) para el ejercicio, reporta una respuesta vacía
         - Asegúrate de incluir solo el contenido que aparece manuscrito
         - Si las respuestas siguieran cualquier patrón de numeración (1, 2, 3, ... a), b), c), ...) respeta ese patrón a la hora de reportar las respuestas
    1.5. Transcribe todo lo identificado

Notas:
a) En todos los pasos mencionados, utiliza técnicas de OCR o cualquier otra técnica avanzada
b) Realiza las transcripciones en formato markdown
"""

f"""
Eres el asistente de un profesor. Tu tarea es analizar analizar los exámenes que se te entreguen,
y devolver la información que se te pida.

El profesor, ha realizado estos pasos:
1. Ha impreso el cuerpo del examen (un .pdf con sus enunciados, instrucciones ...)
2. Ha entregado los papeles impresos al alumno
3. Ha dejado que el alumno resuelva los ejercicios sobre esos papeles impresos (escribiendo las respuestas a mano, con lápiz o bolígrafo)
4. Una vez terminado el examen, ha escaneado todos los papeles y ha generado unos archivos .pdf
5. Finalmente, ha convertido esos archivos .pdf a formato .png.

Cuando el profesor te compartirá esos archivos .png, sigue estos pasos:

1. Lee los ejercicios. Itera sobre ellos, y para cada uno sigue estos pasos:
    1.1. "Id": Identifica el id del ejercicio
    1.2. "Tipo": Identifica el tipo de ejercicio:
         - Rellena el hueco
         - Escribe una definición
         - Identifica la palabra correcta
         - Escribe un diagrama
         - ...
    1.3. "Enunciado": Identifica con precisión el enunciado y el texto originarios del examen (el texto que pertenece al .pdf originario del examen).
    1.4. "Respuestas": Identifica con precisión las respuestas proporcionadas por el alumno:
         - Estas respuestas aparecerán escritas a mano (mediante lápiz o bolígrafo)
         - Si el alumno ha dejado un espacio en blanco, representarlo como ___ en la transcripción.
         - Si las respuestas siguieran cualquier patrón de numeración (1, 2, 3, ... a), b), c), ...) respeta ese patrón a la hora de reportar las respuestas
    1.5. Transcribe todo lo identificado

Notas:
a) En todos los pasos mencionados, utiliza técnicas de OCR o cualquier otra técnica avanzada
b) Realiza las transcripciones en formato markdown
"""


f"""
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

f"""
Te comparto los archivos .png, sigue estos pasos: 

1. "Estudiante": Identifica el nombre del alumno que realizó el examen
2. Transcribe ese campo
"""

f"""
Ahora, sigue estos pasos:
1. Itera sobre los ejercicios presentes en el examen, y para cada uno sigue estos pasos: 
  1.1. "Id": Identifica el id del ejercicio  
  1.2. "Respuestas": Extrae con precisión las respuestas proporcionadas por el alumno:  
        - Las respuestas son las que aparecerán escritas a mano
        - Las respuestas del ejercicio pueden estar dispersas en distintas partes, por lo que busca en todo el examen
        - Si el alumno no ha respondido a parte o totalidad de una pregunta, representa esa ausencia de respuesta como "____"
        - Si las respuestas siguieran cualquier patrón de numeración (1, 2, 3, ... a), b), c), ...) respeta ese patrón
        - No incluyas nada de contenido del enunciado, céntrate solamente en las respuestas
  1.3. Transcribe estos campos 
"""

f"""
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

f"""
Te comparto los archivos .png, sigue estos pasos: 

1. "Profesor": Identifica el nombre del alumno que realizó el examen
2. "Asignatura": Identifica el nombre de la asignatura
3. "Ejercicios": Identifica la cantidad de ejercicios presentes en el examen
4. Transcribe esos campos
"""

f"""
Ahora, sigue estos pasos:
Itera sobre los ejercicios presentes en el examen, y para cada uno sigue estos pasos: 
  1. "Id": Identifica el id del ejercicio
  2. "Puntuación Max": Identifica la puntuación maxima que pueda obtenerse en el ejercicio
  3. "Enunciado": Extrae con precisión los contenidos presentados en el enunciado:
      - El enunciado es el texto que pertenece al .pdf originario del examen, escrito a máquina
  4. "Respuestas": Extrae con precisión las respuestas proporcionadas por el profesor:  
      - Las respuestas son las que aparecerán escritas a mano
      - Las respuestas del ejercicio pueden estar dispersas en distintas partes, por lo que busca en todo el examen
      - Si las respuestas siguieran cualquier patrón de numeración (1, 2, 3, ... a), b), c), ...) respeta ese patrón
      - No incluyas nada de contenido del enunciado, céntrate solamente en las respuestas
  5. "Criterios": Entiende los criterios de evaluación y el desglose de puntuación del ejercicio:
      - Realiza deducciones a partir de las anotaciones del profesor
      - Añade las explicaciones oportunas si es necesario
      - Realiza esta tarea con la máxima exactitud, precisión y detalle
  6. Transcribe estos campos 
"""



Procedo a analizar cada ejercicio según los criterios solicitados:

# Ejercicio 1
- Id: 1
- Puntuación Max: 4,5 puntos
- Enunciado: "Rellena los siguientes apartados:"
[Texto a completar sobre la naturaleza y los cambios, con espacios en blanco para rellenar]

- Respuestas:
  - "CAMBIO" (en "La naturaleza y el mundo están en continuo _____")
  - "VIDA" (en "No habría _____ si no existieran los cambios")
  - "CAMBIOS FÍSICOS" (completando la frase sobre cambios en forma, tamaño, etc.)
  
  Ejemplos de cambios físicos:
  a. "VAPOR" de agua que se condensa en el espejo
  b. "DISOLUCIÓN" del cacao en la leche o el azúcar en el café
  c. "TROCEAR" una hoja de papel
  d. "MOLDEAR" plastilina

  Sobre cambios químicos:
  - "SUSTANCIAS" (en referencia a la obtención de nuevas sustancias)
  - "CAMBIOS QUÍMICOS" (completando la definición)
  
  Ejemplos de cambios químicos:
  a. "DIGESTIÓN" en nuestro estómago
  b. "QUEMAR" papel, madera...
  c. "COCINAR" la cena
  d. "PUTREFACCIÓN" (cuando se estropea algo de comida)

# Ejercicio 2
- Id: 2
- Puntuación Max: 2,5 puntos
- Enunciado: 
  a. "¿Qué es una reacción química?"
  b. "¿Cómo se representa una reacción química?"

- Respuestas:
  a. "UNA REACCIÓN QUÍMICA ES EL PROCESO POR EL QUE UNAS SUSTANCIAS (REACTIVOS) SE TRANSFORMAN EN OTRAS DISTINTAS (PRODUCTO)"
  b. "SUSTANCIAS INICIALES (REACTIVOS) → SUSTANCIAS FINALES (PRODUCTO)"

# Ejercicio 3
- Id: 3
- Puntuación Max: 1,6 puntos
- Enunciado: "¿Cómo sé que hay un cambio químico? Hay múltiples opciones, entre otras encontramos las siguientes:"

- Respuestas:
  a. Porque ha habido un cambio de "COLOR"
  b. Porque se han producido burbujas de "GAS"
  c. Porque el aspecto "EXTERIOR" ha cambiado
  d. Porque aparece un "PRECIPITADO" (sólido en suspensión o al fondo del tubo)
  e. Porque ha cambiado el punto de "FUSIÓN" o "EBULLICIÓN"
  f. Porque ha cambiado su "SOLUBILIDAD"
  g. Porque ha cambiado su "DENSIDAD"

# Ejercicio 4
- Id: 4
- Puntuación Max: 0,4 puntos
- Enunciado: "¿Qué reacción representa la siguiente imagen?"

- Respuesta:
  "SO₃ + H₂O → H₂SO₄"

# Ejercicio 5
- Id: 5
- Puntuación Max: 1 punto
- Enunciado: "¿Qué es la ley de conservación de masa?"

- Respuesta:
  "EN UNA REACCIÓN QUÍMICA LA MASA DE LOS REACTIVOS (SUSTANCIAS INICIALES) ES LA MISMA QUE LA MASA DE LOS PRODUCTOS
(SUSTANCIAS FINALES). POR ELLO, PODEMOS DECIR QUE LA MASA SE CONSERVA EN UNA REACCIÓN QUÍMICA."



Eres el asistente de un profesor. Tu tarea es analizar corregir el examen que se te entregue del alumno, basado en criterios que se incluyan en el examen base del profesor.

El profesor, ha realizado estos pasos:

1. Ha impreso el cuerpo del examen (un .pdf con sus enunciados, instrucciones ...)
2. Ha resuelto los ejercicios sobre esos papeles impresos (escribiendo las respuestas a mano, con lápiz o bolígrafo)
3. Una vez terminado el examen, ha escaneado todos los papeles y ha generado unos archivos .pdf
4. Ha convertido esos archivos .pdf a formato .png.
5. Finalmente, el profesor ha transcrito los contenidos de ese .png a texto mediante un LLM

Además, el profesor también ha realizado estos pasos:

1. Ha impreso el cuerpo del examen (un .pdf con sus enunciados, instrucciones ...)
2. Ha entregado los papeles impresos al alumno
3. Ha dejado que el alumno resuelva los ejercicios sobre esos papeles impresos (escribiendo las respuestas a mano, con lápiz o bolígrafo)
4. Una vez terminado el examen, ha escaneado todos los papeles y ha generado unos archivos .pdf
5. Ha convertido esos archivos .pdf a formato .png.
6. Finalmente, el profesor ha transcrito los contenidos de ese .png a texto mediante un LLM



Eres el asistente de un profesor. Tu tarea es analizar corregir el examen que se te entregue del alumno, basado en criterios que se incluyan en el examen base del profesor.

El profesor, ha realizado estos pasos:

1. Ha impreso el cuerpo del examen (un .pdf con sus enunciados, instrucciones ...)
2. Ha resuelto los ejercicios sobre esos papeles impresos (escribiendo las respuestas a mano, con lápiz o bolígrafo)
3. Una vez terminado el examen, ha escaneado todos los papeles y ha generado unos archivos .pdf
4. Ha convertido esos archivos .pdf a formato .png.
5. Finalmente, el profesor ha transcrito los contenidos de ese .png a texto mediante un LLM

Además, el profesor también ha realizado estos pasos:

1. Ha impreso el cuerpo del examen (un .pdf con sus enunciados, instrucciones ...)
2. Ha entregado los papeles impresos al alumno
3. Ha dejado que el alumno resuelva los ejercicios sobre esos papeles impresos (escribiendo las respuestas a mano, con lápiz o bolígrafo)
4. Una vez terminado el examen, ha escaneado todos los papeles y ha generado unos archivos .pdf
5. Ha convertido esos archivos .pdf a formato .png.
6. Finalmente, el profesor ha transcrito los contenidos de ese .png a texto mediante un LLM

f"""
Este es el examen base del profesor:

Procederé a analizar el examen siguiendo los pasos solicitados:

1. PROFESOR
- Nombre y apellidos: Kepa Orosa Sánchez
- Fecha: 2024-10-30
- Curso: Diversificación
- Evaluación: 1

2. ASIGNATURA
Física y Química (IN02-Los cambios de la materia)

3. EJERCICIOS

EJERCICIO 1
- Id: 1
- Puntuación Max: 4,5 puntos (0,3p x 15)
- Tipo: Rellena el hueco
- Enunciado: Texto con espacios para completar sobre cambios físicos y químicos
- Respuestas:
  * "cambio", "vida"
  * "cambios físicos"
  * "vapor", "disolución", "trocear", "moldear"
  * "sustancias", "cambios químicos"
  * "digestión", "quemar", "cocinar", "putrefacción"
- Criterios: 0,3 puntos por cada respuesta correcta (15 huecos en total)

EJERCICIO 2
- Id: 2
- Puntuación Max: 2,5 puntos (1,25p x 2)
- Tipo: Respuesta corta
- Enunciado: 
  a) ¿Qué es una reacción química?
  b) ¿Cómo se representa una reacción química?
- Respuestas:
  a) Una reacción química es el proceso por el que unas sustancias (reactivos) se transforman en otras distintas (producto)
  b) Sustancias iniciales (reactivos) → sustancias finales (producto)
- Criterios: 1,25 puntos por cada respuesta correcta

EJERCICIO 3
- Id: 3
- Puntuación Max: 1,6 puntos (0,2p x 8)
- Tipo: Completar opciones múltiples
- Enunciado: ¿Cómo sé que hay un cambio químico?
- Respuestas:
  a) "color"
  b) "gas"
  c) "exterior"
  d) "precipitado"
  e) "fusión" o "ebullición"
  f) "solubilidad"
  g) "densidad"
- Criterios: 0,2 puntos por cada respuesta correcta

EJERCICIO 4
- Id: 4
- Puntuación Max: 0,4 puntos
- Tipo: Interpretación de reacción química
- Enunciado: ¿Qué reacción representa la siguiente imagen?
- Respuestas: SO₃ + H₂O → H₂SO₄
- Criterios: Puntuación dividida: 0,1p + 0,1p + 0,2p según anotaciones

EJERCICIO 5
- Id: 5
- Puntuación Max: 1 punto
- Tipo: Definición
- Enunciado: ¿Qué es la ley de conservación de masa?
- Respuestas: En una reacción química la masa de los reactivos (sustancias iniciales) es la misma que la masa de los productos (sustancias finales). Por ello, podemos decir que la masa se conserva en una reacción química.
- Criterios: 1 punto por la definición completa

Este es el examen del alumno:

# Estudiante
Sara Alvarez

# Ejercicios

## Id: 1
### Respuestas:
- Cambio
- vida
- Cambios físicos
- a. ____
- b. ____
- c. Trocear
- d. Moldear
- partículas
- cambios químicos
- a. digestión
- b. Quemar
- c. Cocinar
- d. ____

## Id: 2
### Respuestas:
a) Es el proceso por el que unas sustancias (reactivos) se transforman en otras distintas (productos).
b) Reactivos → Productos

## Id: 3
### Respuestas:
a. color
b. gas
c. exterior
d. ____
e. ____
f. solubilidad
g. densidad

## Id: 4
### Respuestas:
____

## Id: 5
### Respuestas:
Por mucho que 2 moléculas se junten ninguna de las 2 pierde su valor, es decir siguen teniendo ambos su misma masa.

Realiza estos pasos:

Itera sobre los ejercicios presentes en el examen, y para cada uno sigue estos pasos: 
  1. Corrigue el ejercicio del alumno basándote el nos criterios de evaluación, estructura y desglose de puntuación, que se incluyan en el examen base del profesor
  2. Reporta una nota
  3. Reporta una frase corta que justifique la nota y la correción realizada
"""

