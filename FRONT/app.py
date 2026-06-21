from io import BytesIO
from flask import Flask, render_template, request, url_for, redirect, send_file, session
import requests
from datetime import date, datetime, timedelta
import json
import urllib.parse


app = Flask(__name__)
app.secret_key = "una-clave-secreta"

@app.route('/buscar')
def buscar_seccion():

    nombre = request.args.get('nombre_profesor', '')

    texto = request.args.get('busqueda', '').lower().strip()

    if texto.startswith('usuario'):
        return redirect(url_for('seccion_usuarios',nombre_profesor=nombre))

    if texto.startswith('alumno'):
        return redirect(url_for('seccion_alumnos', nombre_profesor=nombre))

    if texto.startswith('grupo'):
        return redirect(url_for('seccion_grupos', nombre_profesor=nombre))

    if texto.startswith('evaluacion'):
        return redirect(url_for('seccion_evaluaciones',nombre_profesor=nombre))

    if texto.startswith('nota'):
        return redirect(url_for('seccion_notas',nombre_profesor=nombre))

    if texto.startswith('asistencia'):
        return redirect(url_for('seccion_asistencias',nombre_profesor=nombre))

    if texto.startswith('curso'):
        return redirect(url_for('seccion_cursos',nombre_profesor=nombre))

    return redirect(url_for('menu_principal', nombre_profesor=nombre, error_busqueda=True))

# 8. Ruta para mostrar el perfil del alumno

@app.route("/historial")
def seccion_historial():
    nombre = request.args.get('nombre_profesor', '')
    id_usuario = request.args.get('id', type=int)
    registros = []
    error = None

    if not id_usuario:
        error = "Falta el id de usuario"
        return render_template('historial.html', nombre_profesor=nombre, historial_alumno=registros, error=error, historial_global=False, usuario_id=None)

    try:
        response = requests.get(f"http://backend:5000/historiales/{id_usuario}", params={"limit": 100, "offset": 0})
        if response.status_code == 200:
            registros = response.json().get('listado', [])
        elif response.status_code == 204:
            registros = []
        else:
            error = f"Error del servidor ({response.status_code})"
    except Exception:
        registros = []
        error = "No se pudo conectar al servidor backend"

    return render_template('historial.html', nombre_profesor=nombre, historial_alumno=registros, error=error, historial_global=False, usuario_id=id_usuario)


@app.route("/historiales")
def seccion_historiales():
    nombre = request.args.get('nombre_profesor', '')
    registros = []
    error = None

    try:
        response = requests.get('http://backend:5000/historiales/', params={"limit": 100, "offset": 0})
        if response.status_code == 200:
            registros = response.json().get('listado', [])
        elif response.status_code == 204:
            registros = []
        else:
            error = f"Error del servidor ({response.status_code})"
    except Exception:
        registros = []
        error = "No se pudo conectar al servidor backend"

    return render_template('historial.html', nombre_profesor=nombre, historial_alumno=registros, error=error, historial_global=True, usuario_id=None)

