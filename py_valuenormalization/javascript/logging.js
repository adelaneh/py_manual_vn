var eventCodes = new Object();
eventCodes['ncp_load']          = 1;
eventCodes['ncp_poc_click']     = 2;
eventCodes['ncp_pureno_click']  = 3;
eventCodes['ncp_pureyes_click'] = 4;
eventCodes['ncp_value_click']   = 5;
eventCodes['ncp_split_done']    = 6;
eventCodes['ncp_merge_click']   = 7;
eventCodes['ncp_cluster_click'] = 8;
eventCodes['ncp_merge_done']    = 9;

var isLogging = document.getElementById('logging_on');

var logNextClusterPageLoad = function(e) {
    var logent = [];
    logent.push(Date.now());
    logent.push(eventCodes['ncp_load']);
    logent.push(allClusts[curClusterLabel].length);
    logent.push(curClusterLabel);
    console.log(logent);
    if (!isLogging) {return;}

    pushLogToServer(logent);

    return;
}

var logPureNoButtonClick = function(e) {
    var logent = [];
    logent.push(Date.now());
    logent.push(eventCodes['ncp_pureno_click']);
    logent.push(allClusts[curClusterLabel].length);
    console.log(logent);
    if (!isLogging) {return;}

    pushLogToServer(logent);

    return;
}

var logPureYesButtonClick = function(e) {
    var logent = [];
    logent.push(Date.now());
    logent.push(eventCodes['ncp_pureyes_click']);
    logent.push(allClusts[curClusterLabel].length);
    console.log(logent);
    if (!isLogging) {return;}

    pushLogToServer(logent);

    return;
}

var logPOCButtonClick = function(clsz) {
    var logent = [];
    logent.push(Date.now());
    logent.push(eventCodes['ncp_poc_click']);
    logent.push(clsz);
    console.log(logent);
    if (!isLogging) {return;}

    pushLogToServer(logent);

    return;
}

var logValueButtonClick = function(eid) {
    var logent = [];
    logent.push(Date.now());
    logent.push(eventCodes['ncp_value_click']);
    logent.push(allClusts[curClusterLabel].length);

    var valIndex        = -1
    var curCluster = allClusts[curClusterLabel].sort();
    for (var tt = 0; tt < curCluster.length; tt++) {
        if (curCluster[tt] == eid) {
            valIndex        = tt + 1;
        }
    }
    logent.push(valIndex);

    logent.push(eid);
    logent.push(document.getElementById(eid).parentElement.className.indexOf("active") == -1);
    console.log(logent);
    if (!isLogging) {return;}

    pushLogToServer(logent);

    return;
}

var logSplitDone = function(e) {
    var logent = [];
    logent.push(Date.now());
    logent.push(eventCodes['ncp_split_done']);
    console.log(logent);
    if (!isLogging) {return;}

    pushLogToServer(logent);

    return;
}

var logMergeButtonClick = function(e) {
    var logent = [];
    logent.push(Date.now());
    logent.push(eventCodes['ncp_merge_click']);
    logent.push(Object.keys(splitClusters).length);
    logent.push(Object.keys(mergedClusters).length);
    console.log(logent);
    if (!isLogging) {return;}

    pushLogToServer(logent);

    return;
}

var logMergeDone = function(e) {
    var logent = [];
    logent.push(Date.now());
    logent.push(eventCodes['ncp_merge_done']);
    console.log(logent);
    if (!isLogging) {return;}

    pushLogToServer(logent);

    return;
}

var logClusterButtonClick = function(eid) {
    var logent = [];
    logent.push(Date.now());
    logent.push(eventCodes['ncp_cluster_click']);
    logent.push(Object.keys(splitClusters).length);
    logent.push(Object.keys(mergedClusters).length);

    var clustIndex        = -1
    var remainingClusters = Object.keys(splitClusters).sort();
    for (var tt = 0; tt < Object.keys(splitClusters).length; tt++) {
        if (remainingClusters[tt] == eid) {
            clustIndex        = tt + 1;
        }
    }
    if (clustIndex == -1) {
        var remainingClusters = Object.keys(mergedClusters).sort();
        for (var tt = 0; tt < Object.keys(mergedClusters).length; tt++) {
            if (remainingClusters[tt] == eid) {
                clustIndex        = Object.keys(splitClusters).length + tt + 1;
            }
        }
    }
    logent.push(clustIndex);

    logent.push(eid);
    logent.push(document.getElementById(eid).parentElement.className.indexOf("active") == -1);
    console.log(logent);
    if (!isLogging) {return;}

    pushLogToServer(logent);

    return;
}

var pushLogToServer = function(ent) {
    var myInput = new Object();
    myInput['logent'] = '"' + ent.join('", "') + '"';

    $.ajax({
        type: 'POST',
        url: '/simple_clustering/push_log',
        timeout: 0,
        data: JSON.stringify(myInput),
    }).done(function(data) {
        console.log('Pushed log entry.');
    }).fail(function(j,s,t) {
        console.log('Something happened!');
        console.log(j.responseText);
        console.log(s);
        console.log(t);
    });

    return;
}
