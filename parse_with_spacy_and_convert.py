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
import pickle
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
tokens2sent_id_info_path = out_dir / 'tokens2sent_id_info.p'
tokens2sent_id_info = defaultdict(list)
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
            t_id_of_w_id = wf_el.get('id').replace('w', 't')
            sent_id2tokens[sent_id].append((wf_el.text, t_id_of_w_id))

        output_path_txt = str(txt_out_folder / 'sentences.txt')
        with open(output_path_txt, 'w') as outfile:
            for sent_id, token_info in sorted(sent_id2tokens.items()):

                tokens = [token for token, t_id in token_info]
                outfile.write(' '.join(tokens) + '\n')

                # update all sentences file and index
                combined_outfile.write(' '.join(tokens) + '\n')

                key = tuple([token.lower() for token in tokens])
                sent_info = {
                    'sent_id' : (stem, sent_id),
                    'index2t_id' : {index : t_id
                                    for index, (token, t_id) in enumerate(token_info)}
                }

                tokens2sent_id_info[key].append(sent_info)
                index += 1


for tokens, sentences in tokens2sent_id_info.items():
    if len(sentences) >= 2:
        print()
        print('there are identical sentences (open-sesame annotation of one of them will be used)')
        print(tokens)
        print([value['sent_id'] for value in sentences])

with open(str(tokens2sent_id_info_path), 'wb') as outfile:
    pickle.dump(tokens2sent_id_info, outfile)







