// mqPlot.js
// Insert Intel verbiage here
//
// Rob Watts <robert.a.watts@intel.com>
//
// History
// 11/5/2015    0.1      Initial version 
// 11/17/2015   0.2      More dynamic and general implementation
// 

var reconnect = false;
var loop;

function mqttInit() {

    var broker = {
	host: config.broker.host,
	port: config.broker.wssPort,    //default port is  WSS port:9001
	id: "client_" + parseInt(Math.random() * 100, 10),
	topic: config.broker.topic,
	reconnectTimeout: config.broker.reconnectTimeout,
	reconnectInterval: config.broker.reconnectInterval,
	protocol: window.location.protocol,
	path: "/mqtt"
    };

    // Create an MQTT client instance using Paho 
    var uri;
    if(broker.protocol === "https:") {
    	uri = "wss://"+broker.host+":"+broker.port+broker.path;

    }
    else {
	broker.port = config.broker.wsPort;
    	uri = "ws://"+broker.host+":"+broker.port+broker.path;
    }
    var client = new Paho.MQTT.Client(uri, broker.id);

    // Object to store chart data
    var charts = {};

    // Link and data lights
    var $link = $(".link");
    var $data = $(".data");

    // Set callback handlers
    client.onConnectionLost = onConnectionLost;	
    client.onMessageArrived = onMessageArrived;
	

    // MQTT connection options
    var mqttOptions = {
	timeout: 3,
	cleanSession: true,
	onSuccess: function () {
	    $("#response").text("MQTT connection succeeded. Connected to topic "
				+ broker.topic + " on "
				+ broker.host + ":" + broker.port);
	    $link.removeClass("disconnected").addClass("connected");
	    client.subscribe(broker.topic, {qos: 1});
	},
	onFailure: function (message) {
		if(reconnect) {
			$("#response").text("MQTT connection failed. Retrying. Error Message -  "
				+ message.errorMessage);
				$link.removeClass("connected").addClass("disconnected");
			
			while(loop < broker.reconnectInterval) {
				loop++;
				setTimeout(function() {
					mqttInit();
				}, broker.reconnectTimeout);
			}	
			reconnect = false;
		}
		else {
			$("#response").text("MQTT connection failed. Please ensure the broker is up. Error Message -  "
			+ message.errorMessage);
			$link.removeClass("connected").addClass("disconnected");
		}
	}
    };
	
    // Handle lost connection and reconnect
    function onConnectionLost(responseObject) {
		reconnect = true;
		loop = 0;	// Reset reconnect loop
		if (responseObject.errorCode !== 0) {
			$("#response").text("MQTT connection lost. Reconnecting. Error Message - "
					+ responseObject.errorMessage);
			$link.removeClass("connected").addClass("disconnected");
		}
			setTimeout( function () {
				var connectOptions = {
					timeout: 3,
					cleanSession: true,
					onSuccess: function () {
						$("#response").text("MQTT connection succeeded. Connected to topic "
								+ broker.topic + " on "
								+ broker.host + ":" + broker.port);
						$link.removeClass("disconnected").addClass("connected");
						client.subscribe(broker.topic, {qos: 1});
					},
					onFailure: function (message) {
						$("#response").text("MQTT connection failed. Retrying. Error Message -  "
								+ message.errorMessage);
						$link.removeClass("connected").addClass("disconnected");
							setTimeout(mqttInit, broker.reconnectTimeout);
					}
				};
				client.connect(connectOptions)}, broker.reconnectTimeout);
	}

    // Handle new messages.
    function onMessageArrived(message) {
    	
	var entry = JSON.parse( message.payloadString );
		
	if ( typeof dataTimeout !== 'undefined' )
	clearTimeout(dataTimeout);
	$data.show();
	dataTimeout = setTimeout(function() {
	    $data.hide();
	}, 100);

	plot(entry);
    };

    client.connect(mqttOptions);
	
};

