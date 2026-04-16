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



# List of features
- National codes implemented:
	- Eurocodes (work in progress)
	- AISC/AASHTO (work in progress)
	- NBR (work in progress)

## Dependencies

- `numpy`, `scipy` — numerical computations
- `handcalcs` — LaTeX formula rendering
- `forallpeople` — unit handling

## Desktop Application (Coming Soon)

While `steelbeam` is designed for interactive use in Jupyter notebooks, we're also building a **standalone desktop application** that lets you perform the same calculations without writing code.

- Point-and-click interface
- Export reports in PDF/LaTeX
- Works offline — no Jupyter required

> Stay tuned for the first beta release!

## Examples

You can find some examples of usage in the examples folder!
