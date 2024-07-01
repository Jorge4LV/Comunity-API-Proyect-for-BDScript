from fastapi import APIRouter, Response, HTTPException
from easy_pil import Editor, Font
from io import BytesIO
import requests
import logging

router = APIRouter()

@router.get("/api/welcomecard/")
def get_custom_image(avatar: str, background: str, ctx1: str, ctx2: str, ctx3: str):
    try:
        # Descargar y procesar el avatar
        avatar_response = requests.get(avatar)
        if avatar_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download avatar image.")
        avatar_image = Editor(BytesIO(avatar_response.content)).resize((150, 150)).circle_image()

        # Descargar y procesar el fondo
        background_response = requests.get(background)
        if background_response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to download background image. Status code: {background_response.status_code}, Reason: {background_response.reason}")
        background_image = Editor(BytesIO(background_response.content)).resize((800, 400)).image

        # Configurar fuentes
        poppins = Font.poppins(size=50, variant="bold")
        poppins_small = Font.poppins(size=25, variant="regular")

        # Desplazamiento horizontal
        horizontal_shift = 63

        # Iniciar el editor con la imagen de fondo
        editor = Editor(background_image)

        # Pegar el avatar y añadir un borde blanco
        editor.paste(avatar_image.image, (250 + horizontal_shift, 90))
        editor.ellipse((250 + horizontal_shift, 90), 150, 150, outline="white", stroke_width=5)

        # Función para añadir texto con sombra
        def add_text_with_shadow(position, text, color, font, align="left"):
            shadow_color = "black"  # Color de la sombra
            shadow_offset = 2  # Desplazamiento de la sombra

            # Texto de sombra
            editor.text((position[0] + shadow_offset, position[1] + shadow_offset), text, color=shadow_color, font=font, align=align)
            # Texto principal
            editor.text(position, text, color=color, font=font, align=align)

        # Añadir texto con borde
        add_text_with_shadow((320 + horizontal_shift, 260), ctx1, color="white", font=poppins, align="center")
        add_text_with_shadow((320 + horizontal_shift, 315), ctx2, color="white", font=poppins_small, align="center")
        add_text_with_shadow((320 + horizontal_shift, 350), ctx3, color="white", font=poppins_small, align="center")

        # Guardar la imagen resultante en un buffer
        img_buffer = BytesIO()
        editor.image.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Devolver la imagen como respuesta
        return Response(content=img_buffer.getvalue(), media_type="image/png")

    except Exception as e:
        logging.error(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=str(e))