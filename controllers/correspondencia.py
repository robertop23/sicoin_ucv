# coding: utf8
T.force('es')
from plugin_solidform import SOLIDFORM

@auth.requires(auth.has_membership('recepcionista') or auth.has_membership('master') or auth.has_membership('supervisor') or auth.has_membership('analista'))
def listar_correspondencias():
    session.pag_editar = URL("editar_correspondencia")
    session.pag_previa = URL('listar_correspondencias')
    db.correspondencia.fecha_registro.readable = True
    db.correspondencia.modificado_por.readable = True
    db.correspondencia.registrado_por.readable = True
    links = None 
    fields = [db.correspondencia.nro_de_documento, db.correspondencia.fecha_registro, db.correspondencia.tipo_de_documento,
              db.correspondencia.estatus,db.correspondencia.remitente,db.correspondencia.destinatario,db.correspondencia.asunto,  
              db.correspondencia.registrado_por, db.correspondencia.modificado_por,]
    orderby = [~db.correspondencia.fecha_registro,] 
    if auth.has_membership('recepcionista'):
        deletable = False
        editable=True
        details = True
        create=True
    if auth.has_membership('analista'):
        deletable = False
        editable=True
        details = True
        create=True
    if auth.has_membership('supervisor'):
        deletable = False
        editable=True
        details = True
        create=False
    query = ((db.correspondencia.registrado_por==auth.user.id) | (db.correspondencia.asignado_a==auth.user.id))
    if auth.has_membership('master'):
        deletable = False
        editable=False
        details = True
        create=True
        query = ((db.correspondencia.registrado_por==auth.user.id) | (db.correspondencia.asignado_a==auth.user.id))
    links = [lambda row: A(TAG[''](SPAN(_class="icon icon-list"),SPAN('Histórico', _class="buttontext button", _title="Histórico")), _class="w2p_trap button btn popup", _href=URL('ver_historico', args=[row.id])),
             lambda row: A(TAG[''](SPAN(_class="icon icon-user"),SPAN('CC a', _class="buttontext button", _title="CC a")), _class="w2p_trap button btn popup", _href=URL('agregarCorrespondenciaMultiple2', args=[row.id]))]
    grid = SQLFORM.grid(query, fields = fields, user_signature=False, selectable = lambda ids: reporte_entregas(ids),deletable=deletable, editable=editable, details = details,create=create, csv=False, orderby = orderby, links = links, paginate = 100)
    return dict(grid = grid)

@auth.requires(auth.has_membership('recepcionista') or auth.has_membership('supervisor') or auth.has_membership('master'))
def listar_correspondencias_departamento():
    #Corrige las busquedas por nombre, devolviendo el id y reconstruyendo el request
    #corregirBusquedas()
    session.pag_editar = URL("editar_correspondencia_departamento")
    session.pag_previa = URL('listar_correspondencias_departamento') 
    db.correspondencia.modificado_por.readable = True
    db.correspondencia.registrado_por.readable = True
    fields = [db.correspondencia.nro_de_documento,db.correspondencia.fecha_registro,
              db.correspondencia.estatus,db.correspondencia.remitente,
              db.correspondencia.destinatario,db.correspondencia.asunto, 
              db.correspondencia.registrado_por, db.correspondencia.modificado_por,]
    orderby = [~db.correspondencia.fecha_registro,] 
    deletable = False
    editable=True
    details = True
    create=False
    db.correspondencia.nro_de_documento.writable = False
    db.correspondencia.fecha_registro.writable = False
    db.correspondencia.tipo_de_documento.writable = False
    db.correspondencia.remitente.writable = False
    db.correspondencia.departamento_origen.writable = False
    db.correspondencia.destinatario.writable = False
    db.correspondencia.departamento_destino.writable = False
    db.correspondencia.asunto.writable = False
    db.correspondencia.registrado_por.writable = False
    links = [lambda row: A(TAG[''](SPAN(_class="icon icon-list"),SPAN('Histórico', _class="buttontext button", _title="Histórico")), _class="w2p_trap button btn popup", _href=URL('ver_historico', args=[row.id]))]
    query = (db.correspondencia.departamento_destino==auth.user.departamento)|(db.correspondencia.departamento_origen==auth.user.departamento)
    #estatus = db.estatus.tipo_estatus == "archivado"
    #constraints = {'db.correspondencia.departamento_destino':auth.user.departamento,
    #               'db.correspondencia.departamento_origen':auth.user.departamento}
    grid = SQLFORM.grid(query, fields = fields, user_signature=False, deletable=deletable, editable=editable, 
                        details = details,create=create, csv=False, orderby = orderby, links = links)
    return dict(grid = grid)      
      
