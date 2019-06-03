"""
Parse text with Spacy and convert to:
-NAF
-txt file with one sentence per line

Usage:
  parse_with_spacy_and_convert.py --input_folder=<input_folder> --output_folder=<output_folder>

Options:
    --input_folder=<input_folder> a folder with text (*.txt) files with all text on the first line (see example_files)
    --output_folder=<output_folder> the output folder

Example:
    python parse_with_spacy_and_convert.py --input_folder="example_files" --output_folder="output"
"""
import shutil
import json
from glob import glob
from collections import defaultdict
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
if out_dir.exists():
    shutil.rmtree(str(out_dir))
out_dir.mkdir(parents=True)

input_folder = arguments['--input_folder']

combined_txt_path = out_dir / 'all_sentences.txt'
index2stem_sent_id_path = out_dir / 'index2stem_sent_id.json'
index2stem_sent_id = dict()
index = 0

with open(str(combined_txt_path), 'w') as combined_outfile:

    for txt_file in glob(f'{input_folder}/*txt'):

        # load file
        with open(txt_file) as infile:
            the_text = infile.readline()

        # parse with spacy and convert to NAF
        nlp = spacy.load('en')
        NAF = spacy_to_naf.text_to_NAF(the_text, nlp)

        # create output folder
        stem = Path(txt_file).stem
        txt_out_folder = Path(out_dir / stem)
        txt_out_folder.mkdir(parents=True)

        # save NAF file
        output_path_naf = str(txt_out_folder / 'base.xml')

        with open(output_path_naf, 'w') as outfile:
            outfile.write(spacy_to_naf.NAF_to_string(NAF))

        # save txt file
        sent_id2tokens = defaultdict(list)
        for wf_el in NAF.xpath('text/wf'):
            sent_id = int(wf_el.get('sent'))
            sent_id2tokens[sent_id].append(wf_el.text)

        output_path_txt = str(txt_out_folder / 'sentences.txt')
        with open(output_path_txt, 'w') as outfile:
            for sent_id, tokens in sorted(sent_id2tokens.items()):
                outfile.write(' '.join(tokens) + '\n')

                # update all sentences file and index
                combined_outfile.write(' '.join(tokens) + '\n')
                index2stem_sent_id[index] = (stem, sent_id)
                index += 1


with open(str(index2stem_sent_id_path), 'w') as outfile:
    json.dump(index2stem_sent_id, outfile)







