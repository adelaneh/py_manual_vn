var compStrCaseInsensitive = function (a, b) {
	return a.toLowerCase().localeCompare(b.toLowerCase());
}

var pureYes = function(e){
	var curClstr = allClusts[curClusterLabel];
	for (var ii = curClstr.length; ii >= 0; ii--) {
		var kk = curClstr[ii];
		var curEl = document.getElementById(kk);
		if (curEl != null) {
			var parentEl = document.getElementById(kk).parentElement;
			if (parentEl.className.indexOf("active") < 0) {
				parentEl.className = parentEl.className.concat(" active");
			}
		}
	}
	pullOutCluster(e);
	return;
}

var pureNo = function(e){
	document.getElementById('ispure_desc_box').style.display = 'none';
	document.getElementById('ispure_box').style.display = 'none';
	document.getElementById('findoment_desc_box').style.display = 'block';
	document.getElementById('findoment_box').style.display = 'block';
	document.getElementById('selectdom_desc_box').style.display = 'none';
	document.getElementById('selectdom_box').style.display = 'none';
	document.getElementById('selectnondom_desc_box').style.display = 'none';
	document.getElementById('selectnondom_box').style.display = 'none';
	return;
}

var removeElementById = function(id) {
	var parentEl = document.getElementById(id).parentElement;
	var grandpaEl = parentEl.parentElement;
	parentEl.innerHTML = '';
	grandpaEl.removeChild(parentEl);
	return;
}

var loadClustersInColumns = function(e) {
	var txt = "<table style=\"width:70%\"><tr>";
	var colCnt = 1;
	var curCluster = allClusts[curClusterLabel].sort();
	var maxColSize = Math.floor(curCluster.length / colCnt);
	if ((curCluster.length / colCnt) != maxColSize) { maxColSize = maxColSize + 1; }
	if (curCluster.length < 11) { maxColSize = 10; }

	for (var colinx = 0; colinx < colCnt; colinx++) {
		var binx = colinx * maxColSize;
		var einx = Math.min((colinx + 1) * maxColSize - 1, curCluster.length - 1);
		txt = txt + "<td>";
		txt = txt + "<div class=\"btn-group\" role=\"group\" data-toggle=\"buttons\">";
		for (var rowinx = binx; rowinx <= einx; rowinx++){
			txt = txt + "<label class=\"btn btn-default btn-block btn_clust\" onclick=\"valueButtonClick(event, '" + curCluster[rowinx] + "');\">";
			txt = txt + "<input id=\"" + curCluster[rowinx] + "\" type=\"checkbox\" autocomplete=\"off\">" + curCluster[rowinx];
			txt = txt + "</label><p></p>";
		}
		txt = txt + "</div></td>";
	}
	txt = txt + "</tr></table>";
	$("#clusters_panel").html(txt);
	return;
}

var purityLt01 = function() {
}

var purityLt05GE01 = function() {
	document.getElementById('ispure_desc_box').style.display = 'none';
	document.getElementById('ispure_box').style.display = 'none';
	document.getElementById('findoment_desc_box').style.display = 'none';
	document.getElementById('findoment_box').style.display = 'none';
	document.getElementById('selectdom_desc_box').style.display = 'block';
	document.getElementById('selectdom_box').style.display = 'block';
	document.getElementById('selectnondom_desc_box').style.display = 'none';
	document.getElementById('selectnondom_box').style.display = 'none';
	return;
}

var purityGE05 = function() {
	document.getElementById('ispure_desc_box').style.display = 'none';
	document.getElementById('ispure_box').style.display = 'none';
	document.getElementById('findoment_desc_box').style.display = 'none';
	document.getElementById('findoment_box').style.display = 'none';
	document.getElementById('selectdom_desc_box').style.display = 'none';
	document.getElementById('selectdom_box').style.display = 'none';
	document.getElementById('selectnondom_desc_box').style.display = 'block';
	document.getElementById('selectnondom_box').style.display = 'block';
	return;
}

var valueButtonClick = function(event, eid) {
	if (document.getElementById('ispure_box').style.display != 'none' || document.getElementById('findoment_box').style.display != 'none') {
		if (document.getElementById(eid).parentElement.className.indexOf("active") > -1) {
			$("[id='"+eid+"'").parent().removeClass("active");
		}
		event.stopImmediatePropagation();
		return;
	}
	
	logValueButtonClick(eid);
}