@auth.requires(auth.has_membership('master'))
def listar_correspondencias_master(): 
    session.pag_previa = URL('listar_correspondencias_master') 
    fields = [db.correspondencia.nro_de_documento,db.correspondencia.fecha_registro,db.correspondencia.estatus,db.correspondencia.remitente,db.correspondencia.destinatario,db.correspondencia.asunto,db.correspondencia.registrado_por, db.correspondencia.modificado_por,]
    orderby = [~db.correspondencia.fecha_registro, db.correspondencia.departamento_origen, db.correspondencia.departamento_origen] 
    deletable = False
    editable=False
    details = True
    create=False
    db.correspondencia.registrado_por.writable = False
    db.correspondencia.modificado_por.writable = False
    links = [lambda row: A(TAG[''](SPAN(_class="icon icon-list"),SPAN('Histórico', _class="buttontext button", _title="Histórico")), _class="w2p_trap button btn popup", _href=URL('ver_historico', args=[row.id]))]
    query =db.correspondencia 
    grid = SQLFORM.grid(query, fields = fields, user_signature=False, deletable=deletable, editable=editable, 
                        details = details,create=create, csv=False, orderby = orderby, links = links)
    return dict(grid = grid)

@auth.requires(auth.has_membership('recepcionista') or auth.has_membership('master') or auth.has_membership('supervisor') or auth.has_membership('analista'))
def agregar_correspondencia():
    session.pag_previa = URL('agregar_correspondencia') 
    request_fields = request.vars.fields or 'default'
    asignados = usuariosDepartamento()

################################ The core ######################################
    # Specify structured fields for the multi-line form layout.
    # A "None" indicates an empty line over which the precedent line spans
    if request_fields == 'default':
        fields = [
                  ['nro_de_documento', 'fecha_correspondencia'],
                  ['tipo_de_documento', 'estatus'],
                  'asunto',
                  ['departamento_origen', 'departamento_destino'],
                  [None, None],
                  ['remitente', 'destinatario'],
                  [None, 'observaciones'],
                  'asignado_a'
                  ]
    
    form = SOLIDFORM(db.correspondencia, fields=fields, tabla = auth.archive)
    if form.process(onsuccess=auth.archive).accepted:
        session.flash = 'registro procesado con éxito'
        redirect(URL('/listar_correspondencias'))
    style = STYLE("""input[type="text"], textarea {width:100%; max-height: 50px;}
                     .w2p_fw {padding-right: 10px; max-width:100%;}
                     .w2p_fl {background: #eee;}
                     .string {max-width: 300px;}
                     .date {max-width: 80px;}""")
    return dict(asignados = asignados,
                form=DIV(style, form),
                #form__factory=form_factory, form__readonly=form_readonly, form__edit=form_edit,
                form_args=DIV(A('fields=default', _href=URL(vars={'fields': 'default'})), ' ',
                               ))

@auth.requires(auth.has_membership('recepcionista') or auth.has_membership('master') or auth.has_membership('supervisor') or auth.has_membership('analista'))
def ver_correspondencia():
    id = request.args(1)
    tabla = request.args(0)
    fields = [
                  ['nro_de_documento', 'fecha_correspondencia'],
                  ['tipo_de_documento', 'estatus'],
                  'asunto',
                  ['departamento_origen', 'departamento_destino'],
                  [None, None],
                  ['remitente', 'destinatario'],
                  [None, 'observaciones'],
                  ['asignado_a', 'registrado_por'],
                  ['modificado_el', 'modificado_por'],
                  ]

    if (tabla == "activo"):
        db.correspondencia.modificado_el.readable = True
        db.correspondencia.modificado_por.readable = True
        correspondencia = db(db.correspondencia.id==id).select().first()
        form = SOLIDFORM(db.correspondencia, correspondencia, fields=fields, showid=False, readonly=True)
    elif (tabla == "archivo"):
        db.correspondencia_archive.modificado_el.readable = True
        db.correspondencia_archive.modificado_por.readable = True
        correspondencia = db(db.correspondencia_archive.id==id).select().first()
        form = SOLIDFORM(db.correspondencia_archive, correspondencia, fields=fields, showid=False, readonly=True)
    if form.accepts(request.vars, session):
        session.flash = 'registro procesado con éxito'
        redirect(URL('/listar_correspondencias'))
     
    style = STYLE("""input[type="text"], textarea {width:100%; max-height: 50px;}
                     .w2p_fw {padding-right: 10px; max-width:100%;}
                     .w2p_fl {background: #eee;}
                     .string {max-width: 300px;}
                     .date {max-width: 80px;}""")
    return dict(id = id, form=DIV(style, form),
                #form__factory=form_factory, form__readonly=form_readonly, form__edit=form_edit,
                form_args=DIV(A('fields=default', _href=URL(vars={'fields': 'default'})), ' ',

                               ))
                            
