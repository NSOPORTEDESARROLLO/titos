## Modulo timecondition

### Endpoint

    - /api/v1/timecondition

### Metodo

    - POST
  
### Flujo

1.  Recibe un Json con una lista de rangos de hora. (ranges)
2.  Recibe un campo "timezone" con el timezone standard, por ejemplo (America/Costa_Rica)
3.  Compara que el rango suministrado este dentro de la hora actual deacuerdo al Timezone
4.  Devuelte un bool (true -> Si esta dentro, false -> No esta dentro)

### Json Recibido

{

    "ranges" : [
        {
            "start_hour" : "08:00",
            "end_hour" : "12:30",
            "days" : [1,2,3]
         }
    ],

    "timezone" : "America/Costa_Rica"


}

### Json de salida
{

    "status" : "on/off",
    "online" : "true/false",
    "msg" : "Time: ${current_time on given timezone} is in/out of the ranges"


}


### Consideraciones

1.  Los rangos pueden ser multiples, incluso en diferente horas del dia
2.  La semana inicia en Lunes (dia 0) Standard internacional 
3.  Si la variable WEBHOOK_TESTER esta activa, manda una copia de la salida
4.  