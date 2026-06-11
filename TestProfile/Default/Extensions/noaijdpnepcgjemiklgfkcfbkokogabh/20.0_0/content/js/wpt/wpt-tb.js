let DOMAIN;
let TO_LANGUAGE;
let FROM_LANGUAGE;
let TB_CANVAS;

let CUR_SHOW=0;
let CUR_TB=0;
let CUR_MO=0;
var doc = FExtension.browserInject.getDocument();
var DETECTED = "";
var invalidElements =  {'APPLET': 1,'AREA': 1,'BASE': 1,'BR': 1,'COL': 1,'B': 1,'HR': 1,'IMG': 1,'INPUT': 1,'IFRAME': 1,'ISINDEX': 1,'LINK': 1,'NOFRAMES': 1,'NOSCRIPT': 1,'META': 1,'OBJECT': 1,'PARAM': 1,'SCRIPT': 1,'STYLE': 1,'SELECT': 1}
var LANGSALL = "";
var MENU = "";
var DET_LANG="";
var GLOBALEVENT="";
var ONCE_ONLY=0;
var SL_DARK="invert(95%)";
var SL_LIGHT="invert(0%)";
var analysisText="";
var SL_IS_SUBDOMAIN = false;
var SL_GWPT_Show_Hide = 0;
var SL_GWPT_Show_Hide_tmp = 0;
var SL_GWHOST = "";
var SL_DETLANG = "";
var SL_D_List = "";
var SL_L_List = "";

var SL_wptDHist = "";
var SL_wptLHist = "";
var SL_wptGlobAuto = "0";
var SL_wptGlobTb = "0";
var SL_wptGlobTip = "0";
var SL_wptGlobLang = "";

var SL_wptGlobAutoTmp = "0";
var SL_wptGlobTbTmp = "1";
var SL_wptGlobTipTmp = "1";
var SL_wptGlobLangTmp = "";


//WPT D temp params
var SL_wptDp1 = ""; // Domain Name
var SL_wptDp2 = 0; // Subdomain
var SL_wptDp3 = "All"; // Language
var SL_wptDp4 = 2; // Always/Never
var SL_wptDp5 = 0; // Show original on MO
var SL_wptDp6 = 0; // Show TB
var SL_wptDp7 = 0; // Reserved
var SL_wptDp8 = 0; // Reserved

//WPT L temp params
var SL_wptLp1 = ""; // Language
var SL_wptLp2 = 0; // Always/Never
var SL_wptLp3 = 0; // Show original
var SL_wptLp4 = 0; // Show TB


var SL_WPT_SKIP = 0;
var SL_WPT_IGRORE = 0;
var SL_WPT_TB_DEFAULT = 0;
var SL_WPT_TEMP_LANG = "";
var SL_WPT_LANG = "";


doc.addEventListener('click', function(e){ WPT_ClickHandler(e) }, false);
window.onresize = function() {WPT_TB_resizeCanvas()};
doc.addEventListener('keyup', function(e){
 if(e.target.id == "SL_wpt_search_box") WPT_FASTTYPE();
 if(e.target.id == "SL_wpt_search_box2") WPT_FASTTYPE2();

 if(e.key==TranslatorIM.SL_HK_CT_wpt.replace("Esc","Escape")) {
	TranslatorIM.SL_BBL_OBJ_OFF(0);
	TranslatorIM.CloseAnyOpenTranslator();			
 }

}, false);

/*
doc.addEventListener('mousemove', function(e){
     if(GEBI("SL_wpt_cp")){
	    var Xarr=GEBI("SL_wpt_cp").getElementsByClassName("SL_wpt_to");
	    if(Xarr.length > 0){ 
		UPDATE_WPT_LANGUAGE_LIST();
		var Real = Xarr[0].id.replace("SL_wpt_to_","")
		var Pattern = SL_FAV_LANGS_WPT.split(",");
		if(Real != Pattern[0]){
		   if(GEBI("SL_wpt_more_opened")) GEBI("SL_wpt_more_opened").id="SL_wpt_more"; 
		   HIDE_MORE_LANGS_WPT_TB();
		   var NAME = SL_GetLongName(Pattern[0]);
		   Xarr[0].value = Pattern[0]+":"+NAME;
		   Xarr[0].innerText = NAME;
		   Xarr[0].id = "SL_wpt_to_"+Pattern[0];
		   Xarr[0].style = "border-bottom:2px solid #1186BB";
		   GEBI("SL_wpt_more").style="border:0px";  		   
		   WPT_RESTORE(e.target.id); 
		}
	    }
     }

}, false);
*/

//OBSERVE MUTATIONS
let previousUrl = '';
const observer = new MutationObserver(function(mutations) {
 window.setTimeout(function() {
  if (window.location.href !== previousUrl) {
	if(RESTORE==0){
		WPT_RUN();
		previousUrl = String(window.location.href);
	}
    }
  }, 1000);
});

const config = {subtree: true, childList: true};
// start listening to changes
observer.observe(document, config);
//OBSERVE MUTATIONS


function WPT_TB_resizeCanvas(){
	var htmlCanvasWidth = window.innerWidth;
	if(htmlCanvasWidth <= 500) HIDE_SOME_FAVS(1);
	if(htmlCanvasWidth > 500 && htmlCanvasWidth <= 700) HIDE_SOME_FAVS(2);
	if(htmlCanvasWidth > 700) HIDE_SOME_FAVS(3);
}


function HIDE_SOME_FAVS(ob){
	for(var i=1; i<doc.getElementsByClassName("SL_wpt_to").length; i++){
		doc.getElementsByClassName("SL_wpt_to")[i].style.display="";
	}
	for(var i=ob; i<doc.getElementsByClassName("SL_wpt_to").length; i++){
		doc.getElementsByClassName("SL_wpt_to")[i].style.display="none";
	}
}

function WPT_FASTTYPE(){
	var curText = GEBI("SL_wpt_search_box").value;
	WPT_FASTTYPE_REBUILD(curText);	
}
function WPT_FASTTYPE2(){
	var curText = GEBI("SL_wpt_search_box2").value;
	WPT_FASTTYPE_REBUILD2(curText);	
}

function UPDATE_WPT_LANGUAGE_LIST(){
	FExtension.browserInject.extensionSendMessage({greeting: 1}, function(response) {
		if(response && response.farewell){
			var theresponse = response.farewell.split("~");
			SL_FAV_LANGS_WPT=theresponse[82];
			SL_LNG_CUSTOM_LIST=theresponse[29];
		}
	});
}

function INIT_WPT_TB(LOC,key){
   try{
     UPDATE_WPT_LANGUAGE_LIST();
     WPT_DETECTION();
     window.setTimeout(function() {
        SL_FAV_LANGS_WPT = uniqFAV(SL_FAV_LANGS_WPT);
	if(SL_FAV_LANGS_WPT.indexOf(",")!=-1){
		var Arr = TranslatorIM.SL_FAV_LANGS_WPT.split(",");
		TO_LANGUAGE = Arr[0];
	} else  TO_LANGUAGE = SL_FAV_LANGS_WPT; 

	LANGSALL = FExtension.element(LOC,'extLanguages').split(",");

	SL_LOC = LOC;

	DOMAIN = top.location.host.toString();
	if(self == top ) {
	    window.setTimeout(function() {
		var SD = SL_DETECTsubDomain();
		chrome.runtime.sendMessage({greeting: "WPT_READ_DB:>"+DOMAIN+"|"+FROM_LANGUAGE+"|"+SD }, function(response) {});
		//UPDATE WPT DB

		chrome.runtime.onMessage.addListener(function (response, sendResponse) {

	             	if(response && response.action){
			     	ROUTER(response.action);

				if(SL_wptDp5=="" || SL_wptDp5==undefined) SL_wptDp5 = TranslatorIM.SL_wptGlobTip;
				if(SL_wptDp6=="" || SL_wptDp6==undefined) SL_wptDp6 = TranslatorIM.SL_wptGlobTb;
				if(SL_wptLp3=="" || SL_wptLp3==undefined) SL_wptLp3 = TranslatorIM.SL_wptGlobTip;
				if(SL_wptLp4=="" || SL_wptLp4==undefined) SL_wptLp4 = TranslatorIM.SL_wptGlobTb;

				if(TranslatorIM.SL_wpt_MANUAL_MODE_OFF!=DOMAIN){
				     	if(ONCE_ONLY == 0){ 
						ONCE_ONLY=key;

					     	if(CUR_SHOW!=0){
						    	WPT_FLIP();
							if(CUR_TB==0) HIDE_WPT_TB();
							else SHOW_WPT_TB();
							if(SL_wptDp4 != 0){
								WPT_TRANSLATOR();
							}
						}
			   	     	}	
				}
				
			}
		});
	    }, 50);
	}
      },150);


   } catch(ex){}	
}



