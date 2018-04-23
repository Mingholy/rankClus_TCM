from init import build_graph, initialize_cluster
from rankFunctions import simple_rank, cluster_reassign, check_null, EM
import multiprocessing as mp
import heapq

class Config:
    input_file = 'data_preprocessed.txt'
    input_path = 'data/'
    output_file = 'output_data.csv'
    output_path = 'output_path/'
    # Number of iteration
    t = 5
    # Cluster numbers for type set. Default is 10
    K = 23
    # Rank method: [Simple_rank|Authority_rank]. Default is 'Simple_rank'
    rank_method = 'Simple_rank'
    # Parameter training method: [EM|BM]. Parameter training method can be specified
    # as a specific algorithm like Baulm-Welch. Default is 'EM'
    iteration_method = 'EM'
    specified_targets = []


config = Config()
feature_target, target_feature, feature_feature = build_graph(config)
clusters = initialize_cluster(target_feature.keys(), config)
rankclus_iter = 0
manager = mp.Manager()

def rank(i, feature_score_cluster, target_score_cluster, target_score_within, clusters):
    print('Ranking in cluster ' + str(i))
    feature_score_cluster[i], target_score_cluster[i], target_score_within[i] = simple_rank(
       feature_target, target_feature, clusters[i]
    )


while rankclus_iter < config.t:
    feature_score_cluster = manager.dict()
    target_score_cluster = manager.dict()
    target_score_within = manager.dict()
    print('Start ranking.')

    pool = mp.Pool(processes=config.K)
    for i in range(config.K):
        pool.apply_async(rank, (i, feature_score_cluster, target_score_cluster, target_score_within, clusters))
    pool.close()
    pool.join()

    feature_score_cluster = dict(feature_score_cluster)
    target_score_cluster = dict(target_score_cluster)

    print('Start EM.')
    prob_target_cluster = EM(target_feature, target_score_cluster, feature_score_cluster, clusters, config)

    print('Start clustering.')
    newcluster = cluster_reassign(clusters, prob_target_cluster, config)
    del clusters
    clusters = newcluster
    if check_null(clusters, config):
        del clusters
        clusters = initialize_cluster(target_feature.keys(), config)
        print('Found null cluster, restart.')
        rankclus_iter = 0
    else:
        rankclus_iter += 1
    print('Iteration ' + str(rankclus_iter))

with open('output.txt', 'w', encoding='utf-8') as f:
    for i in range(config.K):
        f.write('Cluster ' + str(i) + '\n')
        feature_score, target_score, target_score_within = simple_rank(feature_target, target_feature, clusters[i])
        for key in target_score_within.keys():
            line = '{}:{}'.format(key, target_score_within[key])
            print(line)
            f.write(line + '\n')
