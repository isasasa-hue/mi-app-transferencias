from flask  import Flask, request, redirect, url_for, session
import sqlite3
from crear_table import crear_tabla

app = Flask(__name__)
app.secret_key = 'limpieza2025'

DB = 'transferencias.db'
crear_tabla()

# CSS común para todas las páginas
base_style = """
<style>
    body {
        background-color: #e0f0ff;
        font-family: Arial, sans-serif;
        text-align: center;
        margin: 0;
        padding: 20px;
    }
    h2 {
        color: #004080;
    }
    form, table {
        background-color: white;
        display: inline-block;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px #aaa;
        margin-top: 20px;
        text-align: left;
    }
    table {
        border-collapse: collapse;
    }
    th, td {
        padding: 10px;
        border: 1px solid #ccc;
        text-align: center;
    }
    a {
        display: block;
        margin-top: 20px;
        color: #004080;
        text-decoration: none;
        font-weight: bold;
    }
    a:hover {
        color: #00264d;
    }
    input[type=text], input[type=password], input[type=date], input[type=number] {
        width: 100%;
        padding: 8px;
        margin: 6px 0 12px 0;
        box-sizing: border-box;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 16px;
    }
    input[type=submit] {
        background-color: #004080;
        color: white;
        border: none;
        padding: 10px 25px;
        cursor: pointer;
        font-weight: bold;
        border-radius: 5px;
        font-size: 16px;
    }
    input[type=submit]:hover {
        background-color: #003366;
    }
    .watermark {
    position: fixed;
    top: 10px;
    left: 10px;
    opacity: 0.5;
    font-size: 14px;
    color: #004080;
    font-weight: bold;
    font-family: Arial, sans-serif;
    user-select: none; /* no se puede seleccionar */
    pointer-events: none; /* no interfiere con clicks */
    z-index: 9999;
</style>
"""

def page_template(title, body_html):
    return f'''
    <html>
    <head>
        <title>{title}</title>
        {base_style}
    </head>
    <body>
        <h2>{title}</h2>
        {body_html}
        <div class="watermark">Designed by: Jvandekoppel</div>
    </body>
    </html>
    '''

# --- LOGIN ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('usuario') == 'vale' and request.form.get('clave') == 'limpieza2025':
            session['logueado'] = True
            return redirect(url_for('menu'))
        else:
            msg = '<p style="color:red;">Usuario o clave incorrectos</p>'
            return page_template("Iniciar sesión", msg + login_form())
    return page_template("Iniciar sesión", login_form())

def login_form():
    return '''
    <form method="POST">
        Usuario: <input type="text" name="usuario" required><br>
        Clave: <input type="password" name="clave" required><br>
        <input type="submit" value="Entrar">
    </form>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- MENÚ ---

@app.route('/menu')
def menu():
    if not session.get('logueado'):
        return redirect(url_for('login'))

    body = '''
    <ul style="list-style:none; padding-left:0;">
        <li><a href="/agregar">1. Agregar transferencia</a></li>
        <li><a href="/editar">2. Editar transferencia</a></li>
        <li><a href="/buscar">3. Buscar transferencia</a></li>
        <li><a href="/eliminar">4. Eliminar transferencia</a></li>
        <li><a href="/historial">5. Ver historial</a></li>
        <li><a href="/logout">Salir</a></li>
    </ul>
    '''
    return page_template("Menú Principal", body)

# --- AGREGAR ---

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    mensaje = ''
    if request.method == 'POST':
        numero = request.form.get('numero')
        monto = request.form.get('monto')
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO transferencias (numero, monto) VALUES (?, ?)", (numero, monto))
            conn.commit()
            mensaje = '<p style="color:green;">✅ Transferencia agregada correctamente.</p>'
        except sqlite3.IntegrityError:
            mensaje = '<p style="color:red;">❌ Esa transferencia ya existe.</p>'
        conn.close()
    form = '''
    <form method="POST">
        Número de transferencia: <input type="text" name="numero" required>
        Importe: <input type="number" step="0.01" name="monto" required>
        <input type="submit" value="Guardar">
    </form>
    <a href="/menu">Volver al menú</a>
    '''
    return page_template("Agregar Transferencia", form + mensaje)

# --- EDITAR ---

@app.route('/editar', methods=['GET', 'POST'])
def editar():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    mensaje = ''
    datos = None

    if request.method == 'POST':
        if 'buscar' in request.form:
            numero = request.form.get('numero')
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("SELECT * FROM transferencias WHERE numero = ?", (numero,))
            datos = c.fetchone()
            conn.close()
        elif 'guardar' in request.form:
            numero = request.form.get('numero')
            cliente = request.form.get('cliente', '')
            fecha_pedido = request.form.get('fecha_pedido', '')
            fecha_transferencia = request.form.get('fecha_transferencia', '')
            fecha_retiro = request.form.get('fecha_retiro', '')
            factura = request.form.get('factura', '')
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute('''UPDATE transferencias SET cliente=?, fecha_pedido=?, fecha_transferencia=?, 
                         fecha_retiro=?, factura=? WHERE numero=?''',
                      (cliente, fecha_pedido, fecha_transferencia, fecha_retiro, factura, numero))
            conn.commit()
            conn.close()
            mensaje = '<p style="color:green;">✅ Transferencia actualizada.</p>'

    form_html = '''
    <form method="POST">
        Número de transferencia: <input type="text" name="numero" required>
        <input type="submit" name="buscar" value="Buscar">
    </form>
    '''
    if datos:
        form_html += f'''
        <form method="POST">
            <input type="hidden" name="numero" value="{datos[1]}">
            Cliente: <input type="text" name="cliente" value="{datos[3] or ''}">
            Fecha pedido: <input type="date" name="fecha_pedido" value="{datos[4] or ''}">
            Fecha transferencia: <input type="date" name="fecha_transferencia" value="{datos[5] or ''}">
            Fecha retiro: <input type="date" name="fecha_retiro" value="{datos[6] or ''}">
            N° Factura: <input type="text" name="factura" value="{datos[7] or ''}">
            <input type="submit" name="guardar" value="Guardar cambios">
        </form>
        '''
    form_html += mensaje + '<a href="/menu">Volver al menú</a>'
    return page_template("Editar Transferencia", form_html)

# --- BUSCAR ---

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    if not session.get('logueado'):
        return redirect(url_for('login'))

    mensaje = ''
    resultado = None
    if request.method == 'POST':
        numero = request.form.get('numero')
        monto = request.form.get('monto')
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        if numero:
            c.execute("SELECT * FROM transferencias WHERE numero = ?", (numero,))
        elif monto:
            c.execute("SELECT * FROM transferencias WHERE monto = ?", (monto,))
        else:
            mensaje = '<p style="color:red;">Ingresá número o monto.</p>'
            return page_template("Buscar Transferencia", mensaje + '<a href="/menu">Volver al menú</a>')
        resultado = c.fetchone()
        conn.close()
        if resultado:
            mensaje = f'''
           <form method="POST">