function WPT_MUTATION(){
		var SD = SL_DETECTsubDomain();
		chrome.runtime.sendMessage({greeting: "WPT_READ_DB:>"+DOMAIN+"|"+FROM_LANGUAGE+"|"+SD }, function(response) {});

		chrome.runtime.onMessage.addListener(function (response, sendResponse) {
	             	if(response && response.action){
			     	ROUTER(response.action);

				if(SL_wptDp5=="" || SL_wptDp5==undefined) SL_wptDp5 = TranslatorIM.SL_wptGlobTip;
				if(SL_wptDp6=="" || SL_wptDp6==undefined) SL_wptDp6 = TranslatorIM.SL_wptGlobTb;
				if(SL_wptLp3=="" || SL_wptLp3==undefined) SL_wptLp3 = TranslatorIM.SL_wptGlobTip;
				if(SL_wptLp4=="" || SL_wptLp4==undefined) SL_wptLp4 = TranslatorIM.SL_wptGlobTb;
				if(TranslatorIM.SL_wpt_MANUAL_MODE_OFF!=DOMAIN){
					WPT_TRANSLATOR();
				}
			}
		});
}



function WPT_TRANSLATOR(){
//        WPT_RESTORE_ORIGINAL_NODES();
	chrome.runtime.sendMessage({greeting: "ACT_ST:>1,"+DOMAIN}, function(response) {});
	ACTIVATE_THEME(TranslatorIM.THEMEmode);
}



function ROUTER(SRC){
    try{
	//MANUAL MODE
	if(SRC=="open_wpt"){
		CUR_SHOW = 1;
		CUR_TB = 1; 
		CUR_MO = 1;
	} else {
		var TMP = SRC.split("`");
		var TMP1 = TMP[0].split("|");
		var TMP2 = TMP[1].split("|");

		// DOMAIN
       		if(TMP1.length>=2){
		    SL_wptDp1 = TMP1[0]; // Domain Name
		    SL_wptDp2 = TMP1[1]; // Subdomain
		    SL_wptDp3 = TMP1[2]; // Language
		    SL_wptDp4 = TMP1[3]; // Always/Never
		    SL_wptDp5 = TMP1[4]; // Show original on MO
		    SL_wptDp6 = TMP1[5]; // Show TB


		    //LINKS HANDLER
		    CUR_SHOW = 0;
		    if(SL_wptDp4 != 1) {
		 	if(DOMAIN == TranslatorIM.SL_wpt_MANUAL_MODE_ON) {
				CUR_SHOW = 1;
				CUR_TB = SL_wptDp6;
				CUR_MO = SL_wptDp5;
			}
		    } else {
			CUR_SHOW = 1;
			CUR_TB = SL_wptDp6;
			CUR_MO = SL_wptDp5;
		    }
		    //LINKS HANDLER
	        
		    if(SL_wptDp4 != 0){
		       	if(DOMAIN==SL_wptDp1){
       				if(CUR_SHOW == 0) {
					if(SL_wptDp4 == 1) CUR_SHOW = 1;
					if(CUR_TB==0) CUR_TB = SL_wptDp6; 
					if(CUR_MO==0) CUR_MO = SL_wptDp5;
				}
			}
		    } else{
			//NEVER TRANSLATE A DOMAIN
			if(SL_wptDp4 == 1) CUR_SHOW = 1;
			CUR_TB = SL_wptDp6; 
			CUR_MO = SL_wptDp5;
		   } 
                }

		// LANGUAGE
	       	if(TMP2.length>=2){
		    SL_wptLp1 = TMP2[0]; // Language
		    SL_wptLp2 = TMP2[1]; // Always/Never
		    SL_wptLp3 = TMP2[2]; // Show original on MO
		    SL_wptLp4 = TMP2[3]; // Show TB
	        }


       		if(TMP1.length<=2){
			if(SL_wptDp4 != 0){
			       	if(FROM_LANGUAGE==SL_wptLp1){
       					if(CUR_SHOW == 0) {
						if(SL_wptLp2 == 1) CUR_SHOW = 1;
						CUR_TB = SL_wptLp4; 
						CUR_MO = SL_wptLp3;
					}  else{
						CUR_SHOW = 1;
						CUR_TB = SL_wptLp4; 
						CUR_MO = SL_wptLp3;
					}
				}
			}
		} else {
			if(SL_wptDp4 == 0){
				if(CUR_SHOW == 0) {
					CUR_SHOW = 0;
					CUR_TB = 0; 
					CUR_MO = 0;
				}
			} else {
			       	if(FROM_LANGUAGE==SL_wptLp1){
       					if(CUR_SHOW == 0) {
						if(SL_wptLp2 == 1) CUR_SHOW = 1;
						if(CUR_TB==0) CUR_TB = SL_wptDp6; 
						if(CUR_MO==0) CUR_MO = SL_wptDp5;
					}
				}
			}

		}
	}
   } catch(e){}
}






function WPT_ClickHandler(e){

    try{
	var id = e.target.id;
	var fch = e.target.firstChild;
	GLOBALEVENT=e;
	if(id == "SL_wpt_trbutton") BUTTON_WP_TRANSLATION();
	if(id == "SL_wpt_from")   {WPT_RESTORE(id);CLOSE_OPTIONS();}
	if(id == "SL_wpt_logo")	SHOW_OR_HIDE_WPT_TB();
	if(id == "SL_wpt_close")	{
		window.setTimeout(function() {
			TranslatorIM.SL_BBL_OBJ_OFF(0);
			TranslatorIM.CloseAnyOpenTranslator();
		}, 50);


/*
		WPT_RESTORE(id);DELETE_WPT_TB();

	WPT_RESTORE_ORIGINAL_NODES();
*/

				//	chrome.runtime.sendMessage({greeting: "RES_OR:>"}, function(response) {});

	}

	if(id == "SL_wpt_hide")	SHOW_OR_HIDE_WPT_TB();
	if(id == "SL_wpt_hidden_logo")	SHOW_OR_HIDE_WPT_TB();
	if(id == "SL_wpt_more")	MORE_LANGS_WPT_TB();
	if(id == "SL_wpt_donate")	DONATE();
	if(id == "SL_wpt_more_options")	MAIN_OPTIONS();
	if(id == "SL_wpt_Dp1")	CHANGE_STATE(e.target);
	if(id == "SL_wpt_Dp2")	CHANGE_STATE(e.target);
	if(id == "SL_wpt_Dp3")	CHANGE_STATE(e.target);
	if(id == "SL_wpt_Dp4")	CHANGE_STATE(e.target);
	if(id == "SL_wpt_Dp5")	CHANGE_STATE(e.target);
	if(id == "SL_wpt_Dp6")	CHANGE_STATE(e.target);
	if(id == "SL_wpt_Dp7")	CHANGE_STATE(e.target);
	if(id == "SL_wpt_Lp1")	CHANGE_STATE(e.target);
	if(id == "SL_wpt_Lp2")	CHANGE_STATE(e.target);
	if(id == "SL_wpt_Lp3")	CHANGE_STATE(e.target);
	if(id == "SL_wpt_Lp4")	CHANGE_STATE(e.target);

	window.setTimeout(function() {
	   if(fch){
		if(fch.id == "SL_wpt_Dp1")	CHANGE_STATE(fch);
		if(fch.id == "SL_wpt_Dp2")	CHANGE_STATE(fch);
		if(fch.id == "SL_wpt_Dp3")	CHANGE_STATE(fch);
		if(fch.id == "SL_wpt_Dp4")	CHANGE_STATE(fch);
		if(fch.id == "SL_wpt_Dp5")	CHANGE_STATE(fch);
		if(fch.id == "SL_wpt_Dp6")	CHANGE_STATE(fch);
		if(fch.id == "SL_wpt_Dp7")	CHANGE_STATE(fch);
		if(fch.id == "SL_wpt_Lp1")	CHANGE_STATE(fch);
		if(fch.id == "SL_wpt_Lp2")	CHANGE_STATE(fch);
		if(fch.id == "SL_wpt_Lp3")	CHANGE_STATE(fch);
		if(fch.id == "SL_wpt_Lp4")	CHANGE_STATE(fch);
	   }
	}, 50);


	if(id == "SL_wpt_lang_menu" || id == "SL_wpt_FROM_LANG") {
		WPT_SHOW_MORE_LANGS(e);
	}	

	if(id == "SL_wpt_more_opened") {
		if(GEBI("SL_wpt_more_opened")) GEBI("SL_wpt_more_opened").id="SL_wpt_more"; 
		HIDE_MORE_LANGS_WPT_TB();
	}	

	if(id == "SL_wpt_options") OPEN_OPTIONS();

	if(id.indexOf("SL_wpt_to_") != -1 ) SELECT_TO(id);

	if(id.indexOf("SL_wpt_from_") != -1 ) SELECT_FROM(id);

	if(id == "SL_wpt_close_search")	{ 
		GEBI("SL_wpt_search_box").value=""; 
		WPT_FASTTYPE(e); 
		GEBI("SL_wpt_search_box").focus();
	}

	if(id == "SL_wpt_close_search2")	{ 
		GEBI("SL_wpt_search_box2").value=""; 
		WPT_FASTTYPE2(e); 
		GEBI("SL_wpt_search_box2").focus();
	}

	if(id.indexOf("SL_wpt_")==-1 && e.target.className.indexOf("SL_wpt_")==-1) {
		if(GEBI("SL_wpt_options_canvas")){
			if(GEBI("SL_wpt_more_opened")) GEBI("SL_wpt_more_opened").id="SL_wpt_more"; 
			CLOSE_OPTIONS();
			TranslatorIM.SL_wpt_MANUAL_MODE_ON = DOMAIN;
			ONCE_ONLY=0;
			// YouTube links
			if(DOMAIN.indexOf("youtube.")!=-1) TranslatorIM.CloseAnyOpenTranslator();			
			//
			WPT_RESTORE_ORIGINAL_NODES();
			chrome.runtime.sendMessage({greeting: "ACT_ST:>1,"+DOMAIN}, function(response) {});
			FExtension.browserInject.extensionSendMessage({greeting: 1}, function(response) {
				if(response && response.farewell){
					var theresponse = response.farewell.split("~");
					SL_LNG_CUSTOM_LIST=theresponse[29];
					SL_FAV_LANGS_WPT=theresponse[82];
					INIT_WPT_TB(SL_LOC,1);
				}       
			});
		} else HIDE_MORE_LANGS_WPT_TB();
	}
	if(IfClickIsInside(e,"SL_wpt_lang_menu_canvas") == 0 && id != "SL_wpt_lang_menu" && id != "SL_wpt_FROM_LANG"){
		CLOSE_L_MENU();
	}

   } catch(e){}
}