@auth.requires(auth.has_membership('recepcionista') or auth.has_membership('master') or auth.has_membership('supervisor') or auth.has_membership('analista'))
def editar_correspondencia():
    session.pag_previa = URL('editar_correspondencia') 
    id = request.args(0)
    asignados = usuariosDepartamento()
    fields = [
                  ['nro_de_documento', 'fecha_correspondencia'],
                  ['tipo_de_documento', 'estatus'],
                  'asunto',
                  ['departamento_origen', 'departamento_destino'],
                  [None, None],
                  ['remitente', 'destinatario'],
                  [None, 'observaciones'],
                  ['asignado_a'],
                  
                  ]
    if auth.has_membership('analista'):
        db.correspondencia.nro_de_documento.readable = True
        db.correspondencia.nro_de_documento.writable = False
        db.correspondencia.fecha_correspondencia.readable = True
        db.correspondencia.fecha_correspondencia.writable = False
        db.correspondencia.tipo_de_documento.readable = True
        db.correspondencia.tipo_de_documento.writable = False
        db.correspondencia.asunto.readable = True
        db.correspondencia.asunto.writable = False
        db.correspondencia.departamento_origen.readable = True
        db.correspondencia.departamento_origen.writable = False
        db.correspondencia.departamento_destino.readable = True
        db.correspondencia.departamento_destino.writable = False
        db.correspondencia.remitente.readable = True
        db.correspondencia.remitente.writable = False
        db.correspondencia.destinatario.readable = True
        db.correspondencia.destinatario.writable = False        
        db.correspondencia.asignado_a.readable = True
        db.correspondencia.asignado_a.writable = False
    if auth.has_membership('supervisor'):
        db.correspondencia.nro_de_documento.readable = True
        db.correspondencia.nro_de_documento.writable = False
        db.correspondencia.fecha_correspondencia.readable = True
        db.correspondencia.fecha_correspondencia.writable = False
        db.correspondencia.tipo_de_documento.readable = True
        db.correspondencia.tipo_de_documento.writable = False
        db.correspondencia.asunto.readable = True
        db.correspondencia.asunto.writable = False
        db.correspondencia.departamento_origen.readable = True
        db.correspondencia.departamento_origen.writable = False
        db.correspondencia.departamento_destino.readable = True
        db.correspondencia.departamento_destino.writable = False
        db.correspondencia.remitente.readable = True
        db.correspondencia.remitente.writable = False
        db.correspondencia.destinatario.readable = True
        db.correspondencia.destinatario.writable = False        
        db.correspondencia.asignado_a.readable = True
        db.correspondencia.asignado_a.writable = False
    #db.correspondencia.modificado_por.writable = True
    #db.correspondencia.modificado_el.writable = True
    correspondencia = db(db.correspondencia.id==id).select().first()
    form = SOLIDFORM(db.correspondencia, correspondencia, fields=fields, showid=False, readonly=False)
    if form.process(onsuccess=auth.archive).accepted:
        session.flash = 'registro modificado con éxito'
        redirect(URL('/listar_correspondencias'))
     
    style = STYLE("""input[type="text"], textarea {width:100%; max-height: 50px;}
                     .w2p_fw {padding-right: 10px; max-width:100%;}
                     .w2p_fl {background: #eee;}
                     .string {max-width: 300px;}
                     .date {max-width: 80px;}""")
    return dict(asignados = asignados,
                 form=DIV(style, form),
                 #form__factory=form_factory, form__readonly=form_readonly, form__edit=form_edit,
                 form_args=DIV(A('fields=default', _href=URL(vars={'fields': 'default'})), ' ',

                               ))

@auth.requires(auth.has_membership('recepcionista') or auth.has_membership('supervisor') or auth.has_membership('master'))
def ver_correspondencia_departamento():
    id = request.args(0)
    fields = [
                  ['nro_de_documento', 'fecha_correspondencia'],
                  ['tipo_de_documento', 'estatus'],
                  'asunto',
                  ['departamento_origen', 'departamento_destino'],
                  [None, None],
                  ['remitente', 'destinatario'],
                  [None, 'observaciones'],
                  ['asignado_a', 'registrado_por'],
                  ['modificado_el', 'modificado_por'],
                  ]
    db.correspondencia.nro_de_documento.writable = False
    db.correspondencia.fecha_registro.writable = False
    db.correspondencia.tipo_de_documento.writable = False
    db.correspondencia.remitente.writable = False
    db.correspondencia.departamento_origen.writable = False
    db.correspondencia.destinatario.writable = False
    db.correspondencia.departamento_destino.writable = False
    db.correspondencia.asunto.writable = False
    db.correspondencia.registrado_por.writable = False
    db.correspondencia.modificado_el.readable = True
    db.correspondencia.modificado_por.readable = True
    correspondencia = db(db.correspondencia.id==id).select().first()
    form = SOLIDFORM(db.correspondencia, correspondencia, fields=fields, showid=False, readonly=True)

    if form.accepts(request.vars, session):
        session.flash = 'registro procesado con éxito'
        redirect(URL('/listar_correspondencias'))
     
    style = STYLE("""input[type="text"], textarea {width:100%; max-height: 50px;}
                     .w2p_fw {padding-right: 10px; max-width:100%;}
                     .w2p_fl {background: #eee;}
                     .string {max-width: 300px;}
                     .date {max-width: 80px;}""")
    return dict(id = id, form=DIV(style, form),
                #form__factory=form_factory, form__readonly=form_readonly, form__edit=form_edit,
                form_args=DIV(A('fields=default', _href=URL(vars={'fields': 'default'})), ' ',
                               ))
                              
