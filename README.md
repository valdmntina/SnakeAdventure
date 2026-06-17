# 🐍 Snake Adventure

Una versión moderna del clásico juego de la serpiente, desarrollada en **Python** con **pygame**. Incluye niveles progresivos, enemigos tipo fantasma, túneles que teletransportan, un poder al estilo Pac-Man y una tabla de mejores puntajes persistente.

![Lenguaje](https://img.shields.io/badge/Python-3.12-blue) ![Librería](https://img.shields.io/badge/pygame-2.6.1-green)

---

## 📋 Tabla de contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Cómo jugar](#-cómo-jugar)
- [Controles](#-controles)
- [Mecánicas del juego](#-mecánicas-del-juego)
- [Estructura del proyecto](#-estructura-del-proyecto)

---

## ✨ Características

- 🎮 **Jugabilidad clásica de Snake** con movimiento fluido e interpolado entre celdas.
- 📈 **Niveles progresivos**: cada 5 manzanas subes de nivel y la velocidad aumenta.
- 👻 **Enemigos (fantasmas)**: aparecen y persiguen a la serpiente; su número crece con el nivel (hasta 6).
- 🌀 **Túneles de teletransporte**: entras por uno y sales por su par. Cambian de ubicación cada vez que subes de nivel.
- ⚡ **Poder especial** (estilo Pac-Man): al comerlo, los fantasmas se asustan y puedes comértelos para sumar puntos extra.
- 🏆 **Tabla de récords persistente**: los 5 mejores puntajes se guardan en `highscores.json`.
- ⏸️ **Pausa y reinicio** mediante teclado o botones en pantalla.
- 🎨 **Detalles visuales**: ojos animados que parpadean, lengua de la serpiente, halos, auras de poder y efectos al comer.

---

## 🔧 Requisitos

- **Python 3.12** (o superior).
- **pygame 2.6.1** (o compatible).

---

## 🚀 Instalación

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/valdmntina/SnakeAdventure.git
   cd SnakeAdventure
   ```

2. **(Recomendado) Crea y activa un entorno virtual:**

   ```bash
   python -m venv .venv
   ```

   - En **Windows (PowerShell)**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - En **Windows (CMD)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - En **Linux / macOS**:
     ```bash
     source .venv/bin/activate
     ```

3. **Instala la dependencia:**

   ```bash
   pip install pygame
   ```

---

## ▶️ Cómo jugar

Con el entorno virtual activado, ejecuta:

```bash
python main.py
```

Se abrirá una ventana de 800 × 600 con el juego listo para empezar.

---

## 🎮 Controles

| Acción | Teclas |
| --- | --- |
| Mover hacia arriba | `↑` o `W` |
| Mover hacia abajo | `↓` o `S` |
| Mover a la izquierda | `←` o `A` |
| Mover a la derecha | `→` o `D` |
| Pausar / reanudar | `P` (o el botón **Pausar**) |
| Reiniciar partida | `Barra espaciadora` (en *Game Over*) o el botón **Reiniciar** |
| Salir | Cerrar la ventana |

> 💡 Puedes encolar hasta 2 cambios de dirección, lo que permite hacer giros rápidos en esquinas sin perder precisión.

---

## 🕹️ Mecánicas del juego

- **Comer manzanas** 🍎: cada manzana suma 1 punto, hace crecer la serpiente y aumenta ligeramente la velocidad.
- **Subir de nivel** 📊: cada **5 manzanas** subes de nivel. Al hacerlo:
  - Los túneles cambian de posición.
  - Reaparecen fantasmas hasta completar el cupo del nivel.
- **Fantasmas** 👻: se mueven por el tablero persiguiendo tu cabeza. Si te tocan **sin** el poder activo, pierdes.
- **Túneles** 🌀: cada par de túneles del mismo color está conectado; entrar por uno te transporta al otro.
- **Poder especial** ⚡: aparece cada 5 manzanas (cuando hay al menos 2 fantasmas). Al recogerlo:
  - Dura **6 segundos** (con aviso de parpadeo al terminar).
  - Los fantasmas se asustan y huyen.
  - Puedes comértelos para ganar **+3 puntos** por cada uno.
- **Fin de partida** 💀: pierdes si chocas contra un borde, contra tu propio cuerpo o contra un fantasma sin poder. Se muestra la pantalla de *Game Over* con la tabla de mejores puntajes.

---

## 📁 Estructura del proyecto

```
SnakeAdventure/
├── main.py            # Todo el código del juego (lógica + render con pygame)
├── highscores.json    # Mejores 5 puntajes (se crea/actualiza automáticamente)
└── README.md          # Este archivo
```

---

¡Disfruta el juego! 🐍✨