function CHANGE_STATE(ob){
	var id = ob.id.replace("SL_wpt_","");

	var par="";
	var PARAMS_TYPE=1; //LANGUAGES
	if(id.indexOf("Dp")!=-1) PARAMS_TYPE=0; //DOMAINS
	if(id == "Dp3") {
		GEBI("SL_wpt_Dp4").className = GEBI("SL_wpt_Dp4").className.replace("_ACTIVE","");
	 	SL_wptDp3 = 1; 
	 	SL_wptDp4 = 0; 
	}
	if(id == "Dp4") {
		GEBI("SL_wpt_Dp3").className = GEBI("SL_wpt_Dp3").className.replace("_ACTIVE","");
	 	SL_wptDp3 = 0; 
	 	SL_wptDp4 = 1; 
	}
/*
	if(id == "Dp5") {
		if(GEBI("SL_wpt_Dp4").className.indexOf("_ACTIVE")!=-1) SL_wptDp4 = 1; 
		else SL_wptDp4 = 0; 
	}
*/

	if(id == "Lp2") {
		GEBI("SL_wpt_Lp1").className = GEBI("SL_wpt_Lp1").className.replace("_ACTIVE","");
	 	SL_wptLp1 = 0; 
	 	SL_wptLp2 = 1; 
	}

 	if(ob.className.indexOf("_ACTIVE") == -1){
		ob.className = ob.className+"_ACTIVE";
		par = 1;
	} else { 
		ob.className = ob.className.replace("_ACTIVE","");
		par = 0;
	}

	switch(id){
	 	case "Dp1": SL_wptDp1 = par; break; // Domain Name
	 	case "Dp2": SL_wptDp2 = par; break; // Subdomain
	 	case "Dp3": SL_wptDp3 = par; break;
	 	case "Dp4": SL_wptDp4 = par; break;
	 	case "Dp5": SL_wptDp5 = par; break;
	 	case "Dp6": SL_wptDp6 = par; break;
	 	case "Lp1": SL_wptLp1 = par; break;
	 	case "Lp2": SL_wptLp2 = par; break;
	 	case "Lp3": SL_wptLp3 = par; break;
	 	case "Lp4": SL_wptLp4 = par; break;
	}


	var DAlwaysNever=SL_wptDp4;

	if(SL_wptDp3==0 && SL_wptDp4==0) DAlwaysNever=2;
	if(SL_wptDp3==0 && SL_wptDp4==1) DAlwaysNever=0;
	if(SL_wptDp3==1 && SL_wptDp4==0) DAlwaysNever=1;
	var LAlwaysNever=SL_wptLp2;

	var regEx = /^-?[0-9]+$/;
	var W = regEx.test(SL_wptLp1);
	if(W==true){
		if(SL_wptLp1==0 && SL_wptLp2==0) LAlwaysNever=2;
		if(SL_wptLp1==0 && SL_wptLp2==1) LAlwaysNever=0;
		if(SL_wptLp1==1 && SL_wptLp2==0) LAlwaysNever=1;
	} else {
		if(SL_wptLp2==0 && SL_wptLp1==0) LAlwaysNever=2;
		if(SL_wptLp2==0 && SL_wptLp1==1) LAlwaysNever=0;
		if(SL_wptLp2==1 && SL_wptLp1==0) LAlwaysNever=1;
	}
	if(SL_wptDp2=="") SL_wptDp2=0;


	if(DAlwaysNever==undefined) DAlwaysNever=2;


	if(PARAMS_TYPE==0){
	        var DATA = "{"+DOMAIN+","+SL_wptDp2+","+TO_LANGUAGE+","+DAlwaysNever+","+SL_wptDp5+","+SL_wptDp6+",0,0}";
		chrome.runtime.sendMessage({greeting: "WPT_SAVE_D:>"+DATA}, function(response) {});
	} else {
	        var DATA = "{"+FROM_LANGUAGE+","+LAlwaysNever+","+SL_wptLp3+","+SL_wptLp4+"}";
		chrome.runtime.sendMessage({greeting: "WPT_SAVE_L:>"+DATA}, function(response) {});
	}
}


function WPT_RESTORE(ob){
	chrome.runtime.sendMessage({greeting: "CLEAN_ALL:>"}, function(response) {});

	if(GEBI(ob)) GEBI(ob).style = "border-bottom:2px solid #1186BB";
	for(var s=0; s < doc.getElementsByClassName("SL_wpt_to").length; s++){
	 	doc.getElementsByClassName("SL_wpt_to")[s].style="";
	}
}

function SELECT_TO(id){
	var ln = id.replace("SL_wpt_to_","");
	//window.setTimeout(function() {
		SL_SAVE_FAVORITE_LANGUAGES(ln);	
	//}, 50);


}

function SELECT_FROM(id){
        var LNG = id.replace("SL_wpt_from_","");
	var NEWlng = SL_GetLongName(LNG).toUpperCase()+" ";
	GEBI("SL_wpt_lang_menu").innerHTML = DOMPurify.sanitize(NEWlng);	
	FROM_LANGUAGE = LNG;
	CLOSE_L_MENU();
	LANGUAGE_SET_MANAGER(LNG);
        CHANGE_STATE(GLOBALEVENT.target);
}

function If_Mouse_Is_Within_Div(e,ob){
 	var out;
	var divRect = GEBI(ob).getBoundingClientRect();
	if (e.clientX >= divRect.left && e.clientX <= divRect.right && e.clientY >= divRect.top && e.clientY <= divRect.bottom) out=0;
	else out=1;
	return out;
}

function SHOW_OR_HIDE_WPT_TB(){
	HIDE_MORE_LANGS_WPT_TB();
	CLOSE_OPTIONS()
	var OB = GEBI('SL_wpt_canvas');
	if(OB)	OB.parentNode.removeChild(OB);
	if(GEBI("SL_wpt_hidden_logo")){
		var OB1 = GEBI('SL_wpt_hidden_logo');
		if(OB1)	OB1.parentNode.removeChild(OB1);
		SL_setSHOW_HIDE_TB_TMP("SL_GWPT_Show_Hide_tmp",1);
		SHOW_WPT_TB();		
	} else {
		SL_setSHOW_HIDE_TB_TMP("SL_GWPT_Show_Hide_tmp",0);
		HIDE_WPT_TB();
	}
}



function CLOSE_WPT_TB(){
	HIDE_MORE_LANGS_WPT_TB();
	var OB = GEBI('SL_wpt_canvas');
	if(OB)	OB.parentNode.removeChild(OB);
	doc.getElementsByTagName("body")[0].style="margin: 0px 0";
	CLOSE_OPTIONS();
	var s = document.getElementsByTagName("link");
	for(var i=0; i<s.length; i++){
		if(s[i].id == "SL_WPT"){
			document.head.removeChild(s[i]);
		}
	}    
}

function DELETE_WPT_TB(){
	HIDE_MORE_LANGS_WPT_TB();
	window.top.focus();
	var OB = window.top.document.getElementById('SL_wpt_canvas');
	if(OB)	OB.parentNode.removeChild(OB);
	window.top.document.getElementsByTagName("body")[0].style="margin: 0px 0";
	CLOSE_OPTIONS();
	chrome.runtime.sendMessage({greeting: "MM_ON:>"}, function(response) {});
	CUR_SHOW=0;
}


function HIDE_WPT_TB(){
  if(self == top ) {
    if(!GEBI("SL_wpt_hidden_logo")){
	HIDE_MORE_LANGS_WPT_TB();
	if(GEBI("SL_wpt_canvas")) GEBI("SL_wpt_canvas").style.display='none';
	var ext = FExtension.browserInject;
	var cssUrl = ext.getURL('/content/css/tb.css');
	doc.getElementsByTagName("head")[0].insertAdjacentHTML("beforeend","<link id='SL_WPT' rel='stylesheet' href='"+cssUrl+"' />");
	doc.getElementsByTagName("body")[0].style="margin: 0px 0";

	var LOGO = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_hidden_logo";
       	LOGO.setAttributeNode(id);


	var S = doc.createAttribute("style");
	S.value = "top:0px;right:0px;position:fixed;margin:0px;background: transparent url(" + FExtension.browserInject.getURL("/content/img/util/show.png") + ") no-repeat 100% 0";
        LOGO.setAttributeNode(S);

       	LOGO.classList.add("notranslate")
	doc.body.appendChild(LOGO);
    }	
  }       
  TranslatorIM.SL_wpt_MANUAL_MODE_ON = DOMAIN;
  chrome.runtime.sendMessage({greeting: "MM_ON:>"+TranslatorIM.SL_wpt_MANUAL_MODE_ON}, function(response) {});
  CREATE_ERROR_WINDOW();
}