@auth.requires(auth.has_membership('recepcionista') or auth.has_membership('supervisor') or auth.has_membership('master'))
def editar_correspondencia_departamento():
    session.pag_previa = URL('editar_correspondencias_departamento') 
    id = request.args(0)
    asignados = usuariosDepartamento()
    fields = [
                  ['nro_de_documento', 'fecha_correspondencia'],
                  ['tipo_de_documento', 'estatus'],
                  'asunto',
                  ['departamento_origen', 'departamento_destino'],
                  [None, None],
                  ['remitente', 'destinatario'],
                  [None, 'observaciones'],
                  'asignado_a'
                  ]
    db.correspondencia.nro_de_documento.readable = True
    db.correspondencia.nro_de_documento.writable = False
    db.correspondencia.fecha_correspondencia.readable = True
    db.correspondencia.fecha_correspondencia.writable = False
    db.correspondencia.tipo_de_documento.readable = True
    db.correspondencia.tipo_de_documento.writable = False
    db.correspondencia.asunto.readable = True
    db.correspondencia.asunto.writable = False
    db.correspondencia.departamento_origen.readable = True
    db.correspondencia.departamento_origen.writable = False
    db.correspondencia.departamento_destino.readable = True
    db.correspondencia.departamento_destino.writable = False
    db.correspondencia.remitente.readable = True
    db.correspondencia.remitente.writable = False
    db.correspondencia.destinatario.readable = True
    db.correspondencia.destinatario.writable = False        
    db.correspondencia.asignado_a.readable = True
    db.correspondencia.asignado_a.writable = True
    
    correspondencia = db(db.correspondencia.id==id).select().first()
    form = SOLIDFORM(db.correspondencia, correspondencia, fields=fields, showid=False, readonly=False)
    
    if form.process(onsuccess=auth.archive).accepted:
        session.flash = 'registro procesado con éxito'
        redirect(URL('/listar_correspondencias_departamento'))     

    style = STYLE("""input[type="text"], textarea {width:100%; max-height: 50px;}
                     .w2p_fw {padding-right: 10px; max-width:100%;}
                     .w2p_fl {background: #eee;}
                     .string {max-width: 300px;}
                     .date {max-width: 80px;}""")
    return dict(asignados = asignados,
                form=DIV(style, form),
                #form__factory=form_factory, form__readonly=form_readonly, form__edit=form_edit,
                form_args=DIV(A('fields=default', _href=URL(vars={'fields': 'default'})), ' ',
                               ))
                               
