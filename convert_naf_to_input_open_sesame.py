"""
Parse text with Spacy and convert to:
-txt file with one sentence per line
-save mapping from index in txt file to sentence identifier

Usage:
  convert_naf_to_input_open_sesame.py.py --input_folder=<input_folder> --languages=<languages> --output_folder=<output_folder> --verbose=<verbose>

Options:
    --input_folder=<input_folder> a folder with text (*.txt) files (see example_files)
    --languages=<languages> supported: 'en'
    --output_folder=<output_folder> the output folder
    --verbose=<verbose> 0, no output, 1 general stdout, 2 detailled stdout

Example:
    python convert_naf_to_input_open_sesame.py --input_folder="example_files" --languages="en" --output_folder="output" --verbose=1
"""
import shutil
import pickle
import os
from glob import glob
from docopt import docopt
from pathlib import Path
from collections import defaultdict
from lxml import etree


def clean_token(token):
    if '\n' in token:
        token = 'NEWLINE'
    else:
        chars = []
        for char in token:
            if ord(char) not in range(128):
                char = '-'
            chars.append(char)
        token = ''.join(chars)
    return token


assert clean_token('\n') == 'NEWLINE'
assert clean_token('a\n') == 'NEWLINE'
assert clean_token('\n\n') == 'NEWLINE'
assert clean_token('björn') == 'bj-rn'
assert clean_token('hello') == 'hello'

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

verbose = int(arguments['--verbose'])
languages = set(arguments['--languages'].split('-'))
out_dir = Path(arguments['--output_folder'])
if out_dir.exists():
    shutil.rmtree(str(out_dir))
out_dir.mkdir(parents=True)

input_folder = arguments['--input_folder']

combined_txt_path = out_dir / 'all_sentences.txt'
stem2index2sentid_and_tokens_path = out_dir / 'stem2index2sentid_and_tokens.p'
stem2index2sentid_and_tokens = defaultdict(dict)
index = 0

with open(str(combined_txt_path), 'w') as combined_outfile:

    for naf_file in glob(f'{input_folder}/*naf'):

        doc = etree.parse(naf_file)
        basename = os.path.basename(naf_file)
        root = doc.getroot()
        language = root.get('{http://www.w3.org/XML/1998/namespace}lang')

        if language not in languages:
            if verbose >= 2:
                print(f'skipping {naf_file} since language:"{language}" not in {languages}')
            continue

        # save txt file
        sent_id2tokens = defaultdict(list)
        for wf_el in doc.xpath('text/wf'):
            sent_id = int(wf_el.get('sent'))
            t_id_of_w_id = wf_el.get('id').replace('w', 't')

            token = clean_token(wf_el.text)
            assert '\n' not in token, f'newline found in {repr(token)}'

            sent_id2tokens[(basename, sent_id)].append((token, t_id_of_w_id))

        for (basename, sent_id), token_info in sorted(sent_id2tokens.items()):

            tokens = [token for token, t_id in token_info]

            if any([not tokens,
                    tokens == ['"']]):
                continue

            # update all sentences file and index
            combined_outfile.write(' '.join(tokens) + '\n')

            stem2index2sentid_and_tokens[basename][index] = (sent_id, token_info)
            index += 1

# validate
index2line = {}
with open(str(combined_txt_path)) as infile:
    for index, line in enumerate(infile):
        index2line[index] = line.strip('\n')

for stem in stem2index2sentid_and_tokens:
    for index, (sent_id, token_info) in stem2index2sentid_and_tokens[stem].items():
        tokens = ' '.join([token for token, t_id in token_info])
        line_in_mapping = index2line[index]
        assert tokens == line_in_mapping, f'mismatch index {index}:\n dict: {repr(tokens)}\n and\n txt file: {repr(line_in_mapping)}'

with open(str(stem2index2sentid_and_tokens_path), 'wb') as outfile:
    pickle.dump(stem2index2sentid_and_tokens, outfile)

if verbose:
    print(f'saved all sentences to to: {combined_txt_path}')
    print(f'saved mapping index to NAF sentence identifiers to: {stem2index2sentid_and_tokens_path}')







