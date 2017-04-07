var compStrCaseInsensitive = function (a, b) {
	return a.toLowerCase().localeCompare(b.toLowerCase());
}

var vpkey = [];
var ispure_tr_pairs = [];

var matchYes = function(e){
	ispure_tr_pairs.push([vpkey, "1"]);
	return match(e);
}

var matchNo = function(e){
	ispure_tr_pairs.push([vpkey, "0"]);
	return match(e);
}

var match = function(e){
	recorded_resps['times'].push(Date.now());


	if (seq_counter > 0) {
		seq_counter = seq_counter - 1;
		loadValues();
	}
	else {
		calib_app.estimate_ua_match_params(JSON.stringify(recorded_resps), JSON.stringify(ispure_tr_pairs));
	}

	return;
}

var loadValues = function(e) {
	document.getElementById('match_instructions_box').style.display = 'none';
	document.getElementById('start_matching_btn_panel').style.display = 'none';

	document.getElementById('match_desc_box').style.display = 'block';
	document.getElementById('values-panel').style.display = 'block';

	$("#countdown").html( (seq_counter + 1) + " value pairs to go");

	var ci1 = rand_key(allClusts);
	var cc1 = allClusts[ci1][0];
	var cc2 = "";
	if (Math.random() < 0.5) {
		while (allClusts[ci1].length < 2) { ci1 = rand_key(allClusts); }
		cc1 = allClusts[ci1][0];
		cc2 = allClusts[ci1][1];
	}
	else {
		var ci2 = rand_key(allClusts);
		while (ci1 == ci2) { ci2 = rand_key(allClusts); }
		cc2 = allClusts[ci2][0];
	}
	var txt = "<table style=\"width:40%\"><tr>";
	txt = txt + "<td>";
	txt = txt + "<label class=\"btn btn-default btn-block btn_clust\">";
	txt = txt + cc1;
	txt = txt + "</label>";
	txt = txt + "</td>";
	txt = txt + "<td>";
	txt = txt + "<label class=\"btn btn-default btn-block btn_clust\">";
	txt = txt + cc2;
	txt = txt + "</label>";
	txt = txt + "</td>";
	txt = txt + "</tr></table>";
	vpkey = [cc1,cc2];
	$("#values_panel_body").html(txt);

	switchAnswerBoxes(seq_counter);

	recorded_resps['times'].push(Date.now());

	return;
}

var isPureYes = function(e) {
	recorded_resps['times'].push(Date.now());
	recorded_resps['ispure'].push('1');

	if (seq_counter > 0) {
		seq_counter = seq_counter - 1;
		loadClusterValues();
	}
	else {
		calib_app.estimate_ua_ispure_params(JSON.stringify(recorded_resps));
	}

	return;
}

var isPureNo = function(e) {
	recorded_resps['times'].push(Date.now());
	recorded_resps['ispure'].push('0');

	if (seq_counter > 0) {
		seq_counter = seq_counter - 1;
		loadClusterValues();
	}
	else {
		calib_app.estimate_ua_ispure_params(JSON.stringify(recorded_resps));
	}

	return;
}

