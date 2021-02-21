#! /bin/sh

iniPath=/MongoExporterConf/mongoexporter.ini
echo "iniPath:" $iniPath
longMd5=""

reloadMongoExporter() {
    for line in `cat $iniPath`
    do
        echo "line:" $line
        uri=${line%&*}
        echo "uri:" $uri
        addr=${line##*&}
        echo "addr:" $addr
        #lname=${echo '$uri' | sed "s/\//_/g"}
        #exec nohup MongoExporter --mongodb.uri=$uri --web.listen-address=$addr 2>&1 > /MongoExporterLog/${lname}.log &
        exec nohup MongoExporter --mongodb.uri=$uri --web.listen-address=$addr 2>&1 &
    done
}

checkDiff() {
    shortMd5=$(md5sum $iniPath)
    if [ "$longMd5" == "$shortMd5" ]
    then
        return $((1))
    fi
    echo "new md5:" $shortMd5
    reloadMongoExporter
    longMd5=$shortMd5
    return $((0))
}

run() {
    checkDiff
    ret=$?
    if [$ret -ne 0 ]
    then
        return $ret
    fi
}

tick=10
while true
do
    run
    date
    if [ $? -eq 0 ]
    then
        tick=10
    else
        if [$tick -lt 60]
        then
            let tick+=10
        fi
    fi
    sleep $tick
done

