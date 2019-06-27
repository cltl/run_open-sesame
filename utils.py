import os
from datetime import datetime
from collections import defaultdict


def time_in_correct_format(datetime_obj):
    "Function that returns the current time (UTC)"
    return datetime_obj.strftime("%Y-%m-%dT%H:%M:%SUTC")

def creation_time_of_file(path):
    file_info = os.stat(path)
    datetime_obj = datetime.datetime.utcfromtimestamp(file_info.st_ctime)
    return time_in_correct_format(datetime_obj)


def determine_end_of_role(prev_prefix, prefix):
    """
    determine whether the previous token was the last one of the role

    :param str prev_prefix: prefix of the previous BIO annotation
    :param str prefix: current prefix of BIO annotation

    :rtype: bool
    :return: True -> previous token was the last one, False -> either not in role or still in annotation
    """
    add_role = False

    if prefix != 'I':
        # current BIO annotation is O and previous one is I
        if prev_prefix == 'I':
            add_role = True

    return add_role

def load_open_sesame_output(output_path, verbose=0):
    """
    load open-sesame conll output in a representation from
    tokens -> predicates found in those tokens

    :param str output_path: output path from open-sesame conll output
    :return: dict
    :return: mapping tuple index -> predicates found by open-sesame in those tokens
    """
    index2predicates = defaultdict(list)

    sent_id2num_tokens = {}

    index2column_name = {
        'token_index': 0,
        'sentence_index' : 6,
        'token': 1,
        'lemma': 3,
        'frame': 13,
        'role_element': 14
    }

    # this needs to be reset every time a predicate is added to index2predicates
    predicate_info = {
        'frame_label': '',
        'target_index': '',
        'sentence_index' : '',
        'roles': []
    }

    # this needs to be reset every time a predicate is added to index2predicates
    tokens = []

    prev_prefix = None

    with open(output_path) as infile:
        for line in infile:

            # newline
            if line == '\n':

                sent_id = int(line_info['sentence_index'])
                max_token_index = int(line_info['token_index']) + 1
                sent_id2num_tokens[sent_id] = max_token_index

                if predicate_info:

                    if role_info['role_name']:
                        predicate_info['roles'].append(role_info)

                        if verbose >= 2:
                            print(f'added {role_info}')

                    key = predicate_info['sentence_index']
                    index2predicates[key].append(predicate_info)

                    if verbose >= 2:
                        print(f'added predicate {predicate_info["frame_label"]} from {key}')

                    tokens = []
                    predicate_info = {
                        'frame_label': '',
                        'target_index': '',
                        'sentence_index': '',
                        'roles': []
                    }

                    role_info = {
                        'role_name': '',
                        'indices': ''
                    }

                    if verbose >= 2:
                        print('end of predicate')
                else:
                    if verbose >= 2:
                        print('end of file?')
                continue

            # actual content
            elif '\t' in line:
                split = line.strip().split('\t')
                line_info = {key: split[index]
                             for key, index in index2column_name.items()}
                line_info['token_index'] = int(line_info['token_index']) - 1
                tokens.append(line_info['token'])

                # add frame information
                if line_info['frame'] != '_':
                    predicate_info['frame_label'] = line_info['frame']
                    predicate_info['target_index'] = line_info['token_index']
                    predicate_info['sentence_index'] = int(line_info['sentence_index'])

                # role information
                role_element = line_info['role_element']

                # determine where the role is complete and you need to add it and start a new one
                add_role = determine_end_of_role(prev_prefix, prev_prefix)

                if add_role:
                    predicate_info['roles'].append(role_info)

                    if verbose >= 2:
                        print(f'added {role_info}')

                    role_info = {
                        'role_name': '',
                        'indices': ''
                    }

                if any([role_element.startswith('S'), # single token role
                        role_element.startswith('B'), # start of multi-token role
                        role_element.startswith('I') # within multi-token role
                        ]):
                    prefix, role_name = role_element.split('-')

                    # single token role
                    if prefix == 'S':
                        role_info = {
                            'role_name': role_name,
                            'indices': [line_info['token_index']]
                        }
                        predicate_info['roles'].append(role_info) # add role

                        if verbose >= 2:
                            print(f'added {role_info}')

                        role_info = {
                            'role_name': '',
                            'indices': ''
                        }

                    # multi-token role B
                    if prefix == 'B':
                        role_info = {
                            'role_name': role_name,
                            'indices': [line_info['token_index']]
                        }

                    # multi-token role I
                    if prefix == 'I':
                        role_info['indices'].append(line_info['token_index']) # add role

                    prev_prefix = prefix
                else:
                    prev_prefix = role_element

    return index2predicates, sent_id2num_tokens