def ver_historico():
    id_registro = request.args(0)
    #<a href="/sicoin/correspondencia/ver_correspondencia/4" class="w2p_trap button btn"><span class="icon magnifier icon-zoom-in"></span><span title="View" class="buttontext button">Vista</span></a>
    db.correspondencia.id.represent= lambda value, row: CENTER(A(TAG[''](SPAN(_class="icon magnifier icon-zoom-in"),SPAN('', _class="buttontext button")),_class="w2p_trap button btn", _href = URL('ver_correspondencia/activo', args = str(value))))                                                                   
                                                                          
    rows_actual = db(db.correspondencia.id==id_registro).select(db.correspondencia.modificado_el,
                                                                             db.correspondencia.modificado_por,
                                                                             db.correspondencia.nro_de_documento,
                                                                             db.correspondencia.tipo_de_documento,
                                                                             db.estatus.tipo_estatus, 
                                                                             db.correspondencia.remitente,
                                                                             db.correspondencia.departamento_origen,
                                                                             db.correspondencia.destinatario,
                                                                             db.correspondencia.departamento_destino,
                                                                             db.correspondencia.asunto,
                                                                             db.correspondencia.observaciones,
                                                                             db.correspondencia.id,
                                                                     left=[db.estatus.on(db.estatus.id==db.correspondencia.estatus)])
    db.correspondencia_archive.id.represent= lambda value, row: CENTER(A(TAG[''](SPAN(_class="icon magnifier icon-zoom-in"),SPAN('', _class="buttontext button")),_class="w2p_trap button btn", _href = URL('ver_correspondencia/archivo', args = str(value))))
    rows = db(db.correspondencia_archive.current_record==id_registro).select(db.correspondencia_archive.modificado_el,
                                                                             db.correspondencia_archive.modificado_por,
                                                                             db.correspondencia_archive.nro_de_documento,
                                                                             db.correspondencia_archive.tipo_de_documento,
                                                                             db.estatus.tipo_estatus, 
                                                                             db.correspondencia_archive.remitente,
                                                                             db.correspondencia_archive.departamento_origen,
                                                                             db.correspondencia_archive.destinatario,
                                                                             db.correspondencia_archive.departamento_destino,
                                                                             db.correspondencia_archive.asunto,
                                                                             db.correspondencia_archive.observaciones,
                                                                             db.correspondencia_archive.id,
                                                                     left=[db.estatus.on(db.estatus.id==db.correspondencia_archive.estatus)])

    headers = {'correspondencia_archive.modificado_el':{'label':'Modificado el',
                       'class':'', #class name of the header
                       'width':'', #width in pixels or %
                       'truncate': 16, #truncate the content to...
                       'selected': False #agregate class selected to this column
                       },
               'correspondencia_archive.modificado_por':{'label':'Modificado por',
                            'class':'', #class name of the header
                            'width':'', #width in pixels or %
                            'truncate': 16, #truncate the content to...
                            'selected': False #agregate class selected to this column
                            },
               'correspondencia_archive.nro_de_documento':{'label':'Nro Documento',
                            'class':'', #class name of the header
                            'width':'', #width in pixels or %
                            'truncate': 16, #truncate the content to...
                            'selected': False #agregate class selected to this column
                            },
               'correspondencia_archive.tipo_de_documento':{'label':'Tipo Documento',
                            'class':'', #class name of the header
                            'width':'', #width in pixels or %
                            'truncate': 16, #truncate the content to...
                            'selected': False #agregate class selected to this column
                            },
               'estatus.tipo_estatus':{'label':'Estatus',
                            'class':'', #class name of the header
                            'width':'', #width in pixels or %
                            'truncate': 16, #truncate the content to...
                            'selected': False #agregate class selected to this column
                            },
               'correspondencia_archive.remitente':{'label':'Remitente',
                            'class':'', #class name of the header
                            'width':'', #width in pixels or %
                            'truncate': 50, #truncate the content to...
                            'selected': False #agregate class selected to this column
                            },
               'correspondencia_archive.departamento_origen':{'label':'Dpto. Origen',
                            'class':'', #class name of the header
                            'width':'', #width in pixels or %
                            'truncate': 16, #truncate the content to...
                            'selected': False #agregate class selected to this column
                            },
               'correspondencia_archive.destinatario':{'label':'Destinatario',
                            'class':'', #class name of the header
                            'width':'', #width in pixels or %
                            'truncate': 60, #truncate the content to...
                            'selected': False #agregate class selected to this column
                            },
               'correspondencia_archive.departamento_destino':{'label':'Depto. Destino',
                            'class':'', #class name of the header
                            'width':'', #width in pixels or %
                            'truncate': 16, #truncate the content to...
                            'selected': False #agregate class selected to this column
                            },
                'correspondencia_archive.asunto':{'label':'Asunto',
                            'class':'', #class name of the header
                            'width':'15%', #width in pixels or %
                            'truncate': 50, #truncate the content to...
                            'selected': False #agregate class selected to this column
                            },
                'correspondencia_archive.observaciones':{'label':'Observaciones',
                            'class':'', #class name of the header
                            'width':'20%', #width in pixels or %
                            'truncate': 50, #truncate the content to...
                            'selected': False #agregate class selected to this column
                            },
                'correspondencia_archive.id':{'label':'Acción',
                            'class':'', #class name of the header
                            'width':'10%', #width in pixels or %
                            'truncate': 50, #truncate the content to...
                            'selected': False, #agregate class selected to this column
                            'align': 'center'
                            },
           }
    tabla = SQLTABLE(rows, headers = headers)
    tabla_actual = SQLTABLE(rows_actual, truncate = 100)
    return dict(table=tabla, tabla_actual =tabla_actual,id = id)
    
@auth.requires(auth.has_membership('recepcionista') or auth.has_membership('master') or auth.has_membership('supervisor') or auth.has_membership('analista'))
def listar_movimientos():
    session.pag_previa = URL('listar_movimientos') 
    links = None 
    fields = [db.correspondencia.nro_de_documento, db.correspondencia.tipo_de_documento,db.correspondencia.fecha_registro,
              db.correspondencia.estatus,db.correspondencia.remitente,db.correspondencia.destinatario,db.correspondencia.asunto,]
    orderby = ['correspondencia.fecha_registro',] 
    deletable = False
    editable=True
    details = True
    create=True
    documento = db(db.documento.tipo_de_documento=="movimiento").select(db.documento.id).first()
    id_documento_movimiento = documento['id']
    query = (((db.correspondencia.registrado_por==auth.user.id) | (db.correspondencia.asignado_a==auth.user.id)) & (db.correspondencia.tipo_de_documento==id_documento_movimiento))
    links = [lambda row: A(TAG[''](SPAN(_class="icon icon-list"),SPAN('Histórico', _class="buttontext button", _title="Histórico")), _class="w2p_trap button btn popup", _href=URL('ver_historico', args=[row.id]))
            ]
    grid = SQLFORM.grid(query, fields = fields, selectable= lambda ids: reporte_entrega_movimiento(ids), user_signature=False, deletable=deletable, editable=editable, details = details,create=create, csv=False, orderby = orderby, links = links)
    return dict(grid = grid)
    
def reporte_entrega_movimiento(ids):
    if not ids:
        session.flash='No has seleccionado ninguna correspondencia'
    else: 
        #import gluon.contenttype
        al_reporte=db(db.correspondencia.id.belongs(ids)).select(db.correspondencia.nro_de_documento, db.correspondencia.departamento_destino)
        headers = {'correspondencia.nro_de_documento':{'label':'Nro. Documento',
                       'class':'', #class name of the header
                       'width':'', #width in pixels or %
                       'truncate': 16, #truncate the content to...
                       'selected': False #agregate class selected to this column
                       },
               'correspondencia.departamento_destino':{'label':'Departamento Destino',
                            'class':'', #class name of the header
                            'width':'', #width in pixels or %
                            'truncate': 16, #truncate the content to...
                            'selected': False #agregate class selected to this column
                            },           
           }
        tabla_actual = SQLTABLE(al_reporte, truncate = 100, headers = headers)
        session.reporte_movimiento = tabla_actual
        session.flash="Reporte Generado"
        #response.headers['Content-Type']=gluon.contenttype.contenttype('.js')
        #return 'alert("alerta en javascript");'
        #response.render();
        #session.flash=al_reporte[1]        
	return ()
	
