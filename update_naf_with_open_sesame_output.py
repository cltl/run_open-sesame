"""
update NAF files with open-sesame output
will be stored in folder --output_open_sesame/NAF

Usage:
  update_naf_with_open_sesame_output.py --naf_folder=<naf_folder> --output_open_sesame=<output_open_sesame> --commit=<commit> --verbose=<verbose>

Options:
    --naf_folder=<naf_folder> folder with the original NAF files
    --output_open_sesame=<output_open_sesame> output from open sesame
    --commit=<commit> the git commit that you cloned of open-sesame (in development this is 96639aedd24442433365d4d9fca877931fe222e4)

Example:
    python update_naf_with_open_sesame_output.py --naf_folder="example_files" --output_open_sesame="output" --commit="96639aedd24442433365d4d9fca877931fe222e4" --verbose=1
"""
import pickle
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

naf_dir = Path(arguments['--naf_folder'])
open_sesame_dir = Path(arguments['--output_open_sesame'])
naf_output_dir = open_sesame_dir / 'NAF'
naf_output_dir.mkdir()

open_sesame_output_path = open_sesame_dir / 'all_sentences.conll'
open_sesame_txt_path = open_sesame_dir / 'all_sentences.txt'
stem2index2sentid_and_tokens_path = open_sesame_dir / 'stem2index2sentid_and_tokens.p'

btime = utils.creation_time_of_file(str(open_sesame_txt_path))
etime = utils.creation_time_of_file(str(open_sesame_output_path))

assert open_sesame_output_path.exists(), f'open sesame output not found, should be at {open_sesame_output_path}'
assert stem2index2sentid_and_tokens_path.exists()

verbose = int(arguments['--verbose'])

#load open-sesame output
open_sesame, \
index2num_tokens = utils.load_open_sesame_output(str(open_sesame_output_path), verbose=verbose)

#load mapping tokens to sent_ids
stem2index2sentid_and_tokens = pickle.load(open(str(stem2index2sentid_and_tokens_path), 'rb'))

#update NAF files
for stem, index2sentid_and_tokens in stem2index2sentid_and_tokens.items():

    cur_pred_id = 1
    cur_role_id = 1

    # paths
    input_path_xml = naf_dir / stem
    output_path_xml = naf_output_dir / stem

    for path in [input_path_xml]:
        assert path.exists(), f'{path} does not exist'

    # load naf file
    my_parser = KafNafParser(str(input_path_xml))

    # add header
    srl_lp = my_parser.create_linguistic_processor(layer='srl',
                                                   name='open-sesame',
                                                   btimestamp=btime,
                                                   etimestamp=etime,
                                                   version=f'commit-{arguments["--commit"]}')
    my_parser.add_linguistic_processor(layer='srl', my_lp=srl_lp)

    # add srl data
    for main_index, (sent_id, tokens) in index2sentid_and_tokens.items():

        index2t_id = {token_index : t_id
                      for token_index, (token, t_id) in enumerate(tokens)}

        # inspect token alignment
        if main_index in index2num_tokens:
            num_tokens_open_sesame = index2num_tokens[main_index]
            if num_tokens_open_sesame != len(index2t_id):
                if verbose:
                    message = f'problem in alignment sentence {main_index} of file {stem}'
                    print(message)
                continue

        predicates = open_sesame[main_index]

        for predicate in predicates:

            # add predicate
            frame_label = predicate['frame_label']
            predicate_obj = KafNafParserPy.Cpredicate()
            predicate_obj.set_id(f'pr{cur_pred_id}')
            predicate_obj.set_uri(frame_label)

            # add predicate target id
            span_obj = KafNafParserPy.Cspan()
            target_index = predicate["target_index"]
            t_id = index2t_id[target_index]
            span_obj.add_target_id(f'{t_id}')
            predicate_obj.set_span(span_obj)

            for role in predicate['roles']:
                role_obj = KafNafParserPy.Crole()
                role_obj.set_id(f'rl{cur_role_id}')
                role_obj.set_semRole(role['role_name'])

                span_obj = KafNafParserPy.Cspan()
                for index in role['indices']:
                    assert index in index2t_id, f'{stem} {predicate} {index} not in {index2t_id}'
                    t_id = index2t_id[index]
                    span_obj.add_target_id(t_id)
                role_obj.set_span(span_obj)
                predicate_obj.add_role(role_obj)
                cur_role_id += 1

            my_parser.add_predicate(predicate_obj)
            cur_pred_id += 1

    # save file
    my_parser.dump(filename=str(output_path_xml))
