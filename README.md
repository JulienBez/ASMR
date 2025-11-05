# ASMR

ASMR (Align, Segment, Match and Rank) is an empirical, alignment-based algorithm whose goal is the extraction and the identification of Puns in Multiword Expressions (PMWEs). PMWES are characterized by the creation of a pun or a wordplay from a source multiword expression in order to recontextualize it or give it a humorous touch (e.g: "may the force be with you" becoming "may the beer be with you"). This algorithm was made during my PhD thesis. Here is a list of all the publications I made while using it:

- For a Fistful of Puns: Evaluating a Puns in Multiword Expressions Identification Algorithm Without Dedicated Dataset (Bezançon & Lejeune, EMNLP Findings 2025)
- Reconnaissance de défigements dans des tweets en français par des mesures de similarité sur des alignements textuels (Bezançon & Lejeune, JEP/TALN/RECITAL 2023)
- Lost in Variation: An Unsupervised Methodology for Mining Lexico-syntactic Patterns in Middle Arabic Texts (Bezançon et al., WACL 2025)

## Installation

To install ASMR, you must have **Python 3.x** and **pip** installed. Clone this repository on your computer. Open your terminal and go to the ASMR folder (where main.py is). Once in the indicated folder, install required packages with the following command:

```
pip install -r requirements.txt
```

## Data structure

ASMR needs (i) a list of seeds and (ii) a list of sentences. The list of seed must be a **json** file containing a dictionnary with seeds as keys and another dictionnary as values, such as:

```
{
    "this is a seed": {
        "TOK": ["this","is","a","seed"],
        "LEM": ["this","be","a","seed"],
        ... # any other layer you want to include
    }
}
```

The sentence list can be composed of multiple **json** files contained in a folder and structured as follow:

```
[
    {
        "sent": "this is a sentence",
        "metadata": {
            "id" : your_id,
            ... # any other information you want to include
        },
        "parsing": {
            "TOK": ["this","is","a","sentence"],
            "LEM": ["this","be","a","sentence"],
            ... # any other layer you want to include
        }
    }
]
```

You must place the **json** file containing your seeds and the **folder** containing your **json** files of sentences in the **data/** folder. They must have the same name (e.g: **data/a.json** for your seeds and **data/a/*.json** for your sentences).

## How to use

Before to run ASMR, you should probably take a look inside the ASMR parameters file (**src/parameters.py**). Here, you can tune several features of the ASMR algorithm. You can then run ASMR by running the following command:

```
python main.py -pasmr
```

Each letter correspond to a different step performed by the ASMR algorithm:

- **p (pairing)** - *RUN ONCE*, create seed-sentence pairs ;
- **a (Align)** - align the seed and the sentence of each pair ;
- **s (Segment)** - segment the alignments in order to identify common and different elements ;
- **m (Match)** - choose the elements to extract as part of a PMWE-candidate ;
- **r (Rank)** - compute similarity scores between each extracted candidate and each seed to rank them ;
- **R (Results)** - *OPTIONAL*, provide some results, such as statistics and graphs ;
- **M (Metadata)** - *OPTIONAL*, provide some metadata and statistics.

As a result, ASMR will create a new folder in the **output/** folder (e.g: **output/a**). It will contain a copy of your **json** files with new informations (such as aligned sequences, scores, ...) and a ranking for each seed. Once you ran ASMR on your corpus, your next step should be to take a look at the ranking and see if the parameters used produced satisfying results. Otherwise, you can tune them in the **src/parameters.py** file.

## License

ASMR is distributed under the terms of the [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html) license.

## Reference

If you use ASMR in your work, please cite it directly:

```
@inproceedings{bezancon-lejeune-2025-fistful,
    title = "For a Fistful of Puns: Evaluating a Puns in Multiword Expressions Identification Algorithm Without Dedicated Dataset",
    author = {Bezan{\c{c}}on, Julien  and
      Lejeune, Ga{\"e}l},
    editor = "Christodoulopoulos, Christos  and
      Chakraborty, Tanmoy  and
      Rose, Carolyn  and
      Peng, Violet",
    booktitle = "Findings of the Association for Computational Linguistics: EMNLP 2025",
    month = nov,
    year = "2025",
    address = "Suzhou, China",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.findings-emnlp.443/",
    pages = "8350--8370",
    ISBN = "979-8-89176-335-7"
}
```