def reporte_entregas(ids):
    if not ids:
        session.flash='No has seleccionado ninguna correspondencia'
    else: 
        #import gluon.contenttype
	from time import strftime
	db.correspondencia.fecha_correspondencia.represent = lambda value, row : value.strftime('%d-%m-%Y')
        al_reporte=db(db.correspondencia.id.belongs(ids)).select(db.correspondencia.nro_de_documento, 
                                                                 db.correspondencia.departamento_destino,
								 db.correspondencia.asunto, 
                                                                 db.correspondencia.fecha_correspondencia)
        headers = {'correspondencia.nro_de_documento':{'label':'Nro. Documento',
                       'class':'', #class name of the header
                       'width':'', #width in pixels or %
                       'truncate': 30, #truncate the content to...
                       'selected': False #agregate class selected to this column
                       },
               'correspondencia.departamento_destino':{'label':'Departamento Destino',
                            'class':'', #class name of the header
                            'width':'', #width in pixels or %
                            'truncate': 40, #truncate the content to...
                            'selected': False #agregate class selected to this column
                            },
	       'correspondencia.asunto':{'label':'Asunto',
			    'class':'',
			    'width':'',
			    'truncate':40,
			    'selected': False,
	  },
	       'correspondencia.fecha_correspondencia':{ 'label': 'Fecha',
			    'class': '',
                            'width':'',
                            'truncate':20,
                            'selected': False
			},
           }        
	tabla_actual = SQLTABLE(al_reporte, truncate = 100, headers = headers)
        session.reporte = tabla_actual
        #response.headers['Content-Type']=gluon.contenttype.contenttype('.js')
        #return 'alert("alerta en javascript");'
        #response.render();
        #session.flash=al_reporte[1]        
	return ()

def devolver_mes(mes):
    if mes == 1:
        mes= "enero"
    elif mes == 2:
        mes= "febrero"
    elif mes == 3:
        mes= "marzo"
    elif mes == 4:
        mes= "abril"
    elif mes == 5:
        mes= "mayo"
    elif mes == 6:
        mes= "junio"
    elif mes == 7:
        mes= "julio"
    elif mes == 8:
        mes= "agosto"
    elif mes == 9:
        mes= "septiembre"    
    elif mes == 10:
        mes= "octubre"
    elif mes == 11:
        mes= "noviembre"
    else:
        mes = "diciembre"
    return mes
    
def usuariosDepartamento():
    options = [OPTION(t.first_name + " " + t.last_name,_value=t.id) for t in db(db.auth_user.departamento==auth.user.departamento).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name)]
    options.insert(0, OPTION(_value=""))
    usuarios = SELECT(*options, _name="asignado_a", _id="correspondencia_asignados", _class="generic-widget")
    #usuarios = db(db.auth_user.departamento==auth.user.departamento).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name)
    return usuarios

def corregirBusquedas():
    if (request.vars['keywords']) and ('correspondencia.tipo_de_documento =' in request.vars['keywords']):
        documento = request.vars['keywords'].split('= "')[1].split('"')[0]
        id_tipodocumento = buscarTipoDocumento(documento)
        if id_tipodocumento:
            request.vars['keywords'] = 'correspondencia.tipo_de_documento = "' + id_tipodocumento + '"'
        else:
            request.vars['keywords'] = 'correspondencia.tipo_de_documento = "0"'
    if (request.vars['keywords']) and ('correspondencia.estatus =' in request.vars['keywords']):
        estatus = request.vars['keywords'].split('= "')[1].split('"')[0]
        id_estatus = buscarEstatus(estatus)
        if id_estatus:
            request.vars['keywords'] = 'correspondencia.estatus = "' + id_estatus + '"'
        else:
            request.vars['keywords'] = 'correspondencia.estatus = "0"'
    if (request.vars['keywords']) and ('correspondencia.asignado_a =' in request.vars['keywords']):
        usuario = request.vars['keywords'].split('= "')[1].split('"')[0]
        id_usuario = buscarUsuario(usuario)
        if id_usuario:
            request.vars['keywords'] = 'correspondencia.asignado_a = "' + id_usuario + '"'
        else:
            request.vars['keywords'] = 'correspondencia.asignado_a = "0"'
    if (request.vars['keywords']) and ('correspondencia.departamento_origen =' in request.vars['keywords']):
        departamento = request.vars['keywords'].split('= "')[1].split('"')[0]
        id_departamento = buscarDepartamento(departamento)
        if id_departamento:
            request.vars['keywords'] = 'correspondencia.departamento_origen = "' + id_departamento + '"'
        else:
            request.vars['keywords'] = 'correspondencia.departamento_origen = "0"'
    if (request.vars['keywords']) and ('correspondencia.departamento_destino =' in request.vars['keywords']):
        departamento = request.vars['keywords'].split('= "')[1].split('"')[0]
        id_departamento = buscarDepartamento(departamento)
        if id_departamento:
            request.vars['keywords'] = 'correspondencia.departamento_destino = "' + id_departamento + '"'
        else:
            request.vars['keywords'] = 'correspondencia.departamento_destino = "0"'
    return None

