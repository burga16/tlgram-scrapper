# tlgram-scrapper

Herramienta en Python para escanear canales de Telegram y obtener canales relevantes para una búsqueda realizada con un término determinado

## Requisitos:

Instalar librerías utilizadas con el comando:
~~~
pip install -r requirements.txt
~~~

## API Keys de Telegram

Obtener API ID y API Hash en: [https://my.telegram.org/auth?to=apps](https://my.telegram.org/auth?to=apps)

## Cadena de conexión a la base de datos

Crear base de datos en MariaDB y un usuario con permisos sobre esa base de datos, copiar datos de conexión en db_sqlalchemy.py:

~~~
engine = sqlalchemy.create_engine("mariadb+mariadbconnector://username:password@127.0.0.1:port/database_name" pool_pre_ping=True, pool_recycle=1500)
~~~

## Comandos de utilización:

### Buscar canales de tgstat: 
~~~
python tlgram_scrapper.py término_de_búsqueda
~~~

### Importar mensajes:
~~~
python importMessages.py
~~~

### Clasificar grupos:
~~~
python classifyChannels.py
~~~

### Buscar enlaces a canales públicos:

~~~
python checkMessages.py
~~~

### Buscar enlaces a canales privados:

~~~
python checkPrivateLinks.py
~~~