<p>📄 Transferencia encontrada:</p>

<p>Cliente:            {resultado[3] or '-'}</p>
<p>Monto:              {resultado[2] or '-'}</p>
<p>Fecha Pedido:       {resultado[4] or '-'}</p>
<p>Fecha Transfer:     {resultado[5] or '-'}</p>
<p>Fecha Retiro:       {resultado[6] or '-'}</p>
<p>Factura:          {resultado[7] or '-'}</p>
            </form>
            '''
        else:
            mensaje = '<p style="color:red;">❌ Transferencia no encontrada.</p>'

    form_html = '''
    <form method="POST">
        Número: <input type="text" name="numero">
        o Monto: <input type="number" step="0.01" name="monto">
        <input type="submit" value="Buscar">
    </form>
    <a href="/menu">Volver al menú</a>
    '''
    return page_template("Buscar Transferencia", form_html + mensaje)

# --- ELIMINAR con confirmación de contraseña ---

@app.route('/eliminar', methods=['GET', 'POST'])
def eliminar():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    mensaje = ''
    if request.method == 'POST':
        if 'confirmar' not in request.form:
            # Primero pedir número y contraseña
            form_html = '''
            <form method="POST">
                Número de transferencia a eliminar: <input type="text" name="numero" required><br>
                Confirmá tu contraseña: <input type="password" name="clave" required><br>
                <input type="submit" name="confirmar" value="Eliminar">
            </form>
            <a href="/menu">Volver al menú</a>
            '''
            return page_template("Eliminar Transferencia", form_html)
        else:
            numero = request.form.get('numero')
            clave = request.form.get('clave')
            if clave != 'silteamo':
                mensaje = '<p style="color:red;">Clave incorrecta. No se eliminó la transferencia.</p>'
            else:
                conn = sqlite3.connect(DB)
                c = conn.cursor()
                c.execute("SELECT * FROM transferencias WHERE numero = ?", (numero,))
                transferencia = c.fetchone()
                if transferencia:
                    c.execute("DELETE FROM transferencias WHERE numero = ?", (numero,))
                    conn.commit()
                    mensaje = f'<p style="color:green;">✅ Transferencia {numero} eliminada correctamente.</p>'
                else:
                    mensaje = '<p style="color:red;">❌ Número de transferencia no encontrado.</p>'
                conn.close()
            form_html = '''
            <form method="POST">
                Número de transferencia a eliminar: <input type="text" name="numero" required><br>
                Confirmá tu contraseña: <input type="password" name="clave" required><br>
                <input type="submit" name="confirmar" value="Eliminar">
            </form>
            <a href="/menu">Volver al menú</a>
            '''
            return page_template("Eliminar Transferencia", form_html + mensaje)
    else:
        form_html = '''
        <form method="POST">
            Número de transferencia a eliminar: <input type="text" name="numero" required><br>
            Confirmá tu contraseña: <input type="password" name="clave" required><br>
            <input type="submit" name="confirmar" value="Eliminar">
        </form>
        <a href="/menu">Volver al menú</a>
        '''
        return page_template("Eliminar Transferencia", form_html)

# --- HISTORIAL ---

@app.route('/historial')
def historial():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT numero, cliente, monto, fecha_pedido, fecha_transferencia, fecha_retiro, factura FROM transferencias ORDER BY fecha_pedido DESC")
    transferencias = c.fetchall()
    conn.close()
    filas = ''
    for t in transferencias:
        filas += f'''
        <tr>
            <td>{t[0]}</td><td>{t[1] or '-'}</td><td>{t[2] or '-'}</td><td>{t[3] or '-'}</td>
            <td>{t[4] or '-'}</td><td>{t[5] or '-'}</td><td>{t[6] or '-'}</td>
        </tr>
        '''
    tabla = f'''
    <table>
      <tr>
        <th>Número</th><th>Cliente</th><th>Monto</th><th>Fecha Pedido</th>
        <th>Fecha Transferencia</th><th>Fecha Retiro</th><th>Factura</th>
      </tr>
      {filas}
    </table>
    <a href="/menu">Volver al menú</a>
    '''
    return page_template("Historial de Transferencias", tabla)

#if __name__ == '__main__':
 #   app.run(debug=True)