var showClusteringSummary = function(e) {
	var txt = "";
	txt = txt + "<tr><td><b>Number of Clusters</b></td><td>" + (Object.keys(mergedClusters).length) + "</td></tr>";
	var maxClSz = 0;
	var minClSz = 100000;
	for (var kk in mergedClusters) {
		var ccs = mergedClusters[kk].length;
		if (ccs > maxClSz) {
			maxClSz = ccs;
		}
		if (ccs < minClSz) {
			minClSz = ccs;
		}
	}
	txt = txt + "<tr><td><b>Maximum Cluster Size</b></td><td>" + maxClSz + "</td></tr>";
	txt = txt + "<tr><td><b>Minimum Cluster Size</b></td><td>" + minClSz + "</td></tr>";
	$("#clustering_summary_table").html(txt);
	return;
}

var pullOutCluster = function(e){
	var curClstr = allClusts[curClusterLabel];
	var poclust = [];
	for (var ii = curClstr.length - 1; ii >= 0; ii--) {
		var kk = curClstr[ii];
		var curEl = document.getElementById(kk);
		if (curEl != null) {
			var parentEl = document.getElementById(kk).parentElement;
			if (parentEl.className.indexOf("active") > -1) {
				poclust.push(kk);
				removeElementById(kk);
				allClusts[curClusterLabel].splice(allClusts[curClusterLabel].indexOf(kk), 1);
			}
		}
	}
	if (poclust.length < 1) { return; }
	splitClusters[poclust[0]] = poclust;
//	if ((allClusts[curClusterLabel].length != 0) || (document.getElementById('ispure_box_top').style.display == 'none')) {
//		logPOCButtonClick(allClusts[curClusterLabel].length + poclust.length);
//	}

	document.getElementById('ispure_desc_box').style.display = 'block';
	document.getElementById('ispure_box').style.display = 'block';
	document.getElementById('findoment_desc_box').style.display = 'none';
	document.getElementById('findoment_box').style.display = 'none';
	document.getElementById('selectdom_desc_box').style.display = 'none';
	document.getElementById('selectdom_box').style.display = 'none';
	document.getElementById('selectnondom_desc_box').style.display = 'none';
	document.getElementById('selectnondom_box').style.display = 'none';

	if (allClusts[curClusterLabel].length <= 1) {
//		if (allClusts[curClusterLabel].length == 0) {delete allClusts[curClusterLabel];}
		norm_app.reload_split_clusters(JSON.stringify(splitClusters));
	}
	return;
}

var pullOutReminder = function(e){
	var curClstr = allClusts[curClusterLabel];
	var poclust = [];
	for (var ii = curClstr.length - 1; ii >= 0; ii--) {
		var kk = curClstr[ii];
		var curEl = document.getElementById(kk);
		if (curEl != null) {
			var parentEl = document.getElementById(kk).parentElement;
			if (parentEl.className.indexOf("active") == -1) {
				poclust.push(kk);
				removeElementById(kk);
				allClusts[curClusterLabel].splice(allClusts[curClusterLabel].indexOf(kk), 1);
			}
			else {
				parentEl.className = parentEl.className.replace(/(?:^|\s)active(?!\S)/g, '');
			}
		}
	}
	if (poclust.length == curClstr.length) { return; }
	splitClusters[poclust[0]] = poclust;

	document.getElementById('ispure_desc_box').style.display = 'block';
	document.getElementById('ispure_box').style.display = 'block';
	document.getElementById('findoment_desc_box').style.display = 'none';
	document.getElementById('findoment_box').style.display = 'none';
	document.getElementById('selectdom_desc_box').style.display = 'none';
	document.getElementById('selectdom_box').style.display = 'none';
	document.getElementById('selectnondom_desc_box').style.display = 'none';
	document.getElementById('selectnondom_box').style.display = 'none';

	if (allClusts[curClusterLabel].length <= 1) {
		norm_app.reload_split_clusters(JSON.stringify(splitClusters));
	}
	return;
}