function SHOW_WPT_TB(){  
 if(SL_getSHOW_HIDE_TB_TMP("SL_GWPT_Show_Hide_tmp")==1){ 
  if(self == top ) {
    if(!GEBI("SL_wpt_canvas")){

	chrome.runtime.sendMessage({greeting: "MM_OFF:>"}, function(response) {});
	doc.getElementsByTagName("body")[0].style="margin: 45px 0";

	var meta = document.createElement('meta');
	meta.httpEquiv = "viewport";
	meta.content = "width=device-width,initial-scale=1";
	doc.getElementsByTagName('head')[0].appendChild(meta);


	if(GEBI("SL_wpt_hidden_logo")) GEBI("SL_wpt_hidden_logo").style.display='none';
	var ext = FExtension.browserInject;
	var cssUrl = ext.getURL('/content/css/tb.css');
	doc.getElementsByTagName("head")[0].insertAdjacentHTML("beforeend","<link id='SL_WPT' rel='stylesheet' href='"+cssUrl+"' />");




	var TB_CANVAS = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_canvas";
        TB_CANVAS.setAttributeNode(id);

	var LOGO = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_logo";
	LOGO.style = "background: transparent url(" + FExtension.browserInject.getURL("/content/img/util/show.png") + ") no-repeat 100% 0";
       	LOGO.setAttributeNode(id);
	TB_CANVAS.appendChild(LOGO);


	var CP = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_cp";
       	CP.setAttributeNode(id);
	var TD = doc.createElement('td');
	var FBUT = doc.createElement('button');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_from";

       	FBUT.setAttributeNode(id);
	var T = doc.createAttribute("title");
	T.value = FExtension.element(SL_LOC,"extwptShowOriginal")+" ";
       	FBUT.setAttributeNode(T);

	TD.appendChild(FBUT);
	CP.appendChild(TD);



	var TD = doc.createElement('td');
	var SW = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_switch";
	SW.style = "background: white url(" + FExtension.browserInject.getURL("/content/img/util/switch-tb.png") + ") no-repeat 100% 0";

       	SW.setAttributeNode(id);
	TD.appendChild(SW);
	CP.appendChild(TD);

	var TD = doc.createElement('td');
	var S = doc.createAttribute("style");
	S.value = "white-space: nowrap";
       	TD.setAttributeNode(S);
	MENU = CUSTOM_LANGS(LANGSALL);

//	if(MENU.length>=SL_FAV_START){
	if(MENU.length>=1){

		var SL_FAV_LANGS_LONG = SL_ADD_LONG_NAMES(SL_FAV_LANGS_WPT);

       		if(SL_FAV_LANGS_LONG!=""){
			var favArr=SL_FAV_LANGS_LONG.split(","); 
			for(var J=0; J < favArr.length; J++){
			    var CURlang = favArr[J].split(":");
			    var OB_FAV = doc.createElement('button');
			    var CL = doc.createAttribute("class");
			    CL.value = "SL_wpt_to";
		  	    OB_FAV.setAttributeNode(CL)
			    var ID = doc.createAttribute("id");
			    ID.value = "SL_wpt_to_"+CURlang[0];
		  	    OB_FAV.setAttributeNode(ID)

			    var T = doc.createAttribute("title");
			    T.value = FExtension.element(SL_LOC,"extCMTransPageTo")+" " + CURlang[1];
			    OB_FAV.setAttributeNode(T);

			    if(J==0){
				    var ST = doc.createAttribute("style");
				    ST.value = "border-bottom:2px solid #1186BB";
			  	    OB_FAV.setAttributeNode(ST);
			    }
			    OB_FAV.appendChild(doc.createTextNode(CURlang[1]));
			    TD.appendChild(OB_FAV);

			}
		}
	} else {
	    var OB_FAV = doc.createElement('button');
	    var CL = doc.createAttribute("class");
	    CL.value = "SL_wpt_to";
  	    OB_FAV.setAttributeNode(CL);
	    var ST = doc.createAttribute("style");
	    ST.value = "border-bottom:2px solid #1186BB";
  	    OB_FAV.setAttributeNode(ST);
	    OB_FAV.appendChild(doc.createTextNode(SL_GetLongName(TranslatorIM.WPTdstlang)));
	    var id = doc.createAttribute("id");

	    id.value = "SL_wpt_to_"+TranslatorIM.WPTdstlang;
  	    OB_FAV.setAttributeNode(id);

	    TD.appendChild(OB_FAV);
	}
	CP.appendChild(TD);

	var TD = doc.createElement('td');
	var MORE = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_more";
	MORE.style = "background: white url(" + FExtension.browserInject.getURL("/content/img/util/hide.png") + ") no-repeat 100% 0";
       	MORE.setAttributeNode(id);
	TD.appendChild(MORE);
	CP.appendChild(TD);


	var TD = doc.createElement('td');
	var W = doc.createAttribute("width");
	W.value = "100%";

        TD.setAttributeNode(W);
	CP.appendChild(TD);
        TB_CANVAS.appendChild(CP);


	var TRBUTTON = doc.createElement('button');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_trbutton";
       	TRBUTTON.setAttributeNode(id);
	var T = doc.createAttribute("title");
	T.value = FExtension.element(SL_LOC,"extTrButton");
        TRBUTTON.setAttributeNode(T); 
        TRBUTTON.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extTrButton")));	
	var TY = doc.createAttribute("type");
	TY.value = "button";
        TRBUTTON.setAttributeNode(TY); 
	TB_CANVAS.appendChild(TRBUTTON);


	var OPT = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_options";
       	OPT.setAttributeNode(id);
	OPT.style = "background: white url(" + FExtension.browserInject.getURL("/content/img/util/dots-tb.png") + ") no-repeat 100% 0";
	var T = doc.createAttribute("title");
	T.value = FExtension.element(SL_LOC,"extOptions");
        OPT.setAttributeNode(T); 
	TB_CANVAS.appendChild(OPT);


	var HIDE = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_hide";
       	HIDE.setAttributeNode(id);
	var S = doc.createAttribute("style");
	S.value = "top:0px;right:40px;position:absolute; background: white url(" + FExtension.browserInject.getURL("/content/img/util/hide.png") + ") no-repeat 100% 0";
        HIDE.setAttributeNode(S);
	var T = doc.createAttribute("title");
	T.value = "Hide";
        HIDE.setAttributeNode(T); 
	TB_CANVAS.appendChild(HIDE);

	var CLEAR = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_close";
       	CLEAR.setAttributeNode(id);
	var S = doc.createAttribute("style");
	S.value = "top:0px;right:8px;position:absolute;background: white url(" + FExtension.browserInject.getURL("/content/img/util/close-tb.png") + ") no-repeat 100% 0";
        CLEAR.setAttributeNode(S); 
	var T = doc.createAttribute("title");
	T.value = FExtension.element(SL_LOC,"extClearTr");
        CLEAR.setAttributeNode(T); 
	TB_CANVAS.appendChild(CLEAR);

       	TB_CANVAS.classList.add("notranslate")
	doc.body.appendChild(TB_CANVAS);

	window.setTimeout(function() {
		GEBI("SL_wpt_from").innerText = DET_LANG;
	}, 50);

    }    
  }
 } else HIDE_WPT_TB();

 WPT_TB_resizeCanvas(); 
// if(SL_wptDp4!=1) {
	TranslatorIM.SL_wpt_MANUAL_MODE_ON = DOMAIN;
	chrome.runtime.sendMessage({greeting: "MM_ON:>"+TranslatorIM.SL_wpt_MANUAL_MODE_ON}, function(response) {});
// }
   CREATE_ERROR_WINDOW();
}


function SL_ADD_LONG_NAMES(codes){
	var OUT = "";
	var FAV = codes.split(",");
	for (var i=0; i<FAV.length; i++){
		var MARKER = 0;
		for (var j=0; j<MENU.length; j++){
			var M = MENU[j].split(":");
			if(FAV[i] == M[0]){
				OUT = OUT + M[0] + ":" + M[1];
				MARKER=1;
			}
		}
		if(MARKER==1){
			if(i <= FAV.length) OUT = OUT + ","
		}
	}
	if(OUT.slice(-1)==",") 	OUT = OUT.slice(0, OUT.length - 1);
	return OUT;	
}



function CUSTOM_LANGS(list){
	var OUT = "";
       	var list2 = SL_LNG_CUSTOM_LIST;
	if(list2=="all") OUT = list;
	else{
	    for(var i=0; i<list.length; i++){
     		var L1base = list[i].split(":");
	     	var L1short = list2.split(",");
		for(var j=0; j<L1short.length; j++){
		   if(L1base[0] == L1short[j]) OUT=OUT+L1short[j]+":"+L1base[1]+",";
		}
	    }
	    OUT = OUT.substring(0,OUT.length-1);		    
	    OUT = OUT.split(",");
	}
	return OUT;
}

