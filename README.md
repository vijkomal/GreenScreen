# 🌿📺 GreenScreen: Automatic Accessible Presentation Generation from IPCC Reports

[[ICLR Workshop Paper (coming soon!)]]()
[[Notebook example]]()

> **🏗️ Work in Progress:** This repo is currently receiving some love – please check back soon!

The Intergovernmental Panel on Climate Change (IPCC) Summary for Policymakers (SPM) summarizes the current understanding of climate change, potential risks, and mitigation & adaptation strategies. **However, the reports have lower readability scores than scientific publications.**

**GreenScreen** is an LLM-driven pipeline to transform dense sustainability reports into digestible, engaging slide decks to inspire climate action and awareness.

## ⚙️ Pipeline

<div style="display: flex;">
	<img src="https://github.com/kvcs11/GreenScreen/blob/main/assets/pipeline.png"/>
</div>

GreenScreen has three main components: 

- **Report Reader**: Splits PDF into semantic chunks (paragraphs).

- **Slide Creator**: Creates formatted LaTeX code based on content.

- **Presentation Creator**: Assembles slides into final presentation.

The slide creator is powered by an LLM (for example Gemini) to evaluate each content paragraph and convert it into formatted paragraphs.

## 🏗️ Installation

### Using pip (coming soon!)

Install the package using pip, like so:

```bash
pip install greenscreen
```

### From GitHub

1. Clone the repo

```bash
git clone https://github.com/kvcs11/GreenScreen.git
```

2. Setup virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 🍃 Usage

### Web Demo (coming soon!)

To use the interactive web demo, make sure to clone the repo directly from GitHub. Then, start a gradio server using the command below:

```bash
gradio app.py
```

The interface let's you upload a PDF and experiment with the following settings.

## 🔭 Roadmap

- [ ] Finish gradio local demo
- [ ] Convert repo into PyPi Package

## ✌️ Contributing

Any contributions you make are greatly appreciated. If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

## 📬 Contact

Alice Heiman - aheiman [at] stanford [dot] edu <br>
Komal Vij - komalvij [at] stanford [dot] edu

## 🔖 License

GreenScreen's code is released under the MIT License. See [LICENSE](https://github.com/kvcs11/GreenScreen/blob/main/LICENSE) for further details.
