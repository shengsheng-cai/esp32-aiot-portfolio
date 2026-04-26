var	newgaugedate = false ;
var no_old_Timer = true ;
var gdata ;
var gdata_sum = 0;
var a_tag=[] ; 
var tag_sum = 0;
var site_now = 0 ;
var curve_chart ;
var dt_gd , today ;
var dt_from = "" ;
var dt_to = "" ;
var chg_period = false ;
var socket ="";
$(function() {    
		$( "#week" ).button().click( theweek ); 
		$( "#month" ).button().click( themonth ); 
		$( "#all" ).button().click( alltime ); 
		$( "#dt_from" ).change( function () {
				chg_period = true ;
				dt_from =  $(this).val();	
		} ).datepicker({ minDate: -365, maxDate: "+0D" });	
		$( "#dt_to" ).change( function () {
				chg_period = true ;
				dt_to =  $(this).val();	
		} ).datepicker({ minDate: -365, maxDate: "+0D" });	
		$( "#chart" ).button().click( newchart ); 
		$( "#btn_tbl" ).button().click( show_table ); 
		$( "#print" ).button().click( function(){ 
			$( "#btn_rtn,#chart,#btn_tbl,#print,#week,#month,#all" ).hide();
			window.print(); 
			$( "#btn_rtn,#chart,#btn_tbl,#print,#week,#month,#all" ).show();
		} ); 
    	$( "#btn_rtn" ).button().click( function() {
			var form = $('<form action="T_manage.jsp" tabindex="-1" style="position:absolute; top:-1000px" method="post"><input type="text"  /></form>');
			$('body').append(form);
			form.submit();
		});		
		CanvasJS.addColorSet("greenShades",  [  "#2F4F4F", "#008080",  "#2E8B57",  "#3CB371",  "#90EE90"  ]);
		get_all_tag();
});

function websocketInit() {
	var loc = window.location ;
	console.log( loc.href );
	
//    const socket = io.connect( logger=true, engineio_logger=true );
    socket = io.connect( '' , {path: loc.pathname +'socket.io'}  )
    console.log('socket.connected:', socket.connected);
    socket.on('connect', function() {
      console.log("Connected to WS server");
      console.log(socket.connected); 
    });
    socket.on('message', function(event) { console.log(  "websocket event: message, event.data: " + event.data ); });
    socket.on('wstest', function(event) { console.log(  "websocket event: wstest, event.data: " + event.data ); });
    socket.on('datacoming', function(event) {
		try{
            console.log(  "websocket data in : " + event.data );
			var  para = JSON.parse( event.data ) ;
			if ( para && para.dt && para.tmp != undefined  ) {
    			    a_tag.unshift( para ) ;
                    tag_sum = a_tag.length ;
				    if ( site_now == 1) newchart ();
				    else if ( site_now == 2) show_table() ;
			}
		} catch (e) { console.log( 'socket event error:'+ e  );    }
	});
}

//function freshinfo () {
//}

function get_all_tag() {
	dt_gd = ymd_hms_dash( new Date() );
	tag_sum =0;
	$.post( "get_data.jsp" , function(data){
//		try {
	  		a_tag = JSON.parse( data ) ;
			if ( a_tag && a_tag.constructor === Array ) {		
				tag_sum = a_tag.length ;
				if ( site_now == 1) newchart ();
				else if ( site_now == 2) show_table() ;
			} else ( alert( " no data " ) );
			websocketInit();
//			setTimeout( freshinfo , 3000 ); 
//		} catch (e) {  alert( "catch error in getnewgauge" );  }
	})
    .error(function() { 
//		setTimeout( freshinfo , 3000 ); 
//			alert("error"); 
	});
}

