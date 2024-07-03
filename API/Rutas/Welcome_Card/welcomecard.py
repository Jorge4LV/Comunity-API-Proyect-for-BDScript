from fastapi import APIRouter, Response, HTTPException
from easy_pil import Editor, Font
from io import BytesIO
import requests
import logging
from functools import lru_cache

router = APIRouter()

# Configurar fuentes una sola vez
poppins = Font.poppins(size=50, variant="bold")
poppins_small = Font.poppins(size=25, variant="regular")

# Iniciar el editor con el fondo una sola vez
background_url = "https://i.postimg.cc/4xdgRTwz/Bot2vgN.png"
background_response = requests.get(background_url)
if background_response.status_code != 200:
    raise RuntimeError(f"Failed to download background image. Status code: {background_response.status_code}, Reason: {background_response.reason}")
background_image = Editor(BytesIO(background_response.content)).resize((800, 400)).image

@router.get("/api/welcomecard/")
def get_custom_image(avatar: str, ctx1: str, ctx2: str="¡Esperamos que disfrutes tu estancia!", ctx3: str="CLUB DUDUA - «Elegancia y Discreción»"):
    try:
        # Descargar y procesar el avatar si no está en cache
        @lru_cache(maxsize=32)
        def fetch_avatar_image(url):
            response = requests.get(url)
            if response.status_code != 200:
                raise RuntimeError(f"Failed to download avatar image. Status code: {response.status_code}")
            return Editor(BytesIO(response.content)).resize((150, 150)).circle_image().image

        avatar_image = fetch_avatar_image(avatar)

        # Iniciar el editor con una copia del fondo para cada solicitud
        editor = Editor(background_image.copy())

        # Pegar el avatar y añadir un borde blanco
        horizontal_shift = 63
        editor.paste(avatar_image, (250 + horizontal_shift, 90))
        editor.ellipse((250 + horizontal_shift, 90), 150, 150, outline="white", stroke_width=5)

        # Función para añadir texto con trazo oscuro
        def add_text_with_stroke(position, text, color, font, align="left"):
            stroke_color = "black"  # Color del trazo
            stroke_width = 2  # Ancho del trazo

            # Texto con trazo
            editor.text((position[0] - stroke_width, position[1]), text, color=stroke_color, font=font, align=align)
            editor.text((position[0] + stroke_width, position[1]), text, color=stroke_color, font=font, align=align)
            editor.text((position[0], position[1] - stroke_width), text, color=stroke_color, font=font, align=align)
            editor.text((position[0], position[1] + stroke_width), text, color=stroke_color, font=font, align=align)

            # Texto principal
            editor.text(position, text, color=color, font=font, align=align)

        # Añadir texto con trazo oscuro
        add_text_with_stroke((320 + horizontal_shift, 260), ctx1, color="white", font=poppins, align="center")
        add_text_with_stroke((320 + horizontal_shift, 315), ctx2, color="white", font=poppins_small, align="center")
        add_text_with_stroke((320 + horizontal_shift, 350), ctx3, color="white", font=poppins_small, align="center")

        # Guardar la imagen resultante en un buffer
        img_buffer = BytesIO()
        editor.image.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Devolver la imagen como respuesta
        return Response(content=img_buffer.getvalue(), media_type="image/png")

    except Exception as e:
        logging.error(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=str(e))