var generateClusterSizeHistogram = function(e) {
	var values = [];
	for (var kk in mergedClusters) { values.push(mergedClusters[kk].length); }

	var formatCount = d3.format(",.0f");

	var margin = {top: 10, right: 50, bottom: 30, left: 30},
	width = $("#clustering_summary_panel").width() - margin.left - margin.right,
		height = 500 - margin.top - margin.bottom;

	var x = d3.scale.linear()
		.domain([0, Math.max.apply(null, values) + 1])
		.range([0, width]);

	var data = d3.layout.histogram()
		.bins(x.ticks(Math.max.apply(null, values) + 1))
		(values);

	var y = d3.scale.linear()
		.domain([0, d3.max(data, function(d) { return d.y; })])
		.range([height, 0]);

	var xAxis = d3.svg.axis()
		.scale(x)
		.tickValues(x.ticks(Math.max.apply(null, values) + 1))
		.orient("bottom");

	var yAxis = d3.svg.axis()
		.scale(y)
		.orient("left")
		.ticks(Math.min(10, d3.max(data, function(d) { return d.y; })));

	var svg = d3.select("#size_histogram").append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	var bar = svg.selectAll(".hist-bar")
		.data(data)
		.enter().append("g")
		.attr("class", "hist-bar")
		.attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

	bar.append("rect")
		.attr("x", -x(data[0].dx/2))
		.attr("width", x(data[0].dx) - 1)
		.attr("height", function(d) { return height - y(d.y); });

	bar.append("text")
		.attr("dy", ".75em")
		.attr("y", 6)
		.attr("x", 1)
		.attr("text-anchor", "middle")
		.text(function(d) { return formatCount(d.y); });

	svg.append("g")
		.attr("class", "x hist-axis")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis);

	svg.append("g")
		.attr("class", "y hist-axis")
		.call(yAxis)
		.append("text")
		.attr("transform", "rotate(-90)")
		.attr("y", 6)
		.attr("dy", ".71em")

	return;
}

////////////////////////////////////////////////////////////////////////////////
var mergeClusters = function(e) {
	//logMergeButtonClick();
	var mrgdClustLabels = [];

	for(var cLabel in mergedClusters){
		if (document.getElementById(cLabel).parentElement.className.indexOf("active") > -1){
			mrgdClustLabels.push(cLabel);
		}
	}
	if (mrgdClustLabels.length < 2) {
		alert('Please select at least two cluster to merge.');
		return;
	}

	var mrgdClustLabel = mrgdClustLabels.sort(compStrCaseInsensitive)[0];
	var resMergCluster = [];

	for (var ii = mrgdClustLabels.length - 1; ii >= 0; ii--) {
		var kk = mrgdClustLabels[ii];
		for (var jj = mergedClusters[kk].length - 1; jj >= 0; jj--) {
			var vv = mergedClusters[kk][jj];
			resMergCluster.push(vv);
		}
		delete mergedClusters[kk];
	}
	mergedClusters[mrgdClustLabel] = resMergCluster;
	norm_app.reload_local_merging(JSON.stringify(mergedClusters), (document.documentElement && document.documentElement.scrollTop) || document.body.scrollTop || window.pageYOffset);
	return;
}