@app.route("/alumno/<int:padron>")
def perfil_alumno(padron):
    nombre = request.args.get('nombre_profesor', '')
    grupos_alumno = []
    evaluaciones_alumno = []
    notas_alumno = []
    curso_nombre = None
    promedio = 0
    porcentaje = 0
    total_evaluaciones = 0
    evaluaciones_rendidas = 0

    try:
        response_alumno = requests.get(f"http://backend:5000/alumnos/{padron}")
        data_alumno = response_alumno.json() if response_alumno.status_code == 200 else {}

        id_curso = data_alumno.get("ID_CURSO") or data_alumno.get("id_curso")

        if id_curso:
            response_curso = requests.get(f"http://backend:5000/materias/{id_curso}")
            if response_curso.status_code == 200:
                curso_nombre = response_curso.json().get("NOMBRE_MATERIA")

        response_grupos = requests.get(f"http://backend:5000/grupos/del-alumno/{padron}")
        if response_grupos.status_code == 200:
            grupos_alumno = response_grupos.json() 

        response_evaluaciones = requests.get(f"http://backend:5000/evaluaciones/del-alumno/{padron}")
        if response_evaluaciones.status_code == 200:
            evaluaciones_alumno = response_evaluaciones.json()
            if not isinstance(evaluaciones_alumno, list):
                evaluaciones_alumno = []
        
        response_notas = requests.get(f"http://backend:5000/notas/", params={"padron": padron})
        if response_notas.status_code == 200:
            notas_alumno = response_notas.json().get("listado", [])

        if notas_alumno:
            total = sum(float(n.get("NOTA", 0)) for n in notas_alumno)
            promedio = round(total / len(notas_alumno), 2)

        total_evaluaciones = len(evaluaciones_alumno) 
        evaluaciones_rendidas = len(notas_alumno)      

        asistencia_real = 0
        response_asistencia = requests.get(f"http://backend:5000/asistencias/alumno/{padron}/porcentaje")
        if response_asistencia.status_code == 200:
            asistencia_real = response_asistencia.json().get("porcentaje", 0)


        alumno = {
            "NOMBRE": data_alumno.get("NOMBRE") or data_alumno.get("nombre", ""),
            "APELLIDO": data_alumno.get("APELLIDO") or data_alumno.get("apellido", ""),
            "MAIL": data_alumno.get("MAIL") or data_alumno.get("mail", ""),
            "PADRON": data_alumno.get("PADRON") or data_alumno.get("padron", padron),
            "ASISTENCIAS": asistencia_real,
            "CURSO": curso_nombre,
            "PROMEDIO": promedio,
            "EVALUACION": evaluaciones_alumno,
            "GRUPOS": grupos_alumno, 
            "NOTAS": notas_alumno,
            "EVALUACIONES_RENDIDAS": evaluaciones_rendidas,
            "TOTAL_EVALUACIONES": total_evaluaciones,
            "PORCENTAJE_EVALUACIONES": porcentaje,
        }

    except Exception as e:
        print("ERROR EN RUTA PROFILE:", e)
        import traceback
        traceback.print_exc()
        
        alumno = {
            "NOMBRE": "", "APELLIDO": "", "MAIL": "", "PADRON": padron,
            "ASISTENCIAS": 0, "PROMEDIO": 0, "GRUPOS": [], "NOTAS": [],
            "EVALUACIONES_RENDIDAS": 0, "TOTAL_EVALUACIONES": 0, "PORCENTAJE_EVALUACIONES": 0
        }
        
    return render_template("alumno.html", alumno=alumno, nombre_profesor=nombre)

#7. Ruta para mostrar el QR de la clase actual

