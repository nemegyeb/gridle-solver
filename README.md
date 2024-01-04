# gridle-solver

This is a cheat for the mobile game [Gridle by Bill Farmer](https://github.com/billthefarmer/gridle).
It can parse and solve gridle puzzles automatically.

## Getting Started

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/nemegyeb/gridle-solver.git
    ```

2. Navigate to the project directory:

    ```bash
    cd gridle-solver
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Usage

1. Connect your phone so that it is ready to receive adb commands.
   The easiest way to do this is to connect your phone via USB and enable USB debugging for the device you are using.
2. Use the default theme (Dark) and the default highlight colours in gridle. The other themes and highlight colours are not supported and will (most likely) not work.
3. Run `python3 main.py`

## License

This project is licensed under the [GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.html#license-text).
