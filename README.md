# Harvest Rush — SWC3643 Python Programming Language

## Requirements
- Python 3.10 or newer recommended
- Pygame

## Run in PyCharm
1. Extract the ZIP file.
2. Open the `Harvest_Rush_PyCharm` folder as a project in PyCharm.
3. Open the PyCharm Terminal.
4. Install Pygame: `python -m pip install pygame`
5. Run `main.py` using the Run button.

## Controls
- Left/Right arrows or A/D: move the basket
- P: pause/resume
- R: restart
- ESC: return to menu (or exit from the menu)
- Mouse: choose menu options
- Menu language button: switch English / Bahasa Melayu

## Rules
- Apple: +10 points
- Banana: +15 points
- Orange: +10 points
- Golden fruit: +30 points
- Bomb caught: lose one life
- Missing a normal fruit: lose one life
- Last 60 seconds with at least one life to win
- The game gets harder every 15 seconds

## OOP structure
- `Player`: basket movement and rendering
- `Item`: falling objects, types, speed, score and rendering
- `GameManager`: game loop, events, timer, collision rules, levels, menus and score

## Assets
The `assets/` folder contains sprite PNGs and WAV sound effects. The code includes fallback drawing if a sprite is missing and optional sound loading if audio is unavailable.

## Before submission
- Run and test the project on your own computer.
- Add your own name, student ID and screenshots to the report.
- The brief asks for source code in GitHub and a gameplay demonstration video on YouTube.
- Do not claim that you tested the program on your computer until you have done so.
