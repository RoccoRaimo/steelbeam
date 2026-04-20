# steelbeam

A lightweight Python library for structural steel beam design and verification, with native LaTeX formula rendering and multi-code support (Eurocode, AISC, NBR).

> 💡 **Coming soon**: Desktop application for non-interactive usage — works side-by-side with Jupyter notebooks! 


## Installation

> ⚠️ **Work in progress** — package not yet on PyPI

```bash
# Clone and install locally
git clone https://github.com/yourusername/steelbeam.git
cd steelbeam
pip install -e .
```

Or install directly from GitHub:
```bash
pip install git+https://github.com/yourusername/steelbeam.git
```

You can import with:

```python
import steelbeam as sb
```

## Why steelbeam?

- **Code-agnostic**: Switch between Eurocode, AISC, and NBR with a single parameter
- **Transparent calculations**: Every formula is rendered in LaTeX — no black boxes
- **Jupyter-native**: Designed for interactive exploration in notebooks
- **Desktop app coming**: Soon you'll be able to run calculations from a standalone executable without writing code

## How it works

After importing the library, you must create an object representing the steel beam. 
You can select an existing standard profile from the provided databases (currently only the European one) or define a new profile with custom characteristics.

[INSERIRE GIF DI UN BREVE FUNZIONAMENTO DELLA LIBRERIA]

## List of features

- List of functions already implemented for national codes design formulas:
	- Eurocodes
		- Normal force tension resistance :heavy_check_mark:
		- Normal force compression resistance :heavy_check_mark:
		- Bending moment resistance for both axis of profile :heavy_check_mark:
		- Shear resistance for both axis of profile :heavy_check_mark:
		- Combined bending and axial force resistance :heavy_check_mark:
		- Combined bending and shear force resistance :x:
		- Torsion :x:
		- Euler buckling :heavy_check_mark:
		- Compression member buckling :heavy_check_mark:
		- Bending with Lateral-Torsional buckling :heavy_check_mark:
	- AISC/AASHTO (work in progress)
	- NBR (work in progress)
- Configurable partial safety factors
- All resistance functions support both calculation mode and rendered output mode using the handcalcs library
- Configurable precision and unit prefixes for professional documentation output
  
## Dependencies

- `numpy`, `scipy` — numerical computations
- `handcalcs` — LaTeX formula rendering
- `forallpeople` — unit handling

## Desktop Application (Coming Soon)

While `steelbeam` is designed for interactive use in Jupyter notebooks, I'm about to build also a **standalone desktop application** that lets you perform the same calculations without writing code.

- Point-and-click interface
- Export reports in PDF/LaTeX
- Works offline — no Jupyter required

> Stay tuned for the first beta release!
