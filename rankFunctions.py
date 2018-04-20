
from collections import defaultdict
import numpy as np


def simple_rank(feature_target, target_feature, cluster_list):
    """
    A bare rank function for implementation test.
    :param feature_target:
    :param target_feature:
    :param cluster_list:
    :return:
    """
    total_edges = 0
    target_score_within = defaultdict(float)
    feature_score = defaultdict(float)
    target_score = defaultdict(float)

    for target in cluster_list:
        for feature in target_feature[target]:
            temp = target_feature[target][feature]
            target_score_within[target] += temp
            feature_score[feature] += temp
            # every co-occurrence should be counted as one edge.
            total_edges += temp
    for target in target_score_within:
        target_score_within[target] = float(target_score_within[target]) / float(total_edges)
    for feature in feature_target:
        feature_score[feature] = float(feature_score[feature]) / float(total_edges)

    target_score_sum = 0
    for target in target_feature:
        temp_score = 0
        for feature in target_feature[target]:
            temp_score += (target_feature[target][feature] * feature_score[feature])
        target_score[target] = temp_score
        target_score_sum += temp_score
    for target in target_score:
        target_score[target] = target_score[target] / float(target_score_sum)
    return feature_score, target_score, target_score_within


def EM(target_feature, target_score_list, feature_score_list, cluster, _config):
    prob_k = {}
    sum_path = 0
    K = _config.K
    t = _config.t
    for i in range(K):
        prob_k[i] = 0
        for target in cluster[i]:
            for feature in target_feature[target]:
                prob_k[i] += target_feature[target][feature]
                sum_path += target_feature[target][feature]
    for i in range(K):
        prob_k[i] /= float(sum_path)

    sum_path_weights = 0.0
    for target in target_feature:
        for feature in target_feature[target]:
            sum_path_weights += target_feature[target][feature]

    for i in range(t):
        # Calculate expectation
        prob_target_feature_k = {}
        for target in target_feature:
            prob_target_feature_k[target] = {}
            for feature in target_feature[target]:
                prob_target_feature_k[target][feature] = {}
                sum_path_weights += target_feature[target][feature]
                sum_prob = 0.0
                for k in range(K):
                    temp = target_score_list[k][target] * \
                        feature_score_list[k][feature] * \
                        prob_k[k]
                    sum_prob += temp
                    prob_target_feature_k[target][feature][k] = temp

                for k in range(K):
                    prob_target_feature_k[target][feature][k] /= float(sum_prob)

        # Maximize expectation
        for k in range(K):
            prob_k[k] = 0.0
            for target in target_feature:
                for feature in target_feature[target]:
                    prob_k[k] += prob_target_feature_k[target][feature][k] * target_feature[target][feature]
            prob_k[k] /= sum_path_weights

    prob_target_cluster = {}
    for target in target_feature.keys():
        sum_prob = 0.0
        prob_target_cluster[target] = []
        for k in range(K):
            temp = target_score_list[k][target] * prob_k[k]
            sum_prob += temp
            prob_target_cluster[target].append(temp)
        prob_target_cluster[target] = np.array(prob_target_cluster[target]) / float(sum_prob)

    return prob_target_cluster


def calculate_similarity(a, b):
    sum_multiply = np.sum(a * b)
    sum_a = np.sqrt(np.sum(a * a))
    sum_b = np.sqrt(np.sum(b * b))
    similarity = float(sum_multiply) / float(sum_a * sum_b)
    return similarity


def cluster_reassign(cluster, prob_target_cluster, _config):
    K = _config.K
    center = {}
    for k in range(K):
        center[k] = np.zeros(K)
        target_num = len(cluster[k])
        for target in cluster[k]:
            center[k] += prob_target_cluster[target]
        center[k] /= float(target_num)

    new_cluster = defaultdict(list)
    for target in prob_target_cluster:
        max_sim = -1
        max_id = -1
        for i in range(K):
            temp_sim = calculate_similarity(prob_target_cluster[target], center[i])
            if temp_sim > max_sim:
                max_sim = temp_sim
                max_id = i
        assert(max_id != -1)
        new_cluster[max_id].append(target)

    return new_cluster


def check_null(cluster, _config):
    K = _config.K
    result = False
    for i in range(K):
        if len(cluster[i]) == 0:
            result = True
            break
    return result