function WPT_DETECTION(){
	if(DET_LANG==""){
	      	var rootTranslateNode = getRootNode();
      		analysisText = getAnalysisText(rootTranslateNode);

	     	if(analysisText){
			analysisText = analysisText.substring(0, 1000);

			i18n_LanguageDetect(analysisText);
			window.setTimeout(function() {
				var LN = SL_GetLongName(DETECTED);
				DET_LANG = LN;
			}, 250);
		} else {
			//IF A TEXT WAS NOT COLECTED
			DETECTED = "en";
			var LN = SL_GetLongName(DETECTED);
			DET_LANG = LN;
		}
	} else {
		var LN = SL_GetLongName(DETECTED);
			DET_LANG = LN;
	}

        FROM_LANGUAGE = DETECTED;
        // WRITE WPT HISTORY
	if(TranslatorIM.SL_wpt_MANUAL_MODE_ON == location.host){
	WPT_FLIP();

        SL_FAV_LANGS_WPT = uniqFAV(SL_FAV_LANGS_WPT);
	if(SL_FAV_LANGS_WPT.indexOf(",")!=-1){
		var Arr = TranslatorIM.SL_FAV_LANGS_WPT.split(",");
		TO_LANGUAGE = Arr[0];
	} else  TO_LANGUAGE = SL_FAV_LANGS_WPT; 

		var Pattern = SL_FAV_LANGS_WPT.split(",");
	        chrome.runtime.sendMessage({greeting: "WPT_HIST:>"+location.href+";"+DETECTED+"/"+Pattern[0]}, function(response) {});
	}

}

function WPT_FLIP(){
	var SRC = TranslatorIM.SL_WPTsrclang;
	var DST = TranslatorIM.SL_WPTdstlang;
      	if(TranslatorIM.WPTflip=="1" && SRC!="auto"){
		var Pattern = SL_FAV_LANGS_WPT.split(",");
		if(DETECTED == Pattern[0]){
		     if(!GEBI("SL_wpt_canvas")){
			SL_FAV_LANGS_WPT=SRC+","+SL_FAV_LANGS_WPT;
			SL_FAV_LANGS_WPT=uniqFAV(SL_FAV_LANGS_WPT);
			chrome.runtime.sendMessage({greeting: "WPT_lng:>"+SL_FAV_LANGS_WPT}, function(response) {}); 		
		     }
	        }
      	}
}


function SL_GetLongName(code){
	for (var i = 0; i < LANGSALL.length; i++){
		var templang = LANGSALL[i].split(":");
		if(code == templang[0]){ 
			return (templang[1]);
		}
	}
}

function SL_GetLangCode(name){
	for (var i = 0; i < LANGSALL.length; i++){
		var templang = LANGSALL[i].split(":");
		if(name == templang[1]){ 
			return (templang[0]);
		}
	}
}


function i18n_LanguageDetect(text){
//	text = text.substring(0,300);
        if(text.length>0){
		chrome.i18n.detectLanguage(text, function(result) {
			lng = result.languages[0].language;
			if(lng=="zh") lng = "zh-CN";
			if(lng=="zh-Hant") lng = "zh-TW";
			if(lng !=""){
				LANGSALL = FExtension.element(SL_LOC,'extLanguages').split(",");
				var cntr = 0;
       			        for (var i=0;i<LANGSALL.length;i++){
	        		   var templang=LANGSALL[i].split(":");
				   if(templang[0]==lng) cntr++;
				}
				if(cntr==0) lng="en";
			} else {
			       lng="en";
			}
			DETECTED = lng;
			FROM_LANGUAGE = lng;
		});
	}
}


function getAnalysisText (target) {

      var s = top.document.getElementsByTagName("meta");
      analysisText="";
      for (var i=0; i<s.length; i++){
		if(s[i].name=="description"){
			analysisText = s[i].content;
		}
      }

      if(analysisText != ""){
	      var tmp = analysisText.split(" ");
	      var newString = "";
	      if(tmp.length>3){
		      for (var i=3; i<tmp.length; i++){
			newString = newString + tmp[i] + " ";
		      }
		      analysisText = newString;
	      }
      }

      if(analysisText=="" || analysisText.length<20){
	      var iterator = getIterator(target), textnode, analysisText = "";
	      while ((textnode = iterator.nextNode())) {
	        if(textnode.data.length>1){
		        analysisText += textnode.data + ". ";
	        	if (analysisText.length >= 4096) {
		          break;
	        	}
		}
	      }
      }	
      return analysisText;
}

function getIterator(root) {
      var NodeFilter = window.NodeFilter,
          Node = window.Node,
          target = root || doc.body;

      return doc.createNodeIterator(target, NodeFilter.SHOW_TEXT, {
        acceptNode: function(node) {
          if (/^\s*$/.test(node.textContent) || node.parentNode.nodeType !== Node.ELEMENT_NODE || node.isChunked) {
            return NodeFilter.FILTER_REJECT;
          }
          while ((node = node.parentNode) !== target) {
            var tag = node ? node.nodeName : 'SCRIPT';
            if (invalidElements[tag]) {
              return NodeFilter.FILTER_REJECT;
            }
          }

          return NodeFilter.FILTER_ACCEPT;
        }
      }, false);
}

function getRootNode() {
      var host = window.location.host;
      switch (host) {
      case 'twitter.com':
        return doc.querySelector(".js-tweet-text");
        break;
      case 'github.com':
        return doc.querySelector(".announce");
        break;
      case 'bitbucket.org':
        return doc.querySelector("#wiki");
        break;
      }
      return null;
}

function MORE_LANGS_WPT_TB() {
   UPDATE_WPT_LANGUAGE_LIST();
   window.setTimeout(function() {	
        CLOSE_OPTIONS();
	HIDE_MORE_LANGS_WPT_TB();
	var BIGMENU = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_bigmenu";
       	BIGMENU.setAttributeNode(id);

	var SEARCH = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_search";
       	SEARCH.setAttributeNode(id);
       	BIGMENU.appendChild(SEARCH);


	var THELANGS = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_the_langs";
        THELANGS.setAttributeNode(id);

	MENU = CUSTOM_LANGS(LANGSALL);

	for(J=0; J < MENU.length; J++){
	    var CURlang = MENU[J].split(":");
	    var OB_FAV = doc.createElement('button');
	    var ID = doc.createAttribute("id");
	    ID.value = "SL_wpt_to_"+CURlang[0];
  	    OB_FAV.setAttributeNode(ID);
	    var CL = doc.createAttribute("class");
	    CL.value = "SL_wpt_to_more";
  	    OB_FAV.setAttributeNode(CL);

	    OB_FAV.appendChild(doc.createTextNode(CURlang[1]));
                SL_FAV_LANGS_WPT = uniqFAV(SL_FAV_LANGS_WPT);
		var SL_FAV_LANGS_LONG = SL_ADD_LONG_NAMES(SL_FAV_LANGS_WPT);
       		if(SL_FAV_LANGS_LONG!=""){
			var favArr=SL_FAV_LANGS_LONG.split(","); 
			if(MENU[J]==favArr[0]){
			    var ST = doc.createAttribute("style");
			    ST.value = "border-bottom:2px solid #1186BB";
		  	    OB_FAV.setAttributeNode(ST);
			    var Xarr=GEBI("SL_wpt_cp").getElementsByClassName("SL_wpt_to");

			    if(Xarr.length > 0){
			       Xarr[0].value = favArr[0];
			       var Xarr1 = favArr[0].split(":");
			       Xarr[0].innerText = Xarr1[1];
			       Xarr[0].id = "SL_wpt_to_"+Xarr1[0];
			    }

			}
		}
	    THELANGS.appendChild(OB_FAV);
	}

        BIGMENU.appendChild(THELANGS);
       	BIGMENU.classList.add("notranslate")
	doc.body.appendChild(BIGMENU);

       	BUILD_WPT_SEARCH();
	window.setTimeout(function() {
		GEBI("SL_wpt_more").id="SL_wpt_more_opened";
	}, 5);

	ACTIVATE_THEME(TranslatorIM.THEMEmode);
   }, 50);
}

function WPT_FASTTYPE_REBUILD(text){
	text = text.toLowerCase();
	var OB = GEBI('SL_wpt_the_langs');
	if(OB)	OB.parentNode.removeChild(OB);
	var THELANGS = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_the_langs";
        THELANGS.setAttributeNode(id);
	MENU = CUSTOM_LANGS(LANGSALL);

	for(J=0; J < MENU.length; J++){
	    var CURlang = MENU[J].split(":");
	    var OB_FAV = doc.createElement('button');
	    var ID = doc.createAttribute("id");
	    ID.value = "SL_wpt_to_"+CURlang[0];
  	    OB_FAV.setAttributeNode(ID);
	    var CL = doc.createAttribute("class");
	    CL.value = "SL_wpt_to_more";
  	    OB_FAV.setAttributeNode(CL);
  	    if(CURlang[1].toLowerCase().indexOf(text)!=-1){
	    	OB_FAV.appendChild(doc.createTextNode(CURlang[1]));
		var SL_FAV_LANGS_LONG = SL_ADD_LONG_NAMES(SL_FAV_LANGS_WPT);
       		if(SL_FAV_LANGS_LONG!=""){
			var favArr=SL_FAV_LANGS_LONG.split(","); 
			if(MENU[J]==favArr[0]){
			    var ST = doc.createAttribute("style");
			    ST.value = "border-bottom:2px solid #1186BB";
		  	    OB_FAV.setAttributeNode(ST);
			}
		}
	    	THELANGS.appendChild(OB_FAV);
	    }
	}
       	THELANGS.classList.add("notranslate")

	if(THELANGS.innerText=="") THELANGS.innerText = "No results";
	GEBI("SL_wpt_bigmenu").appendChild(THELANGS);
}
function WPT_FASTTYPE_REBUILD2(text){
        var DL = SL_GetLongName(DETECTED);

	text = text.toLowerCase();
	var OB = GEBI('SL_wpt_the_langs');
	if(OB)	OB.parentNode.removeChild(OB);
	var THELANGS = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_the_langs";
        THELANGS.setAttributeNode(id);
	MENU = CUSTOM_LANGS(LANGSALL);
	for(J=0; J < MENU.length; J++){
	    var CURlang = MENU[J].split(":");
	    var OB_FAV = doc.createElement('button');
	    var ID = doc.createAttribute("id");
	    ID.value = "SL_wpt_from_"+CURlang[0];
  	    OB_FAV.setAttributeNode(ID);
	    var CL = doc.createAttribute("class");
	    CL.value = "SL_wpt_to_more";
  	    OB_FAV.setAttributeNode(CL);
  	    if(CURlang[1].toLowerCase().indexOf(text)!=-1){
			if(CURlang[1]==DL){
			    var ST = doc.createAttribute("style");
			    ST.value = "border-bottom:2px solid #1186BB";
		  	    OB_FAV.setAttributeNode(ST);
			}

	    	OB_FAV.appendChild(doc.createTextNode(CURlang[1]));
	    	THELANGS.appendChild(OB_FAV);
	    }
	}
       	THELANGS.classList.add("notranslate")
	if(THELANGS.innerText=="") THELANGS.innerText = "No results";
	GEBI("SL_wpt_search2").appendChild(THELANGS);
}


