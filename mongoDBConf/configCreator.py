# -*-coding:utf-8-*-
import os
import sys
import yaml
import collections
import configparser

from multiConfigParser import MultiConfigParser


def makeDirs(path):
    if isinstance(path, list):
        map(makeDirs, path)
    else:
        try:
            os.makedirs(path)
        except Exception as e:
            if getattr(e, "errno", 0) != 17:
                raise

generalPath="./deployment/{suffix}/{type}/"

def monitorConfig(innerConf):
    global prometheusPort
    # 1. basic info
    host = innerConf.get("basic", "mongoExporterHostName")
    monitorSuffix=innerConf.get("basic", "monitorSuffix")
    prometheusPort = int(innerConf.get("basic", "prometheusPort"))
    mongoExportPort = int(innerConf.get("basic", "exporterPort"))

    try:
        mongoJobs = innerConf.get("mongo", "uri")
    except:
        mongoJobs = []
    jobNameList = [x.split("&")[0] for x in mongoJobs]
    if len(set(jobNameList)) != len(jobNameList):
        raise Exception("Replicate Mongonode Name")

    try:
        nodeJobs = innerConf.get("node", "uri").split("\n")
    except:
        nodeJobs = []

    prometheusConfPath = generalPath.format(type="PrometheusConf", suffix=monitorSuffix)
    prometheusDataPath = generalPath.format(type="PrometheusData", suffix=monitorSuffix)
    mongoExporterConfPath = generalPath.format(type="MongoExporterConf", suffix=monitorSuffix)
    mongoExporterLogPath = generalPath.format(type="MongoExporterLog", suffix=monitorSuffix)
    makeDirs(prometheusConfPath)
    makeDirs(prometheusDataPath)
    makeDirs(mongoExporterConfPath)
    makeDirs(mongoExporterLogPath)
    
    # 2. Prometheus
    promConf = {"global":{"evaluation_interval": "15s", "scrape_interval": "15s"},"scrape_configs":[]}
    ## 2.1 Prometheus [Node Exporter]
    for job in nodeJobs:
        jobName, addr = job.split("&")
        promConf["scrape_configs"].append({"static_configs": [{"targets": [addr]}], "job_name": jobName, \
            "relabel_configs":[{"source_labels": ["__address__"], "regex":".*" \
            , "target_label": "instance", "replacement": jobName}]})

    ## 2.2 Prometheus [Mongo Exporter]
    addrList = []
    for job in mongoJobs: 
        jobName, mongoUrl = job.split("&")
        addr = "{}:{}".format(host, mongoExportPort)
        faddr = ":{}".format(mongoExportPort)
        addrList.append("&".join([mongoUrl, faddr]))
        mongoExportPort += 1
        promConf["scrape_configs"].append({"static_configs": [{"targets": [addr]}], "job_name": jobName, \
            "relabel_configs":[{"source_labels": ["__address__"], "regex":".*" \
            , "target_label": "instance", "replacement": jobName}]})

    print("DEBUG: ", addrList)
    ## 2.3 Prometheus Config
    with open("{}/prometheus.yml".format(prometheusConfPath), "w") as f:
        yaml.dump(promConf, f)

    # 3 Mongo Exporter Config
    with open("{}/mongoexporter.ini".format(mongoExporterConfPath), "w") as f:
        f.write("\n".join(addrList))

    # 4 Docker Compose File
    composeTemplateName = "./docker-compose.template"
    with open(composeTemplateName, "r") as f:
        composeTemplate = f.read()
    composeTemplate = composeTemplate.format(CURRENT_UID=os.getuid(), CURRENT_GID=os.getgid()
        , REPO_PATH=".", MONITOR_SUFFIX=monitorSuffix, PROMETHEUS_PORT=prometheusPort, HOST=host)
    with open("./deployment/compose{}.yml".format(monitorSuffix), "w") as f:
        f.write(composeTemplate)

    print('********************************')
    print("[Prometheus    Config]: [{}/prometheus.yml]".format(prometheusConfPath))
    print("[MongoExporter Config]: [{}/mongoexporter.ini]".format(mongoExporterConfPath))
    print("[DockerCompose Config]: [./deployment/compose{}.yml]".format(monitorSuffix))
    print('********************************')

if __name__ == "__main__":
    configfile = None
    if len(sys.argv) != 2:
        print("Exp: {} configPath".format(__file__))
        exit(-1)
    else:
        configfile = sys.argv[1]

    #conf = configparser.ConfigParser(dict_type=MultiOrderedDict)
    conf = MultiConfigParser()
    conf.read(configfile)
    sections = conf.sections()
    if len(sections) == 0:
        print("config file error")
        exit(-1)

    monitorConfig(conf)

