#encoding: utf-8

from flask import Flask

app = Flask(__name__)

@app.route('/uploadData', methods=['POST'])
def uploadData():
    """Data upload handler.
    """


@app.route('/cluster?fileId=<fileId>', methods=['GET'])
def cluster(fileId):
    """Cluster request handler.
    
    :param fileId: data file to cluster.
    :type fileId: String
    """


@app.route('/resultList', methods=['GET'])
def getResultList():
    """Result list handler.
    """


@app.route('/result/<taskId>', methods=['GET'])
def getResult(taskId):
    """Get result conteng.
    
    :param taskId: task id assigned.
    :type taskId: String
    """