// Take the data point entry and plot it using jqPlot
function plot(entry) {
    
    // jqPlot expects values as numbers, not strings
    if (typeof entry.datum !== 'undefined') {
	if ( isNumber(entry.datum[1]))
	    entry.datum[1] = parseFloat(entry.datum[1]);
    };
    
    // If the chart is there, update it
    if ( charts.hasOwnProperty(entry.id) ){
	charts[entry.id].jqplot.destroy();
	
	if ( entry.chartType == "gauge" ) {
	    charts[entry.id].data = [entry.datum];
	}
	else {
	    // Remove oldest datum if appropriate, or remove an empty chart
	    // initialization datum if it exists.
	    if ( (charts[entry.id].data.length > parseInt(entry.points, 10) - 1 )
		 || (charts[entry.id].data[0].length == 0) ) {
	 	charts[entry.id].data.shift();
	    }
	    charts[entry.id].data.push(entry.datum);
	}
    }
    // If the chart is not there, add it
    else {
	charts[entry.id] = {
	    type: entry.chartType,
	    data: [entry.datum]
	};

	$("#charts").append("<div class='chart' id='" + entry.id + "'/>");
    }
    
    // Populate the chart options
    if ( entry.chartType == "gauge" ) {
	charts[entry.id].options = {
	    title: entry.title,
	    seriesDefaults: {
	 	renderer: $.jqplot.MeterGaugeRenderer,
	 	rendererOptions: {
	 	    label: entry.units,
		    intervals:[parseInt(entry.targetLow, 10),
			       parseInt(entry.targetHigh, 10),
			       parseInt(entry.max, 10)],
		    intervalColors:['#E7E658', '#66cc66', '#cc6666']
		}
	    }
	}
	if (entry.min !== "")
	    charts[entry.id].options.seriesDefaults.rendererOptions.min
	    = parseInt(entry.min, 10);
	if (entry.max !== "")
	    charts[entry.id].options.seriesDefaults.rendererOptions.max
	    = parseInt(entry.max, 10);
	
	if (charts[entry.id].data[0].length == 0)
	    charts[entry.id].data = [[0,0]];
    }
    // If it's not a gauge, it's a line
    else {
	charts[entry.id].options = {
	    canvasOverlay: {
		show: ((entry.targetHigh !== "") && (entry.targetLow !== "")),
		objects: [
		    { rectangle: { ymax: parseInt(entry.targetHigh, 10),
				   ymin: parseInt(entry.targetLow, 10),
				   xminOffset: "0px",
				   xmaxOffset: "0px",
				   yminOffset: "0px",
				   ymaxOffset: "0px",
				   color: "rgba(0, 200, 0, 0.3)" }
		    }
		]
	    },
	    title: entry.title,
	    axes:{
		xaxis:{
		    renderer:$.jqplot.DateAxisRenderer,
		    //	tickOptions:{formatString:'%H:%M:%S'},
		    showTicks: false
		},
		yaxis:{
		    label: entry.units,
		    labelRenderer: $.jqplot.CanvasAxisLabelRenderer
		}
	    },
	    series:[{
		lineWidth:2,
		markerOptions: {
		    show:false
		},
		rendererOptions: {
		    smooth: true
		}
	    }]
	};
	if (entry.min !== "")
	    charts[entry.id].options.axes.yaxis.min
	    = parseInt(entry.min, 10);
	if (entry.max !== "")
	    charts[entry.id].options.axes.yaxis.max
	    = parseInt(entry.max, 10);
    }

    // Update the source
    $("#" + entry.id).attr("data-source", entry.dataSource);
    
    // Plot it    
    charts[entry.id].jqplot =
	$.jqplot(entry.id, [charts[entry.id].data], charts[entry.id].options);

};

// Check for numeric value	
function isNumber(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
};
/**
$(document).ready(function() {
	mqttInit();
    config.charts.forEach(function(chart) {
	chart.id = chart.title.replace(/ /g,"_");
	chart.datum = []; // Initialize with an empty data point
	plot(chart);
    });
    
});
**/