var loadPureClustersInColumns = function(e) {
	var repeatMrgBtnEvery = 15;
	var txt = "<table style=\"width:100%;\">";
	var remainingClusters = Object.keys(mergedClusters).sort(compStrCaseInsensitive);
	$("#clust-cnt-cell").html("<b>Number of clusters: " + remainingClusters.length + "</b><p></p>");

	for (var rowinx = 0; rowinx < remainingClusters.length; rowinx++){
		txt = txt + "<tr>";
		txt = txt + "<td><div style=\"width:100%;\" class=\"btn-group\" role=\"group\" data-toggle=\"buttons\"><label class=\"btn outline btn-block btn_clust_mrg\" data-container=\"body\" data-toggle=\"popover\" data-placement=\"right\" data-html=\"true\" data-content=\"";
		for (var valinx = 0; valinx < mergedClusters[remainingClusters[rowinx]].length; valinx++){
			txt = txt + mergedClusters[remainingClusters[rowinx]].sort(compStrCaseInsensitive)[valinx]
			if (valinx < mergedClusters[remainingClusters[rowinx]].length - 1) {
				txt = txt + "<br />";
			}
		}
		txt = txt + "\" data-trigger=\"hover\">";// onclick=\"logClusterButtonClick('" + remainingClusters[rowinx]+ "');\">";
		txt = txt + "<input id=\"" + remainingClusters[rowinx] + "\" type=\"checkbox\" autocomplete=\"off\">" + remainingClusters[rowinx];
		txt = txt + "</label></div></td>";

		txt = txt + "<td>";
		if ( rowinx % repeatMrgBtnEvery == 0) {
			txt = txt + "<button class=\"btn btn-primary\" id=\"mrgbtntop" + rowinx + "\" type=\"button\" onclick=\"mergeClusters()\">Merge Selected Values</button>";
		}
		txt = txt + "</tr>";
	}
	txt = txt + "</table>";
	//	console.log(txt);
//	$("#clusters_labels_panel").html(txt);
//	$("#pure_cell").html(txt);
	document.getElementById("pure_cell").innerHTML = txt;
	return;
}

var loadPureClustersInColumns_OLD = function(e) {
	var repeatMrgBtnEvery = 15;
	var txt = "<table style=\"width:90%;\"><tr>";
	var colCnt = 1;
	var remainingClusters = Object.keys(mergedClusters).sort(compStrCaseInsensitive);
	$("#clust-cnt-cell").html("<b>Number of clusters: " + remainingClusters.length + "</b><p></p>");
	var maxColSize = Math.floor(remainingClusters.length / colCnt);
	if ((remainingClusters.length / colCnt) != maxColSize) { maxColSize = maxColSize + 1; }
	if (remainingClusters.length < 11) { maxColSize = 10; }

	for (var colinx = 0; colinx < colCnt; colinx++) {
		var binx = colinx * maxColSize;
		var einx = Math.min((colinx + 1) * maxColSize - 1, remainingClusters.length - 1);
		txt = txt + "<td>";
		txt = txt + "<div class=\"btn-group\" role=\"group\" data-toggle=\"buttons\">";
		for (var rowinx = binx; rowinx <= einx; rowinx++){
			//			if (curClusterLabel != remainingClusters[rowinx]) {
			//				txt = txt + "<label class=\"btn btn-default btn-block btn_clust\">";
			txt = txt + "<label class=\"btn outline btn-block btn_clust_mrg\" data-container=\"body\" data-toggle=\"popover\" data-placement=\"right\" data-html=\"true\" data-content=\"";
			//				txt = txt + "Something";
			for (var valinx = 0; valinx < mergedClusters[remainingClusters[rowinx]].length; valinx++){
				txt = txt + mergedClusters[remainingClusters[rowinx]].sort(compStrCaseInsensitive)[valinx]
				if (valinx < mergedClusters[remainingClusters[rowinx]].length - 1) {
					txt = txt + "<br />";
				}
			}
			txt = txt + "\" data-trigger=\"hover\">";// onclick=\"logClusterButtonClick('" + remainingClusters[rowinx]+ "');\">";
			txt = txt + "<input id=\"" + remainingClusters[rowinx] + "\" type=\"checkbox\" autocomplete=\"off\">" + remainingClusters[rowinx];
			txt = txt + "</label><p></p>";
			//			}
		}
		txt = txt + "</div>";
		txt = txt + "</td>";
	}
	txt = txt + "</tr></table>";
	//	console.log(txt);
//	$("#clusters_labels_panel").html(txt);
//	$("#pure_cell").html(txt);
	document.getElementById("pure_cell").innerHTML = txt;
	return;
}

