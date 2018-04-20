"""
@author: Mingholy
Initial works of building a RankClus model.
1. I/O tasks
2. data pre-processing
3. build bi-type graph
4. create target type set and feature type set.
"""

from collections import defaultdict
import random
import os
import csv


def read_data(_config):
    with open(os.path.join(_config.input_path, _config.input_file), 'r', encoding='utf8') as f:
        lines = list(csv.reader(f))
    return lines


def write_data(_config, lines):
    with open(os.path.join(_config.output_path, _config.output_file), 'w', encoding='utf8') as f:
        try:
            for line in lines:
                f.write(line + '\n')
        except UnicodeError:
            print('File encode error! Write file failed.')
            return False
    return True


def build_graph(_config):
    """
    build undirected graph for links between target-feature, feature-feature
    :param _config: configurations
    :return: target_feature: key: dict[target][feature], value: link count
    :return: feature_target: key: dict[feature][target], value: link count
    :return: feature_feature:  key: dict[feature][feature], value: co-occurrence count
    """
    # To cluster medicine, treat medicine as target_set.
    target_set = set()
    # Symptoms are of feature_set.
    feature_set = set()
    raw_lines = read_data(_config)
    # TODO: Format is yet to be defined.
    # current:
    # symptom, medicine, medicine, medicine...
    for line in raw_lines:
        target_set.add(line[0])
        for i in range(1, len(line)):
            feature_set.add(line[i])

    target_feature = {}
    feature_target = {}
    feature_feature = {}

    for target in target_set:
        target_feature[target] = defaultdict(int)
    for feature in feature_set:
        feature_target[feature] = defaultdict(int)
        feature_feature[feature] = defaultdict(int)

    # build undirected graph for target-feature, feature-feature.
    for line in raw_lines:
        current_target = line[0]
        length = len(line)
        for i in range(1, length):
            # count target-feature links
            target_feature[current_target][line[i]] += 1
            feature_target[line[i]][current_target] += 1
            # for each symptom with multiple medicines, these medicines have inter-relationships as well.
            for j in range(i + 1, length):
                feature_feature[line[i]][line[j]] += 1
                feature_feature[line[j]][line[i]] += 1
    return feature_target, target_feature, feature_feature


def initialize_cluster(target_list, _config):
    """
    initialize clusters with region knowledge.
    :param target_list: target list
    :param _config: configuration
    :return:  cluster dict, key: cluster id, value: list for target items.
    """
    K = _config.K
    target_list = list(target_list)
    random.shuffle(target_list)
    flag = False
    while not flag:
        flag = True
        cluster = defaultdict(list)
        '''
        Initial top N cluster with specified target item, if given.
        '''
        size = len(_config.specified_targets)
        if size:
            for i in range(size):
                cluster[i].append(_config.specified_targets[i])
        for target_item in target_list:
            if target_item in _config.specified_targets:
                continue
            random_id = random.randint(0, K - 1)
            cluster[random_id].append(target_item)
        for i in range(K):
            if len(cluster[i]) == 0:
                flag = False
                print('Initialize error!Null cluster found.')
                break
    return cluster

