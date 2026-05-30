# Traductor Roleplay - Neverwinter NEE by Exar22

Esta es una aplicación diseñada para capturar y traducir automáticamente el chat de **Neverwinter Nights: Enhanced Edition** del inglés al español, facilitando una experiencia fluida de roleplay en servidores internacionales.
---
---

## Configuración Necesaria en el Juego (¡Obligatorio!)

Para que Neverwinter Nights guarde tu chat en tiempo real y la aplicación pueda leerlo, debes asegurarte de tener activado el Log de cliente. Sigue estos sencillos pasos:

1. Ve a tus documentos, en la ruta: `Documentos\Neverwinter Nights\`.
2. Abre el archivo **`settings.tml`** con el bloc de notas.
3. Busca la sección `[Game]` y asegúrate de cambiar o añadir las siguientes líneas:
   ```
   [game.log]
		flush-immediately = true
		[game.log.chat]
			[game.log.chat.all]
				enabled = false
			[game.log.chat.emotes]
				enabled = true
			[game.log.chat.text]
				enabled = true
		[game.log.debug]
			assert = false
			network = false
			nui = false
			scriptvm = false
		[game.log.resman]
			[game.log.resman.lookup-failures]
				enabled = false
---

## Características Principales

* **Modo Híbrido:** Funciona de forma gratuita e ilimitada con *Google Translate* por defecto, o de manera mas precisa conectando una API Key de *DeepL de desarrollador* que es gratuita.
* **Envío de Texto Bidireccional:** Escribe en español dentro de la app, presiona *Enter* y el texto se enviará traducido al inglés directamente al chat del juego.

---

## Cómo Utilizar la Aplicación

1. **Descarga el ejecutable:** Ve a la sección de **Releases** (Lanzamientos) a la derecha de este repositorio y descarga el archivo `.exe`.
2. **Ejecuta el programa:** Ábrelo despues de iniciar el juego neverwinter nights enchanced edition, La app detectará automáticamente tu archivo de logs.
3. *(Opcional)* Si cuentas con una clave de desarrollador de DeepL, pégala en la sección inferior de ajustes y presiona **Conectar DeepL**.
4. Para que la traduccion funcione perfectamente debes de precionar *enter* en el juego para que se active el chat del juego, luego vas a la aplicacion, escribes lo que quieras decir en español y presionas *enter*, automaticamente se pegara lo que escribiste en la aplicacion de traduccion en el chat del juego ya en ingles listo para volver al juego volver a precionar *enter*.

---

## Nota Importante de Compatibilidad

> **Permisos de Administrador:** Si ejecutas *Neverwinter Nights* con permisos de Administrador, es **estrictamente necesario** que abras este traductor dando **Clic derecho -> Ejecutar como Administrador**. 
> 
> De lo contrario, los sistemas de seguridad de Windows impedirán que la función automática de teclado (`PyAutoGUI`) envíe tus traducciones al juego.