function BUILD_WPT_SEARCH(){
	MENU = CUSTOM_LANGS(LANGSALL);
	if(MENU.length>=SL_FAV_START){
		var CONTAINER = doc.createElement('div');
		var id = doc.createAttribute("id");
		id.value = "SL_wpt_search_container";
       		CONTAINER.setAttributeNode(id);

		var LOOKUP = doc.createElement('div');
		var id = doc.createAttribute("id");
		id.value = "SL_wpt_LookUp";
	       	LOOKUP.setAttributeNode(id);
		LOOKUP.style="background: transparent url(" + FExtension.browserInject.getURL("/content/img/util/search.png") + ") no-repeat 100% 0";
	      	CONTAINER.appendChild(LOOKUP);



		var BOX = doc.createElement('input');
		var id = doc.createAttribute("id");
		id.value = "SL_wpt_search_box";
	       	BOX.setAttributeNode(id);
		var tp = doc.createAttribute("type");
		tp.value = "search";
       		BOX.setAttributeNode(tp);
		var VL = doc.createAttribute("placeholder");
		VL.value = FExtension.element(SL_LOC,"extSearch");
       		BOX.setAttributeNode(VL);
	      	CONTAINER.appendChild(BOX);

	
		var X = doc.createElement('div');
		var id = doc.createAttribute("id");
		id.value = "SL_wpt_close_search";
       		X.setAttributeNode(id);
       		X.style="background: transparent url(" + FExtension.browserInject.getURL("/content/img/util/close-tb.png") + ") no-repeat 100% 0";
		var T = doc.createAttribute("title");
		T.value = FExtension.element(SL_LOC,"extDelete");
	        X.setAttributeNode(T); 

	      	CONTAINER.appendChild(X);
       		GEBI("SL_wpt_search").appendChild(CONTAINER);
		GEBI("SL_wpt_search_box").focus();
	}
}

function BUILD_WPT_SEARCH2(){
	MENU = CUSTOM_LANGS(LANGSALL);
	if(MENU.length>=SL_FAV_START){
		var CONTAINER = doc.createElement('div');
		var id = doc.createAttribute("id");
		id.value = "SL_wpt_search_container2";
       		CONTAINER.setAttributeNode(id);

		var LOOKUP = doc.createElement('div');
		var id = doc.createAttribute("id");
		id.value = "SL_wpt_LookUp";
	       	LOOKUP.setAttributeNode(id);
		LOOKUP.style="background: transparent url(" + FExtension.browserInject.getURL("/content/img/util/search.png") + ") no-repeat 100% 0";
	      	CONTAINER.appendChild(LOOKUP);



		var BOX = doc.createElement('input');
		var id = doc.createAttribute("id");
		id.value = "SL_wpt_search_box2";
	       	BOX.setAttributeNode(id);
		var tp = doc.createAttribute("type");
		tp.value = "search";
       		BOX.setAttributeNode(tp);
		var VL = doc.createAttribute("placeholder");
		VL.value = FExtension.element(SL_LOC,"extSearch");
       		BOX.setAttributeNode(VL);
	      	CONTAINER.appendChild(BOX);

	
		var X = doc.createElement('div');
		var id = doc.createAttribute("id");
		id.value = "SL_wpt_close_search2";
       		X.setAttributeNode(id);
		X.style = "background: transparent url(" + FExtension.browserInject.getURL("/content/img/util/close-tb.png") + ") no-repeat 100% 0";
		var T = doc.createAttribute("title");
		T.value = FExtension.element(SL_LOC,"extDelete");
	        X.setAttributeNode(T); 

	      	CONTAINER.appendChild(X);
       		GEBI("SL_wpt_search2").appendChild(CONTAINER);
		GEBI("SL_wpt_search_box2").focus();
	}
}


function HIDE_MORE_LANGS_WPT_TB() {
	var OB = GEBI('SL_wpt_bigmenu');
	if(OB)	OB.parentNode.removeChild(OB);	
}

function uniqFAV(FAV) {
	var OUT = "";
	var array = FAV.split(",");
	const uniqueArray = array.filter((value, index, self) => {
		return self.indexOf(value) === index;
	});
	for(var i=0;i<SL_FAV_START; i++) {
	        if(uniqueArray[i]!="undefined") 		OUT = OUT + uniqueArray[i]+",";		
	}
 	return(OUT);
}


function SL_SAVE_FAVORITE_LANGUAGES(ln){
	window.setTimeout(function() {
		
	var OUT = "";
	var OUT2 = "";

	if(SL_FAV_LANGS_WPT.indexOf(ln)!=-1){
		SL_FAV_LANGS_WPT = SL_FAV_LANGS_WPT.replace(ln+",",""); 
		SL_FAV_LANGS_WPT = SL_FAV_LANGS_WPT.replace(ln,"");
	}
	OUT = ln + ",";	
	var ARR = SL_FAV_LANGS_WPT.split(",");
	for (var i = 0; i < ARR.length; i++){
	 	OUT = OUT + ARR[i]+",";
	}
	if(OUT.slice(-1)==",") 	OUT = OUT.slice(0, OUT.length - 1);
	var TMP = OUT.split(",");

	if(TMP.length > SL_FAV_START) {
		for (var j = 0; j < TMP.length-1; j++){
		 	OUT2 = OUT2 + TMP[j]+",";
		}		
		OUT = OUT2 
	}
	if(OUT.slice(-1)==",") 	OUT = OUT.slice(0, OUT.length - 1);
       	OUT = uniqFAV(OUT);

	chrome.runtime.sendMessage({greeting: "WPT_lng:>"+OUT}, function(response) {}); 		

	if(GEBI("SL_wpt_more_opened")) GEBI("SL_wpt_more_opened").id="SL_wpt_more"; 
	HIDE_MORE_LANGS_WPT_TB();

	//CLOSE_WPT_TB();
	chrome.runtime.sendMessage({greeting: "CLEAN_ALL:>"}, function(response) {});

	chrome.runtime.sendMessage({greeting: "RES_OR:>"}, function(response) {});
	window.setTimeout(function() {
		FExtension.browserInject.extensionSendMessage({greeting: 1}, function(response) {
			if(response && response.farewell){
				var theresponse = response.farewell.split("~");
				WPTdstlang=theresponse[20];
				var tmpl=theresponse[82];
				if(tmpl.indexOf(",")!=-1){
					var tmpl2 = tmpl.split(",");
					WPTdstlang = tmpl2[0];
				} else {
					WPTdstlang = tmpl;
				}

				TranslatorIM.WPTdstlang = WPTdstlang;
				SL_LOC=theresponse[22];
				SL_LNG_CUSTOM_LIST=theresponse[29];
				SL_FAV_LANGS_WPT=theresponse[82];
	//			TranslatorIM.WPTdstlang=theresponse[20];

				window.setTimeout(function() {
	        	                CLOSE_WPT_TB();
					INIT_WPT_TB(SL_LOC,1); 			
					RESTORE=0;
					FORCE_WP_TRANSLATION();
//					if(GLOBALEVENT.target.className!="SL_wpt_to")  MORE_LANGS_WPT_TB();
				}, 150);


			}
		});
	}, 50);	
	}, 250);	
}

function dynamicallyLoadScript(url) {
	var script = document.createElement("script");
	script.src = url;
	script.id = "SL_WPT";
	document.head.appendChild(script);
}