var loadSampleClustersInColumns = function(e) {
	var txt = "<table style=\"width:70%\"><tr>";
	var colCnt = 1;
	var curCluster = "";
	if (curClusterLabel in samples_pe_clusts10) {
		curCluster = samples_pe_clusts10[curClusterLabel].sort(compStrCaseInsensitive);
	} else if (curClusterLabel in samples_pe_clusts20) {
		curCluster = samples_pe_clusts20[curClusterLabel].sort(compStrCaseInsensitive);
	}

	var maxColSize = Math.floor(curCluster.length / colCnt);
	if ((curCluster.length / colCnt) != maxColSize) { maxColSize = maxColSize + 1; }
	if (curCluster.length < 11) { maxColSize = 10; }

	for (var colinx = 0; colinx < colCnt; colinx++) {
		var binx = colinx * maxColSize;
		var einx = Math.min((colinx + 1) * maxColSize - 1, curCluster.length - 1);
		txt = txt + "<td>";
		txt = txt + "<div class=\"btn-group\" role=\"group\" data-toggle=\"buttons\">";
		for (var rowinx = binx; rowinx <= einx; rowinx++){
			txt = txt + "<label class=\"btn btn-default btn-block btn_clust\" onclick=\"valueButtonClickCalib(event, '" + curCluster[rowinx] + ", false');\">";
			txt = txt + "<input id=\"" + curCluster[rowinx] + "\" type=\"checkbox\" autocomplete=\"off\">" + curCluster[rowinx];
			txt = txt + "</label><p></p>";
		}
		txt = txt + "</div></td>";
	}
	txt = txt + "</tr></table>";
	$("#clusters_panel").html(txt);
	return;
}

var cluster_doment_vals = new Object();

var calcPurity = function() {
	var curCluster = "";
	var lambda = 0;
	if (curClusterLabel in samples_pe_clusts10) {
		curCluster = samples_pe_clusts10[curClusterLabel].sort(compStrCaseInsensitive);
		lambda = 10;
	} else if (curClusterLabel in samples_pe_clusts20) {
		curCluster = samples_pe_clusts20[curClusterLabel].sort(compStrCaseInsensitive);
		lambda = 20;
	}
	var clstsz = curCluster.length;
	var domentvalcnt = 0;
	cluster_doment_vals[curClusterLabel] = [];
	for (var ii = curCluster.length - 1; ii >= 0; ii--) {
		var kk = curCluster[ii];
		var curEl = document.getElementById(kk);
		if (curEl != null) {
			var parentEl = document.getElementById(kk).parentElement;
			if (parentEl.className.indexOf("active") > -1) {
				domentvalcnt ++;
				cluster_doment_vals[curClusterLabel].push(kk);
			}
		}
	}

	if (domentvalcnt == 0) {
		alert("Please select at least one value.");
		return;
	}

	if (curClusterLabel in samples_pe_clusts10) {
		delete samples_pe_clusts10[curClusterLabel];
	} else if (curClusterLabel in samples_pe_clusts20) {
		delete samples_pe_clusts20[curClusterLabel];
	}
	if (!(lambda in cluster_purities)) {
		cluster_purities[lambda] = [];
	}
//	cluster_purities[lambda].push(domentvalcnt / clstsz);
	cluster_purities[lambda].push(domentvalcnt);
	cluster_purities[lambda].push(clstsz);
	//console.log(cluster_purities);
	if (Object.keys(samples_pe_clusts10).length > 0) {
		curClusterLabel = Object.keys(samples_pe_clusts10)[0];
	} else if (Object.keys(samples_pe_clusts20).length > 0) {
		curClusterLabel = Object.keys(samples_pe_clusts20)[0];
	} else {
		calib_app.estimate_purity_function_params(JSON.stringify(cluster_purities), JSON.stringify(cluster_doment_vals));
		return;
	}
	$('#countdown').html(( Object.keys(samples_pe_clusts10).length + Object.keys(samples_pe_clusts20).length ) + " Cluster(s) to Go");
	loadSampleClustersInColumns();

	return;
}

var values = [];

var loadClusterValues = function(e) {
	document.getElementById('ispure_instructions_box').style.display = 'none';
	document.getElementById('start_ispure_btn_panel').style.display = 'none';

	document.getElementById('ispure_desc_box').style.display = 'block';
	document.getElementById('values-panel').style.display = 'block';
	document.getElementById('ispure_box_bottom').style.display = 'block';

	$("#countdown").html( (seq_counter + 1) + " clusters to go");

	recorded_resps['times'].push(Date.now());
	values = [];
	var ci1 = rand_key(allClusts);
	var trycnt = 0;
	while (ci1 in recorded_resps['clusters'] || allClusts[ci1].length == 1 || trycnt < 20) {
		ci1 = rand_key(allClusts);
		trycnt = trycnt + 1;
	}
	for (var jj = 0; jj < allClusts[ci1].length; jj++) {
		values.push(allClusts[ci1][jj]);
	}
	values.sort(compStrCaseInsensitive);
	if (trycnt == 20) { values = shuffle(values); }
	fillClusterTable(false);
	recorded_resps['clusters'].push(ci1);
}

