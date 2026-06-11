'use strict';
var SL_DARK="invert(95%)";
var PACK_PARAMS;

var VIEW=1;
var SEARCHTERM_D="all";
var SEARCHTERM_L="all";
var ITEM="";
setTimeout(function() {	
        var SL_Languages = CUSTOM_LANGS(FExtension.element(GET("SL_LOCALIZATION"),'extLanguages'));
	(function(){GEBI("SL_info").addEventListener("click",function(){FExtension.browserPopup.openNewTab(this.href);},!1);} )();

	(function(){GEBI("SRV6").addEventListener("click",function(){SL_ACTIVE = GEBI("SRV6"); SL_TMP=SL_ACTIVE.value; SL_ACTIVE.focus();SL_MSG_HANDLER(event);},!1); } )();
	(function(){GEBI("SRV6").addEventListener("mouseout",function(){NoneColor(6);},!1); } )();
	(function(){GEBI("SRV6").addEventListener("paste",function(){ PREVENT_PASTE(event); },!1);} )();

	(function(){GEBI("SRV7").addEventListener("click",function(){SL_ACTIVE = GEBI("SRV7"); SL_TMP=SL_ACTIVE.value; SL_ACTIVE.focus();SL_MSG_HANDLER(event);},!1); } )();
	(function(){GEBI("SRV7").addEventListener("mouseout",function(){NoneColor(7);},!1); } )();
	(function(){GEBI("SRV7").addEventListener("paste",function(){ PREVENT_PASTE(event); },!1);} )();

	(function(){GEBI("SRV12").addEventListener("click",function(){SL_ACTIVE = GEBI("SRV12"); SL_TMP=SL_ACTIVE.value; SL_ACTIVE.focus();SL_MSG_HANDLER(event);},!1); } )();
	(function(){GEBI("SRV12").addEventListener("mouseout",function(){NoneColor(12);},!1); } )();
	(function(){GEBI("SRV12").addEventListener("paste",function(){ PREVENT_PASTE(event); },!1);} )();

	(function(){GEBI("SRV13").addEventListener("click",function(){SL_ACTIVE = GEBI("SRV13"); SL_TMP=SL_ACTIVE.value; SL_ACTIVE.focus();SL_MSG_HANDLER(event);},!1); } )();
	(function(){GEBI("SRV13").addEventListener("mouseout",function(){NoneColor(13);},!1); } )();
	(function(){GEBI("SRV13").addEventListener("paste",function(){ PREVENT_PASTE(event); },!1);} )();

	(function(){GEBI("SL_HK6").addEventListener("click",function(){ SL_HIDE_HK("SL_HK6","SL_HIDE6");},!1); } )();
	(function(){GEBI("SL_HK7").addEventListener("click",function(){ SL_HIDE_HK("SL_HK7","SL_HIDE7");},!1); } )();
	(function(){GEBI("SL_HK12").addEventListener("click",function(){ SL_HIDE_HK("SL_HK12","SL_HIDE12");},!1); } )();
	(function(){GEBI("SL_HK13").addEventListener("click",function(){ SL_HIDE_HK("SL_HK13","SL_HIDE13");},!1); } )();

	(function(){GEBI("SL_LOC").addEventListener("change",function(){SL_SAVE_LOC();},!1);} )();
	(function(){GEBI("SL_LNG_STATUS").addEventListener("click",function(){ SL_LANGS(); },!1); } )();

	(function(){GEBI("SL_THEME").addEventListener("change",function(){SL_SAVE_THEME();},!1);} )();

	(function(){GEBI("reset_all6").addEventListener("click",function(){ RESET_ALL_HK(6);},!1);} )();
	(function(){GEBI("reset_all7").addEventListener("click",function(){ RESET_ALL_HK(7);},!1);} )();
	(function(){GEBI("reset_all12").addEventListener("click",function(){ RESET_ALL_HK(12);},!1);} )();
	(function(){GEBI("reset_all13").addEventListener("click",function(){ RESET_ALL_HK(13);},!1);} )();

	(function(){window.addEventListener("mousemove",function(){
		BUILD_RESET_ICN(6);
		BUILD_RESET_ICN(7);
		BUILD_RESET_ICN(12);
		BUILD_RESET_ICN(13);
	},!1);} )();


	GEBI('SL_H_SEARCH').onkeyup = function() { FAST_SEARCH(event); };
	GEBI('SL_H_SEARCH').onfocus = function() { FAST_SEARCH(event); };
	GEBI('SL_SORT').onchange = function() { if(VIEW==1) SEARCHTERM_D=GEBI('SL_SORT').value;if(VIEW==2) SEARCHTERM_L=GEBI('SL_SORT').value; FAST_SEARCH(); };


//	(function(){GEBI("SL_down_box").addEventListener("click",function(){ SL_LANGS(); },!1); } )();
//	(function(){GEBI("SL_down").addEventListener("click",function(){ SL_LANGS(); },!1); } )();

	(function(){GEBI("domains").addEventListener("click",function(){ VIEW_MANAGER(1); },!1); } )();
	(function(){GEBI("languages").addEventListener("click",function(){ VIEW_MANAGER(2); },!1); } )();

	(function(){GEBI("SL_clear_box").addEventListener("click",function(){ ClearSearchBox(); },!1); } )();



	document.addEventListener("click", function(){ ClickHolder(event); });

	(function(){window.addEventListener("click",function(event){
		SL_MSG_HANDLER(event);
	},!1);} )();

	//AUTOSAVE BLOCK
	window.addEventListener('change',function(e){
		save_options(0);
	},!1);
	//AUTOSAVE BLOCK

	GEBI('SL_translate_container').style.opacity="1";
	CONSTRUCTOR();
	var OB = GEBI('SL_langSrc_wpt');
	if(GET("SL_LNG_LIST").indexOf("auto")!=-1 || GET("SL_LNG_LIST")=="all"){
		var OB1 = document.createElement('option');
		var v = document.createAttribute("value");
		v.value = "auto";
		OB1.setAttributeNode(v);
		OB1.appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extDetect_language_from_box')));
		OB.appendChild(OB1); 
	}
	var SL_TMP = SL_Languages.split(",");
	for(var J=0; J < SL_TMP.length; J++){
	    var SL_TMP2=SL_TMP[J].split(":");
	    var OB2 = document.createElement('option');
	    var v = document.createAttribute("value");
	    v.value = SL_TMP2[0];
	    OB2.setAttributeNode(v);
	    //OB2.appendChild(document.createTextNode(SL_TMP2[1].replace("&#160;"," ")));
	    OB2.appendChild(document.createTextNode(SL_TMP2[1]));
	    OB.appendChild(OB2);
	}

	var OB3 = GEBI('SL_langDst_wpt');
	for(var J=0; J < SL_TMP.length; J++){
	    var SL_TMP2=SL_TMP[J].split(":");
	    var OB2 = document.createElement('option');
	    v = document.createAttribute("value");
	    v.value = SL_TMP2[0];
	    OB2.setAttributeNode(v);
	    //OB2.appendChild(document.createTextNode(SL_TMP2[1].replace("&#160;"," ")));
	    OB2.appendChild(document.createTextNode(SL_TMP2[1]));
	    OB3.appendChild(OB2);
	}
	INIT();


function CONSTRUCTOR(){
	GEBI('SL_BG_op').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSLBG_op')));
	GEBI('SL_setLS4allTr').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSLsetLS4allTr')));
	GEBI('SLSeSo').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSeSo')));
	GEBI('SLSeTa').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSeTa')));
	GEBI('SL_TrHi').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extTrHist')));
	GEBI('SL_WpTH').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extWpTH')));
	GEBI('SL_sc').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extHotKeys')));
	GEBI('SL_il').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extLOC')));
	GEBI('SL_L_BOX').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extLangs')+":"));
	GEBI('SL_LNG_STATUS').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extCustomize')));
	GEBI('SL_wptttl').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extADV')));
	GEBI('SL_wptDAlways').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extwptDAlways')));
	GEBI('SL_wptDTb').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extwptDTb')));
	GEBI('SL_wptDOrTip').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extwptDOrTip')));
	GEBI('SL_wptDReset').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extwptDReset')));
	GEBI('SL_wptLReset').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extwptLReset')));
//	GEBI('SL_wptReset1').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extwptReset')));
//	GEBI('SL_wptReset2').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extwptReset')));
	GEBI('SL_SH_OR').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extCMsot')));
	GEBI('SL_CL_TR').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extCMct')));
	GEBI('SL_theme_ttl').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extTHEME')));
	GEBI('SL_theme_1').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extLIGHT')));
	GEBI('SL_theme_2').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extDARK')));
	GEBI('SL_WPTflip').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSwitch_languages_ttl')));
	GEBI('SL_TR_op').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extTR_op')));
	switch(PLATFORM){
	 case "Opera" : GEBI('SL_info').href="https://imtranslator.net/tutorials/presentations/imtranslator-for-opera/opera-webpage-translation-options/"; break;
	 case "Chrome": GEBI('SL_info').href="https://imtranslator.net/tutorials/presentations/imtranslator-for-chrome/webpage-translation-options/"; break;
	 default      : GEBI('SL_info').href="https://imtranslator.net/tutorials/presentations/";break;
	}
	ACTIVATE_THEME(GET("THEMEmode"));
	WPT_DB_SORTING();
}



function INIT(){
  ACTIVATE_MENU_ELEMENT(4);
  GEBI("SL_LOC").value=GET("SL_LOCALIZATION");
	var mySL_langSrc_wpt = GET("SL_langSrc_wpt");
	var mySL_langSrcSelect_wpt = GEBI("SL_langSrc_wpt");
	for (var i = 0; i < mySL_langSrcSelect_wpt.options.length; i++) {
		var mySL_langSrcOption_wpt = mySL_langSrcSelect_wpt.options[i];
		if (mySL_langSrcOption_wpt.value == mySL_langSrc_wpt) {
			mySL_langSrcOption_wpt.selected = "true";
			break;
		}
	}

	var mySL_langDst_wpt = GET("SL_langDst_wpt");
	var mySL_langDstSelect_wpt = GEBI("SL_langDst_wpt");
	for (var i = 0; i < mySL_langDstSelect_wpt.options.length; i++) {
		var mySL_langDstOption_wpt = mySL_langDstSelect_wpt.options[i];
		if (mySL_langDstOption_wpt.value == mySL_langDst_wpt) {
			mySL_langDstOption_wpt.selected = "true";
			break;
		}
	}

	var SL_TH_3 = GET("SL_TH_3");
	if(SL_TH_3=="1")  GEBI("SL_TH_3").checked = true;
	else GEBI("SL_TH_3").checked = false;

	var SL_global_lng_wpt = GET("SL_global_lng_wpt");
	if(SL_global_lng_wpt=="true")  GEBI("SL_global_lng_wpt").checked = true;
	else GEBI("SL_global_lng_wpt").checked = false;


        var SL_THEMEmode = GET("THEMEmode");
	if(SL_THEMEmode==0)  GEBI("SL_THEME").value = 0;
	else GEBI("SL_THEME").value = 1;



  var tempTIP = GET("SL_wptGlobTip");
  if(tempTIP=="1") GEBI("SL_SOOOM").checked=true;
  else GEBI("SL_SOOOM").checked=false;

  var tempTB = GET("SL_wptGlobTb");
  if(tempTB=="1") GEBI("SL_Toolbar").checked=true;
  else GEBI("SL_Toolbar").checked=false;




  var tempHK6 = GET("SL_HK_wptbox1");
  if(tempHK6=="true") GEBI("SL_HK6").checked=true;
  else GEBI("SL_HK6").checked=false;
  
  GEBI("SRV6").value=GET("SL_HK_wpt1");

  var tempHK7 = GET("SL_HK_wptbox2");
  if(tempHK7=="true") GEBI("SL_HK7").checked=true;
  else 	 GEBI("SL_HK7").checked=false;

  GEBI("SRV7").value=GET("SL_HK_wpt2");

  var tempHK12 = GET("SL_HK_SObox_wpt");
  if(tempHK12=="true") GEBI("SL_HK12").checked=true;
  else 	 GEBI("SL_HK12").checked=false;

  GEBI("SRV12").value=GET("SL_HK_SO_wpt");

  var tempHK13 = GET("SL_HK_CTbox_wpt");
  if(tempHK13=="true") GEBI("SL_HK13").checked=true;
  else 	 GEBI("SL_HK13").checked=false;

  GEBI("SRV13").value=GET("SL_HK_CT_wpt").replace("Escape", "Esc");

  var WPTflip = GET("WPTflip");
  if(WPTflip=="1")  GEBI("WPTflip").checked = true;
  else GEBI("WPTflip").checked = false;


  SL_HIDE_HK("SL_HK6","SL_HIDE6");
  SL_HIDE_HK("SL_HK7","SL_HIDE7");
  SL_HIDE_HK("SL_HK12","SL_HIDE12");
  SL_HIDE_HK("SL_HK13","SL_HIDE13");

  save_options(1);
  EDITOR(1);
}








function ACTIVATE_MENU_ELEMENT(st){
  var win = top.frames['menu'];
  var li = win.document.getElementsByTagName("li");
  for(var i=1; i<=li.length; i++){
        if(st==i) win.document.getElementById('SL_options_menu'+i).className='SL_options-menu-on';
        else win.document.getElementById('SL_options_menu'+i).className='SL_options-menu-off';
  }
}

function SL_SAVE_LOC(){
  SET("SL_LOCALIZATION", GEBI("SL_LOC").value);
  CONSTRUCTOR();
  BG_WORKING_SET();
  parent.frames["menu"].location.reload();
  location.reload();
}

function SL_RESET(st){
  var isMac = navigator.platform.toUpperCase().indexOf('MAC')>=0;
  if(isMac==false)  var r=confirm("Do you really want to delete all records?");
  else r=true;
  if (r==true){
	  if(st==1) {
		SET("SL_wptDHist","");
		if(GET("SL_wptDHist")=="") {
			EDITOR(st);
			GEBI("NoRecords").style.display="block";
		}
	  } else {
		SET("SL_wptLHist","");
		if(GET("SL_wptLHist")=="") {
			EDITOR(st);
			GEBI("NoRecords").style.display="block";
		}
	  }	
  }
}


function SL_SAVE_THEME(){
  SET("THEMEmode", GEBI("SL_THEME").value);
  BG_WORKING_SET();
  location.reload();
}

function ACTIVATE_THEME(st){
 	if(st==1){
		var bg="#191919";
		var clr="#BF7D44";
		var clr_deact="#BDBDBD";
		GEBI("SL_translate_container").style.filter=SL_DARK;
		var LBLS = document.getElementsByClassName("SL_BG_op");
		for(var i=0; i<LBLS.length; i++) LBLS[i].style.color=clr;
		var A = document.getElementsByTagName("a");
		for(var i=0; i<A.length; i++) A[i].style.color=clr;

		setTimeout(function() {
			var SL_lngSrc_opt = GEBI("SL_langSrc_wpt").getElementsByTagName("option");
			for(var j=0; j<SL_lngSrc_opt.length; j++) SL_lngSrc_opt[j].setAttribute("style", "background:"+bg+" !important;color:#fff;");
			var SL_lngSrc_opt = GEBI("SL_langDst_wpt").getElementsByTagName("option");
			for(var j=0; j<SL_lngSrc_opt.length; j++) SL_lngSrc_opt[j].setAttribute("style", "background:"+bg+" !important;color:#fff;");
		}, 1000);

		GEBI("SL_AUTOKEYS").style.filter=SL_DARK;	
	}
}



function BUILD_RESET_ICN(ob){
	GEBI("reset_all"+ob).title="Reset to default";
}

function VIEW_MANAGER(V){
	GEBI("SL_H_SEARCH").value="";
	if(GEBI("Content").style.display=="block") HideEDITOR();
	else EDITOR(V);
	if(VIEW!=V) EDITOR(V);	
	GEBI("SL_SORT").value = "all";
	SEARCHTERM_D="all";
	SEARCHTERM_L="all";
}

function HideEDITOR(){
//  CloseWindowAndRestore();
  var ob = GEBI("Content");	
  GEBI("SL_search_tool").style.display="none";
  ob.innerText="";
  ob.style.display="none";
  GEBI("domains").className="tablinksP";
  GEBI("languages").className="tablinksP";
  GEBI("DArrow").src="../../img/util/arrow-down.png";
  GEBI("LArrow").src="../../img/util/arrow-down.png";
}

function EDITOR(st){

 	  WPT_DB_SORTING();
	  var ob = GEBI("Content");
	  ob.style.padding="10px";
	  ob.style.display="block";
	  var ROWS="";
	  var NORECORDS="<div id=NoRecords align=center>No records</div>";
	  var term1=GEBI("SL_H_SEARCH").value;
	  var term2 = GEBI("SL_SORT").value;

	  if(st==1){
		VIEW = 1;
		var HEADER = "<div class='TopMenu' id='TopMenu' align=left><table id='dtable' width=160><tr><td><img src='../../../../content/img/util/triggerkey.png'></td><td><div id='SL_control1'><span id='DAddNew'>Add</span><img id='DAddNewImg' title='Add new' src='../../../../content/img/util/cross.gif'></div></td><td><div id='SL_control2'><span id='DClearAll'></span><img id='DClearAllImg' src='../../../../content/img/util/remove.png'></div></td></tr></table></div>";
		GEBI("domains").className="tablinksA";
		GEBI("DArrow").src="../../img/util/arrow-up.png";
		GEBI("languages").className="tablinksP";
		GEBI("LArrow").src="../../img/util/arrow-down.png";
		var D_HIST = GET("SL_wptDHist").replace(/{|}/g,"");
		var itms = D_HIST.split(":");
		for(var i=0; i<itms.length; i++){
			var D_elem = itms[i].split(",");
			if(itms[i]!=""){
				var dt = D_TERM_Finder(itms[i]);
				if(D_elem[0].toLowerCase().indexOf(term1.toLowerCase())!=-1 && dt==1){
					ROWS = ROWS +"<div class=caps><table width=100%><tr><td width=90% title='"+D_elem[0]+"'>"+ D_elem[0] + "</td><td width=5% align=right><img class='DOpen' id='"+i+":"+itms[i]+"' title='"+FExtension.element(GET("SL_LOCALIZATION"),'extwptMoreOptions')+"' src='../../../../content/img/util/dots-tb.png'></td><td width=5% align=right><img class='DDelete' id='{"+itms[i]+"}' title='"+FExtension.element(GET("SL_LOCALIZATION"),'extDelete')+": "+D_elem[0]+"' src='../../../../content/img/util/remove.png'></td></tr></table><div id='cap"+i+"'></div></div>";
				}
			}
		}
		  var ttl = FExtension.element(GET("SL_LOCALIZATION"),'extClose');
		  var DM = FExtension.element(GET("SL_LOCALIZATION"),'extwptDName');
		  var SDM = FExtension.element(GET("SL_LOCALIZATION"),'extwptSDName');
		  var ALWAYS = FExtension.element(GET("SL_LOCALIZATION"),'extwptAlwaysTranslateThisSite');
		  var NEVER = FExtension.element(GET("SL_LOCALIZATION"),'extwptNeverTranslateThisSite');
		  var MO = FExtension.element(GET("SL_LOCALIZATION"),'extwptDOrTip');
		  var TB = FExtension.element(GET("SL_LOCALIZATION"),'extwptDTb');
		  var SAVE = FExtension.element(GET("SL_LOCALIZATION"),'extSaveButton');


		  var LINE1 = "<table width=100%><tr><td width=30%>"+DM+":</td><td width=70% nowrap>https://<input id='newdom' class='SRVwpt' type=text placeholder='Domain name'></td></tr></table>";
		  var LINE2 = "<table width=90%><tr><td width=5%><div class='SL_BOX' id='wpt_Dp1'></div></td><td width=95%>"+SDM+"</td></tr></table>";
		  var LINE3 = "<table width=90%><tr><td width=5%><div class='SL_BOX' id='wpt_Dp2'></div></td><td width=95%>"+ALWAYS+"</td></tr></table>";
		  var LINE4 = "<table width=90%><tr><td width=5%><div class='SL_BOX' id='wpt_Dp3'></div></td><td width=95%>"+NEVER+"</td></tr></table>";
		  var CL4 = "SL_BOX";
                  if(GET("SL_wptGlobTip")==1) CL4 = "SL_BOX_ACTIVE";
		  var LINE5 = "<table width=90%><tr><td width=5%><div class='"+CL4+"' id='wpt_Dp4'></div></td><td width=95%>"+MO+"</td></tr></table>";
		  var CL5 = "SL_BOX";
                  if(GET("SL_wptGlobTb")==1) CL5 = "SL_BOX_ACTIVE";
		  var LINE6 = "<table width=90%><tr><td width=5%><div class='"+CL5+"' id='wpt_Dp5'></div></td><td width=95%>"+TB+"</td></tr></table>";
		  var SAVEBTN = "<div align=right><button class='SL_button' id='SL_save_btn'>"+SAVE+"</button></div>";
		  var ENTRY_WINDOW="<div id=ewnd align=center><div align=right><img id='CloseDMN' src='../../../../content/img/util/remove.png' title='"+ttl+"'></div><div id='contentwnd' style='width:90%;' align=center>"+LINE1+LINE2+LINE3+LINE4+LINE5+LINE6+SAVEBTN+"</div></div>";

	  }else{
		VIEW = 2;
		var TMP="";
		var HEADER = "<div class='TopMenu' id='TopMenu' align=left><table  id='ltable' width=200><tr><td><img src='../../../../content/img/util/triggerkey.png'></td><td><div id='SL_control1'><span id='LAddNew'>Add</span><img id='LAddNewImg' title='Add new' src='../../../../content/img/util/cross.gif'></div></td><td><div id='SL_control2'><span id='LClearAll'></span><img id='LClearAllImg' src='../../../../content/img/util/remove.png'></div></td></tr></table></div>";
		GEBI("domains").className="tablinksP";
		GEBI("LArrow").src="../../img/util/arrow-up.png";
		GEBI("languages").className="tablinksA";
		GEBI("DArrow").src="../../img/util/arrow-down.png";
		var L_HIST = GET("SL_wptLHist").replace(/{|}/g,"");
		var itms = L_HIST.split(":");
		for(var i=0; i<itms.length; i++){
			var L_elem = itms[i].split(",");
			var L_ln = SL_Languages.split(",")
			var lt = L_TERM_Finder(itms[i]);
			for(var j=0; j<L_ln.length; j++){
				var L_ln_elem = L_ln[j].split(":");
				if(L_elem[0]==L_ln_elem[0]){ TMP = L_ln_elem[1]; j=100000; }
			}
			if(itms[i]!="" && TMP.toLowerCase().indexOf(term1.toLowerCase())!=-1 && lt==1) ROWS = ROWS +"<div class=caps id='cap"+i+"'><table width=100%><tr><td width=90% title='"+TMP+"'>"+ TMP + "</td><td width=5% align=right><img class='LOpen' id='{"+itms[i]+"}' title='"+FExtension.element(GET("SL_LOCALIZATION"),'extwptMoreOptions')+"' src='../../../../content/img/util/dots-tb.png'></td><td width=5% align=right><img class='LDelete' id='{"+itms[i]+"}' title='"+FExtension.element(GET("SL_LOCALIZATION"),'extDelete')+": "+TMP+"' src='../../../../content/img/util/remove.png'></td></tr></table></div>";		
		}
		  var ttl = FExtension.element(GET("SL_LOCALIZATION"),'extClose');
		  var DM = FExtension.element(GET("SL_LOCALIZATION"),'extSeSo');
		  var ALWAYS = FExtension.element(GET("SL_LOCALIZATION"),'extwptAlwaysTranslateThisLanguage');
		  var MO = FExtension.element(GET("SL_LOCALIZATION"),'extwptDOrTip');
		  var TB = FExtension.element(GET("SL_LOCALIZATION"),'extwptDTb');
		  var SAVE = FExtension.element(GET("SL_LOCALIZATION"),'extSaveButton');
		  var LNG_ALL_LIST="";
		  var LNG_LST = SL_Languages.split(",");
		  for(var J=0; J < LNG_LST.length; J++){
		    var LNG_LST2=LNG_LST[J].split(":");
		    LNG_ALL_LIST=LNG_ALL_LIST+"<option value='"+LNG_LST2[0]+"'>"+LNG_LST2[1]+"</option>";
		  }


		  var LINE1 = "<table width=100%><tr><td width=50% nowrap>"+DM+":</td><td width=50% nowrap><select id='alllangs'>"+LNG_ALL_LIST+"</select></td></tr></table>";
		  var LINE2 = "<table width=90%><tr><td width=5%><div class='SL_BOX' id='wpt_Lp1'></div></td><td width=95%>"+ALWAYS+"</td></tr></table>";
		  var CL3 = "SL_BOX";
                  if(GET("SL_wptGlobTip")==1) CL3 = "SL_BOX_ACTIVE";
		  var LINE4 = "<table width=90%><tr><td width=5%><div class='"+CL3+"' id='wpt_Lp3'></div></td><td width=95%>"+MO+"</td></tr></table>";
		  var CL4 = "SL_BOX";
                  if(GET("SL_wptGlobTb")==1) CL4 = "SL_BOX_ACTIVE";
		  var LINE5 = "<table width=90%><tr><td width=5%><div class='"+CL4+"' id='wpt_Lp4'></div></td><td width=95%>"+TB+"</td></tr></table>";
		  var SAVEBTN = "<div align=right><button class='SL_button' id='SL_save_btn'>"+SAVE+"</button></div>";
		  var ENTRY_WINDOW="<div id=ewnd align=center><div align=right><img id='CloseDMN' src='../../../../content/img/util/remove.png' title='"+ttl+"'></div><div id='contentwnd' style='width:90%;' align=center>"+LINE1+LINE2+LINE4+LINE5+SAVEBTN+"</div></div>";


	  }
	  ob.innerHTML = DOMPurify.sanitize(ENTRY_WINDOW+HEADER +'<br><br><br><br>' + ROWS + NORECORDS);

	  if(GEBI("SL_search_tool")) GEBI("SL_search_tool").style.display="block";
	  GEBI("SL_SORT").innerText="";
	  if(GEBI("SL_SORT").length==0){
	    if(st==1){
	        var p1 = FExtension.element(GET("SL_LOCALIZATION"),'extAllRecords');
        	var p2 = FExtension.element(GET("SL_LOCALIZATION"),'extwptDName');
	        var p3 = FExtension.element(GET("SL_LOCALIZATION"),'extwptSDName');
        	var p4 = FExtension.element(GET("SL_LOCALIZATION"),'extwptAlwaysTranslateThisSite');
	        var p5 = FExtension.element(GET("SL_LOCALIZATION"),'extwptNeverTranslateThisSite');
        	var p6 = FExtension.element(GET("SL_LOCALIZATION"),'extwptDOrTip');
	        var p7 = FExtension.element(GET("SL_LOCALIZATION"),'extwptDTb');

		var OPT="<option value='all'>"+p1+"</option>";
		OPT=OPT+"<option value='dom'>"+p2+"</option>";
		OPT=OPT+"<option value='sdom'>"+p3+"</option>";
		OPT=OPT+"<option value='always'>"+p4+"</option>";
		OPT=OPT+"<option value='never'>"+p5+"</option>";
		OPT=OPT+"<option value='mo'>"+p6+"</option>";
		OPT=OPT+"<option value='tb'>"+p7+"</option>";
	    } else {
        	var p1 = FExtension.element(GET("SL_LOCALIZATION"),'extAllRecords');
	        var p2 = FExtension.element(GET("SL_LOCALIZATION"),'extwptAlwaysTranslateThisLanguage');
	        var p4 = FExtension.element(GET("SL_LOCALIZATION"),'extwptDOrTip');
        	var p5 = FExtension.element(GET("SL_LOCALIZATION"),'extwptDTb');

		var OPT="<option value='all'>"+p1+"</option>";
		OPT=OPT+"<option value='always'>"+p2+"</option>";
		OPT=OPT+"<option value='mo'>"+p4+"</option>";
		OPT=OPT+"<option value='tb'>"+p5+"</option>";
	    }	
	    GEBI("SL_SORT").innerHTML=DOMPurify.sanitize(OPT);
	    if(VIEW==1) GEBI("SL_SORT").value = SEARCHTERM_D;
	    if(VIEW==2) GEBI("SL_SORT").value = SEARCHTERM_L;
	  }

	  if(GEBI('DClearAll')){
        	var RESET = FExtension.element(GET("SL_LOCALIZATION"),'extwptReset');
		GEBI('DClearAll').appendChild(document.createTextNode(RESET));
		GEBI('DClearAllImg').title = RESET;
		if(GET("SL_wptDHist")=="") GEBI("NoRecords").style.display="block";
	  }

	  if(GEBI('LClearAll')){
	        var RESET = FExtension.element(GET("SL_LOCALIZATION"),'extwptReset');
		GEBI('LClearAll').appendChild(document.createTextNode(RESET));
		GEBI('LClearAllImg').title = RESET;
		if(GET("SL_wptLHist")=="") GEBI("NoRecords").style.display="block";
	  }
	  if(GEBI("ltable")) GEBI("ltable").style.marginLeft=GEBI("languages").offsetLeft+"px";
}

function D_TERM_Finder(ob){
	var OUT = 0;
	var par = ob.split(",");
	if(SEARCHTERM_D=="dom" && par[1]!=1) OUT = 1;
	if(SEARCHTERM_D=="sdom" && par[1]==1) OUT = 1;
	if(SEARCHTERM_D=="always" && par[3]==1) OUT = 1;
	if(SEARCHTERM_D=="never" && par[3]==0) OUT = 1;
	if(SEARCHTERM_D=="mo" && par[4]==1) OUT = 1;
	if(SEARCHTERM_D=="tb" && par[5]==1) OUT = 1;
	if(SEARCHTERM_D=="all") OUT = 1;
	return(OUT);
}

function L_TERM_Finder(ob){
	var OUT = 0;
	var par = ob.split(",");
	if(SEARCHTERM_L=="always" && par[1]==1) OUT = 1;
//	if(SEARCHTERM_L=="never" && par[1]!=1) OUT = 1;
	if(SEARCHTERM_L=="mo" && par[2]==1) OUT = 1;
	if(SEARCHTERM_L=="tb" && par[3]==1) OUT = 1;
	if(SEARCHTERM_L=="all") OUT = 1;
	return(OUT);
}


function ClickHolder(e){
 	var id = e.target.id;
	if(id == "DClearAllImg" || id == "DClearAll") SL_RESET(1);
	if(id == "LClearAllImg" || id == "LClearAll") SL_RESET(2);
	if(e.target.className == "DDelete") DeleteD_Row(e.target.id); 
	if(e.target.className == "LDelete") DeleteL_Row(e.target.id); 
	if(e.target.className == "DOpen") EditD_Row(e.target.id);
	if(e.target.className == "LOpen") EditL_Row(e.target.id);

	if(id == "DAddNewImg" || id == "DAddNew") ADD_NEW_DOMAIN();
	if(id == "LAddNewImg" || id == "LAddNew") ADD_NEW_LANGUAGE();
	if(id == "CloseDMN") CloseWindowAndRestore();
	if(id == "SL_save_btn") SAVE_NEW_ENTRY();
	if(id == "SL_save_edited_btn") SAVE_EDITED_ENTRY();

	if(id == "wpt_Dp1") MODIFY_D_BOX(1);
	if(id == "wpt_Dp2") MODIFY_D_BOX(2);
	if(id == "wpt_Dp3") MODIFY_D_BOX(3);
	if(id == "wpt_Dp4") MODIFY_D_BOX(4);
	if(id == "wpt_Dp5") MODIFY_D_BOX(5);
	if(id == "wpt_Lp1") MODIFY_L_BOX(1);
	if(id == "wpt_Lp3") MODIFY_L_BOX(3);
	if(id == "wpt_Lp4") MODIFY_L_BOX(4);

}


function openCity(evt, cityName) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(cityName).style.display = "block";
  evt.currentTarget.className += " active";
} 





function SL_DEL_AUTO(ob){
	GEBI("SRV"+ob).value = "Auto Translate"; 
	GEBI("SRV"+ob).placeholder = "Auto Translate"; 
        GEBI("MSG"+ob).style.visibility="hidden";
	save_options(0);
}                          


function RESET_ALL_HK(id){
        var st = "";
        switch (id){
         case 6: st = 'SL_HK_wpt1'; break;
         case 7: st = 'SL_HK_wpt2'; break;
         case 12: st = 'SL_HK_SO_wpt'; break;
         case 13: st = 'SL_HK_CT_wpt'; break;
	}
	EXTENSION_DEFAULTS();
	GET_PACK_PARAMS();
	setTimeout(function() {	
		for(var i=0; i<PACK_PARAMS.length; i++){
			var tmp = PACK_PARAMS[i].split(";");
			var curDBname = tmp[0];
			var curDBparam = tmp[1];
			var DBparam = GET(curDBname);
			if(curDBname == st){
				SET(curDBname, curDBparam);			
				GEBI("MSG"+id).style.visibility="hidden";
			}
		}
		var newParam = GET(st);
		newParam = newParam.replace("Escape","Esc");
		GEBI("SRV"+id).value=newParam;
	}, TIME_OUT);
}

function WPT_DB_SORTING(){
 	D_SORT();
 	L_SORT();
}


function D_SORT(){
	var DBNAME = "SL_wptDHist";
        var HIST = GET(DBNAME);
	HIST = HIST.replace(/{|}/g,"");
        var ARR = HIST.split(":")
	ARR.sort();
	var OUT = "";
        for(var i = 0; i < ARR.length; i++){
		if(i < ARR.length-1) OUT = OUT + ARR[i] + "}:{";        	    
		else  OUT = OUT + ARR[i];
	}
	if(OUT!=""){
		OUT="{" + OUT +"}";
		SET(DBNAME, OUT);
	}
}

function L_SORT(){
	var DBNAME = "SL_wptLHist";
        var HIST = GET(DBNAME);
	HIST = HIST.replace(/{|}/g,"");
        var ARR= HIST.split(":");
	var OUT = "";
	for(var i=0; i<ARR.length; i++){
		var L_elem = ARR[i].split(",");
		var L_ln = SL_Languages.split(",")
		for(var j=0; j<L_ln.length; j++){
			var L_ln_elem = L_ln[j].split(":");
			if(L_elem[0]==L_ln_elem[0]){ HIST = HIST.replace(L_ln_elem[0], L_ln_elem[1]);}
		}
	}
        ARR= HIST.split(":").sort();
	OUT = "";
	for(var i=0; i<ARR.length; i++){
		var Elem = ARR[i].split(",");
		var LN = SL_Languages.split(",")
		for(var j=0; j<LN.length; j++){
			var LN_elem = LN[j].split(":");
			if(Elem[0]==LN_elem[1]){ 
				if(i<ARR.length-1) OUT = OUT + LN_elem[0]+","+Elem[1]+","+Elem[2]+","+Elem[3] +":";
				else OUT = OUT + LN_elem[0]+","+Elem[1]+","+Elem[2]+","+Elem[3]
			}
		}	
	}
	OUT = OUT.replace(/:/g,"}:{");
	if(OUT!=""){
		OUT="{" + OUT +"}";
		SET(DBNAME, OUT);
	}
}


function ADD_NEW_DOMAIN(){
	GrayOutContant();
}


function ADD_NEW_LANGUAGE(){
	GrayOutContant();
}

function GrayOutContant(){
	GEBI("TopMenu").style.visibility="hidden";
	var rows = document.getElementsByClassName("caps");
	for(var i=0; i < rows.length; i++){
	 	rows[i].style.visibility="hidden";
	}
	GEBI("ewnd").style.display="block";
	var H = "418px"
	GEBI("Content").style.height=H;
}

function MODIFY_D_BOX(id){
 	if(GEBI("wpt_Dp"+id).className=="SL_BOX") GEBI("wpt_Dp"+id).className="SL_BOX_ACTIVE";
	else GEBI("wpt_Dp"+id).className="SL_BOX";
	if(id==2){
		if(GEBI("wpt_Dp2").className=="SL_BOX_ACTIVE" && GEBI("wpt_Dp3").className=="SL_BOX_ACTIVE") GEBI("wpt_Dp3").className="SL_BOX";
	}
	if(id==3){
		if(GEBI("wpt_Dp2").className=="SL_BOX_ACTIVE" && GEBI("wpt_Dp3").className=="SL_BOX_ACTIVE") GEBI("wpt_Dp2").className="SL_BOX";
	}
}

function MODIFY_L_BOX(id){
 	if(GEBI("wpt_Lp"+id).className=="SL_BOX") GEBI("wpt_Lp"+id).className="SL_BOX_ACTIVE";
	else GEBI("wpt_Lp"+id).className="SL_BOX";
}

function SAVE_NEW_ENTRY(){
 	if(VIEW==1){
 	        var DBNAME = "SL_wptDHist";
	        var HIST = GET(DBNAME);
		var DN = GEBI("newdom").value.toLowerCase();
		var err="Enter Valid Domain Name";
		if(DN.indexOf(":/") !=-1 ){
		 	var dnTMP = DN.split("/");
			for(var i=0; i<dnTMP.length; i++){
				if(dnTMP[i].length > 3 && dnTMP[i] != "https:" && dnTMP[i] != "http:" ){ DN = dnTMP[i].replace(/\//ig,""); i=1000;}
			}
		}
		if(DN=="") {
			GEBI("newdom").style.border="1px solid red";
		        alert("Error: "+err);
		        DN.name.focus();
		        return false;
		} else {
		    if (/^((?:(?:(?:\w[\.\-\+]?)*)\w)+)((?:(?:(?:\w[\.\-\+]?){0,62})\w)+)\.(\w{2,6})$/.test(DN)) {
			var P1=0;
			if(GEBI("wpt_Dp1").className=="SL_BOX_ACTIVE") P1=1;
			var P2=0;
			if(GEBI("wpt_Dp2").className=="SL_BOX_ACTIVE") P2=1;
			var P3=0;
			if(GEBI("wpt_Dp3").className=="SL_BOX_ACTIVE") P3=1;
			if(P2==0 && P3==0) P2=2;
			if(P2==1 && P3==0) P2=1;
			if(P2==0 && P3==1) P2=0;
			var P4=0;
			if(GEBI("wpt_Dp4").className=="SL_BOX_ACTIVE") P4=1;
			var P5=0;
			if(GEBI("wpt_Dp5").className=="SL_BOX_ACTIVE") P5=1;
			var ROW = "{"+DN+","+P1+",all,"+P2+","+P4+","+P5+",0,0}";

			var CNT=0;
			if(HIST==""){
				GEBI("newdom").style.border="1px solid #C1C1C1";
				SET(DBNAME,ROW); 
				EDITOR(1);
			} else {
				var HIST_LINE = HIST.replace(/{|}/g,"").split(":");
				for(var i=0; i<HIST_LINE.length; i++){
				 	var HIST_PAR = HIST_LINE[i].split(",");
					if(HIST_PAR[0].toLowerCase()==DN.toLowerCase()) CNT++;
				}
				if(CNT!=0){
					SAVE_EDITED_ENTRY()
					EDITOR(1);
				} else {
					GEBI("newdom").style.border="1px solid #C1C1C1";
					var NEWROW = ROW+":"+HIST
					SET(DBNAME,NEWROW); 
					EDITOR(1);
				}
			}
			GEBI("newdom").style.border="1px solid #C1C1C1";
		    }
		    else {
			GEBI("newdom").style.border="1px solid red";
		        alert("Error: " +err);
		        DN.name.focus();
		        return false;
		    }
		}

	} else {
 	        var DBNAME = "SL_wptLHist";
	        var HIST = GET(DBNAME);
		var P1=0;
		if(GEBI("wpt_Lp1").className=="SL_BOX_ACTIVE") P1=1;
		var P2=0;
		var P3=0;
		if(GEBI("wpt_Lp3").className=="SL_BOX_ACTIVE") P3=1;
		var P4=0;
		if(GEBI("wpt_Lp4").className=="SL_BOX_ACTIVE") P4=1;
		var ROW = "{"+GEBI("alllangs").value+","+P1+","+P3+","+P4+"}";
	        if(HIST == ""){
			SET(DBNAME,ROW); 
			EDITOR(2);
		} else {
			if(HIST.indexOf(GEBI("alllangs").value)!=-1) {
				SAVE_EDITED_ENTRY()
				EDITOR(2);
			} else {
				var NEWROW = ROW+":"+HIST
				SET(DBNAME,NEWROW); 
                                EDITOR(2);
			}
		}	
	}
}




function SAVE_EDITED_ENTRY(){
 	if(VIEW==1){
 	        var DBNAME = "SL_wptDHist";
	        var HIST = GET(DBNAME);
		var DN = GEBI("newdom").value.toLowerCase();
		if(DN=="") {
			GEBI("newdom").style.border="1px solid red";
		        alert("Enter Valid Domain Name");
		        DN.name.focus();
		        return false;
		} else {
			var P1=0;
			if(GEBI("wpt_Dp1").className=="SL_BOX_ACTIVE") P1=1;
			var P2=0;
			if(GEBI("wpt_Dp2").className=="SL_BOX_ACTIVE") P2=1;
			var P3=0;
			if(GEBI("wpt_Dp3").className=="SL_BOX_ACTIVE") P3=1;
			if(P2==0 && P3==0) P2=2;
			if(P2==1 && P3==0) P2=1;
			if(P2==0 && P3==1) P2=0;
			var P4=0;
			if(GEBI("wpt_Dp4").className=="SL_BOX_ACTIVE") P4=1;
			var P5=0;
			if(GEBI("wpt_Dp5").className=="SL_BOX_ACTIVE") P5=1;
			var ROW = "{"+DN+","+P1+",all,"+P2+","+P4+","+P5+",0,0}";
		}
		var DMNS = HIST.split(":");
		var OUT = "";
		var temp = ITEM.split(":");
		ITEM = "{"+temp[1]+"}";
		for (var i=0; i<DMNS.length; i++){
		 	if(DMNS[i] == ITEM){
		 	 	HIST=HIST.replace(DMNS[i],ROW);	
				SET(DBNAME,HIST); 
                                EDITOR(1);
				i=1000;
			}
		}
	} else {
 	        var DBNAME = "SL_wptLHist";
	        var HIST = GET(DBNAME);
		var P1=0;
		if(GEBI("wpt_Lp1").className=="SL_BOX_ACTIVE") P1=1;
		var P3=0;
		if(GEBI("wpt_Lp3").className=="SL_BOX_ACTIVE") P3=1;
		var P4=0;
		if(GEBI("wpt_Lp4").className=="SL_BOX_ACTIVE") P4=1;
		var ROW = "{"+GEBI("alllangs").value+","+P1+","+P3+","+P4+"}";

	        if(HIST != ""){
			var LNGS = HIST.split(":");
			var LN = GEBI("alllangs").value;
			var OUT = "";
			for (var i=0; i<LNGS.length; i++){
		 		if(LNGS[i]==ITEM){
		 	 		HIST=HIST.replace(LNGS[i],ROW);	
					SET(DBNAME,HIST); 
                	                EDITOR(2);
					i=1000;
				}
			}
		}	
	}
}


function EditD_Row(itm){
	ITEM = itm;
	EDIT_DOMAIN(itm);	
}

function EditL_Row(itm){
	ITEM = itm;
	EDIT_LANGUAGE(itm);
}

function EDIT_LANGUAGE(itm){
	GrayOutContant();
        var HIST = GET("SL_wptLHist");
	itm = itm.replace(/{|}/g,""); 
	var LINE = itm.split(","); 
	if(HIST!="") {	

		var L_ln = SL_Languages.split(",")
		var lt = L_TERM_Finder(LINE[0]);
		var ALL_LANGS="";
		for(var j=0; j<L_ln.length; j++){
			var L_ln_elem = L_ln[j].split(":");
			var sel = "";
			if(LINE[0]==L_ln_elem[0]){ sel = " selected "; }
			ALL_LANGS=ALL_LANGS+"<option "+ sel +" value='"+L_ln_elem[0]+"'>" + L_ln_elem[1] + "</option>";
		}


	        GEBI("alllangs").style.width = "220px";
	        GEBI("alllangs").innerHTML = DOMPurify.sanitize(ALL_LANGS);

		if(LINE[1]==1) {
			GEBI("wpt_Lp1").className="SL_BOX_ACTIVE";
	       	} else {
			GEBI("wpt_Lp1").className="SL_BOX";
		}
		if(LINE[1]==2) {
			GEBI("wpt_Lp1").className="SL_BOX";
		}

		if(LINE[2]==1) GEBI("wpt_Lp3").className="SL_BOX_ACTIVE";
	       	else GEBI("wpt_Lp3").className="SL_BOX";

		if(LINE[3]==1) GEBI("wpt_Lp4").className="SL_BOX_ACTIVE";
	       	else GEBI("wpt_Lp4").className="SL_BOX";

		GEBI("SL_save_btn").id = "SL_save_edited_btn";
	}

}


function EDIT_DOMAIN(itm){
	GrayOutContant();
        var HIST = GET("SL_wptDHist");
	var data = itm.split(":"); 
	var OUT = data[0]; 
	var LINE = data[1].split(","); 
	if(HIST!="") {	
	        GEBI("newdom").value = LINE[0];
		var ro = document.createAttribute("readonly");
		ro.value = "readonly";
	       	GEBI("newdom").setAttributeNode(ro);

		if(LINE[1]==1) GEBI("wpt_Dp1").className="SL_BOX_ACTIVE";
	       	else GEBI("wpt_Dp1").className="SL_BOX";

		if(LINE[3]==1) {
			GEBI("wpt_Dp3").className="SL_BOX";
			GEBI("wpt_Dp2").className="SL_BOX_ACTIVE";
	       	} else {
			GEBI("wpt_Dp3").className="SL_BOX_ACTIVE";
			GEBI("wpt_Dp2").className="SL_BOX";
		}
		if(LINE[3]==2) {
			GEBI("wpt_Dp2").className="SL_BOX";
			GEBI("wpt_Dp3").className="SL_BOX";
		}

		if(LINE[4]==1) GEBI("wpt_Dp4").className="SL_BOX_ACTIVE";
	       	else GEBI("wpt_Dp4").className="SL_BOX";

		if(LINE[5]==1) GEBI("wpt_Dp5").className="SL_BOX_ACTIVE";
	       	else GEBI("wpt_Dp5").className="SL_BOX";

		GEBI("SL_save_btn").id = "SL_save_edited_btn";
	}
}

function DeleteD_Row(itm){
        var HIST = GET("SL_wptDHist");
	if(HIST!="") {	
		HIST = HIST.replace(itm+":","");
		HIST = HIST.replace(":"+itm,"");
		HIST = HIST.replace(itm,"");
		SET("SL_wptDHist",HIST);
		EDITOR(VIEW);
	}
}

function DeleteL_Row(itm){
        var HIST = GET("SL_wptLHist");
	if(HIST!="") {	
		HIST = HIST.replace(itm+":","");
		HIST = HIST.replace(":"+itm,"");
		HIST = HIST.replace(itm,"");
		SET("SL_wptLHist",HIST);
		EDITOR(VIEW);
	}
}

function CloseWindowAndRestore(){
	GEBI("TopMenu").style.visibility="visible";
	var rows = document.getElementsByClassName("caps");
	for(var i=0; i < rows.length; i++){
	 	rows[i].style.visibility="visible";
	}
	GEBI("ewnd").style.display="none";
	GEBI("Content").style.height="auto";
	EDITOR(VIEW);
}

function ClearSearchBox(){
  GEBI("SL_H_SEARCH").value="";
  EDITOR(VIEW);
}
function FAST_SEARCH(){
   	EDITOR(VIEW);
}
}, TIME_OUT);

function GEBI(id){ return document.getElementById(id);}
function save_options(st) {
 setTimeout(function() {
	var SL_select_S_wpt = GEBI("SL_langSrc_wpt");
	var SL_select_T_wpt = GEBI("SL_langDst_wpt");

	if(SL_select_S_wpt.value!=SL_select_T_wpt.value){

		if(GEBI("SL_TH_3").checked==true) SET("SL_TH_3","1");
		else SET("SL_TH_3", "0");

		if(GEBI("SL_global_lng_wpt").checked==true){
			SET("SL_global_lng", GEBI("SL_global_lng_wpt").checked);
			SET("SL_global_lng_bbl", GEBI("SL_global_lng_wpt").checked);
			SET("SL_global_lng_wpt", GEBI("SL_global_lng_wpt").checked);
			SET("SL_global_lng_it", GEBI("SL_global_lng_wpt").checked);

			SET("SL_langSrc", SL_select_S_wpt.children[SL_select_S_wpt.selectedIndex].value);
			SET("SL_langSrc2", SL_select_S_wpt.children[SL_select_S_wpt.selectedIndex].value);
			SET("SL_langSrc_bbl", SL_select_S_wpt.children[SL_select_S_wpt.selectedIndex].value);
			SET("SL_langSrc_wpt", SL_select_S_wpt.children[SL_select_S_wpt.selectedIndex].value);
			SET("SL_langSrc_it", SL_select_S_wpt.children[SL_select_S_wpt.selectedIndex].value);

			SET("SL_langDst", SL_select_T_wpt.children[SL_select_T_wpt.selectedIndex].value);
			SET("SL_langDst2", SL_select_T_wpt.children[SL_select_T_wpt.selectedIndex].value);
			SET("SL_langDst_bbl", SL_select_T_wpt.children[SL_select_T_wpt.selectedIndex].value);
			SET("SL_langDst_wpt", SL_select_T_wpt.children[SL_select_T_wpt.selectedIndex].value);
			SET("SL_langDst_it", SL_select_T_wpt.children[SL_select_T_wpt.selectedIndex].value);

			var IDS = document.getElementById("SL_langDst_wpt").value;
	   		SL_SAVE_FAVORITE_LANGUAGES(IDS, "SL_FAV_LANGS_IMT");
	   		SL_SAVE_FAVORITE_LANGUAGES(IDS, "SL_FAV_LANGS_BBL");
	   		SL_SAVE_FAVORITE_LANGUAGES(IDS, "SL_FAV_LANGS_IT");
	   		SL_SAVE_FAVORITE_LANGUAGES(IDS, "SL_FAV_LANGS_WPT");

		} else {
			SL_SAVE_FAVORITE_LANGUAGES(document.getElementById("SL_langDst_wpt").value, "SL_FAV_LANGS_WPT");
			SET("SL_langDst_name_wpt", SL_select_T_wpt.children[SL_select_T_wpt.selectedIndex].text);
			SET("SL_global_lng", GEBI("SL_global_lng_wpt").checked);
			SET("SL_global_lng_bbl", GEBI("SL_global_lng_wpt").checked);
			SET("SL_global_lng_wpt", GEBI("SL_global_lng_wpt").checked);
			SET("SL_global_lng_it", GEBI("SL_global_lng_wpt").checked);
		}	


		RESET_TEMPS_TO_DEFAULT();

		var SL_langSrc_wpt = SL_select_S_wpt.children[SL_select_S_wpt.selectedIndex].value;
		SET("SL_langSrc_wpt", SL_langSrc_wpt);
		
		var SL_langDst_wpt = SL_select_T_wpt.children[SL_select_T_wpt.selectedIndex].value;
		SET("SL_langDst_wpt", SL_langDst_wpt);
		SET("SL_WPT_TEMP_LANG", SL_langDst_wpt);


		
		var SL_langDst_name_wpt = SL_select_T_wpt.children[SL_select_T_wpt.selectedIndex].text;
		SET("SL_langDst_name_wpt", SL_langDst_name_wpt);

                SET("SL_HK_wptbox1", GEBI("SL_HK6").checked);
                SET("SL_HK_wptbox2", GEBI("SL_HK7").checked);
                SET("SL_HK_SObox_wpt", GEBI("SL_HK12").checked);
                SET("SL_HK_CTbox_wpt", GEBI("SL_HK13").checked);

                SET("SL_HK_wpt1", GEBI("SRV6").value);
                SET("SL_HK_wpt2", GEBI("SRV7").value);
                SET("SL_HK_SO_wpt", GEBI("SRV12").value);
                SET("SL_HK_CT_wpt", GEBI("SRV13").value);

                if(GEBI("SL_SOOOM").checked==true) SET("SL_wptGlobTip", "1");
                else SET("SL_wptGlobTip", "0");

                if(GEBI("SL_Toolbar").checked==true) {
			SET("SL_wptGlobTb", "1");
                }else{
			SET("SL_wptGlobTb", "0");
		}

		if(GEBI("WPTflip").checked==true)  SET("WPTflip",1);
		else SET("WPTflip",0);

//------TIME STAMP--------------
	new Date().getTime();
	SET("SL_TS", Date.now());
//==============================

		if(GEBI("SL_global_lng_wpt").checked==true){
			SET("SL_langDst_name", SL_langDst_name_wpt);
			SET("SL_langDst_name_bbl", SL_langDst_name_wpt);
			SET("SL_langDst_name_wpt", SL_langDst_name_wpt);
			SET("SL_langDst_name_it", SL_langDst_name_wpt);
		}

//		SET("SL_Flag", "FALSE");
                PREPARE_RCM_CONTENT();

		if(GEBI('autohotkeys')){
		  var frame = GEBI('autohotkeys');
		}

	}else alert(FExtension.element(GET("SL_LOCALIZATION"),'extS_T_L_diff'));
 }, 100);
}

function SL_SAVE_FAVORITE_LANGUAGES(ln, TR){
	var OUT = "";
	var OUT2 = "";
	var SL_FAV_LANGS = GET(TR);
	var SL_FAV_MAX = GET("SL_FAV_MAX");
	if(SL_FAV_LANGS.indexOf(ln)!=-1){
		SL_FAV_LANGS = SL_FAV_LANGS.replace(ln+",",""); 
		SL_FAV_LANGS = SL_FAV_LANGS.replace(ln,"");
	}
	OUT = ln + ",";	
	var ARR = SL_FAV_LANGS.split(",");
	for (var i = 0; i < ARR.length; i++){
	 	OUT = OUT + ARR[i]+",";
	}
	if(OUT.slice(-1)==",") 	OUT = OUT.slice(0, OUT.length - 1);
	var TMP = OUT.split(",");
	if(TMP.length > SL_FAV_MAX) {
		for (var j = 0; j < TMP.length-1; j++){
		 	OUT2 = OUT2 + TMP[j]+",";
		}		
		OUT = OUT2 
	}
	if(OUT.slice(-1)==",") 	OUT = OUT.slice(0, OUT.length - 1);
	SET(TR, OUT);
}