def buscarTipoDocumento(tipodocumento):
    busqueda = "%" + tipodocumento + "%"
    try:
        id_tipodocumento = db(db.documento.tipo_de_documento.like(busqueda)).select(db.documento.id).first()
        if id_tipodocumento:
            return str(id_tipodocumento['id'])
    except:
        return None
    
def buscarEstatus(estatus):
    busqueda = "%" + estatus + "%"
    try:
        id_estatus = db(db.estatus.tipo_estatus.like(busqueda)).select(db.estatus.id).first()
        if id_estatus:
            return str(id_estatus['id'])
    except:
        return None
    
def buscarUsuario(usuario):
    busqueda = "%" + usuario + "%"
    try:
        id_usuario = db((db.auth_user.first_name.like(busqueda)) | (db.auth_user.last_name.like(busqueda))).select(db.auth_user.id).first()
        if id_usuario:
            return str(id_usuario['id'])
    except:
        return None
    
def buscarDepartamento(departamento):
    busqueda = "%" + departamento + "%"
    try:
        id_departamento = db(db.departamento.departamento.like(busqueda)).select(db.departamento.id).first()
        if id_departamento:
            return str(id_departamento['id'])
    except:
        return None
    
def correspondenciasDependencia():
    session.documento = ''
    session.dependencia = ''
    form = SQLFORM.factory(Field('documento',label = 'Tipo de Documento', requires= IS_IN_DB(db, db.documento.id, '%(tipo_de_documento)s', 
                                                                                             zero ='Seleccione un tipo de documento')),
                           Field('dependencia', requires= IS_IN_DB(db, db.dependencia.id, '%(dependencia)s',
                                                                   zero ='Seleccione una dependencia')),
                           submit_button='Enviar')
    #form = SQLFORM.factory(db.documento, db.dependencia)
    if form.process().accepted:
        session.documento = form.vars.documento
        session.dependencia = form.vars.dependencia
        redirect(URL('/agregarCorrespondenciaMultiple'))
    else:
        session.flash='Ha ocurrido un error'
    return dict(form = form)
    
def agregarCorrespondenciaMultiple():
    request_fields = request.vars.fields or 'default'

################################ The core ######################################
    # Specify structured fields for the multi-line form layout.
    # A "None" indicates an empty line over which the precedent line spans
    if request_fields == 'default':
        fields = [
                  ['nro_de_documento', 'fecha_correspondencia'],
                  ['tipo_de_documento', 'estatus'],
                  'asunto',
                  [None, None],
                  ['remitente', 'destinatario'],
                  [None, 'observaciones'],
                  ]
    form = SOLIDFORM(db.correspondencia, fields=fields, tabla = auth.archive)
    if form.process(onsuccess=auth.archive).accepted:
        db.rollback()
        usuario = db(db.auth_user.departamento==auth.user.departamento).select(db.auth_user.departamento).first()
        departamentoUsuario = db(db.departamento.id==usuario['departamento']).select(db.departamento.id).first()
        documento = db(db.documento.id==session.documento).select(db.documento.tipo_de_documento).first()
        dependencia = db(db.dependencia.id==session.dependencia).select(db.dependencia.id).first()
        departamentos = db(db.departamento.dependencia==session.dependencia).select(db.departamento.id)
        db.correspondencia.destinatario.readable = False
        db.correspondencia.destinatario.writable = False
        for departamento in departamentos:
            if departamentoUsuario['id'] == departamento['id']:
                continue
            else:
                db.correspondencia.insert(nro_de_documento = form.vars.nro_de_documento, fecha_correspondencia = form.vars.fecha_correspondencia,
                                      tipo_de_documento = form.vars.tipo_de_documento, estatus = form.vars.estatus,
                                      remitente = form.vars.remitente, departamento_origen = departamentoUsuario['id'],
                                      destinatario = form.vars.destinatario, departamento_destino = departamento['id'],
                                      asunto = form.vars.asunto, observaciones = form.vars.observaciones )
        
        session.flash = 'Han sido registrado los documento con éxito'
        redirect(URL('/listar_correspondencias'))
    style = STYLE("""input[type="text"], textarea {width:100%; max-height: 50px;}
                     .w2p_fw {padding-right: 10px; max-width:100%;}
                     .w2p_fl {background: #eee;}
                     .string {max-width: 300px;}
                     .date {max-width: 80px;}""")
    return dict(form=DIV(style, form),
                #form__factory=form_factory, form__readonly=form_readonly, form__edit=form_edit,
                form_args=DIV(A('fields=default', _href=URL(vars={'fields': 'default'})), ' ',
                               ))

