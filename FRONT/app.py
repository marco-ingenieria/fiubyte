from flask import Flask, render_template, request, url_for, redirect
import requests
from datetime import date, datetime, timedelta
import json
import urllib.parse


app = Flask(__name__)

@app.route('/buscar')
def buscar_seccion():

    nombre = request.args.get('nombre_profesor', '')

    texto = request.args.get('busqueda', '').lower().strip()

    if texto.startswith('usuario'):
        return redirect(url_for('seccion_usuarios',nombre_profesor=nombre))

    if texto.startswith('alumno'):
        return redirect(url_for('seccion_alumnos', nombre_profesor=nombre))

    if texto.startswith('historial'):
        return redirect(url_for('seccion_historiales',nombre_profesor=nombre))

    if texto.startswith('grupo'):
        return redirect(url_for('seccion_grupos', nombre_profesor=nombre))

    if texto.startswith('evaluacion'):
        return redirect(url_for('seccion_evaluaciones',nombre_profesor=nombre))

    if texto.startswith('nota'):
        return redirect(url_for('seccion_notas',nombre_profesor=nombre))

    if texto.startswith('asistencia'):
        return redirect(url_for('seccion_asistencias',nombre_profesor=nombre))

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
    grupos_alumno=[]

    try:
        response_alumno= requests.get(f"http://backend:5000/alumnos/{padron}")
        data_alumno=response_alumno.json()

        response_grupos = requests.get(f"http://backend:5000/grupos/del-alumno/{padron}")
        if response_grupos.status_code == 200:
            grupos_alumno = response_grupos.json() # Esto carga la lista real de grupos

        alumno = {
            "NOMBRE": data_alumno.get("NOMBRE") or data_alumno.get("nombre"),
            "APELLIDO": data_alumno.get("APELLIDO") or data_alumno.get("apellido"),
            "MAIL": data_alumno.get("MAIL") or data_alumno.get("mail"),
            "PADRON": data_alumno.get("PADRON") or data_alumno.get("padron", padron),
            "ASISTENCIAS": data_alumno.get("ASISTENCIAS") or data_alumno.get("asistencias", 0),
            "PROMEDIO": data_alumno.get("PROMEDIO") or data_alumno.get("promedio", 0),
            "TRABAJOS": data_alumno.get("TRABAJOS") or data_alumno.get("trabajos", 0),
            
            # Le asignamos la lista que responda nuestra API de grupos
            "GRUPOS": grupos_alumno, 
            
            "NOTAS": data_alumno.get("NOTAS") or data_alumno.get("notas", [])
        }
    except Exception:
        alumno = {
            "NOMBRE": "", "APELLIDO": "", "MAIL": "", "PADRON": padron,
            "ASISTENCIAS": 0, "PROMEDIO": 0, "TRABAJOS": 0, "GRUPOS": [], "NOTAS": []
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
        qr_data = json.dumps({
            "clase_id": clase_encontrada.get("ID"),
            "tema": clase_encontrada.get("TEMA", ""),
            "fecha": str(clase_encontrada.get("FECHA", "")),
            "horario": str(clase_encontrada.get("HORARIO", "")),
        }, default=str)
        qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=400x400&data=" + urllib.parse.quote(qr_data)

    if request.method == "POST":
        if not curso_id:
            error = "Debe seleccionar un curso para enviar el QR"
        else:
            try:
                payload = {"id_curso": int(curso_id)}
                response = requests.post(f"http://backend:5000/clases/{id_clase_int}/enviar-qr", json=payload, timeout=30)
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
        qr_url=qr_url
    )

# 7. Ruta de la sección de Asistencias

 #la idea de dejarla afuera es para q acumule las clses agregadas, si la dejo adentro se reinicia cada vez que se hace un POST