var valueButtonClickCalib = function(e, clust, isFindDom) {
	if (!isFindDom) { return; }

	recorded_resps['times'].push(Date.now());

	if (seq_counter > 0) {
		seq_counter = seq_counter - 1;
		loadClusterValuesForFindDom();
	}
	else {
		calib_app.estimate_ua_finddom_params(JSON.stringify(recorded_resps));
	}

	return;
}

var loadClusterValuesForFindDom = function(e) {
	document.getElementById('finddom_instructions_box').style.display = 'none';
	document.getElementById('start_finddom_btn_panel').style.display = 'none';

	document.getElementById('finddom_desc_box').style.display = 'block';
	document.getElementById('values-panel').style.display = 'block';

	$("#countdown").html( (seq_counter + 1) + " clusters to go");

	recorded_resps['times'].push(Date.now());

	var omega_1 = 7;
	var maxtries = 100;

	values = [];
	var ci1 = rand_key(allClusts);
	var trycnt = 0;
	if (seq_counter > 2) {
		while ( ( ci1 in recorded_resps['clusters'] || allClusts[ci1].length == 1 || allClusts[ci1].length > omega_1 ) && trycnt < maxtries ) {
			ci1 = rand_key(allClusts);
			trycnt = trycnt + 1;
		}
	}
	else {
		while ( (ci1 in recorded_resps['clusters'] || allClusts[ci1].length <= omega_1 ) && trycnt < maxtries) {
			ci1 = rand_key(allClusts);
			trycnt = trycnt + 1;
		}
	}
	for (var jj = 0; jj < allClusts[ci1].length; jj++) {
		values.push(allClusts[ci1][jj]);
	}
	values.sort(compStrCaseInsensitive);
	if (trycnt == maxtries) { values = shuffle(values); }
	fillClusterTable(true);
	recorded_resps['clusters'].push(ci1);
}