var mergeClustersGlobally = function(e) {
	//logMergeButtonClick();
	var remainingClusters = Object.keys(mergedClusters).sort(compStrCaseInsensitive);
	var colCnt = Math.min(remainingClusters.length, 3);
	var colHeaders = remainingClusters.slice(0, colCnt);
	var clustsToDel = [];
	var resultClusters = new Object();

	for (var colinx = 0; colinx < colHeaders.length; colinx++) {
		resultClusters[colHeaders[colinx]] = mergedClusters[colHeaders[colinx]].slice(0);
		clustsToDel.push(colHeaders[colinx]);
		for (var rowinx = colHeaders.length; rowinx < remainingClusters.length; rowinx++) {
			var cbid = rowinx + "@" + colinx;
			if (document.getElementById(cbid).checked == true) {
				for (var valinx = 0; valinx < mergedClusters[remainingClusters[rowinx]].length; valinx++){
					resultClusters[colHeaders[colinx]].push(mergedClusters[remainingClusters[rowinx]][valinx]);
				}
				clustsToDel.push(remainingClusters[rowinx]);
			}
		}
	}

	var resToDel = [];
	for (var colinx1 = 0; colinx1 < colHeaders.length; colinx1++) {
		for (var colinx2 = colinx1 + 1; colinx2 < colHeaders.length; colinx2++) {
			var cbid = colinx2 + "@" + colinx1;
			if (document.getElementById(cbid).checked == true) {
				if (colHeaders[colinx2] == colHeaders[colinx1]) {
					continue;
				}
				for (var valinx = 0; valinx < resultClusters[colHeaders[colinx2]].length; valinx++){
					resultClusters[colHeaders[colinx1]].push(resultClusters[colHeaders[colinx2]][valinx]);
				}
				resToDel.push(colHeaders[colinx2]);
				console.log(colHeaders[colinx1]);
				console.log(colHeaders[colinx2]);
				colHeaders[colinx2] = colHeaders[colinx1];
			}
		}
	}

	// Clean up
	for (var rtdinx = 0; rtdinx < resToDel.length; rtdinx++) {
		delete resultClusters[resToDel[rtdinx]]
	}
	for (var ctdinx = 0; ctdinx < clustsToDel.length; ctdinx++) {
		delete mergedClusters[clustsToDel[ctdinx]]
	}

	norm_app.reload_global_merging(JSON.stringify(mergedClusters), JSON.stringify(resultClusters));
	return;
}

var loadGlobalMergeClusters = function(e) {
	var repeatHeaderEvery = 15;
	$("#iteration-cnt").html("Iteration No. " + gmic);
	var txt = "<table id=\"global-merge-table\" class=\"table table-condensed table-hover\" style=\"width: 100%;\">";
	var remainingClusters = Object.keys(mergedClusters).sort(compStrCaseInsensitive);
	var colCnt = Math.min(remainingClusters.length, 3);
	var colHeaders = remainingClusters.slice(0, colCnt);
	var headerTXT = "<tr><td style=\"width: 25%;\" align=\"center\"><p></p></td>";
	for (var colinx = 0; colinx < colHeaders.length; colinx++) {
		headerTXT = headerTXT + "<td style=\"width: 25%;\" align=\"center\" data-container=\"body\" data-toggle=\"popover\" data-placement=\"top\" data-html=\"true\" data-trigger=\"hover\" data-content=\"";
		for (var valinx = 0; valinx < mergedClusters[colHeaders[colinx]].length; valinx++){
			headerTXT = headerTXT + mergedClusters[colHeaders[colinx]][valinx] + "<br />";
		}
		headerTXT = headerTXT + "\"><b>" + colHeaders[colinx] + "</b></td>";
	}
	headerTXT = headerTXT + "</tr>";
	txt = txt + "<thead>" + headerTXT + "</thead>";
	txt = txt + "<tbody>";

	for (var rowinx = 0; rowinx < remainingClusters.length; rowinx++) {
		if ( (rowinx + 1) % repeatHeaderEvery == 0) {
			txt = txt + headerTXT;
		}

		txt = txt + "<tr><td style=\"width: 25%;\" data-container=\"body\" data-toggle=\"popover\" data-placement=\"top\" data-html=\"true\" data-trigger=\"hover\" data-content=\"";
		for (var valinx = 0; valinx < mergedClusters[remainingClusters[rowinx]].length; valinx++){
			txt = txt + mergedClusters[remainingClusters[rowinx]][valinx] + "<br />";
		}
		txt = txt + "\">" + remainingClusters[rowinx] + "</td>";

		for (var colinx = 0; colinx < colHeaders.length; colinx++) {
			txt = txt + "<td style=\"width: 25%;\" align=\"center\"><input id=\"" + rowinx + "@" + colinx + "\" type=\"checkbox\" data-container=\"body\" data-toggle=\"popover\" data-placement=\"left\" data-html=\"true\" data-trigger=\"hover\" data-content=\"";
			for (var valinx = 0; valinx < mergedClusters[colHeaders[colinx]].length; valinx++){
				txt = txt + mergedClusters[colHeaders[colinx]][valinx] + "<br />";
			}
			txt = txt + "\"";
			if (colinx == rowinx) {
				txt = txt + " checked disabled";
			}
			else if (rowinx < colHeaders.length) {
				txt = txt + " onclick=\"document.getElementById('" + colinx + "@" + rowinx + "').checked = this.checked;\"";
			}
			txt = txt + "></td>";
		}
		txt = txt + "</tr>";
	}
	txt = txt + "</tbody></table>";

	document.getElementById("pure_cell").innerHTML = txt;
	$('#global-merge-table').on('hover', 'tbody tr', function(event) {
		$(this).addClass('highlight').siblings().removeClass('highlight');
	});
	return;
}

