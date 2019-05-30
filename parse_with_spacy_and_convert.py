"""
Parse text with Spacy and convert to:
-NAF
-txt file with one sentence per line

Usage:
  parse_with_spacy_and_convert.py --input_path=<input_path> --output_folder=<output_folder>

Options:
    --input_path=<input_path> a text file with all text on the first line (see example_files/example.txt)
    --output_folder=<output_folder> the output folder

Example:
    python parse_with_spacy_and_convert.py --input_path="example_files/example.txt" --output_folder="output"
"""
from docopt import docopt
from pathlib import Path
import spacy_to_naf
import spacy
from collections import defaultdict


# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

out_dir = Path(arguments['--output_folder'])
if not out_dir.exists():
    out_dir.mkdir(parents=True)

input_path = Path(arguments['--input_path'])

# load file
with open(arguments['--input_path']) as infile:
    the_text = infile.readline()

# parse with spacy and convert to NAF
nlp = spacy.load('en')
NAF = spacy_to_naf.text_to_NAF(the_text, nlp)


# save NAF file
output_path_naf = str(out_dir / input_path.stem) + '.xml'

with open(output_path_naf, 'w') as outfile:
    outfile.write(spacy_to_naf.NAF_to_string(NAF))

# save txt file
sent_id2tokens = defaultdict(list)
for wf_el in NAF.xpath('text/wf'):
    sent_id = int(wf_el.get('sent'))
    sent_id2tokens[sent_id].append(wf_el.text)

output_path_txt = str(out_dir / input_path.stem) + '.txt'
with open(output_path_txt, 'w') as outfile:
    for sent_id, tokens in sorted(sent_id2tokens.items()):
        outfile.write(' '.join(tokens) + '\n')