var shuffle = function(o) {
	for(var j, x, i = o.length; i; j = Math.floor(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
	return o;
}

var fillClusterTable = function(isFindDom) {
	var txt = "<table style=\"width:70%\"><tr>";
	var colCnt = 1;
	//	var curCluster = values.sort();
	var curCluster = values;
	var maxColSize = Math.floor(curCluster.length / colCnt);
	if ((curCluster.length / colCnt) != maxColSize) { maxColSize = maxColSize + 1; }
	if (curCluster.length < 11) { maxColSize = 10; }

	for (var colinx = 0; colinx < colCnt; colinx++) {
		var binx = colinx * maxColSize;
		var einx = Math.min((colinx + 1) * maxColSize - 1, curCluster.length - 1);
		txt = txt + "<td>";
		txt = txt + "<div class=\"btn-group\" role=\"group\" data-toggle=\"buttons\">";
		for (var rowinx = binx; rowinx <= einx; rowinx++){
			txt = txt + "<label class=\"btn btn-default btn-block btn_clust\" onclick=\"valueButtonClickCalib(event, '" + curCluster[rowinx] + "', " + isFindDom + ");\">";
			txt = txt + "<input id=\"" + curCluster[rowinx] + "\" type=\"checkbox\" autocomplete=\"off\">" + curCluster[rowinx];
			txt = txt + "</label><p></p>";
		}
		txt = txt + "</div></td>";
	}
	txt = txt + "</tr></table>";
	$("#values_panel_body").html(txt);
	return;
}

var generateRandomClusters = function(e) {
	var purity = 0.;
	var qq = rand_index(20) + 2;
	if (Math.random() < 0.5){
		var cc = rand_index(uap_clusters.length);
		for (var jj = 0; jj < qq; jj++) {
			var hh = rand_index(uap_clusters[cc].length);
			values.push(uap_clusters[cc][hh]);
		}
		purity = 1.;
	}
	else {
		var ccnts = new Object();
		for (var jj = 0; jj < qq; jj++) {
			var cc = rand_index(uap_clusters.length);
			if (cc in Object.keys(ccnts)) { ccnts[cc] = ccnts[cc] + 1; }
			else { ccnts[cc] = 1; }
			var tt = rand_index(uap_clusters[cc].length);
			values.push(uap_clusters[cc][tt]);
		}
		var maxcc = 0;
		var maxclust = "";
		var ccnks = Object.keys(ccnts);
		for (var ccx = 0; ccx < ccnks.length; ccx++) {
			var cc = ccnks[ccx];
			if (ccnts[cc] > maxcc) {
				maxcc = ccnts[cc];
				maxclust = uap_clusters[cc][0];
			}
		}
		console.log(maxclust);
		console.log(maxcc);
		console.log(qq);
		purity = 1. * maxcc / qq;
	}
	return purity;
}

var switchIsPureAnswerBoxes = function(e) {
	if (e % 2 == 0) {
		document.getElementById('ispure_box_top').style.display = 'none';
		document.getElementById('ispure_box_bottom').style.display = 'block';
	}
	else {
		document.getElementById('ispure_box_top').style.display = 'block';
		document.getElementById('ispure_box_bottom').style.display = 'none';
	}
	return;
}

var switchAnswerBoxes = function(e) {
	if (e % 2 == 0) {
		document.getElementById('match_yesno_box_top').style.display = 'none';
		document.getElementById('match_yesno_box_bottom').style.display = 'block';
	}
	else {
		document.getElementById('match_yesno_box_top').style.display = 'block';
		document.getElementById('match_yesno_box_bottom').style.display = 'none';
	}
	return;
}

function rand_index(ll){
	return Math.floor(Math.random() * ll);
}

function rand_key(ll){
	var result;
	var count = 0;
	for (var prop in ll)
		if (Math.random() < 1/++count)
			result = prop;
	return result;
}

var generateRandomClustersForFindDom = function(e) {
	var purity = 0.;
	var qq = rand_index(20) + 2;
	var hh = rand_index(qq - 1) + 1;
	var ccnts = new Object();
	var cct = rand_index(uap_clusters.length);
	ccnts[cct] = 0;
	for (var jj = 0; jj < hh; jj++) {
		ccnts[cct] = ccnts[cct] + 1;
		var tt = rand_index(uap_clusters[cct].length);
		values.push(uap_clusters[cct][tt]);
	}
	console.log(ccnts);
	for (var jj = 0; jj < qq - hh; jj++) {
		var cc = rand_index(uap_clusters.length);
		console.log(cc.toString() in Object.keys(ccnts));
		if (cc.toString() in Object.keys(ccnts)) { ccnts[cc] = ccnts[cc] + 1; }
		else { ccnts[cc] = 1; }
		var tt = rand_index(uap_clusters[cc].length);
		values.push(uap_clusters[cc][tt]);
	}
	var maxcc = 0;
	var maxclust = "";
	var ccnks = Object.keys(ccnts);
	for (var ccx = 0; ccx < ccnks.length; ccx++) {
		var cc = ccnks[ccx];
		if (ccnts[cc] > maxcc) {
			maxcc = ccnts[cc];
			maxclust = uap_clusters[cc][0];
		}
	}
	console.log(ccnts);
	console.log(maxclust);
	console.log(maxcc);
	console.log(qq);
	purity = 1. * maxcc / qq;
	values = shuffle(values);
	return purity;
}