@app.route("/qr", methods=["GET", "POST"])
def mostrar_qr():
    error = None
    success = None
    curso_id = None
    clase_encontrada = None
    cursos = []
    qr_url = None
    registro_url = None
    asistieron = []

    if request.method == "POST":
        id_clase = request.form.get("id")
        curso_id = request.form.get("curso_id")
    else:
        id_clase = request.args.get("id")

    if not id_clase:
        error = "Falta el id de la clase"
        return render_template("qr.html", clase=None, error=error, success=success, cursos=cursos, curso_id=curso_id, qr_url=qr_url)

    try:
        id_clase_int = int(id_clase)
    except ValueError:
        error = "ID de clase inválido"
        return render_template("qr.html", clase=None, error=error, success=success, cursos=cursos, curso_id=curso_id, qr_url=qr_url)

    try:
        
        response = requests.get(f"http://backend:5000/clases/{id_clase_int}")
        if response.status_code == 200:
            clase_encontrada = response.json().get("clase")
            if isinstance(clase_encontrada.get("PROFESORES"), str):
                clase_encontrada["PROFESORES"] = json.loads(clase_encontrada["PROFESORES"])
        else:
            error = "Clase no encontrada"
    except Exception:
        error = "No se pudo conectar al servidor backend"

    try:
        response = requests.get("http://backend:5000/materias/", params={"limit": 100, "offset": 0})
        if response.status_code == 200:
            cursos = response.json().get("listado", [])
    except Exception:
        cursos = []

    if clase_encontrada:
        registro_base_url = request.host_url.rstrip("/")
        registro_url = f"{registro_base_url}/asistencias/registro/{clase_encontrada.get('ID')}"
        qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=400x400&data=" + urllib.parse.quote(registro_url)

        try:
            response = requests.get(
                f"http://backend:5000/asistencias/{id_clase_int}",
                params={"limit": 100, "offset": 0},
                timeout=10
            )
            if response.status_code == 200:
                listado = response.json().get("listado", [])
                asistieron = [alumno for alumno in listado if alumno.get("ASISTIO")]
        except Exception:
            asistieron = []

    if request.method == "POST":
        if not curso_id:
            error = "Debe seleccionar un curso para enviar el QR"
        else:
            try:
                payload = {
                    "id_curso": int(curso_id),
                    "registro_base_url": request.host_url.rstrip("/")
                }
                headers = {"authorization": f"Bearer {session.get('token')}"}
                response = requests.post(f"http://backend:5000/clases/{id_clase_int}/enviar-qr", headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    success = "QR enviado a los alumnos del curso seleccionado"
                else:
                    try:
                        data = response.json()
                        error = data.get("errors", [])[0].get("description") if data.get("errors") else data.get("message") or f"Error del servidor ({response.status_code})"
                    except Exception:
                        error = f"Error del servidor ({response.status_code})"
            except Exception:
                error = "No se pudo conectar para enviar el QR"

    return render_template(
        "qr.html",
        clase=clase_encontrada,
        error=error,
        success=success,
        cursos=cursos,
        curso_id=curso_id,
        qr_url=qr_url,
        registro_url=registro_url,
        asistieron=asistieron
    )

# 7. Ruta de la sección de Asistencias

 #la idea de dejarla afuera es para q acumule las clses agregadas, si la dejo adentro se reinicia cada vez que se hace un POST

@app.route("/asistencias/registro/<int:clase_id>")
def registrar_asistencia_qr(clase_id):
    padron = request.args.get("padron", type=int)

    if padron is None:
        return f"""
        <html>
            <head>
                <title>Registrar asistencia</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body style="font-family: Arial, sans-serif; max-width: 420px; margin: 40px auto; padding: 0 16px;">
                <h1>Registrar asistencia</h1>
                <form method="GET" action="/asistencias/registro/{clase_id}">
                    <label for="padron">Padrón</label>
                    <input id="padron" name="padron" type="number" required
                           style="display:block; width:100%; box-sizing:border-box; margin:8px 0 16px; padding:10px;">
                    <button type="submit" style="padding:10px 14px;">Registrar</button>
                </form>
            </body>
        </html>
        """, 200

    try:
        response = requests.get(
            f"http://backend:5000/asistencias/registro/{clase_id}",
            params={"padron": padron},
            timeout=10
        )
        if response.status_code in (200, 201):
            return "<h1>Asistencia registrada</h1><p>Ya podés cerrar esta página.</p>", 200
        try:
            data = response.json()
            error = data.get("errors", [{}])[0].get("description", "No se pudo registrar la asistencia")
        except Exception:
            error = "No se pudo registrar la asistencia"
        return f"<h1>No se pudo registrar la asistencia</h1><p>{error}</p>", response.status_code
    except Exception:
        return "<h1>No se pudo registrar la asistencia</h1><p>No se pudo conectar con el servidor.</p>", 500

@app.route("/asistencias", methods=["GET", "POST"])
def seccion_asistencias():
    clases = []
    hora_local = datetime.utcnow() - timedelta(hours=3)
    hoy_str = hora_local.strftime("%Y-%m-%d")
    nombre = request.args.get('nombre_profesor', '')

    error_url = request.args.get("error_msg")
    edit_error_id = request.args.get("edit_error_id")

    if edit_error_id in ["None", "", "null"]:
        edit_error_id = None

    global_error = error_url if error_url else None

    cursos = []
    try:
        response_cursos = requests.get("http://backend:5000/materias/", params={"limit": 100, "offset": 0})
        if response_cursos.status_code == 200:
            cursos = response_cursos.json().get("listado", [])
        else:
            cursos = []
    except Exception:
        cursos = []


    if request.method == "POST":
        fecha = request.form.get("fecha")
        tema = request.form.get("tema", "").strip()
        horario = request.form.get("horario")

        docente1 = request.form.get("docente1", "")
        docente2 = request.form.get("docente2", "")
        docente3 = request.form.get("docente3", "")
        profesores = [d for d in [docente1, docente2, docente3] if d]

        if not fecha or not tema or not horario:
            global_error="Fecha, curso y horario obligatorios"
        
        else:
            try:
                headers = {"authorization": f"Bearer {session.get('token')}"}
                response = requests.post("http://backend:5000/clases/",
                    headers=headers,
                    json={
                    "profesores": profesores,
                    "fecha": fecha,
                    "horario": horario,
                    "tema": tema
                })
                if response.status_code == 201:
                    return redirect(url_for('seccion_asistencias', 
                                            nombre_profesor=nombre,
                                            curso_id=request.args.get('curso_id', ''),
                                            orden=request.args.get('orden', '')))
                elif response.status_code == 400:
                    global_error = response.json().get("error", "El curso seleccionado no existe")
                else:
                    global_error = "Campos obligatorios incompletos o inválidos"
            except Exception:
                global_error = "Error de conexión con el servidor"

    try:
        response = requests.get("http://backend:5000/clases/", params={"limit": 100, "offset": 0})
        clases_raw = response.json().get("listado", [])
    except Exception as e:
        clases_raw = []

    for c in clases_raw:
        try:
            fecha_obj = datetime.strptime(c.get("FECHA", ""), "%a, %d %b %Y %H:%M:%S %Z").date()
            fecha_str = fecha_obj.strftime("%Y-%m-%d")
            if fecha_str == hoy_str:
                estado = "HOY"
            elif fecha_str < hoy_str:
                estado = "Finalizada"
            else:
                estado = "Próximamente"
        except:
            estado = "Desconocido"
            fecha_str = ""

        try:
            profesores_lista = json.loads(c.get("PROFESORES", "[]"))
        except:
            profesores_lista = []

        clases.append({
            "id": c.get("ID"),
            "fecha": fecha_str,
            "tema": c.get("TEMA", ""),
            "horario": str(c.get("HORARIO", "")),
            "docente1": profesores_lista[0] if len(profesores_lista) > 0 else "",
            "docente2": profesores_lista[1] if len(profesores_lista) > 1 else "",
            "docente3": profesores_lista[2] if len(profesores_lista) > 2 else "",
            "estado": estado,
            "asistieron": []
        })

    filtrar_curso = request.args.get("curso_id", "")
    if filtrar_curso and filtrar_curso not in ["None", "", "Todos"]:
        clases = [c for c in clases if c["tema"] == str(filtrar_curso)]

    for clase in clases:
        try:
            response = requests.get(
                f"http://backend:5000/asistencias/{clase['id']}",
                params={"limit": 100, "offset": 0},
                timeout=10
            )
            if response.status_code == 200:
                listado = response.json().get("listado", [])
                clase["asistieron"] = [alumno for alumno in listado if alumno.get("ASISTIO")]
        except Exception:
            clase["asistieron"] = []

    orden = request.args.get("orden", "asc")

    if orden == "asc":
        clases.sort(key=lambda c: c["fecha"])
    elif orden == "desc":
        clases.sort(key=lambda c: c["fecha"], reverse=True)
    elif orden == "HOY":
        clases_actuales = [c for c in clases if c["estado"] == "HOY"]
        resto = [c for c in clases if c["estado"] != "HOY"]
        clases = clases_actuales + resto

    if not error_url or error_url in ["None","","null"]:
        edit_error_id = ""
        global_error = ""
    else:
        global_error=error_url
        if edit_error_id in ["None","","null"]:
            edit_error_id=""

    print(request.args)
    
    return render_template(
        "asistencias.html",
        clases=clases,
        cursos=cursos,
        nombre_profesor=nombre,
        error=global_error,
        edit_error_id=edit_error_id
    )

@app.route('/editar_clase/<int:id>', methods=['POST'])
def editar_clase(id):
    nombre = request.args.get('nombre_profesor') or request.form.get('nombre_profesor', '')
    docente1 = request.form.get('docente1', '')
    docente2 = request.form.get('docente2', '')
    docente3 = request.form.get('docente3', '')
    profesores = [d for d in [docente1, docente2, docente3] if d]
    fecha = request.form.get('fecha')
    horario = request.form.get('horario')
    tema = request.form.get('tema', '').strip()

    curso_id_actual = request.args.get('curso_id', '')
    orden_actual = request.args.get('orden', '')

    if not fecha or not tema or not horario:
        return redirect(url_for('seccion_asistencias', 
                                nombre_profesor=nombre,
                                error_msg="Campos obligatorios incompletos o inválidos",
                                edit_error_id=id,
                                curso_id=curso_id_actual,
                                orden=orden_actual))
    
    try:
        headers = {"authorization": f"Bearer {session.get('token')}"}
        response = requests.patch(f"http://backend:5000/clases/{id}",
            headers=headers,
            json={
            "profesores": profesores,
            "fecha": fecha,
            "horario": horario,
            "tema": tema
        })
        print("STATUS PATCH:", response.status_code)
        print("BODY:", response.text)
        if response.status_code == 400:
            error_msg_back = response.json().get("error", "El curso seleccionado no existe")
            return redirect(url_for('seccion_asistencias', 
                                    nombre_profesor=nombre,
                                    error_msg=error_msg_back,
                                    edit_error_id=id,
                                    curso_id=curso_id_actual,
                                    orden=orden_actual))
        
        if response.status_code == 200 or response.status_code ==201:
            return redirect(url_for('seccion_asistencias', 
                                    nombre_profesor=nombre, 
                                    curso_id=curso_id_actual, 
                                    orden=orden_actual))
        
        return redirect(url_for('seccion_asistencias', 
                                nombre_profesor=nombre,
                                error_msg="No se pudo actualizar la clase en el servidor",
                                edit_error_id=id,
                                curso_id=curso_id_actual,
                                orden=orden_actual))
                                    
    except Exception:
        return redirect(url_for('seccion_asistencias', 
                                nombre_profesor=nombre, 
                                curso_id=curso_id_actual, 
                                orden=orden_actual))


@app.route('/eliminar_clase/<int:id>', methods=['POST'])
def eliminar_clase(id):
    nombre = request.args.get('nombre_profesor', '')
    curso_id_actual = request.args.get('curso_id', '')
    orden_actual = request.args.get('orden', '')
    try:
        headers = {"authorization": f"Bearer {session.get('token')}"}
        requests.delete(f"http://backend:5000/clases/{id}",headers=headers)
    except Exception as e:
        pass
    return redirect(url_for('seccion_asistencias', 
                            nombre_profesor=nombre, 
                            curso_id=curso_id_actual, 
                            orden=orden_actual))

# 6. Ruta de la sección de Notas
@app.route('/notas')
def seccion_notas():
    nombre = request.args.get('nombre_profesor', '')
    return render_template('notas.html', nombre_profesor=nombre)

@app.route('/api/notas', methods=['GET'])
def api_get_notas():
    id_evaluacion = request.args.get('id_evaluacion', type=int)
    padron        = request.args.get('padron', type=int)
    params = {'limit': 100, 'offset': 0}
    if id_evaluacion:
        params['id_evaluacion'] = id_evaluacion
    if padron:
        params['padron'] = padron
    try:
        r = requests.get('http://backend:5000/notas/', params=params)
        return r.json(), r.status_code
    except Exception:
        return {'error': 'No se pudo conectar al backend'}, 500
        
@app.route('/api/notas', methods=['POST'])
def api_crear_nota():
    try:
        headers = {"authorization": f"Bearer {session.get('token')}"}
        r = requests.post('http://backend:5000/notas/',
                          headers=headers,
                          json=request.get_json())
        return r.json(), r.status_code
    except Exception:
        return {'error': 'No se pudo conectar al backend'}, 500
        
# 5. Ruta de la sección de Evaluaciones
@app.route('/evaluaciones')
def seccion_evaluaciones():
    nombre = request.args.get('nombre_profesor', '')
    return render_template('registro_evaluaciones.html', nombre_profesor=nombre)


@app.route('/api/evaluaciones', methods=['GET'])
def api_get_evaluaciones():
    try:
        r = requests.get('http://backend:5000/evaluaciones/',
                         params={'limit': 100, 'offset': 0})
        return r.json(), r.status_code
    except Exception:
        return {'error': 'No se pudo conectar al backend'}, 500


@app.route('/api/evaluaciones', methods=['POST'])
def api_crear_evaluacion():
    try:
        headers = {"authorization": f"Bearer {session.get('token')}"}
        r = requests.post('http://backend:5000/evaluaciones/',
                          headers=headers,
                          json=request.get_json())
        return r.json(), r.status_code
    except Exception:
        return {'error': 'No se pudo conectar al backend'}, 500


@app.route('/api/evaluaciones/<int:id>', methods=['PATCH'])
def api_editar_evaluacion(id):
    try:
        headers = {"authorization": f"Bearer {session.get('token')}"}
        r = requests.patch(f'http://backend:5000/evaluaciones/{id}',
                            headers=headers,
                           json=request.get_json())
        return r.json(), r.status_code
    except Exception:
        return {'error': 'No se pudo conectar al backend'}, 500


@app.route('/api/evaluaciones/<int:id>', methods=['DELETE'])
def api_eliminar_evaluacion(id):
    try:
        headers = {"authorization": f"Bearer {session.get('token')}"}
        r = requests.delete(f'http://backend:5000/evaluaciones/{id}',headers=headers)
        # 204 no tiene body
        if r.status_code == 204:
            return '', 204
        return r.json(), r.status_code
    except Exception:
        return {'error': 'No se pudo conectar al backend'}, 500
        

@app.route('/grupos', methods=["POST", "GET"])
def seccion_grupos():
    nombre_profesor = request.args.get('nombre_profesor', '')
    padron_asignar = request.form.get('padron_asignar')
    grupo_id = request.form.get('grupo_id')
 
    if request.method == "POST":
        crear = request.form.get('crear')
        eliminar = request.form.get('eliminar')

        if eliminar:
            try:
                headers = {"authorization": f"Bearer {session.get('token')}"}
                requests.delete(f"http://backend:5000/grupos/{eliminar}",headers=headers)
            except Exception as e:
                print("Error al eliminar grupo")
        elif crear:
            try:
                headers = {"authorization": f"Bearer {session.get('token')}"}
                requests.post("http://backend:5000/grupos/",
                    headers=headers,
                    json={
                    "nombre": crear
                })
            except Exception as e:
                print("Error al crear grupo")
        elif padron_asignar and grupo_id:
            try:
                headers = {"authorization": f"Bearer {session.get('token')}"}
                requests.post(f"http://backend:5000/grupos/asignar-alumnos",
            headers=headers,
            json={
            "id_grupo": int(grupo_id),
            "padrones_alumnos": [{"padron": int(padron_asignar)}]
                })
            except Exception as e:
                print("Error al asignar alumno ")

    grupos = []
    try:
        response = requests.get("http://backend:5000/grupos/", params={"limit": 30, "offset": 0})
        grupos = response.json().get("listado", [])
    except Exception as e:
        print("Hubo un error")

    return render_template('grupos.html', nombre_profesor=nombre_profesor, grupos=grupos)

@app.route('/grupo-detalle')
def detalle_grupo():
    nombre_profesor = request.args.get('nombre_profesor')
    
    id_grupo = request.args.get('id')

    grupo_simulado = {
        "nombre": id_grupo if id_grupo else "Grupo Sin Nombre",
        "materia": "Diseño de Sistemas",
        "integrantes": ["Juan Pérez", "Ana Gómez", "Lucas Díaz"]
    }
    return render_template(
        'grupo_individual.html', 
        nombre_profesor=nombre_profesor,
        grupo=grupo_simulado
    )

@app.route('/descargar_pdf_grupos', methods=['GET'])
def descargar_grupos_pdf():
    nombre_profesor = request.args.get('nombre_profesor', '')
    try:
        r = requests.get("http://backend:5000/grupos/pdf")
        if r.ok:
            return send_file(
                BytesIO(r.content),
                mimetype="application/pdf",
                as_attachment=True,
                download_name="listado_grupos.pdf"
            )
    except Exception as e:
        print(e)
    return redirect(url_for('seccion_grupos',nombre_profesor=nombre_profesor))


@app.route('/alumnos', methods=["POST","GET"])
def seccion_alumnos():
    nombre = request.args.get('nombre_profesor', '')
    id_curso = request.args.get('id_curso', '')
    crear_alumno = request.form.get('crear_alumno')
    eliminar_alumno = request.form.get('eliminar_alumno')
    
    if crear_alumno:
        print("FORM COMPLETO:", dict(request.form), flush=True)
        try:
            headers = {"authorization": f"Bearer {session.get('token')}"}
            response = requests.post("http://backend:5000/alumnos/",
                headers=headers,
                json={
                "nombre": request.form.get('crear_alumno'),
                "apellido": request.form.get('apellido'),
                "email": request.form.get('email'),
                "padron": request.form.get('padron'),
                "id_curso": request.form.get('id_curso')
            })

            print(response.json(), flush=True)
        except Exception as e:
            print(f"Error al crear alumno {e}", flush=True)
    if eliminar_alumno:
        try:
            headers = {"authorization": f"Bearer {session.get('token')}"}
            requests.delete(f"http://backend:5000/alumnos/{eliminar_alumno}", headers=headers)
        except Exception as e:
            print("Error al eliminar alumno")

    try:
        resp_cursos = requests.get("http://backend:5000/materias/", params={"limit": 100, "offset": 0})
        cursos = resp_cursos.json().get("listado", [])
    except Exception as e:
        cursos = []

    try:
        if id_curso:
            response = requests.get(f"http://backend:5000/alumnos/curso/{id_curso}", params={"limit": 100, "offset": 0})
        else:
            response = requests.get("http://backend:5000/alumnos/", params={"limit": 100, "offset": 0})
        alumnos = response.json().get("listado", [])
    except Exception as e:
        alumnos = []

    return render_template('alumnos.html', nombre_profesor=nombre, alumnos=alumnos, cursos=cursos, id_curso=id_curso)

@app.route('/cargar_csv_alumnos', methods=['POST'])
def crear_alumnos_csv():
    nombre_profesor = request.args.get('nombre_profesor', '')
    csv = request.files.get('alumnos')
    try:
        headers = {"authorization": f"Bearer {session.get('token')}"}
        r = requests.post("http://backend:5000/alumnos/csv", headers=headers, files={"alumnos": (csv.filename, csv.stream, csv.content_type)})
    except Exception as e:
        print(e)
    return redirect(url_for('seccion_alumnos',nombre_profesor=nombre_profesor))

@app.route('/descargar_pdf_alumnos', methods=['GET'])
def descargar_alumnos_pdf():
    nombre_profesor = request.args.get('nombre_profesor', '')
    columnas = request.args.getlist("columnas")    
    
    query = "&".join([f"{columna}=1" for columna in columnas])
    try:
        r = requests.get(f"http://backend:5000/alumnos/pdf?{query}")
        if r.ok:
            return send_file(
                BytesIO(r.content),
                mimetype="application/pdf",
                as_attachment=True,
                download_name="listado_alumnos.pdf"
            )
    except Exception as e:
        print(e)
    return redirect(url_for('seccion_alumnos',nombre_profesor=nombre_profesor))


# 1. Ruta de la sección de Usuarios
@app.route('/usuarios')
def seccion_usuarios():
    nombre = request.args.get('nombre_profesor', '')
    mensaje = request.args.get('mensaje', '')
    error = request.args.get('error', '')
    try:
        response = requests.get("http://backend:5000/usuarios/", params={"limit": 30, "offset": 0})
        usuarios = response.json().get("listado", [])
    except Exception as e:
        usuarios = []
        if not error:
            error = "No se pudo cargar la lista de usuarios"
    return render_template('usuarios.html', nombre_profesor=nombre, usuarios=usuarios, mensaje=mensaje, error=error)

@app.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    nombre_profesor = request.args.get('nombre_profesor', '')
    nombre = request.form.get('nombre')
    contrasenia = request.form.get('contrasenia')

    if not nombre or not contrasenia:
        return redirect(url_for('seccion_usuarios', nombre_profesor=nombre_profesor, error='Nombre y contraseña son obligatorios'))

    try:
        headers = {"authorization": f"Bearer {session.get('token')}"}
        response = requests.post("http://backend:5000/usuarios/",headers=headers, json={
            "nombre": nombre,
            "contrasenia": contrasenia
        }, timeout=10)
        if response.status_code == 201:
            return redirect(url_for('seccion_usuarios', nombre_profesor=nombre_profesor, mensaje='Usuario creado correctamente'))
        else:
            dato = response.json()
            descripcion = 'No se pudo crear el usuario'
            if isinstance(dato, dict) and dato.get('errors'):
                descripcion = dato['errors'][0].get('description', descripcion)
            return redirect(url_for('seccion_usuarios', nombre_profesor=nombre_profesor, error=descripcion))
    except Exception:
        return redirect(url_for('seccion_usuarios', nombre_profesor=nombre_profesor, error='Error de conexión con el backend'))

@app.route('/eliminar_usuario', methods=['POST'])
def eliminar_usuario():
    nombre_profesor = request.args.get('nombre_profesor', '')
    id = request.form.get('eliminar-usuario-id')
    try:
        headers = {"authorization": f"Bearer {session.get('token')}"}
        requests.delete(f"http://backend:5000/usuarios/{id}",headers=headers)
    except Exception as e:
        pass
    return redirect(url_for('seccion_usuarios',nombre_profesor=nombre_profesor))

# 0. Ruta del Panel Principal (Se activa al entrar a http://127.0.0.1:5000)
@app.route('/')
def inicio():
    return render_template('inicio.html')


def obtener_estadisticas_cursada():
    """
    Función auxiliar para obtener los contadores en tiempo real del panel lateral.
    Filtra las clases ya cursadas (antiguas o de HOY) de forma nativa por fecha.
    """
    total_alumnos = 0
    total_grupos = 0
    total_clases = 0
    total_usuarios = 0
    total_cursos = 0

    hora_local = datetime.utcnow() - timedelta(hours=3)
    hoy_str = hora_local.strftime("%Y-%m-%d")

    fecha_hoy_formateada = hora_local.strftime("%d/%m/%Y")
    try:
        res_alumnos = requests.get("http://backend:5000/alumnos/", params={"limit": 500, "offset": 0}, timeout=2)
        if res_alumnos.status_code == 200:
            datos = res_alumnos.json()
            alumnos_lista = datos.get("listado", [])
            total_alumnos = 0
            for al in alumnos_lista:
                if al.get("ABANDONO") == 0:
                    total_alumnos += 1
    except Exception:
        total_alumnos = 0

    try:
        res_clases = requests.get("http://backend:5000/clases/", params={"limit": 500, "offset": 0}, timeout=2)
        if res_clases.status_code == 200:
            datos = res_clases.json()
            clases_lista = datos.get("listado", []) 
            for c in clases_lista:
                try:
                    fecha_obj = datetime.strptime(c.get("FECHA", ""), "%a, %d %b %Y %H:%M:%S %Z").date()
                    fecha_str = fecha_obj.strftime("%Y-%m-%d")
                    
                    if fecha_str <= hoy_str:
                        total_clases += 1
                except Exception:
                    total_clases += 1
    except Exception:
        total_clases = 0

    try:
        res_grupos = requests.get("http://backend:5000/grupos/", params={"limit": 500, "offset": 0}, timeout=2)
        if res_grupos.status_code == 200:
            datos = res_grupos.json()
            grupos_lista = datos.get("listado", []) 
            total_grupos = len(grupos_lista)
    except Exception:
        total_grupos = 0

    try:
        res_usuarios = requests.get("http://backend:5000/usuarios/", params={"limit": 500, "offset": 0}, timeout=2)
        if res_usuarios.status_code == 200:
            datos = res_usuarios.json()
            usuarios_lista = datos.get("listado", []) 
            total_usuarios = len(usuarios_lista)
    except Exception:
        total_usuarios = 0

    try:
        res_cursos = requests.get("http://backend:5000/materias/", params={"limit": 500, "offset": 0}, timeout=2)
        if res_cursos.status_code == 200:
            datos = res_cursos.json()
            cursos_lista = datos.get("listado", []) 
            total_cursos = len(cursos_lista)
    except Exception:
        total_cursos = 0

    return total_alumnos, total_grupos, total_clases, total_usuarios, total_cursos,fecha_hoy_formateada

@app.route('/menu')
def menu_principal():
    nombre = request.args.get('nombre_profesor', '')
    error_busqueda = request.args.get('error_busqueda')

    t_alumnos, t_grupos, t_clases, t_usuarios, t_cursos, f_hoy = obtener_estadisticas_cursada()

    return render_template(
        'menu_principal.html',
        nombre_profesor=nombre, 
        error_busqueda=error_busqueda,
        total_alumnos=t_alumnos,
        total_grupos=t_grupos,
        total_clases=t_clases,
        total_usuarios=t_usuarios,
        total_cursos=t_cursos,
        fecha_actual=f_hoy
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form["nombre_profesor"]
        password = request.form["password"]
        try:
            headers = {"authorization": f"Bearer {session.get('token')}"}
            response = requests.post("http://backend:5000/usuarios/login", headers=headers, json={
                "nombre": nombre,
                "contrasenia": password
            })
            if response.status_code == 200:
                data = response.json()
                session['token'] = data.get('access_token')
                return redirect(url_for(
                    'menu_principal',
                    nombre_profesor=nombre
                ))
            else:
                return render_template("login.html", error="Usuario o contraseña incorrectos")
        except Exception as e:
            return render_template("login.html", error="No se pudo conectar al servidor")
    return render_template("login.html")

@app.route('/grupo/<int:id>', methods=["GET", "POST"])
def ver_grupo(id):
    nombre = request.args.get('nombre_profesor', '')
    lista_alumnos = [] 
    eliminar_alumno = None
    if request.method == "POST":
        eliminar_alumno= request.form.get('eliminar')
        if eliminar_alumno:
            try:
                headers = {"authorization": f"Bearer {session.get('token')}"}
                requests.delete("http://backend:5000/grupos/alumnos",headers=headers,
                json={"id_grupo": id, "padron_alumno": int(eliminar_alumno)})
            except Exception as e:
                print("Error al eliminar alumno del grupo")
    try:
        response = requests.get(f"http://backend:5000/grupos/alumnos/{id}")
        lista_alumnos = response.json()
    except Exception as e:
        print('Hubo un error al obtener los alumnos del grupo')
    return render_template('detalle_grupo.html', integrantes=lista_alumnos,nombre_profesor=nombre,ID=id)

# 9. ruta para listado de cursos y detalle de cada curso 
@app.route('/cursos', methods=["POST", "GET"])
def seccion_cursos():
    nombre = request.args.get('nombre_profesor', '')
    if request.method == "POST":
        crear_curso = request.form.get('crear-curso')
        eliminar_curso = request.form.get('eliminar-curso')
        if eliminar_curso:
            try:
                headers = {"authorization": f"Bearer {session.get('token')}"}
                requests.delete(f"http://backend:5000/materias/{eliminar_curso}",headers=headers)
            except Exception as e:
                print("Error al eliminar curso")
        elif crear_curso:
            try:
                headers = {"authorization": f"Bearer {session.get('token')}"}
                requests.post("http://backend:5000/materias/", headers=headers, json={
                    "nombre_materia": crear_curso,
                    "cuatrimestre":int(request.form.get('cuatrimestre-crear')),
                    "anio":int(request.form.get('anio-crear',2026))})
            except Exception as e:
                print("Error al crear curso")
    try:
        response = requests.get("http://backend:5000/materias/", params={"limit": 30, "offset": 0})
        cursos = response.json().get("listado", [])
    except Exception as e:
        cursos = []
        print("Hubo un error al obtener los cursos")
    return render_template('cursos.html', nombre_profesor=nombre, cursos=cursos)

@app.route('/curso/<int:id>', methods=["GET", "POST"])
def ver_curso(id):
    nombre = request.args.get('nombre_profesor', '')
    try:
        response = requests.get(f"http://backend:5000/materias/{id}")
        curso = response.json().get("materia", {})
    except Exception as e:
        curso = {}
    return render_template('detalle_curso.html', curso=curso, nombre_profesor=nombre, ID=id)

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))