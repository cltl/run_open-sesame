# Run open-sesame

The goal of this repository is to run [open-sesame](https://github.com/swabhs/open-sesame)
on your own data. The repository is created to work with NAF XML.
You use the Python module **spacy_to_naf.py** (available after you run install.sh)
to convert your own text to NAF files.

### Prerequisites
Open-sesame uses Python2.7. 
All other code in this repository will make use of Python 3.7

### Installing

A number of external modules need to be installed, which are listed in **requirements.txt**.
Depending on how you installed Python, you can probably install the requirements using one of following commands:
```bash
pip install -r requirements.txt
```

## How to use
```bash
python parse_with_spacy_and_convert.py.py -h
```
For more information about how to use.

## TODO
* fix begin and end timestamp

## Authors

* **Marten Postma** (m.c.postma@vu.nl)

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgements
We make use the of converter from [Spacy to NAF](https://github.com/cltl/SpaCy-to-NAF) for which we thank Emiel van Miltenburg.