function OPEN_OPTIONS(){
   if(GEBI("SL_wpt_options_canvas"))	CLOSE_OPTIONS();
   else {
	CLOSE_OPTIONS();
	var SD = SL_DETECTsubDomain();
	if(GEBI("SL_wpt_more_opened")) GEBI("SL_wpt_more_opened").id="SL_wpt_more";
	HIDE_MORE_LANGS_WPT_TB();

	DOMAIN = window.location.host;

	if (DOMAIN.length >= 40) DOMAIN = DOMAIN.substring(0,40)+"...";
	FROM_LANGUAGE = DETECTED;
	var OPTIONS = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_options_canvas";
       	OPTIONS.setAttributeNode(id);
	var TTL1 = doc.createElement('div');
	var SPAN = doc.createElement('span');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options_TTL";
       	SPAN.setAttributeNode(CL);
        SPAN.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extwptDName")+":"));	
	TTL1.appendChild(SPAN);	

	var SPAN = doc.createElement('span');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options_TTL2";
       	SPAN.setAttributeNode(CL);
        SPAN.appendChild(doc.createTextNode(DOMAIN));	
        TTL1.appendChild(SPAN);	
        OPTIONS.appendChild(TTL1);	
	var BOX7 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	if(SL_wptDp2!=1) CL.value = "SL_BOX";
	else CL.value = "SL_BOX_ACTIVE";
       	BOX7.setAttributeNode(CL);
	var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_Dp2";
	BOX7.setAttributeNode(ID);
	var OP7 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options";
	OP7.setAttributeNode(CL);
	var ST = doc.createAttribute("style");
	ST.value = "margin-left:10px";
	OP7.setAttributeNode(ST);
        OP7.appendChild(BOX7);	
        if(SD == false){
		OP7.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extwptSDName")));	
		OPTIONS.appendChild(OP7);
	}

	var BOX2 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	if(SL_wptDp4==1) CL.value = "SL_BOX_ACTIVE";
	else CL.value = "SL_BOX";
       	BOX2.setAttributeNode(CL);
	var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_Dp3";
       	BOX2.setAttributeNode(ID);
	var OP2 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options";
       	OP2.setAttributeNode(CL);
        OP2.appendChild(BOX2);	
        OP2.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extwptAlwaysTranslateThisSite")));	
        OPTIONS.appendChild(OP2);	

	var BOX3 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	if(SL_wptDp4==0) CL.value = "SL_BOX_ACTIVE";
	else CL.value = "SL_BOX";
       	BOX3.setAttributeNode(CL);
	var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_Dp4";
       	BOX3.setAttributeNode(ID);
	var OP3 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options";
       	OP3.setAttributeNode(CL);
        OP3.appendChild(BOX3);	
        OP3.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extwptNeverTranslateThisSite")));	
        OPTIONS.appendChild(OP3);	

	var BOX4 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	if(SL_wptDp5!=1) CL.value = "SL_BOX";
	else CL.value = "SL_BOX_ACTIVE";
       	BOX4.setAttributeNode(CL);
	var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_Dp5";
       	BOX4.setAttributeNode(ID);
	var OP4 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options";
       	OP4.setAttributeNode(CL);
        OP4.appendChild(BOX4);
        OP4.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extwptDOrTip")));	
        OPTIONS.appendChild(OP4);	

	var BOX5 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	if(SL_wptDp6!=1) CL.value = "SL_BOX";
	else CL.value = "SL_BOX_ACTIVE";
       	BOX5.setAttributeNode(CL);
	var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_Dp6";
       	BOX5.setAttributeNode(ID);
	var OP5 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options";
       	OP5.setAttributeNode(CL);
        OP5.appendChild(BOX5);
        OP5.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extwptDTb")));	
        OPTIONS.appendChild(OP5);

	var HR = doc.createElement('div');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options_line";
       	HR.setAttributeNode(CL);
        OPTIONS.appendChild(HR);

	var TTL2 = doc.createElement('div');
	var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_line";
       	TTL2.setAttributeNode(ID);

	var TD = doc.createElement('td');
	var SPAN = doc.createElement('span');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options_TTL";
       	SPAN.setAttributeNode(CL);
        SPAN.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extwptLanguage")+":"));	
	TD.appendChild(SPAN);
	TTL2.appendChild(TD);

	var TD = doc.createElement('td');
	var SPAN = doc.createElement('span');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options_TTL2";
       	SPAN.setAttributeNode(CL);
        SPAN.appendChild(doc.createTextNode(SL_GetLongName(FROM_LANGUAGE).toUpperCase()));	
        TTL2.appendChild(SPAN);	
	var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_lang_menu";

       	SPAN.setAttributeNode(ID);
	TD.appendChild(SPAN);
	TTL2.appendChild(TD);

	var TD = doc.createElement('td');
	var MORE = doc.createElement('div');
	var id = doc.createAttribute("id");
	id.value = "SL_wpt_FROM_LANG";
       	MORE.setAttributeNode(id);
	MORE.style="background: transparent url(" + FExtension.browserInject.getURL("/content/img/util/hide.png") + ") no-repeat 100% 0";
	TD.appendChild(MORE);
	TTL2.appendChild(TD);
        OPTIONS.appendChild(TTL2);	
	var BOX1 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	if(SL_wptLp2!=1) CL.value = "SL_BOX";
	else CL.value = "SL_BOX_ACTIVE";
       	BOX1.setAttributeNode(CL);
	var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_Lp1";
       	BOX1.setAttributeNode(ID);
	var OP1 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options";
       	OP1.setAttributeNode(CL);
        OP1.appendChild(BOX1);
        OP1.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extwptAlwaysTranslateThisLanguage")));	
        OPTIONS.appendChild(OP1);	


	var BOX3 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	if(SL_wptLp3!=1) CL.value = "SL_BOX";
	else CL.value = "SL_BOX_ACTIVE";
       	BOX3.setAttributeNode(CL);
	var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_Lp3";
       	BOX3.setAttributeNode(ID);
	var OP3 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options";
       	OP3.setAttributeNode(CL);
        OP3.appendChild(BOX3);
        OP3.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extwptDOrTip")));	
        OPTIONS.appendChild(OP3);	

	var BOX4 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	if(SL_wptLp4!=1) CL.value = "SL_BOX";
	else CL.value = "SL_BOX_ACTIVE";
       	BOX4.setAttributeNode(CL);
	var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_Lp4";
       	BOX4.setAttributeNode(ID);
	var OP4 = doc.createElement('div');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options";
       	OP4.setAttributeNode(CL);
        OP4.appendChild(BOX4);
        OP4.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extwptLTb")));	
        OPTIONS.appendChild(OP4);	


	var HR = doc.createElement('div');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options_line";
       	HR.setAttributeNode(CL);
        OPTIONS.appendChild(HR);	


	var TTL3 = doc.createElement('span');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options_LNK";
       	TTL3.setAttributeNode(CL);
	var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_more_options";
       	TTL3.setAttributeNode(ID);


        TTL3.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extwptMoreOptions")));	
        OPTIONS.appendChild(TTL3);	

	var HR = doc.createElement('div');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options_line";
       	HR.setAttributeNode(CL);
        OPTIONS.appendChild(HR);	

	var TTL4 = doc.createElement('span');
	var CL = doc.createAttribute("class");
	CL.value = "SL_wpt_options_LNK";
       	TTL4.setAttributeNode(CL);
	var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_donate";
       	TTL4.setAttributeNode(ID);
        TTL4.appendChild(doc.createTextNode(FExtension.element(SL_LOC,"extContribution_ttl")));	
        OPTIONS.appendChild(TTL4);	

       	OPTIONS.classList.add("notranslate")
	doc.body.appendChild(OPTIONS);
	ACTIVATE_THEME(TranslatorIM.THEMEmode);
   }	
}

function CLOSE_OPTIONS(){
	var OB = GEBI('SL_wpt_options_canvas');
	if(OB)	OB.parentNode.removeChild(OB);		
	CLOSE_L_MENU();
}
	

function CLOSE_L_MENU(){
	if(GEBI("SL_wpt_FROM_LANG")) GEBI("SL_wpt_FROM_LANG").style.transform="scaleY(-1)";
	var OB = GEBI('SL_wpt_lang_menu_canvas');
	if(OB)	OB.parentNode.removeChild(OB);	
}



function ACTIVATE_THEME(st){
 	if(st==1){
		var bg="#191919";
		var clr="#BF7D44";
		var clr_deact="#BDBDBD";
		if(GEBI("SL_wpt_canvas")) GEBI("SL_wpt_canvas").style.filter=SL_DARK;
		if(GEBI("SL_wpt_bigmenu")) GEBI("SL_wpt_bigmenu").style.filter=SL_DARK;
		if(GEBI("SL_wpt_options_canvas")) GEBI("SL_wpt_options_canvas").style.filter=SL_DARK;
		if(GEBI("SL_wpt_lang_menu_canvas")) GEBI("SL_wpt_lang_menu_canvas").style.filter=SL_DARK;
	}
}

function DONATE(){
       window.location="https://imtranslator.net"+_CGI+"&a=0";
}

function MAIN_OPTIONS(){
	var st = "wpt";
	chrome.runtime.sendMessage({greeting: "OPEN_O:>"+st}, function(response) {});
}


