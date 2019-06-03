"""
update NAF files with open-sesame output
In each folder in the <input_folder> an XML will be added in which the output of open-sesame is incorporated

Usage:
  update_naf_with_open_sesame_output.py --input_folder=<input_folder> --commit=<commit> --verbose=<verbose>

Options:
    --input_folder=<input_folder> a folder with a folder for each document (output from parse_with_spacy_and_convert.py)
    --commit=<commit> the git commit that you cloned of open-sesame (in development this is 96639aedd24442433365d4d9fca877931fe222e4)

Example:
    python update_naf_with_open_sesame_output.py --input_folder="output" --commit="96639aedd24442433365d4d9fca877931fe222e4" --verbose=1
"""
import pickle
from collections import defaultdict
from docopt import docopt
from pathlib import Path
import utils

from KafNafParserPy import KafNafParser
import KafNafParserPy

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

main_dir = Path(arguments['--input_folder'])
open_sesame_output_path = main_dir / 'all_sentences.conll'
tokens2sent_id_info_path = main_dir / 'tokens2sent_id_info.p'
assert open_sesame_output_path.exists()
assert tokens2sent_id_info_path.exists()

verbose = int(arguments['--verbose'])

#load open-sesame output
open_sesame = utils.load_open_sesame_output(str(open_sesame_output_path), verbose=verbose)

#load mapping tokens to sent_ids
tokens2sent_id_info = pickle.load(open(str(tokens2sent_id_info_path), 'rb'))

for tokens in open_sesame:
    assert tokens in tokens2sent_id_info, f'{tokens} not found in NAF'

for tokens in tokens2sent_id_info.keys():
    if tokens not in open_sesame:
        if verbose >= 2:
            print(f'No open-sesame output for: {tokens}')

# restructure it per document
stem2sentid2predicates = dict()
for tokens, token_info in tokens2sent_id_info.items():
    open_sesame_output = open_sesame[tokens]

    if open_sesame_output:
        for sentence_info in token_info:
            stem, sent_id = sentence_info['sent_id']
            if stem not in stem2sentid2predicates:
                stem2sentid2predicates[stem] = defaultdict(list)

            for predicate_info in open_sesame_output:
                predicate_info['index2t_id'] = sentence_info['index2t_id']
                stem2sentid2predicates[stem][sent_id].append(predicate_info)


#TODO: update NAF files

for stem, sentid2predicates in stem2sentid2predicates.items():

    cur_pred_id = 1
    cur_role_id = 1

    # paths
    input_path_xml = main_dir / stem / 'base.xml'
    output_path_xml = main_dir / stem / 'srl.xml'

    for path in [input_path_xml]:
        assert path.exists()

    # load naf file
    my_parser = KafNafParser(str(input_path_xml))

    # add header
    srl_lp = my_parser.create_linguistic_processor(layer='srl',
                                                   name='open-sesame',
                                                   version=f'commit-{arguments["--commit"]}')
    my_parser.add_linguistic_processor(layer='srl', my_lp=srl_lp)

    # add srl data
    for sent_id, predicates in sentid2predicates.items():
        for predicate in predicates:


            # add predicate
            predicate_obj = KafNafParserPy.Cpredicate()
            predicate_obj.set_id(f'pr{cur_pred_id}')
            predicate_obj.set_uri(predicate['frame_label'])

            # add predicate target id
            span_obj = KafNafParserPy.Cspan()
            span_obj.add_target_id('t1')
            predicate_obj.set_span(span_obj)

            for role in predicate['roles']:
                role_obj = KafNafParserPy.Crole()
                role_obj.set_id(f'rl{cur_role_id}')
                role_obj.set_semRole(role['role_name'])

                span_obj = KafNafParserPy.Cspan()
                for index in role['indices']:
                    t_id = predicate['index2t_id'][index]
                    span_obj.add_target_id(t_id)
                role_obj.set_span(span_obj)
                predicate_obj.add_role(role_obj)
                cur_role_id += 1

            my_parser.add_predicate(predicate_obj)
            cur_pred_id += 1

    # save file
    my_parser.dump(filename=str(output_path_xml))