var loadMergedClustersInColumns = function(e) {
	var txt = "<table style=\"width:30%;\"><tr>";
	var colCnt = 1;
	var remainingClusters = Object.keys(mergedClusters).sort();
	var maxColSize = Math.floor(remainingClusters.length / colCnt);
	if ((remainingClusters.length / colCnt) != maxColSize) { maxColSize = maxColSize + 1; }
	if (remainingClusters.length < 11) { maxColSize = 10; }

	for (var colinx = 0; colinx < colCnt; colinx++) {
		var binx = colinx * maxColSize;
		var einx = Math.min((colinx + 1) * maxColSize - 1, remainingClusters.length - 1);
		txt = txt + "<td>";
		txt = txt + "<div class=\"btn-group\" role=\"group\" data-toggle=\"buttons\">";
		for (var rowinx = binx; rowinx <= einx; rowinx++){
			//			if (curClusterLabel != remainingClusters[rowinx]) {
			//				txt = txt + "<label class=\"btn btn-default btn-block btn_clust\">";
			txt = txt + "<label class=\"btn btn-success btn-block btn_clust_res\" data-container=\"body\" data-toggle=\"popover\" data-placement=\"left\" data-html=\"true\" data-content=\"";
			//				txt = txt + "Something";
			for (var valinx = 0; valinx < mergedClusters[remainingClusters[rowinx]].length; valinx++){
				txt = txt + mergedClusters[remainingClusters[rowinx]][valinx] + "<br />";
			}
			txt = txt + "\" data-trigger=\"hover\" onclick=\"logClusterButtonClick('" + remainingClusters[rowinx]+ "');\">";
			txt = txt + "<input id=\"" + remainingClusters[rowinx] + "\" type=\"checkbox\" autocomplete=\"off\">" + remainingClusters[rowinx];
			txt = txt + "</label><p></p>";
			//			}
		}
		txt = txt + "</div>";
		txt = txt + "</td>";
	}
	txt = txt + "</tr></table>";
	//	console.log(txt);
	$("#results_cell").html(txt);
	return;
}
////////////////////////////////////////////////////////////////////////////////

var doneMerging = function(e) {
	logMergeDone();
	for(var cLabel in splitClusters){
		mergedClusters[cLabel] = splitClusters[cLabel];
	}

	var myInput = new Object();
	myInput['merged_clusters'] = mergedClusters;
	myInput['value_file_name'] = value_file_name;
	myInput['cluster_file_name'] = cluster_file_name;
	myInput['done'] = "1";
	$.ajax({
		type: 'POST',
		url: "/simple_clustering/result_summary",
		timeout: 0,
		data: JSON.stringify(myInput),
	}).done(function( data ) {
		window.location = "/simple_clustering/result_summary";
//		document.open();
//		document.write(data);
//		document.close();
	}).fail(function(j,s,t) {
		alert(j.responseText);
		alert(s);
		alert(t);
	});
//	window.onload = function() {
//		document.getElementById("pocbtndiv").style.display = 'none';
//	};

	return false;
}