function SL_DETECTsubDomain() {
		var url = doc.location.host;
		// IF THERE, REMOVE WHITE SPACE FROM BOTH ENDS
		url = url.replace(new RegExp(/^\s+/),""); // START
		url = url.replace(new RegExp(/\s+$/),""); // END
 
		// IF FOUND, CONVERT BACK SLASHES TO FORWARD SLASHES
		url = url.replace(new RegExp(/\\/g),"/");
 
		// IF THERE, REMOVES 'http://', 'https://' or 'ftp://' FROM THE START
		url = url.replace(new RegExp(/^http\:\/\/|^https\:\/\/|^ftp\:\/\//i),"");
 
		// IF THERE, REMOVES 'www.' FROM THE START OF THE STRING
		url = url.replace(new RegExp(/^www\./i),"");
 
		// REMOVE COMPLETE STRING FROM FIRST FORWARD SLASH ON
		url = url.replace(new RegExp(/\/(.*)/),"");
 
		// REMOVES '.??.??' OR '.???.??' FROM END - e.g. '.CO.UK', '.COM.AU'
		if (url.match(new RegExp(/\.[a-z]{2,3}\.[a-z]{2}$/i))) {
		      url = url.replace(new RegExp(/\.[a-z]{2,3}\.[a-z]{2}$/i),"");
 
		// REMOVES '.??' or '.???' or '.????' FROM END - e.g. '.US', '.COM', '.INFO'
		} else if (url.match(new RegExp(/\.[a-z]{2,4}$/i))) {
		      url = url.replace(new RegExp(/\.[a-z]{2,4}$/i),"");
		}
 
		// CHECK TO SEE IF THERE IS A DOT '.' LEFT IN THE STRING
		var subDomain = (url.match(new RegExp(/\./g))) ? true : false;
 
		return(subDomain);
 
}

function WPT_SHOW_MORE_LANGS(e){
        var DL = SL_GetLongName(DETECTED);
	var OB = GEBI('SL_wpt_lang_menu_canvas');
	if(!OB){	
		var SL_OPT_LANG_MENU = doc.createElement("div");
		var wpt_lang_menu = doc.createAttribute("id");
		wpt_lang_menu.value = "SL_wpt_lang_menu_canvas";
	        SL_OPT_LANG_MENU.setAttributeNode(wpt_lang_menu);
		var SL_OPT_LANG_MENUclass = doc.createAttribute("class");
		SL_OPT_LANG_MENUclass.value = "SL_OPT_LANG_MENU";
        	SL_OPT_LANG_MENU.setAttributeNode(SL_OPT_LANG_MENUclass);

		var SL_OPT_LANG_MENUstyle = doc.createAttribute("style");
		SL_OPT_LANG_MENUstyle.value = "top:"+(e.clientY+10)+"px";
	        SL_OPT_LANG_MENU.setAttributeNode(SL_OPT_LANG_MENUstyle);


		var WPT_SEARCH = doc.createElement("div");
		var wpt_lang_menu = doc.createAttribute("id");
		wpt_lang_menu.value = "SL_wpt_search2";
	        WPT_SEARCH.setAttributeNode(wpt_lang_menu);
	    	SL_OPT_LANG_MENU.appendChild(WPT_SEARCH);


		var WPT_LBOX = doc.createElement("div");
		var wpt_lang_menu = doc.createAttribute("id");
		wpt_lang_menu.value = "SL_wpt_the_langs";
	        WPT_LBOX.setAttributeNode(wpt_lang_menu);



		MENU = CUSTOM_LANGS(LANGSALL);

		for(J=0; J < MENU.length; J++){
		    var CURlang = MENU[J].split(":");
		    var OB_FAV = doc.createElement('button');
		    var ID = doc.createAttribute("id");
		    ID.value = "SL_wpt_from_"+CURlang[0];
  		    OB_FAV.setAttributeNode(ID);
		    var CL = doc.createAttribute("class");
		    CL.value = "SL_wpt_to_more";
	  	    OB_FAV.setAttributeNode(CL);

		    	OB_FAV.appendChild(doc.createTextNode(CURlang[1]));
			if(CURlang[1]==DL){
			    var ST = doc.createAttribute("style");
			    ST.value = "border-bottom:2px solid #1186BB";
		  	    OB_FAV.setAttributeNode(ST);
			}

		    	WPT_LBOX.appendChild(OB_FAV);
		}

	        SL_OPT_LANG_MENU.appendChild(WPT_LBOX);	
       		SL_OPT_LANG_MENU.classList.add("notranslate")

		doc.body.appendChild(SL_OPT_LANG_MENU);
		ACTIVATE_THEME(TranslatorIM.THEMEmode);        
		BUILD_WPT_SEARCH2();
		GEBI("SL_wpt_FROM_LANG").style.transform="scaleY(1)";
	} else 	{
		GEBI("SL_wpt_FROM_LANG").style.transform="scaleY(-1)";
		OB.parentNode.removeChild(OB);	
	}
}



function IfClickIsInside(e,ob){
	var st = 0;
        const DIV_OB = GEBI(ob);
	if(DIV_OB){
		var divRect = DIV_OB.getBoundingClientRect();
		if (e.clientX >= (divRect.left-20) && e.clientX <= divRect.right && e.clientY >= divRect.top && e.clientY <= divRect.bottom) st=1;
	}
	return(st);
}


function FORCE_WP_TRANSLATION(){
	WPT_PREVIOUS="";
	SHOW_WPT_TB();
//	TranslatorIM.ACTIVATE_WPT(0, top.location.host);
	WPT_TRANSLATOR();
}

function BUTTON_WP_TRANSLATION(){
	GEBI("SL_wpt_from").style="";
	SELECT_TO(doc.getElementsByClassName("SL_wpt_to")[0].id);
	WPT_PREVIOUS="";
	SHOW_WPT_TB();
	WPT_TRANSLATOR();
}

function LANGUAGE_SET_MANAGER(lng){
	chrome.runtime.sendMessage({greeting: "WPT_GET_L:>"+lng}, function(response) {});
	chrome.runtime.onMessage.addListener(function (response, sendResponse) {
             if(response && response.langset){
		var LSET = response.langset;
		if(LSET == "#"){
			GEBI("SL_wpt_Lp1").className="SL_BOX";
			GEBI("SL_wpt_Lp3").className="SL_BOX";
			GEBI("SL_wpt_Lp4").className="SL_BOX";
			SL_wptLp3 = 0; // Show original
			SL_wptLp4 = 0; // Show TB
		} else {
		 	var ARR = LSET.split(",");
			if(ARR[1] == 0)	{
				GEBI("SL_wpt_Lp1").className="SL_BOX";
				SL_wptLp3 = 0;
			} else {  
				GEBI("SL_wpt_Lp1").className="SL_BOX_ACTIVE";
				SL_wptLp3 = 1;
			}
			if(ARR[2] == 0)	{
				GEBI("SL_wpt_Lp3").className="SL_BOX";
				SL_wptLp3 = 0;
			} else {  
				GEBI("SL_wpt_Lp3").className="SL_BOX_ACTIVE";
				SL_wptLp3 = 1;
			}
			if(ARR[3] == 0)	{
				GEBI("SL_wpt_Lp4").className="SL_BOX";
				SL_wptLp4 = 0;
			} else { 
				GEBI("SL_wpt_Lp4").className="SL_BOX_ACTIVE";
				SL_wptLp4 = 1;
			}
		}
	     }
	});

}

function SL_setSHOW_HIDE_TB_TMP(cname, cvalue, exdays) {
	    var s = ""; 
	    if(String(document.location).indexOf('https:')!=-1) s=" secure;"; 
	    document.cookie = cname + "=" + cvalue + "; expires=0; path=/;"+s;

}


function SL_getSHOW_HIDE_TB_TMP(cname) {
	    var name = cname + "=";
	    var ca = document.cookie.split(';');
	    for(var i=0; i<ca.length; i++) {
	        var c = ca[i];
	        while (c.charAt(0)==' ') c = c.substring(1);
	        if (c.indexOf(name) == 0){
		 var resp = c.substring(name.length,c.length);
		 return resp;
		}
	    }
	return SL_wptDp6;			
}

function GEBI(ob){
	return(doc.getElementById(ob));
}

function CREATE_ERROR_WINDOW(){
	var OB = GEBI('SL_wpt_container');
	if(OB)	OB.parentNode.removeChild(OB);

        var OB_CONTAINER = doc.createElement('div');
        var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_container";
  	OB_CONTAINER.setAttributeNode(ID);
        var CL = doc.createAttribute("class");
	CL.value = "notranslate";
  	OB_CONTAINER.setAttributeNode(CL);

        var OB_ERROR = doc.createElement('div');
        var ID = doc.createAttribute("id");
	ID.value = "SL_wpt_error";
  	OB_ERROR.setAttributeNode(ID);

        OB_CONTAINER.appendChild(OB_ERROR);	
	doc.body.appendChild(OB_CONTAINER);
	var ARR = SL_FAV_LANGS_WPT.split(",");
	var LANG = ARR[0];
	var SHOW_STATUS = FIND_LNG(LANG);
	var ERROR="";
	for(var i=0; i<LANGSALL.length; i++){
		var tmp = LANGSALL[i].split(":");
		if(LANG == tmp[0]) LANG = tmp[1];
	}
        var ERROR = LANG + " : " + FExtension.element(SL_LOC,"extnotsupported");
        GEBI("SL_wpt_error").innerHTML= DOMPurify.sanitize(ERROR);	
	if(SHOW_STATUS == 0) GEBI("SL_wpt_container").style.display="block";
	else GEBI("SL_wpt_container").style.display="none";
}

function FIND_LNG(LANG){
	var OUT = 0;
	var tmp = LISTofLANGsets[0].split(",");
	for(var i=0; i<tmp.length; i++){
		if(tmp[i] == LANG) OUT = 1;
	}
	return(OUT);
}