function newchart () {
		if ( curve_chart ) $("div#curves").empty();
		else {
			$("div#curves").addClass("div_show") ;
			if ( site_now ==2  ) {
				$("div#table").removeClass("div_show") ;
				$("#hd_table,#bd_table").empty();
			}
		}
		site_now = 1 ;
		var dt_ceiling = (dt_to) ? dt_to : "z" ;
		var dt_floor =   (dt_from) ? dt_from : "" ;
		var a_data = [] ;
		var a_td = [];
		if ( tag_sum>0 )  	a_tag.forEach( function( o ) {		
				var  dd = o.dt.substr(0, 10);
				if ( dt_ceiling >=  dd  &&   dd >= dt_floor )	 {
					var dt = new Date( o.dt );
					a_td.push({		x: dt, y: parseInt( o.tmp )/100	});
				}
		});
//console.log( a_td );
		a_data.push({name:"溫度",type:"line",xValueType: "dateTime", showInLegend: true, dataPoints: a_td}) ;
		curve_chart = new CanvasJS.Chart("curves",{	title: { text: "溫度 曲線圖" },	colorSet: "greenShades",	
					zoomEnabled: true, exportEnabled: true,  exportFileName: "溫度 曲線圖",
					toolTip: {	shared: true	},
					legend: { 	verticalAlign: "top",	horizontalAlign: "center", fontSize: 14, fontWeight: "bold", fontFamily: "calibri", fontColor: "dimGrey"	},
					axisX: {	labelAngle: 30 , valueFormatString:"YYYY-MM-DD hh:mm TT"  },    //  title: "測量時間"
					axisY:{	includeZero: false	}, 
					data: a_data,
					legend:{  cursor:"pointer",
						itemclick : function(e) {
								if (typeof(e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {  e.dataSeries.visible = false;
												}  else { e.dataSeries.visible = true; }
								curve_chart.render();
						}
					}
				});		
		curve_chart.render();
}

$.datepicker.regional['zh-TW'] = {
		closeText: '關閉',
		prevText: '&#x3c;上月',
		nextText: '下月&#x3e;',
		currentText: '今天',
		monthNames: ['一月','二月','三月','四月','五月','六月',
		'七月','八月','九月','十月','十一月','十二月'],
		monthNamesShort: ['一','二','三','四','五','六',
		'七','八','九','十','十一','十二'],
		dayNames: ['星期日','星期一','星期二','星期三','星期四','星期五','星期六'],
		dayNamesShort: ['週日','週一','週二','週三','週四','週五','週六'],
		dayNamesMin: ['日','一','二','三','四','五','六'],
		weekHeader: '週',
		dateFormat: 'yy-mm-dd',
		firstDay: 1,
		isRTL: false,
		showMonthAfterYear: true,
		yearSuffix: '年'};
$.datepicker.setDefaults($.datepicker.regional['zh-TW']);

function show_table() {
		if ( curve_chart ) {
			curve_chart = null;
			$("div#curves").empty().removeClass("div_show") ;
		}
		if ( site_now == 2 ) $("#bd_table").empty();
		else {
			$("div#table").addClass("div_show") ;
			$("#hd_table").append( 
'<tr class="ui-widget-header"><th class="tbl_g_tm">測量時間</th><th class="tbl_g_val">溫度</th></tr>' );
		}
		site_now = 2 ;
		var s = '</td><td>';
		var dt_ceiling = (dt_to) ? dt_to : "z" ;
		var dt_floor =   (dt_from) ? dt_from : "" ;
		if ( tag_sum>0 )  	a_tag.forEach( function( o ) {	
				var  dd = o.dt.substr(0, 10);
				if ( dt_ceiling >=  dd  &&   dd >= dt_floor )	 $("#bd_table").append('<tr><td>'+o.dt.substr(0, 19)+s+(parseInt(o.tmp)/100)+'</td></tr>');
		});
}
function ymd_hms_dash( date ){
	var m = date.getMonth(),	 d = date.getDate(),	 h = date.getHours(),	 n = date.getMinutes(),	 s = date.getSeconds();
	return date.getFullYear()+(m<9?"-0":"-")+(m+1)+(d<=9?"-0":"-")+d+(h<=9?" 0":" ")+h+(n<=9?":0":":")+n+(s<=9?":0":":")+s;
}
function date_dash_str( date ){
	var mm = date.getMonth(), dd = date.getDate();
	return date.getFullYear()+(mm<9?"-0":"-")+(mm+1)+(dd<=9?"-0":"-")+dd;
}
function set_dt_to() {
	today = new Date() ;
	chg_period = true ;
	dt_to = date_dash_str( today );
	$("#dt_to").val(dt_to) ; 
}
function theweek() {
	set_dt_to();
	var day = today.getDay();
	today.setDate( today.getDate() - (( --day <0)?6:day));
	dt_from = date_dash_str( today );
	$("#dt_from").val(dt_from) ; 
}
function themonth() {
	set_dt_to();
	today.setDate(1);
	dt_from = date_dash_str( today );
	$("#dt_from").val(dt_from) ; 
}
function alltime() {
	dt_from = dt_to = "";
	$("#dt_to").val(dt_to) ; 
	$("#dt_from").val(dt_from) ; 
}

