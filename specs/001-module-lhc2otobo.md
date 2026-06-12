## Modulo lhc2otobo

### Endpoint

    -   /api/v1/lhc2otobo/updatewithimage


### Variable de entorno

1.  OTOBO_IP
2.  OTOBO_USER
3.  OTOBO_PWD

### Datos de Otobo

1. Url de Otobo: https://${OTOBO_IP}/otobo/nph-genericinterface.pl/Webservice/Ticket/TicketUpdate/TicketID


### Flujo

1. Recibe el Json de Livehelper
2. Revisa el campo File (Imagen en base64)
3. Si existe el valor en el campo File:
   1. Extrae el valor del key: "averia_imagen_file" de la lista additional_data, por ejemplo file=1071_89d1d83fea0945cb3cc27c72849531b4, extraes 1071_89d1d83fea0945cb3cc27c72849531b4 y se usa como nombre de archivo.
   2. Revisa el archivo del campo file para determinar su extension 
   3. Arma un nombre de archivo con el nombre obtenido y la extension
   4. Si la variable de entorno WEBHOOK_TESTER tiene una url valida entonces envia el json 
   5. Envia mediante POST la solicitud a la URL del Otobo usando los datos que coincidan del json recibido
   6. Espera la respuesta y la devuelve tal cual al LHC
4. Si no existe data en el campo file:
   1. Si la variable de entorno WEBHOOK_TESTER tiene una url valida entonces envia el json
   2. Envia el json sin campo File a la  url de Otobo
   3. Espera la respuesta y la devuelve tal cual al LHC 



### Armar el Body 

1.  Revisa el el valor del key: "menu_principal" de la lista recibida
2.  Si el valor es igual a 3:
    1.  El body es:
      "Medidor : (value del key: numero_medidor)
       Telefono : (value del key: numero_telefono)
       Nombre: (value del key: nombre_usuario)
       Descripcion: (value del key: descripcion_averia)"
    2. El body es texto plano y se inserta en el campo Body del json saliente
 3. Si el valor es igual a 4:
    1.  El body es:
      "Suscriptor : (value del key: numero_suscriptor)
       Telefono : (value del key: numero_telefono)
       Nombre: (value del key: nombre_usuario)
       Descripcion: (value del key: descripcion_averia)"
    2. El body es texto plano y se inserta en el campo Body del json saliente


### Json Recibido

{
  "ticketnumber": ,
  "title": ,
  "queue":,
  "subject":,
  "additional_data": [
    {
      "key": "menu_principal",
      "identifier": "menu_principal",
      "value": 
    },
    {
      "key": "averia_energia",
      "identifier": "averia_energia",
      "value": 
    },
    {
      "key": "numero_medidor",
      "identifier": "numero_medidor",
      "value": 
    },
    {
      "key": "numero_telefono",
      "identifier": "numero_telefono",
      "value": 
    },
    {
      "key": "nombre_usuario",
      "identifier": "nombre_usuario",
      "value": 
    },
    {
      "key": "descripcion_averia",
      "identifier": "descripcion_averia",
      "value": 
    },
    {
      "key": "averia_energia_confirm",
      "identifier": "averia_energia_confirm",
      "value": 
    },
    {
      "key": "averia_imagen",
      "identifier": "averia_imagen",
      "value": 
    },
    {
      "key": "averia_imagen_file",
      "identifier": "averia_imagen_file",
      "value": 
    }
  ],
    "file" : (Base64 raw)
}

### Json para enviar con campo File


{
   "UserLogin": ${OBOTO_USER},
   "Password": ${OTOBO_PWD},
   "TicketNumber": ( ticketnumber en json recibido ),
   "Ticket":{
      "Title": (title en json recibido),
      "Queue": (queue en json recibido)
   },
   "Article":{
      "Subject": (subject en json recibido),
      "Body":,
      "ContentType":"text/plain; charset=utf8"
   },
 
    "Attachment" = [
        {
            "ContentType" : "image/${tipo de imagen}"
            "Filename" : ${nombre del archivo}, 
            "Content" : ${Contenido en base 64 valido}
        }
                    ]
}

### Json para enviar sin campo File

{
   "UserLogin": ${OBOTO_USER},
   "Password": ${OTOBO_PWD},
   "TicketNumber": ( ticketnumber en json recibido ),
   "Ticket":{
      "Title": (title en json recibido),
      "Queue": (queue en json recibido)
   },
   "Article":{
      "Subject": (subject en json recibido),
      "Body":,
      "ContentType":"text/plain; charset=utf8"
   }

}