@app.route("/asistencias", methods=["GET", "POST"])
def seccion_asistencias():
    clases = []
    # Reemplaza tu hoy_str actual por este:
    hora_local = datetime.utcnow() - timedelta(hours=3)
    hoy_str = hora_local.strftime("%Y-%m-%d")
    nombre = request.args.get('nombre_profesor', '')

    error_url = request.args.get("error_msg")
    edit_error_id = request.args.get("edit_error_id")

    if edit_error_id in ["None", "", "null"]:
        edit_error_id = None

    global_error = error_url if error_url else None

    if request.method == "POST":
        fecha = request.form.get("fecha")
        tema = request.form.get("tema", "").strip()
        horario = request.form.get("horario")

        docente1 = request.form.get("docente1", "")
        docente2 = request.form.get("docente2", "")
        docente3 = request.form.get("docente3", "")
        profesores = [d for d in [docente1, docente2, docente3] if d]

        if not fecha or not tema or not horario:
            global_error="El tema es obligatorio"
        
        else:
            try:
                response = requests.post("http://backend:5000/clases/", json={
                    "profesores": profesores,
                    "fecha": fecha,
                    "horario": horario,
                    "tema": tema
                })
                if response.status_code == 201:
                    return redirect(url_for('seccion_asistencias', nombre_profesor=nombre))
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
            "estado": estado
        })

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

    return render_template(
        "asistencias.html",
        clases=clases,
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

    if not fecha or not tema or not horario:
        return redirect(url_for('seccion_asistencias', 
                                nombre_profesor=nombre,
                                error_msg="Campos obligatorios incompletos o inválidos",
                                edit_error_id=id))

    try:
        response = requests.patch(f"http://backend:5000/clases/{id}", json={
            "profesores": profesores,
            "fecha": fecha,
            "horario": horario,
            "tema": tema
        })
        if response.status_code != 200:
            return redirect(url_for('seccion_asistencias', 
                                    nombre_profesor=nombre))
    except Exception:
        pass

    return redirect(url_for('seccion_asistencias', nombre_profesor=nombre))

@app.route('/eliminar_clase/<int:id>', methods=['POST'])
def eliminar_clase(id):
    try:
        requests.delete(f"http://backend:5000/clases/{id}")
    except Exception as e:
        pass
    return redirect(url_for('seccion_asistencias', nombre_profesor=request.args.get('nombre_profesor', '')))

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
        r = requests.post('http://backend:5000/notas/',
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
        r = requests.post('http://backend:5000/evaluaciones/',
                          json=request.get_json())
        return r.json(), r.status_code
    except Exception:
        return {'error': 'No se pudo conectar al backend'}, 500


@app.route('/api/evaluaciones/<int:id>', methods=['PATCH'])
def api_editar_evaluacion(id):
    try:
        r = requests.patch(f'http://backend:5000/evaluaciones/{id}',
                           json=request.get_json())
        return r.json(), r.status_code
    except Exception:
        return {'error': 'No se pudo conectar al backend'}, 500


@app.route('/api/evaluaciones/<int:id>', methods=['DELETE'])
def api_eliminar_evaluacion(id):
    try:
        r = requests.delete(f'http://backend:5000/evaluaciones/{id}')
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
                requests.delete(f"http://backend:5000/grupos/{eliminar}")
            except Exception as e:
                print("Error al eliminar grupo")
        elif crear:
            try:
                requests.post("http://backend:5000/grupos/", json={
                    "nombre": crear
                })
            except Exception as e:
                print("Error al crear grupo")
        elif padron_asignar and grupo_id:
            try:
                requests.post(f"http://backend:5000/grupos/asignar-alumnos", json={
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
def detalle_grupo_especifico():
    nombre_profesor = request.args.get('nombre_profesor', '')
    
    id_grupo = request.args.get('id', '')

    grupo_simulado = {
        "nombre": id_grupo if id_grupo else "Grupo Sin Nombre",
        "materia": "Diseño de Sistemas",
        "integrantes": ["Juan Pérez", "Ana Gómez", "Lucas Díaz"]
    }

    return render_template(
        'grupo_individual.html', # Esta es la nueva plantilla física para la hoja del grupo
        nombre_profesor=nombre_profesor,
        grupo=grupo_simulado
    )

@app.route('/alumnos', methods=["POST","GET"])
def seccion_alumnos():
    nombre = request.args.get('nombre_profesor', '')
    id_curso = request.args.get('id_curso', '')
    crear_alumno = request.form.get('crear_alumno')
    eliminar_alumno = request.form.get('eliminar_alumno')
    
    if crear_alumno:
        
        print("FORM COMPLETO:", dict(request.form), flush=True)
        try:
            requests.post("http://backend:5000/alumnos/", json={
                "nombre": request.form.get('crear_alumno'),
                "apellido": request.form.get('apellido'),
                "email": request.form.get('email'),
                "padron": request.form.get('padron'),
                "id_curso": request.form.get('id_curso')
            })
        except Exception as e:
            print("Error al crear alumno")

    if eliminar_alumno:
        try:
            requests.delete(f"http://backend:5000/alumnos/{eliminar_alumno}")
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
        r = requests.post("http://backend:5000/alumnos/csv", files={"alumnos": (csv.filename, csv.stream, csv.content_type)})
    except Exception as e:
        print(e)
        pass
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
        response = requests.post("http://backend:5000/usuarios/", json={
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
        requests.delete(f"http://backend:5000/usuarios/{id}")
    except Exception as e:
        pass
    return redirect(url_for('seccion_usuarios',nombre_profesor=nombre_profesor))

# 0. Ruta del Panel Principal (Se activa al entrar a http://127.0.0.1:5000)
@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/menu')
def menu_principal():
    nombre = request.args.get('nombre_profesor', '')
    error_busqueda = request.args.get('error_busqueda')
    return render_template('menu_principal.html',nombre_profesor=nombre, error_busqueda=error_busqueda)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form["nombre_profesor"]
        password = request.form["password"]
        try:
            response = requests.post("http://backend:5000/usuarios/login", json={
                "nombre": nombre,
                "contrasenia": password
            })
            if response.status_code == 200:
                return render_template("menu_principal.html", nombre_profesor=nombre)
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
                requests.delete("http://backend:5000/grupos/alumnos",
    json={"id_grupo": id, "padron_alumno": int(eliminar_alumno)}
)
            except Exception as e:
                print("Error al eliminar alumno del grupo")

    try:
        response = requests.get(f"http://backend:5000/grupos/alumnos/{id}")
        lista_alumnos = response.json()
    except Exception as e:
        print('Hubo un error al obtener los alumnos del grupo')
    return render_template('detalle_grupo.html',eliminar=eliminar_alumno, integrantes=lista_alumnos,nombre_profesor=nombre,ID=id)
@app.route('/listado')
def seccion_listado():
    return render_template('listado.html')
if __name__ == '__main__':
    app.run(debug=True)