def agregarCorrespondenciaMultiple2():
    options = [OPTION(t.first_name + " " + t.last_name,_value=t.id) for t in db(db.auth_user.departamento).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name)]
    usuarios = SELECT(*options, _name="usuarios", _class="chzn-select", _multiple='', _style="width:400px")
    error = ''
    if request.vars['formcc'] and request.vars['usuarios']:
        usuarios = request.vars['usuarios']
        id_correspondencia = request.args(0)
        correspondencia = db.correspondencia[id_correspondencia]  
        for usuario in usuarios:
            usuario = int(usuario)
            registro_usuario = db(db.auth_user.id==usuario).select(db.auth_user.departamento).first()
            id_correspondencia_nueva = db.correspondencia.insert(**db.correspondencia._filter_fields(correspondencia))
            correspondencia_nueva = db.correspondencia(id_correspondencia)
            correspondencia_nueva.update_record(fecha_registro = request.now, asignado_a = usuario,
                                                registrado_por = auth.user.id, modificado_por = auth.user.id,
                                                departamento_destino = registro_usuario['departamento'],
                                                modificado_el = request.now)
        session.flash = 'Copias creadas con éxito'
        redirect(URL('/listar_correspondencias'))
    if request.vars['formcc'] and not request.vars['usuarios']:
        error = DIV('Seleccione al menos un usuario', _class="error", _style="display: inline-block; ")
        print request.vars['usuarios']
    
    return dict(usuarios = usuarios, error = error)

def ver_actual():
    try:
        id_registro = request.args(0)
        rows = db(db.correspondencia.id==id_registro).select(db.correspondencia.modificado_el,
                                                                                 db.correspondencia.modificado_por,
                                                                                 db.correspondencia.nro_de_documento,
                                                                                 db.correspondencia.tipo_de_documento,
                                                                                 db.estatus.tipo_estatus, 
                                                                                 db.correspondencia.remitente,
                                                                                 db.correspondencia.departamento_origen,
                                                                                 db.correspondencia.destinatario,
                                                                                 db.correspondencia.departamento_destino,
                                                                                 db.correspondencia.asunto,
                                                                                 db.correspondencia.observaciones,
                                                                         left=[db.estatus.on(db.estatus.id==db.correspondencia.estatus)])
    
        headers = {'correspondencia.modificado_el':{'label':'Modificado el',
                           'class':'', #class name of the header
                           'width':'', #width in pixels or %
                           'truncate': 16, #truncate the content to...
                           'selected': False #agregate class selected to this column
                           },
                   'correspondencia.modificado_por':{'label':'Modificado por',
                                'class':'', #class name of the header
                                'width':'', #width in pixels or %
                                'truncate': 16, #truncate the content to...
                                'selected': False #agregate class selected to this column
                                },
                   'correspondencia.nro_de_documento':{'label':'Nro Documento',
                                'class':'', #class name of the header
                                'width':'', #width in pixels or %
                                'truncate': 16, #truncate the content to...
                                'selected': False #agregate class selected to this column
                                },
                   'correspondencia.tipo_de_documento':{'label':'Tipo Documento',
                                'class':'', #class name of the header
                                'width':'', #width in pixels or %
                                'truncate': 16, #truncate the content to...
                                'selected': False #agregate class selected to this column
                                },
                   'estatus.tipo_estatus':{'label':'Estatus',
                                'class':'', #class name of the header
                                'width':'', #width in pixels or %
                                'truncate': 16, #truncate the content to...
                                'selected': False #agregate class selected to this column
                                },
                   'correspondencia.remitente':{'label':'Remitente',
                                'class':'', #class name of the header
                                'width':'', #width in pixels or %
                                'truncate': 50, #truncate the content to...
                                'selected': False #agregate class selected to this column
                                },
                   'correspondencia.departamento_origen':{'label':'Dpto. Origen',
                                'class':'', #class name of the header
                                'width':'', #width in pixels or %
                                'truncate': 16, #truncate the content to...
                                'selected': False #agregate class selected to this column
                                },
                   'correspondencia.destinatario':{'label':'Destinatario',
                                'class':'', #class name of the header
                                'width':'', #width in pixels or %
                                'truncate': 60, #truncate the content to...
                                'selected': False #agregate class selected to this column
                                },
                   'correspondencia.departamento_destino':{'label':'Depto. Destino',
                                'class':'', #class name of the header
                                'width':'', #width in pixels or %
                                'truncate': 16, #truncate the content to...
                                'selected': False #agregate class selected to this column
                                },
                    'correspondencia.asunto':{'label':'Asunto',
                                'class':'', #class name of the header
                                'width':'15%', #width in pixels or %
                                'truncate': 50, #truncate the content to...
                                'selected': False #agregate class selected to this column
                                },
                    'correspondencia.observaciones':{'label':'Observaciones',
                                'class':'', #class name of the header
                                'width':'20%', #width in pixels or %
                                'truncate': 50, #truncate the content to...
                                'selected': False #agregate class selected to this column
                                },
               }
        tabla_actual = SQLTABLE(rows, headers = headers)
        return dict(tabla_actual = tabla_actual)
    except:
        return dict()