var plotClusters = function(e) {
	var numVals = 0;
	flare = new Object();
	flare['name'] = 'All values';
	flare['children'] = [];
	console.log(mergedClusters);
	for (var tt in mergedClusters) {
		curChild = new Object();
		curChild['name'] = tt + " (" + mergedClusters[tt].length + ")";
		curChild['children'] = [];
		numVals = numVals + mergedClusters[tt].length;
		for (var jj = 0; jj < mergedClusters[tt].length; jj++) {
			var curCC = new Object();
			curCC['name'] = mergedClusters[tt][jj];
			curChild['children'].push(curCC);
		}
		flare['children'].push(curChild);
	}

	var margin = {top: 20, right: 120, bottom: 20, left: 120},
	width = $("#clustering_summary_panel").width() - margin.right - margin.left,
//		height = 1200 - margin.top - margin.bottom;
		height = (15 * numVals) - margin.top - margin.bottom;

	var i = 0,
	duration = 750,
		root;

	var tree = d3.layout.tree()
		.size([height, width]);

	var diagonal = d3.svg.diagonal()
		.projection(function(d) { return [d.y, d.x]; });

	var svg = d3.select("#d3cluster").append("svg")
		.attr("width", width + margin.right + margin.left)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	//	d3.2json("http://bl.ocks.org/mbostock/raw/4063550/flare.json", function(error, flare) {
	//		if (error) throw error;

	root = flare;
	root.x0 = height / 2;
	root.y0 = 0;

	function collapse(d) {
		if (d.children) {
			d._children = d.children;
			d._children.forEach(collapse);
			d.children = null;
		}
	}

	root.children.forEach(function(d) {
		if (d.children.length <= 1) {
			collapse(d);
		}
	});
	update(root);

	d3.select(self.frameElement).style("height", "1200px");

	function update(source) {

		// Compute the new tree layout.
		var nodes = tree.nodes(root).reverse(),
		links = tree.links(nodes);

		// Normalize for fixed-depth.
		nodes.forEach(function(d) { d.y = d.depth * 180; });

		// Update the nodes…
		var node = svg.selectAll("g.node")
			.data(nodes, function(d) { return d.id || (d.id = ++i); });

		// Enter any new nodes at the parent's previous position.
		var nodeEnter = node.enter().append("g")
			.attr("class", "node")
			.attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
			.on("click", click);

		nodeEnter.append("circle")
			.attr("r", 1e-6)
			.style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

		nodeEnter.append("text")
			.attr("x", function(d) { return d.children || d._children ? -10 : 10; })
			.attr("dy", ".35em")
			.attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
			.text(function(d) { return d.name; })
			.style("fill-opacity", 1e-6);

		// Transition nodes to their new position.
		var nodeUpdate = node.transition()
			.duration(duration)
			.attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

		nodeUpdate.select("circle")
			.attr("r", 4.5)
			.style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

		nodeUpdate.select("text")
			.style("fill-opacity", 1);

		// Transition exiting nodes to the parent's new position.
		var nodeExit = node.exit().transition()
			.duration(duration)
			.attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
			.remove();

		nodeExit.select("circle")
			.attr("r", 1e-6);

		nodeExit.select("text")
			.style("fill-opacity", 1e-6);

		// Update the links…
		var link = svg.selectAll("path.link")
			.data(links, function(d) { return d.target.id; });

		// Enter any new links at the parent's previous position.
		link.enter().insert("path", "g")
			.attr("class", "link")
			.attr("d", function(d) {
				var o = {x: source.x0, y: source.y0};
				return diagonal({source: o, target: o});
			});

		// Transition links to their new position.
		link.transition()
			.duration(duration)
			.attr("d", diagonal);

		// Transition exiting nodes to the parent's new position.
		link.exit().transition()
			.duration(duration)
			.attr("d", function(d) {
				var o = {x: source.x, y: source.y};
				return diagonal({source: o, target: o});
			})
		.remove();

		// Stash the old positions for transition.
		nodes.forEach(function(d) {
			d.x0 = d.x;
			d.y0 = d.y;
		});
	}

	// Toggle children on click.
	function click(d) {
		if (d.children) {
			d._children = d.children;
			d.children = null;
		} else {
			d.children = d._children;
			d._children = null;
		}
		update(d);
	}
}
