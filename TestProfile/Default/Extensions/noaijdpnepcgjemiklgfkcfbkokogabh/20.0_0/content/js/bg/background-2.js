try{
	self.importScripts('../../../content/js/common/FExtension.js');
	self.importScripts('../../../content/browser/js/FBrowser.js'); 
	self.importScripts('../../../content/browser/chrome/FBrowserChrome.js'); 
	self.importScripts('../../../content/js/common/FStorage.js'); 
} catch (ex){}
var NEW_SESSION="";
var SLIDL="";
var ALL_VOICES;
var winWidth = 480 ;
var winHeight = 650 ;
var GLOB_CNTR = 2;

var PLATFORM = "Chrome";
var EXPORT_EXT = " SL";
var GLOB_PREF = "SL";


//var PLATFORM = "Opera";
//var EXPORT_EXT = " SL";
//var GLOB_PREF = "SL";



//for GT only
//var PLATFORM = "Opera";
//var EXPORT_EXT = " GT";
//var GLOB_PREF = "SLG";



//var SL_GEO = new Array ("com","es","de","it","fr","rs","pn","ps","sn","so");
var SL_GEO = new Array ("com");
var DET = 0;
// 0 - G
// 1 - SL
var _TP = "chr-ImTranslator"
var _FOLDER = "extensions";
var _CGI = "/"+_FOLDER+"/?tp="+_TP;

var reservedHK = "_HK_bb1,_HK_bb2,_HK_btn,_HK_gt1,_HK_gt2,_HK_it1,_HK_it2,_HK_opt,_HK_wpt1,_HK_wpt2,_change_lang_HK_it,_HK_SO_wpt,_HK_CT_wpt";
var SL_TTS = "en,es,ru,de,pt,fr,it,ko,ja,zh-CN,zh-TW,en-gb,fr-CA,lzh,yue,pt-PT";             
var G_TTS = "ar,cs,da,nl,fi,el,hi,hu,no,pl,sk,sv,th,tr,la,bn,id,km,uk,vi";
    G_TTS = G_TTS+","+SL_TTS;

var LISTofPRpairsDefault=",af,ak,am,ar,as,ay,az,ba,be,bg,bho,bm,bn,bo,bs,ca,ceb,ckb,co,cs,cv,cy,da,de,doi,dsb,dv,ee,el,emj,en,en-gb,eo,es,et,eu,fa,fi,fj,fo,fr,fr-CA,fy,ga,gd,gl,gn,gom,gu,ha,haw,hi,hmn,hr,hsb,ht,hu,hy,id,ig,ikt,ilo,is,it,iu,iu-Latn,iw,ja,jw,ka,kazlat,kk,km,kn,ko,kri,ku,ky,la,lb,lg,ln,lo,lt,lug,lus,lv,lzh,mai,mg,mhr,mi,mk,ml,mn,mni-Mtei,mn-Mong,mr,mrj,ms,mt,my,ne,nl,no,nso,ny,nya,om,or,otq,pa,pap,pl,prs,ps,pt,pt-PT,qu,ro,ru,run,rw,sa,sah,sd,si,sk,sl,sm,sn,so,sq,sr,sr-Latn,srsl,st,su,sv,sw,ta,te,tg,th,ti,tk,tl,tlh-Latn,tlsl,tn,to,tr,ts,tt,ty,udm,ug,uk,ur,uz,uzbcyr,vi,xh,yi,yo,yua,yue,zh-CN,zh-TW,zu";
var LISTofPR = new Array ("Google","Microsoft","Translator","Yandex");
var LISTofLANGsets = new Array (",af,ak,am,ar,as,ay,az,be,bg,bho,bm,bn,bs,ca,ceb,ckb,co,cs,cy,da,de,doi,dv,ee,el,en,eo,es,et,eu,fa,fi,fr,fr-CA,fy,ga,gd,gl,gn,gom,gu,ha,haw,hi,hmn,hr,ht,hu,hy,id,ig,ilo,is,it,iw,ja,jw,ka,kk,km,kn,ko,kri,ku,ky,la,lb,lg,ln,lo,lt,lus,lv,mai,mg,mi,mk,ml,mn,mni-Mtei,mr,ms,mt,my,ne,nl,no,nso,ny,om,or,pa,pl,ps,pt,pt-PT,qu,ro,ru,rw,sa,sd,si,sk,sl,sm,sn,so,sq,sr,srsl,st,su,sv,sw,ta,te,tg,th,ti,tk,tl,tlsl,tr,ts,tt,ug,uk,ur,uz,vi,xh,yi,yo,zh-CN,zh-TW,zu",",af,am,ar,as,az,ba,bg,bho,bn,bo,bs,ca,ckb,cs,cy,da,de,dsb,dv,el,en,en-gb,es,et,eu,fa,fi,fj,fo,fr,fr-CA,ga,gl,gom,gu,ha,hi,hmn,hr,hsb,ht,hu,hy,id,ig,ikt,is,it,iu,iu-Latn,iw,ja,ka,kk,km,kn,ko,ku,ky,ln,lo,lt,lug,lv,lzh,mai,mg,mi,mk,ml,mn,mn-Mong,mr,ms,mt,my,ne,nl,no,nso,nya,or,otq,pa,pl,prs,ps,pt,pt-PT,ro,ru,run,rw,sd,si,sk,sl,sm,sn,so,sq,sr,sr-Latn,srsl,st,sv,sw,ta,te,th,ti,tk,tl,tlh-Latn,tlsl,tn,to,tr,tt,ty,ug,uk,ur,uz,vi,xh,yo,yua,yue,zh-CN,zh-TW,zu",",af,am,ar,az,ba,be,bg,bn,bs,ca,ceb,cs,cv,cy,da,de,el,emj,en,eo,es,et,eu,fa,fi,fr,ga,gd,gl,gu,hi,hr,ht,hu,hy,id,is,it,iw,ja,jv,ka,kazlat,kk,km,kn,ko,ky,la,lb,lo,lt,lv,mg,mhr,mi,mk,ml,mn,mr,mrj,ms,mt,my,ne,nl,no,pa,pap,pl,pt,ro,ru,sah,si,sk,sl,sq,sr,sr-Latn,srsl,su,sv,sw,ta,te,tg,th,tl,tlsl,tr,tt,udm,uk,ur,uz,uzbcyr,vi,xh,yi,zh-CN,zu",",af,am,ar,az,ba,be,bg,bn,bs,ca,ceb,cs,cv,cy,da,de,el,emj,en,eo,es,et,eu,fa,fi,fr,ga,gd,gl,gu,hi,hr,ht,hu,hy,id,is,it,iw,ja,jv,ka,kazlat,kk,km,kn,ko,ky,la,lb,lo,lt,lv,mg,mhr,mi,mk,ml,mn,mr,mrj,ms,mt,my,ne,nl,no,pa,pap,pl,pt,ro,ru,sah,si,sk,sl,sq,sr,sr-Latn,srsl,su,sv,sw,ta,te,tg,th,tl,tlsl,tr,tt,udm,uk,ur,uz,uzbcyr,vi,xh,yi,zh-CN,zu");

                                  
var LISTofPRpairs = new Array ();

var PACK_PARAMS = new Array();

for (var SL_I = 0 ; SL_I < LISTofPR.length; SL_I++){
    switch(LISTofPR[SL_I]){
	case "Google": LISTofPRpairs[SL_I]=LISTofLANGsets[0];break;
	case "Microsoft": LISTofPRpairs[SL_I]=LISTofLANGsets[1];break;
	case "Translator": LISTofPRpairs[SL_I]=LISTofLANGsets[2];break;
	case "Yandex": LISTofPRpairs[SL_I]=LISTofLANGsets[3];break;
    }	
}

var DO_NOT_TRUST_WORD = "be,bg,mk,sr,kk,mn,tg";
var DO_NOT_TRUST_TEXT = "zh";

var ImTranslator_theurl = "https://imtranslator.net/";
    

var PRESET="";
var GDATA="";
var PACK_PARAMS = new Array();
var CACHE_PACK_PARAMS = new Array();
clearInterval(SLIDL);

chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse){

	if(request.msg && request.msg.indexOf("SET:>") !=-1) {
            var RESP = request.msg.replace("SET:>","");
	    if(RESP != "") {
		var ARR = RESP.split("#");
		ImTranslatorBG.set(ARR[0],ARR[1]);
	    }	
	}

	if(request.msg && request.msg.indexOf("WS:>") !=-1) {
		ImTranslatorBG.SL_WorkingSet();
	}

	if(request.msg && request.msg.indexOf("RCM:>") !=-1) {
		ImTranslatorBG.PREPARE_RCM_CONTENT();
		ImTranslatorBG.SL_WorkingSet();
	}


	if(request.msg && request.msg.indexOf("RCM_CHANGE:>") !=-1) {
            var RESP = request.msg.replace("RCM_CHANGE:>","");
	    if(RESP != "") {
		ImTranslatorBG.SL_callbackRequestToChangeRightClickMenu(RESP);
	    }	
	}

	if(request.msg && request.msg.indexOf("UPDATE_HISTORY:>") !=-1) {
            var RESP = request.msg.replace("UPDATE_HISTORY:>","");
	    if(RESP != "") {
		ImTranslatorBG.updateHistory(RESP);
	    }	
	}

	if(request.msg && request.msg.indexOf("DEF:>") !=-1) {
		EXTENSION_DEFAULTS();
	}

                                                  
    }
);

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if(request.msg && request.msg.indexOf("GET_ALL:>") !=-1) {
	
	if(CACHE_PACK_PARAMS.length==0){
 		ImTranslatorBG.GET_STORE_DATA();
		setTimeout(function(){
			sendResponse({data: CACHE_PACK_PARAMS});
		}, 100);
	} else {
		sendResponse({data: CACHE_PACK_PARAMS});
	}
  }

  if(request.msg && request.msg.indexOf("SET_CACHE:>") !=-1) {
	
	ImTranslatorBG.GET_STORE_DATA();
  }

  if(request.msg && request.msg.indexOf("GET_PP:>") !=-1) {
	sendResponse({data: PACK_PARAMS});
  }

  if(request.msg && request.msg.indexOf("GET_ALL_VOICES:>") !=-1) {
        if(ImTranslatorBG.get("SL_GVoices")=="1") ALL_VOICES=G_TTS;
        else ALL_VOICES=SL_TTS;
	sendResponse({data: ALL_VOICES});
  }

  if(request.msg && request.msg.indexOf("PLANSHET_RESET:>") !=-1) {
	ImTranslatorBG.SL_Planshet_Reset();
  }

  
});


ImTranslatorBG = {
	MSKEY: "",
	AKEY: "",
	DO_ONCE_ONLY: 0,
	IT_CLEAR: 0,
	CACHE: "",
        BTNstatus: 0,
    	BaseGTK:  "451769.3009291968",
        GFROZEN: 60,
	INTERNAL_ONLY: 0,
	YSID: "",
	YSIDold: "",
	YSIDstatus: false,
	/////////////
	audioElement: "",
	audioStatus: "on",
	ADVkey: 1, 
	// 1 - show for all
	// 2 - show for new
	// 3 - show for old
	// 4 - do not show for all

	/////////////
	NEW_GDETECT: "",
	NEW_GTRANSLATE: "",
	DIC_TRIGGER: 0,
        tempresp: "",
	seltext: null,
	myWindow: "",
	NORUN: 0,
	ImTranslator_URL: "https://translate.imtranslator.net/1/",
	TextTransLimit: 8000,
	ImTranslator_Wconst: 550,
	ImTranslator_Hconst: 550,
        THE_URL: "",
        URL: "",
	first_run: false,
	the_ID0: null,
	the_ID1: null,
	the_ID2: null,
	the_ID3: null,
	the_ID4: null,
	the_ID5: null,
	the_ID6: null,
	the_ID7: null,
	the_ID8: null,
	the_ID9: null,
        ALLvoices: "",
        BUBBLE_RESP: "",
        BUBBLE_DET: "",
        INLINE_RESP: "",
	SLIDL: "",
	TRIGGER: 0,
	IT_DetLang: "",
        TMP_HIST_SEG: "",
        TMP_IT_SEG: "",
	PUSH_TXT: "",
        
	set : function(key, value){              // Storing key function

if(key == "PLD_LOC"){chrome.storage.local.set({ 'PLD_LOC': value });}
if(key == "PLD_DPROV"){chrome.storage.local.set({ 'PLD_DPROV': value });}
if(key == "BL_D_PROV"){chrome.storage.local.set({ 'BL_D_PROV': value });}
if(key == "PLT_OLD_TS_TR"){chrome.storage.local.set({ 'PLT_OLD_TS_TR': value });}
if(key == "SL_YHIST"){chrome.storage.local.set({ 'SL_YHIST': value });}
if(key == "SL_global_lng_it"){chrome.storage.local.set({ 'SL_global_lng_it': value });}
if(key == "SL_other_wpt"){chrome.storage.local.set({ 'SL_other_wpt': value });}
if(key == "SL_langDst_bbl"){chrome.storage.local.set({ 'SL_langDst_bbl': value });}
if(key == "SL_GWPTHist"){chrome.storage.local.set({ 'SL_GWPTHist': value });}
if(key == "SL_YKEY"){chrome.storage.local.set({ 'SL_YKEY': value });}
if(key == "MoveBBLX"){chrome.storage.local.set({ 'MoveBBLX': value });}
if(key == "PLT_TR_FIRSTRUN"){chrome.storage.local.set({ 'PLT_TR_FIRSTRUN': value });}
if(key == "SL_langDst_name_it"){chrome.storage.local.set({ 'SL_langDst_name_it': value });}
if(key == "PLT_LOC"){chrome.storage.local.set({ 'PLT_LOC': value });}
if(key == "SL_HKset"){chrome.storage.local.set({ 'SL_HKset': value });}
if(key == "SL_GVoices"){chrome.storage.local.set({ 'SL_GVoices': value });}
if(key == "PLD_TTSvolume"){chrome.storage.local.set({ 'PLD_TTSvolume': value });}
if(key == "SL_BBL_X"){chrome.storage.local.set({ 'SL_BBL_X': value });}
if(key == "SL_change_lang_HK_it"){chrome.storage.local.set({ 'SL_change_lang_HK_it': value });}
if(key == "SL_no_detect_it"){chrome.storage.local.set({ 'SL_no_detect_it': value });}
if(key == "SL_HK_CTbox_wpt"){chrome.storage.local.set({ 'SL_HK_CTbox_wpt': value });}
if(key == "SL_DOM"){chrome.storage.local.set({ 'SL_DOM': value });}
if(key == "SL_HK_wptbox1"){chrome.storage.local.set({ 'SL_HK_wptbox1': value });}
if(key == "SL_pin_bbl2"){chrome.storage.local.set({ 'SL_pin_bbl2': value });}
if(key == "SL_HK_btn"){chrome.storage.local.set({ 'SL_HK_btn': value });}
if(key == "SL_Delay"){chrome.storage.local.set({ 'SL_Delay': value });}
if(key == "SL_wptGlobTb"){chrome.storage.local.set({ 'SL_wptGlobTb': value });}
if(key == "SL_SLVoices"){chrome.storage.local.set({ 'SL_SLVoices': value });}
if(key == "TTSvolume"){chrome.storage.local.set({ 'TTSvolume': value });}
if(key == "SL_ENABLE"){chrome.storage.local.set({ 'SL_ENABLE': value });}
if(key == "SL_HK_optbox"){chrome.storage.local.set({ 'SL_HK_optbox': value });}
if(key == "PLT_PROV"){chrome.storage.local.set({ 'PLT_PROV': value });}
if(key == "SL_DBL_bbl"){chrome.storage.local.set({ 'SL_DBL_bbl': value });}
if(key == "SL_HK_btnbox"){chrome.storage.local.set({ 'SL_HK_btnbox': value });}
if(key == "SL_other_it"){chrome.storage.local.set({ 'SL_other_it': value });}
if(key == "WPTflip"){chrome.storage.local.set({ 'WPTflip': value });}
if(key == "SL_CM2"){chrome.storage.local.set({ 'SL_CM2': value });}
if(key == "SL_Fontsize_bbl"){chrome.storage.local.set({ 'SL_Fontsize_bbl': value });}
if(key == "SL_HK_wptbox2"){chrome.storage.local.set({ 'SL_HK_wptbox2': value });}
if(key == "SL_langSrc"){chrome.storage.local.set({ 'SL_langSrc': value });}
if(key == "SL_inject_before"){chrome.storage.local.set({ 'SL_inject_before': value });}
if(key == "SL_FAV_LANGS_WPT"){chrome.storage.local.set({ 'SL_FAV_LANGS_WPT': value });}
if(key == "SL_GotIt"){chrome.storage.local.set({ 'SL_GotIt': value });}
if(key == "SL_HK_SO_wpt"){chrome.storage.local.set({ 'SL_HK_SO_wpt': value });}
if(key == "SL_HK_it1"){chrome.storage.local.set({ 'SL_HK_it1': value });}
if(key == "SL_pr_bbl"){chrome.storage.local.set({ 'SL_pr_bbl': value });}
if(key == "PLD_DIC_FIRSTRUN"){chrome.storage.local.set({ 'PLD_DIC_FIRSTRUN': value });}
if(key == "SL_langDst_name_bbl"){chrome.storage.local.set({ 'SL_langDst_name_bbl': value });}
if(key == "SL_FAV_LANGS_BBL"){chrome.storage.local.set({ 'SL_FAV_LANGS_BBL': value });}
if(key == "SL_HK_bb1"){chrome.storage.local.set({ 'SL_HK_bb1': value });}
if(key == "SL_LNG_LIST"){chrome.storage.local.set({ 'SL_LNG_LIST': value });}
if(key == "SL_Import_Report"){chrome.storage.local.set({ 'SL_Import_Report': value });}
if(key == "SL_CM5"){chrome.storage.local.set({ 'SL_CM5': value });}
if(key == "SL_hide_translation"){chrome.storage.local.set({ 'SL_hide_translation': value });}
if(key == "SL_BTN_X"){chrome.storage.local.set({ 'SL_BTN_X': value });}
if(key == "SL_translation_mos_bbl"){chrome.storage.local.set({ 'SL_translation_mos_bbl': value });}
if(key == "SL_HK_SObox_wpt"){chrome.storage.local.set({ 'SL_HK_SObox_wpt': value });}
if(key == "SL_SaveText_box_gt"){chrome.storage.local.set({ 'SL_SaveText_box_gt': value });}
if(key == "SL_BBL_Y"){chrome.storage.local.set({ 'SL_BBL_Y': value });}
if(key == "SL_TS"){chrome.storage.local.set({ 'SL_TS': value });}
if(key == "SL_DICT_PRESENT"){chrome.storage.local.set({ 'SL_DICT_PRESENT': value });}
if(key == "AVOIDAUTODETECT"){chrome.storage.local.set({ 'AVOIDAUTODETECT': value });}
if(key == "SL_TH_2"){chrome.storage.local.set({ 'SL_TH_2': value });}
if(key == "SL_BACK_VIEW"){chrome.storage.local.set({ 'SL_BACK_VIEW': value });}
if(key == "SL_langDst2"){chrome.storage.local.set({ 'SL_langDst2': value });}
if(key == "INLINEflip"){chrome.storage.local.set({ 'INLINEflip': value });}
if(key == "FORSEbubble"){chrome.storage.local.set({ 'FORSEbubble': value });}
if(key == "SL_TH_1"){chrome.storage.local.set({ 'SL_TH_1': value });}
if(key == "SL_langDst"){chrome.storage.local.set({ 'SL_langDst': value });}
if(key == "SL_PrefTrans"){chrome.storage.local.set({ 'SL_PrefTrans': value });}
if(key == "SL_LOCALIZATION"){chrome.storage.local.set({ 'SL_LOCALIZATION': value });}
if(key == "SL_CM1"){chrome.storage.local.set({ 'SL_CM1': value });}
if(key == "SL_pin_bbl"){chrome.storage.local.set({ 'SL_pin_bbl': value });}
if(key == "SL_Fontsize_bbl2"){chrome.storage.local.set({ 'SL_Fontsize_bbl2': value });}
if(key == "SL_TH_4"){chrome.storage.local.set({ 'SL_TH_4': value });}
if(key == "WINDOW_TOP"){chrome.storage.local.set({ 'WINDOW_TOP': value });}
if(key == "SL_show_back2"){chrome.storage.local.set({ 'SL_show_back2': value });}
if(key == "BL_T_PROV"){chrome.storage.local.set({ 'BL_T_PROV': value });}
if(key == "THE_URL"){chrome.storage.local.set({ 'THE_URL': value });}
if(key == "SL_inject_brackets"){chrome.storage.local.set({ 'SL_inject_brackets': value });}
if(key == "SL_style"){chrome.storage.local.set({ 'SL_style': value });}
if(key == "SL_CM7"){chrome.storage.local.set({ 'SL_CM7': value });}
if(key == "FRUN"){chrome.storage.local.set({ 'FRUN': value });}
if(key == "PLT_TTSvolume"){chrome.storage.local.set({ 'PLT_TTSvolume': value });}
if(key == "SL_line_break"){chrome.storage.local.set({ 'SL_line_break': value });}
if(key == "SL_UNTRUST"){chrome.storage.local.set({ 'SL_UNTRUST': value });}
if(key == "SL_show_button_bbl"){chrome.storage.local.set({ 'SL_show_button_bbl': value });}
if(key == "SL_session"){chrome.storage.local.set({ 'SL_session': value });}
if(key == "SL_Timing"){chrome.storage.local.set({ 'SL_Timing': value });}
if(key == "SL_FAV_TRIGGER"){chrome.storage.local.set({ 'SL_FAV_TRIGGER': value });}
if(key == "SL_other_gt"){chrome.storage.local.set({ 'SL_other_gt': value });}
if(key == "SL_HK_opt"){chrome.storage.local.set({ 'SL_HK_opt': value });}
if(key == "ran_before"){chrome.storage.local.set({ 'ran_before': value });}
if(key == "SL_CM3"){chrome.storage.local.set({ 'SL_CM3': value });}
if(key == "AVOIDAUTODETECT_LNG"){chrome.storage.local.set({ 'AVOIDAUTODETECT_LNG': value });}
if(key == "ADV"){chrome.storage.local.set({ 'ADV': value });}
if(key == "SL_FAV_LANGS_IMT"){chrome.storage.local.set({ 'SL_FAV_LANGS_IMT': value });}
if(key == "SL_FAV_MAX"){chrome.storage.local.set({ 'SL_FAV_MAX': value });}
if(key == "SL_global_lng_bbl"){chrome.storage.local.set({ 'SL_global_lng_bbl': value });}
if(key == "MoveBBLY"){chrome.storage.local.set({ 'MoveBBLY': value });}
if(key == "SL_wptGlobAuto"){chrome.storage.local.set({ 'SL_wptGlobAuto': value });}
if(key == "SL_HK_it2"){chrome.storage.local.set({ 'SL_HK_it2': value });}
if(key == "SL_HKset_inv"){chrome.storage.local.set({ 'SL_HKset_inv': value });}
if(key == "SL_langDst_name_wpt"){chrome.storage.local.set({ 'SL_langDst_name_wpt': value });}
if(key == "SL_FAV_START"){chrome.storage.local.set({ 'SL_FAV_START': value });}
if(key == "WINDOW_WIDTH"){chrome.storage.local.set({ 'WINDOW_WIDTH': value });}
if(key == "SL_TH_3"){chrome.storage.local.set({ 'SL_TH_3': value });}
if(key == "SL_dict_bbl"){chrome.storage.local.set({ 'SL_dict_bbl': value });}
if(key == "WINDOW_LEFT"){chrome.storage.local.set({ 'WINDOW_LEFT': value });}
if(key == "SL_global_lng"){chrome.storage.local.set({ 'SL_global_lng': value });}
if(key == "SL_BTN_Y"){chrome.storage.local.set({ 'SL_BTN_Y': value });}
if(key == "SL_Flag"){chrome.storage.local.set({ 'SL_Flag': value });}
if(key == "SL_show_back"){chrome.storage.local.set({ 'SL_show_back': value });}
if(key == "SL_langDst_bbl2"){chrome.storage.local.set({ 'SL_langDst_bbl2': value });}
if(key == "SL_HK_CT_wpt"){chrome.storage.local.set({ 'SL_HK_CT_wpt': value });}
if(key == "SL_HK_wpt1"){chrome.storage.local.set({ 'SL_HK_wpt1': value });}
if(key == "SL_dictionary"){chrome.storage.local.set({ 'SL_dictionary': value });}
if(key == "SL_langSrc_wpt"){chrome.storage.local.set({ 'SL_langSrc_wpt': value });}
if(key == "SL_change_lang_HKbox_it"){chrome.storage.local.set({ 'SL_change_lang_HKbox_it': value });}
if(key == "SL_langDst_name"){chrome.storage.local.set({ 'SL_langDst_name': value });}
if(key == "SL_langSrc_bbl"){chrome.storage.local.set({ 'SL_langSrc_bbl': value });}
if(key == "SL_CM6"){chrome.storage.local.set({ 'SL_CM6': value });}
if(key == "SL_ALL_PROVIDERS_BBL"){chrome.storage.local.set({ 'SL_ALL_PROVIDERS_BBL': value });}
if(key == "SL_other_bbl"){chrome.storage.local.set({ 'SL_other_bbl': value });}
if(key == "SL_History"){chrome.storage.local.set({ 'SL_History': value });}
if(key == "SL_langSrc_it"){chrome.storage.local.set({ 'SL_langSrc_it': value });}
if(key == "SL_HK_gt2"){chrome.storage.local.set({ 'SL_HK_gt2': value });}
if(key == "SL_HK_bb2box"){chrome.storage.local.set({ 'SL_HK_bb2box': value });}
if(key == "SL_HK_bb2"){chrome.storage.local.set({ 'SL_HK_bb2': value });}
if(key == "SL_bbl_loc_langs"){chrome.storage.local.set({ 'SL_bbl_loc_langs': value });}
if(key == "SL_ALL_PROVIDERS_GT"){chrome.storage.local.set({ 'SL_ALL_PROVIDERS_GT': value });}
if(key == "SL_wptDHist"){chrome.storage.local.set({ 'SL_wptDHist': value });}
if(key == "THEMEmode"){chrome.storage.local.set({ 'THEMEmode': value });}
if(key == "SL_global_lng_wpt"){chrome.storage.local.set({ 'SL_global_lng_wpt': value });}
if(key == "SL_HK_wpt2"){chrome.storage.local.set({ 'SL_HK_wpt2': value });}
if(key == "SL_Dtext"){chrome.storage.local.set({ 'SL_Dtext': value });}
if(key == "SL_WPT_TEMP_LANG"){chrome.storage.local.set({ 'SL_WPT_TEMP_LANG': value });}
if(key == "SL_no_detect"){chrome.storage.local.set({ 'SL_no_detect': value });}
if(key == "SL_langSrc_bbl2"){chrome.storage.local.set({ 'SL_langSrc_bbl2': value });}
if(key == "SL_wptGlobLang"){chrome.storage.local.set({ 'SL_wptGlobLang': value });}
if(key == "SL_wptLHist"){chrome.storage.local.set({ 'SL_wptLHist': value });}
if(key == "SL_CM4"){chrome.storage.local.set({ 'SL_CM4': value });}
if(key == "SL_langDst_it2"){chrome.storage.local.set({ 'SL_langDst_it2': value });}
if(key == "SL_anchor"){chrome.storage.local.set({ 'SL_anchor': value });}
if(key == "SL_FK_box1"){chrome.storage.local.set({ 'SL_FK_box1': value });}
if(key == "SL_no_detect_bbl"){chrome.storage.local.set({ 'SL_no_detect_bbl': value });}
if(key == "SL_SaveText_box_bbl"){chrome.storage.local.set({ 'SL_SaveText_box_bbl': value });}
if(key == "SL_FK_box2"){chrome.storage.local.set({ 'SL_FK_box2': value });}
if(key == "SL_whole_word"){chrome.storage.local.set({ 'SL_whole_word': value });}
if(key == "SL_pr_gt"){chrome.storage.local.set({ 'SL_pr_gt': value });}
if(key == "SL_wptGlobTip"){chrome.storage.local.set({ 'SL_wptGlobTip': value });}
if(key == "SL_HK_gt1"){chrome.storage.local.set({ 'SL_HK_gt1': value });}
if(key == "SL_sort"){chrome.storage.local.set({ 'SL_sort': value });}
if(key == "SL_SavedText_gt"){chrome.storage.local.set({ 'SL_SavedText_gt': value });}
if(key == "SL_ALL_PROVIDERS_IT"){chrome.storage.local.set({ 'SL_ALL_PROVIDERS_IT': value });}
if(key == "WINDOW_HEIGHT"){chrome.storage.local.set({ 'WINDOW_HEIGHT': value });}
if(key == "PLD_OLD_TS"){chrome.storage.local.set({ 'PLD_OLD_TS': value });}
if(key == "SL_dict"){chrome.storage.local.set({ 'SL_dict': value });}
if(key == "SL_langSrc2"){chrome.storage.local.set({ 'SL_langSrc2': value });}
if(key == "SL_Version"){chrome.storage.local.set({ 'SL_Version': value });}
if(key == "SL_langDst_it"){chrome.storage.local.set({ 'SL_langDst_it': value });}
if(key == "SL_BBL_TS"){chrome.storage.local.set({ 'SL_BBL_TS': value });}
if(key == "SL_show_button_bbl2"){chrome.storage.local.set({ 'SL_show_button_bbl2': value });}
if(key == "SL_FAV_LANGS_IT"){chrome.storage.local.set({ 'SL_FAV_LANGS_IT': value });}
if(key == "SL_langDst_wpt"){chrome.storage.local.set({ 'SL_langDst_wpt': value });}
if(key == "SL_Fontsize"){chrome.storage.local.set({ 'SL_Fontsize': value });}
if(key == "SL_langDst_wpt"){chrome.storage.local.set({ 'SL_langDst_wpt': value });}
if(key == "SL_langDst_wpt2"){chrome.storage.local.set({ 'SL_langDst_wpt2': value });}

if(key == "SL_wpt_MANUAL_MODE_OFF"){chrome.storage.local.set({ 'SL_wpt_MANUAL_MODE_OFF': value });}
if(key == "SL_wpt_MANUAL_MODE_ON"){chrome.storage.local.set({ 'SL_wpt_MANUAL_MODE_ON': value });}
if(key == "SL_pr_it"){chrome.storage.local.set({ 'SL_pr_it': value });}


		  GDATA = GDATA + key + "^" + value +";";
			if(GDATA != ""){
				var arr = GDATA.split(";");
				for (var i=0; i<arr.length-1; i++){
					var arr2 = arr[i].split("^");
				}
				ImTranslatorBG.UPDATE_CACHE(GDATA);
				GDATA="";
			}

	},

    	get : function(key){                  // Retrieving key function
    	        var val = null;
		for(var i=0; i<CACHE_PACK_PARAMS.length; i++){
			var arr = CACHE_PACK_PARAMS[i].split("^");
			if(arr[0] == key){
				if(arr[0]!="SL_DICT_PRESENT" && arr[0]!="SL_SavedText_gt") val = arr[1];
				else {
					if(arr[0]=="SL_DICT_PRESENT") val = CACHE_PACK_PARAMS[i].replace("SL_DICT_PRESENT^","");
					if(arr[0]=="SL_SavedText_gt") val = CACHE_PACK_PARAMS[i].replace("SL_SavedText_gt^","");
				}
			}
		}

	       	return val;
	},

	init: function(state){
		try{
			ImTranslatorBG.GET_MS_KEY();			  
			const TOmins = 60 * 5;
			ImTranslatorBG.startTimer(TOmins);
		}catch(e){}

	    setTimeout(function(){
                ImTranslatorBG.set("SL_GWPTHist", "");
                 
/*UBRAL VK
		chrome.runtime.onMessage.addListener(function(request, sender, sendResponse)
		{
		    switch(request.message){
		        case 'setText':
		            window.seltext = request.data
		            break;
		        default:
		            sendResponse({data: 'Invalid arguments'});
		        	break;
		    }
		});

*/
		var tmpDOM = ImTranslatorBG.get("SL_DOM");
		if(tmpDOM==null) ImTranslatorBG.set("SL_DOM", "auto");
		else {
			if(tmpDOM!="auto" && tmpDOM!="com" && tmpDOM!="com.ar" && tmpDOM!="com.au" && tmpDOM!="com.bd" && tmpDOM!="com.br" && tmpDOM!="com.co" && tmpDOM!="com.eg" && tmpDOM!="com.hk" && tmpDOM!="com.my" && tmpDOM!="com.mx" && tmpDOM!="com.ph" && tmpDOM!="com.sa" && tmpDOM!="com.tr" && tmpDOM!="com.tw" && tmpDOM!="com.ua" && tmpDOM!="com.vn" && tmpDOM!="co.in" && tmpDOM!="co.id" && tmpDOM!="co.il" && tmpDOM!="co.nz" && tmpDOM!="co.jp" && tmpDOM!="co.kr" && tmpDOM!="co.uk" && tmpDOM!="co.za" && tmpDOM!="ae" && tmpDOM!="at" && tmpDOM!="by" && tmpDOM!="be" && tmpDOM!="bg" && tmpDOM!="ca" && tmpDOM!="cl" && tmpDOM!="cz" && tmpDOM!="dz" && tmpDOM!="de" && tmpDOM!="es" && tmpDOM!="fr" && tmpDOM!="gr" && tmpDOM!="it" && tmpDOM!="kz" && tmpDOM!="nl" && tmpDOM!="pl" && tmpDOM!="pt" && tmpDOM!="rs" && tmpDOM!="ru") ImTranslatorBG.set("SL_DOM", "auto");
		}

		if(state==0) ImTranslatorBG.SL_Welcome();

		// if pop-up bubble is disabled - the preferred translation becomes gray-out. If previously preferred translation was set as the pop-up bubble than activates the first translator in the list (ImTranslator).
                if(ImTranslatorBG.get("SL_ENABLE") == "false" && ImTranslatorBG.get("SL_PrefTrans")==3){
			ImTranslatorBG.set("SL_PrefTrans", 1);
		}

		if(ImTranslatorBG.get("SL_ENABLE")=='false') ImTranslatorBG.SL_callbackRequestToChangeRightClickMenu(0);

		ImTranslatorBG.LOC_TABLE();
		
		chrome.runtime.onMessage.addListener(
				ImTranslatorBG.onMessage
			);

		chrome.runtime.onMessage.addListener(
				ImTranslatorBG.ClearMessage
			);

		chrome.runtime.onMessage.addListener(
				ImTranslatorBG.Status
			);

		chrome.runtime.onMessage.addListener(
				ImTranslatorBG.onMessage
		);



	        if(ImTranslatorBG.get("SL_GVoices")=="1") ALL_VOICES=G_TTS;
	        else ALL_VOICES=SL_TTS;


            ImTranslatorBG.GET_STORE_DATA();
	    }, 5);	   
	},
	                   

	NewTAB: function(url) {
	 FExtension.browser.openNewTab(url);
	},

	LOC_TABLE: function(){
 	 setTimeout(function(){
          var loc = chrome.i18n.getUILanguage();
          var layers="en,zh,zt,cs,nl,tl,fr,de,el,hi,it,ja,ko,pl,pt,ro,ru,sr,es,sv,tr,uk,vi,bg,sk";
          if(ImTranslatorBG.get("SL_LOCALIZATION")=="none" || ImTranslatorBG.get("SL_LOCALIZATION")=="" || ImTranslatorBG.get("SL_LOCALIZATION")==null){
	          var tmp = loc.split("-");
        	  if(tmp.length>=2) loc = tmp[0];
	          if(loc=="fil") loc="tl";
	          if(loc=="en-US") loc="en";
	          if(loc=="en-AU") loc="en";
	          if(loc=="en-GB") loc="en";
	          if(loc=="pt-BR") loc="pt";
	          if(loc=="pt-PT") loc="pt";
	          if(loc=="es-419") loc="es";
	          if(loc=="zh-CN") loc="zh";
	          if(loc=="zh-TW") loc="zt";

	          if(layers.indexOf(loc)!=-1) ImTranslatorBG.set("SL_LOCALIZATION",loc);
		  else ImTranslatorBG.set("SL_LOCALIZATION","en");
	   }

	  }, 50);
	},


	Lexicon: function(LongLngName) {
	 LongLngName=LongLngName.replace("ька","ьку");
	 return LongLngName;
	},

	open_trans_www: function(state,lang) {
	 var EXT="";

	 if(state==1) EXT="&anno=2";
	 var URL_host=content.document.location.href;
	 var LEGO=URL_host.split("&u=");
	 if(LEGO.length>1){
	  var newLANG1=LEGO[0].split("&tl=");
	  var FINALline=newLANG1[0]+"&tl="+lang;
	  URL_host=FINALline+"&u="+LEGO[1];
	 }
	 var GOhead=0;

//	 if(URL_host.indexOf("https://")>-1) {alert(FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extWPTalert1'));GOhead=1;}
	 if(URL_host.indexOf("file:///")>-1) {alert(FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extWPTalert2'));GOhead=1;}
	 ImTranslatorBG.set("SL_langDst_wpt", lang);

	 if(GOhead==0) ImTranslatorBG.SL_WEB_PAGE_TRANSLATION_MO_PRELOAD();

	},
	
	
	setDefault: function(){
	        FExtension.store.setDefault();
	},



	
	getUPDATES: function(){
	        FExtension.store.getUPDATES();
	},

	ClearMessage: function(request, sender, sendResponse) {
	    if (request.greeting == "Clear")  ImTranslatorBG.SL_callbackRequestToAdd_Clear();
	    else{
		if(PLATFORM=="Chrome")  ImTranslatorBG.SL_callbackRequestToRemove_Clear();
	    }
	},


	onMessage: function(request, sender, sendResponse) {
/*
		FExtension.browser.executeForSelectedTab(null, function(tab) { 
			if(tab){				
				ImTranslatorBG.set("THE_URL", tab.url);				
			}
		});
*/




//VK REQUEST 
                

                ImTranslatorBG.BUBBLE_RESP= ImTranslatorBG.BUBBLE_RESP.replace(/~/g,"^");                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
		sendResponse({farewell: ImTranslatorBG.get("SL_HKset")+"~"+ImTranslatorBG.get("SL_HKset_inv")+"~"+ImTranslatorBG.get("SL_langSrc_bbl")+"|"+ImTranslatorBG.get("SL_langDst_bbl")+"|"+ImTranslatorBG.get("SL_Fontsize_bbl")+"|"+ImTranslatorBG.get("SL_show_button_bbl")+"|"+ImTranslatorBG.get("SL_pin_bbl")+"|"+ImTranslatorBG.get("SL_translation_mos_bbl")+"|"+ImTranslatorBG.get("SL_MOSHK_bbl")+"|"+ImTranslatorBG.get("SL_no_detect_bbl")+"|BLANK|"+ImTranslatorBG.get("SL_ENABLE")+"|"+ImTranslatorBG.get("SL_TH_2")+"|"+ImTranslatorBG.get("SL_TH_4")+"|BLANK|"+ImTranslatorBG.get("SL_no_detect_it")+"|"+ImTranslatorBG.get("SL_dict_bbl")+"|"+ImTranslatorBG.get("SL_MOSHK_bbl2")+"|BLANK~"+ImTranslatorBG.get("SL_FK_box1")+"|"+ImTranslatorBG.get("SL_inlinerFK1")+"|BLANK~"+ImTranslatorBG.get("SL_FK_box2")+"|"+ImTranslatorBG.get("SL_inlinerFK2")+"|BLANK|"+ImTranslatorBG.get("SL_DBL_bbl")+"~"+ImTranslatorBG.get("SL_HK_gt1")+"~"+ImTranslatorBG.get("SL_HK_gt2")+"~"+ImTranslatorBG.get("SL_HK_it1")+"~"+ImTranslatorBG.get("SL_HK_it2")+"~"+ImTranslatorBG.get("SL_HK_bb1")+"~"+ImTranslatorBG.get("SL_other_bbl")+"~"+ImTranslatorBG.get("SL_Timing")+"~"+ImTranslatorBG.get("SL_Fontsize_bbl")+"~"+ImTranslatorBG.get("SL_BBL_TS")+"~"+ImTranslatorBG.get("SL_HK_wpt1")+"~"+ImTranslatorBG.get("SL_HK_wpt2")+"~"+ImTranslatorBG.get("SL_HK_opt")+"~"+ImTranslatorBG.get("SL_HK_wptbox1")+"~"+ImTranslatorBG.get("SL_HK_wptbox2")+"~"+ImTranslatorBG.get("SL_HK_optbox")+"~"+ImTranslatorBG.get("SL_langDst_wpt")+"~"+ImTranslatorBG.get("SL_langSrc_wpt")+"~"+ImTranslatorBG.get("SL_LOCALIZATION")+"~BLANK~"+ImTranslatorBG.get("SL_Flag")+"~"+ImTranslatorBG.get("SL_GVoices")+"~"+ImTranslatorBG.get("SL_SLVoices")+"~"+ALL_VOICES+"~"+ImTranslatorBG.get("SL_SaveText_box_bbl")+"~"+ImTranslatorBG.get("SL_LNG_LIST")+"~"+ImTranslatorBG.get("SL_DOM")+"~"+ImTranslatorBG.get("SL_GWPTHist")+"~BLANK~BLANK~"+ImTranslatorBG.get("SL_GWPT_Show_Hide")+"~"+ImTranslatorBG.get("SL_GWPT_Show_Hide_tmp")+"~"+ImTranslatorBG.get("SL_wptDHist")+"~"+ImTranslatorBG.get("SL_wptLHist")+"~"+ImTranslatorBG.get("SL_wptGlobAuto")+"~"+ImTranslatorBG.get("SL_wptGlobTb")+"~"+ImTranslatorBG.get("SL_wptGlobTip")+"~"+ImTranslatorBG.get("SL_wptGlobLang")+"~"+ImTranslatorBG.get("SL_ALL_PROVIDERS_BBL")+"~"+ImTranslatorBG.get("SL_DICT_PRESENT")+"~"+ImTranslatorBG.get("SL_HK_bb2")+"~"+ImTranslatorBG.get("SL_HK_bb2box")+"~"+ImTranslatorBG.get("SL_BTN_X")+"~"+ImTranslatorBG.get("SL_BTN_Y")+"~"+ImTranslatorBG.get("SL_BBL_X")+"~"+ImTranslatorBG.get("SL_BBL_Y")+"~"+ImTranslatorBG.get("FORSEbubble")+"~"+ImTranslatorBG.BUBBLE_DET+"~"+ImTranslatorBG.BUBBLE_RESP+"~"+ImTranslatorBG.get("TTSvolume")+"~"+ImTranslatorBG.get("BL_D_PROV")+"~"+ImTranslatorBG.get("BL_T_PROV")+"~"+ImTranslatorBG.get("INLINEflip")+"~"+ImTranslatorBG.get("SL_ALL_PROVIDERS_IT")+"~"+ImTranslatorBG.get("THEMEmode")+"~"+ImTranslatorBG.get("SL_Delay")+"~"+ImTranslatorBG.get("SL_langSrc_bbl2")+"~"+ImTranslatorBG.get("SL_langDst_bbl2")+"~"+ImTranslatorBG.get("SL_show_button_bbl2")+"~"+ImTranslatorBG.get("SL_Fontsize_bbl2")+"~BLANK~"+ImTranslatorBG.get("SL_bbl_loc_langs")+"~"+ImTranslatorBG.get("SL_change_lang_HKbox_it")+"~"+ImTranslatorBG.get("SL_change_lang_HK_it")+"~"+ImTranslatorBG.get("SL_langDst_it2")+"~"+ImTranslatorBG.get("SL_pin_bbl2")+"~"+ImTranslatorBG.audioStatus+"~"+ImTranslatorBG.get("MoveBBLX")+"~"+ImTranslatorBG.get("MoveBBLY")+"~"+ImTranslatorBG.get("SL_HK_SObox_wpt")+"~"+ImTranslatorBG.get("SL_HK_SO_wpt")+"~"+ImTranslatorBG.get("SL_HK_CTbox_wpt")+"~"+ImTranslatorBG.get("SL_HK_CT_wpt")+"~"+ImTranslatorBG.get("SL_WPT_TEMP_LANG")+"~"+ImTranslatorBG.get("SL_FAV_START")+"~"+ImTranslatorBG.get("SL_FAV_MAX")+"~"+ImTranslatorBG.get("SL_FAV_LANGS_BBL")+"~"+ImTranslatorBG.get("SL_FAV_LANGS_IT")+"~"+ImTranslatorBG.get("SL_FAV_LANGS_WPT")+"~"+ImTranslatorBG.get("WPTflip")+"~"+ImTranslatorBG.get("SL_UNTRUST")+"~"+ImTranslatorBG.get("SL_style")+"~"+ImTranslatorBG.get("SL_inject_before")+"~"+ImTranslatorBG.get("SL_inject_brackets")+"~"+ImTranslatorBG.get("SL_line_break")+"~"+ImTranslatorBG.get("SL_whole_word")+"~"+ImTranslatorBG.get("SL_hide_translation")+"~"+ImTranslatorBG.get("SL_dictionary")+"~"+ImTranslatorBG.get("SL_langSrc_it")+"~"+ImTranslatorBG.get("SL_langDst_it")+"~"+ImTranslatorBG.get("SL_wpt_MANUAL_MODE_ON")+"~"+ImTranslatorBG.get("SL_wpt_MANUAL_MODE_OFF")+"~"+ImTranslatorBG.get("SL_HK_SObox_wpt")+"~"+ImTranslatorBG.get("SL_HK_SO_wpt")+"~"+ImTranslatorBG.get("SL_HK_CTbox_wpt")+"~"+ImTranslatorBG.get("SL_HK_CT_wpt")+"~" +ImTranslatorBG.MSKEY+"~"+ImTranslatorBG.get("SL_other_it") });
			
		var RESP = request.greeting;

		setTimeout(function(){
               		if(ImTranslatorBG.TRIGGER==1){
				ImTranslatorBG.TRIGGER=0;
			}
		},1000);


		if(request.from){
			var contentTabId;
			if (request.from == "content_detect") {  

			    var url = request.url;
			    var cgi = request.cgi;

                            ImTranslatorBG.SL_GOOGLE_DETECT(url,cgi,100);
			    contentTabId = sender.tab.id;

			    var cnt=0;
			    setTimeout(function(){
				    ImTranslatorBG.SLIDNEW_GDETECT = setInterval(function(){
					if(ImTranslatorBG.NEW_GDETECT!="<#>" || cnt>250) {
						clearInterval(ImTranslatorBG.SLIDNEW_GDETECT);
						ImTranslatorBG.SLIDNEW_GDETECT="";
						var newGDRESULT = ImTranslatorBG.NEW_GDETECT;
							chrome.tabs.sendMessage(contentTabId, {
						      	from: "background",
				      			detected: newGDRESULT
						});
						ImTranslatorBG.NEW_GDETECT="";
                                	}else cnt++;
			    	},200);  
	        	    },10);  
			}

			if (request.from == "content_translate") {  
			    var url = request.url;
			    var cgi = request.cgi;
			    var theQ = request.theQ;

                            ImTranslatorBG.SL_NEW_GTRANSLATE(url,cgi,theQ);
			    contentTabId = sender.tab.id;
			    var cnt=0;
			    setTimeout(function(){
				    ImTranslatorBG.SLIDNEW_GTRANSLATE = setInterval(function(){
					if(ImTranslatorBG.NEW_GTRANSLATE!="" || cnt>250) {
						clearInterval(ImTranslatorBG.SLIDNEW_GTRANSLATE);
						ImTranslatorBG.SLIDNEW_GTRANSLATE="";
						var newGTRESULT = ImTranslatorBG.NEW_GTRANSLATE;
							chrome.tabs.sendMessage(contentTabId, {
						      	from: "background",
				      			translation: newGTRESULT
						});
						ImTranslatorBG.NEW_GTRANSLATE="";
                                	}else cnt++;
			    	},200);  
	        	    },10);  
			}

		}



//		if (RESP != "" && RESP!="1" && RESP!=FExtension.store.getLocalStorage().length){
		if (RESP != "" && RESP!="1"){
			RESP=(RESP + "").replace("{empty}",ImTranslatorBG.get("SL_langSrc_wpt")+"|"+ImTranslatorBG.get("SL_langDst_wpt"));
	                if(RESP.length && RESP.length>10 && RESP.indexOf("SAVE_D:>")==-1 && RESP.indexOf("SAVE_L:>")==-1 ) {

				if(request.greeting && request.greeting.indexOf("[i]") !=-1) {
				        var SAVE_I = request.greeting.replace("[i]","");
					if(ImTranslatorBG.TMP_HIST_SEG != SAVE_I){
		        	                if(RESP.indexOf('~~5^^') && ImTranslatorBG.get("SL_TH_4")==1) ImTranslatorBG.setHistory(SAVE_I);
						ImTranslatorBG.TMP_HIST_SEG = SAVE_I;
					}
				}

				if(request.greeting && request.greeting.indexOf("[wp]") !=-1) {
				        var SAVE_WP = request.greeting.replace("[wp]","");
	        	                if(RESP.indexOf('~~4^^') && ImTranslatorBG.get("SL_TH_3")==1) ImTranslatorBG.setHistory(SAVE_WP);
				}

				if(request.greeting && request.greeting.indexOf("[b]") !=-1) {
				        var SAVE_B = request.greeting.replace("[b]","");
	        	                if(RESP.indexOf('~~2^^') && ImTranslatorBG.get("SL_TH_2")==1) ImTranslatorBG.setHistory(SAVE_B);
				}

			}


			if(request.greeting && request.greeting.indexOf("SAVE_D:>") !=-1) {
			        var SAVE_D = request.greeting.replace("SAVE_D:>","");

	                        var D_HIST = ImTranslatorBG.get("SL_wptDHist");
                                if(D_HIST!="") {
	                                var D1 = D_HIST.split(":");
	                                var CNT1 = 0;
        	                        for(var I=0; I<D1.length; I++){
						var D2 = D1[I].split(",");
						if(SAVE_D.indexOf(D2[0])>-1){
							D_HIST = D_HIST.replace(D1[I],SAVE_D);
							ImTranslatorBG.set("SL_GWPT_Show_Hide",D2[4]);
							ImTranslatorBG.set("SL_GWPT_Show_Hide_tmp",D2[4]);
							CNT1++;
						}
					}
					if(CNT1==0) D_HIST = D_HIST +":"+ SAVE_D;
				} else D_HIST = SAVE_D;
			        ImTranslatorBG.set("SL_wptDHist", D_HIST);

			}
			if(request.greeting && request.greeting.indexOf("TTS_BBL_on:>") !=-1) {
			        var tmp = request.greeting.replace("TTS_BBL_on:>","").split("||");
			        
				var BTN = tmp[0];
				var baseUrl = tmp[1];
				var status = ImTranslatorBG.STOP_PLAY_HANDLER(BTN);
				if(status == 0){

			        return new Promise((resolve, reject) => {
			            const http = new XMLHttpRequest
			            http.onload = e => {
					const reader = new FileReader();
			                reader.onloadend = function() {
					     ImTranslatorBG.audioElement = document.createElement('audio');
					     ImTranslatorBG.audioElement.setAttribute('src', reader.result);
					     ImTranslatorBG.audioElement.setAttribute('preload', 'auto');
					     ImTranslatorBG.audioElement.setAttribute('autoplay', '');
					     document.body.appendChild (ImTranslatorBG.audioElement);
					     ImTranslatorBG.audioStatus="on";
			                    resolve(reader.result)
			                }
			                reader.readAsDataURL(e.target.response)
			            }
    
			            http.onerror = e => {
					ImTranslatorBG.audioStatus="off";
			            }
    
			            http.open("GET", baseUrl)
			            http.responseType = "blob"
			            http.send()
			        })

				}
			} 



			if(request.greeting && request.greeting.indexOf("TTS_BBL_off:>") !=-1) {
				try {
				       document.body.removeChild (ImTranslatorBG.audioElement);
					ImTranslatorBG.BTNstatus=2;
				} catch (ex){}	
			}



			if(request.greeting && request.greeting.indexOf("SAVE_L:>") !=-1) {
			        var SAVE_L = request.greeting.replace("SAVE_L:>","");

	                        var L_HIST = ImTranslatorBG.get("SL_wptLHist");
                                if(L_HIST!="") {
	                                var L1 = L_HIST.split(":");
	                                var CNT2 = 0;
        	                        for(var I=0; I<L1.length; I++){
						var L2 = L1[I].split(",");
						if(SAVE_L.indexOf(L2[0])>-1){
							L_HIST = L_HIST.replace(L1[I],SAVE_L);
							CNT2++;
						}
					}
					if(CNT2==0) L_HIST = L_HIST +":"+ SAVE_L;
				} else L_HIST = SAVE_L;
			        ImTranslatorBG.set("SL_wptLHist", L_HIST);
			}


			if(request.greeting && request.greeting.indexOf("SAVE_COORD:>") !=-1) {
			        var COORDS = request.greeting.replace("SAVE_COORD:>","");
				var SAVE_COORDS = COORDS.split(",");
			        ImTranslatorBG.set("SL_BBL_X", SAVE_COORDS[0]);
			        ImTranslatorBG.set("SL_BBL_Y", SAVE_COORDS[1]);
			}



			if(request.greeting && request.greeting.indexOf("WPT_HIST:>") !=-1) {
			        var TMPDATA = request.greeting.replace("WPT_HIST:>","");
				var SAVE_TMPDATA = TMPDATA.split(";");
			        ImTranslatorBG.ADD_WPT_HIST(SAVE_TMPDATA[0],SAVE_TMPDATA[1]);
			}


			if(request.greeting && request.greeting.indexOf("SAVE_DATA:>") !=-1) {
			        var TMPDATA = request.greeting.replace("SAVE_DATA:>","");
				var SAVE_TMPDATA = TMPDATA.split(":");
			        ImTranslatorBG.set(SAVE_TMPDATA[0], SAVE_TMPDATA[1]);
			}

			if(request.greeting && request.greeting.indexOf("RCL:>") !=-1) {
//				ImTranslatorBG.RCL();
			}

			if(request.greeting && request.greeting.indexOf("CM_BBL:>") !=-1) {
			        var TMPDATA = request.greeting.replace("CM_BBL:>","");
                                ImTranslatorBG.SL_BBL_Reset(TMPDATA);
			}

			if(request.greeting && request.greeting.indexOf("IT:>") !=-1) {
			        var TMPDATA = request.greeting.replace("IT:>","");
//				if(ImTranslatorBG.TMP_IT_SEG != TMPDATA){
					ImTranslatorBG.SL_INLINE(TMPDATA);
					ImTranslatorBG.TMP_IT_SEG = TMPDATA;
//				}
			}

			if(request.greeting && request.greeting.indexOf("ITY:>") !=-1) {
			        var TMPDATA = request.greeting.replace("ITY:>","");
//				if(ImTranslatorBG.TMP_IT_SEG != TMPDATA){
					ImTranslatorBG.SL_Y_INLINE(TMPDATA);
					ImTranslatorBG.TMP_IT_SEG = TMPDATA;
//				}
			}

			if(request.greeting && request.greeting.indexOf("wpt1:>") !=-1) {
	        		var str = request.greeting.replace("wpt1:>","");
			        str = str.split("*");
				ImTranslatorBG.SL_WPT(chrome.info, chrome.tabs, str[0], str[1]);
			}
			if(request.greeting && request.greeting.indexOf("wpt2:>") !=-1) {
	        		var str = request.greeting.replace("wpt2:>","");
			        str = str.split("*");
				ImTranslatorBG.SL_WPT_MO(chrome.info, chrome.tabs, str[0], str[1]);

			}



			if(request.greeting && request.greeting.indexOf("wptCM:>") !=-1) {
	        		var str = request.greeting.replace("wptCM:>","");
	        		if(str){
					FExtension.browser.updateContextMenus(ImTranslatorBG.the_ID4, FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransPageTo')+ " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(str)),ImTranslatorBG.ContMenuClick);
				}
			}


//WPT---------
			if(request.greeting && request.greeting.indexOf("WPT_lng:>") !=-1) {
				var WPT_lng = request.greeting.replace("WPT_lng:>","");
				var Ltmp = WPT_lng.split(",")
				var Llist = "";               
				if(Ltmp.length>3) Ltmp.length=ImTranslatorBG.get('SL_FAV_MAX');
				for (var i = 0; i < Ltmp.length; i++){
				    if(i < Ltmp.length-1) Llist = Llist + Ltmp[i]+",";
				    else Llist = Llist + Ltmp[i];
				}
				ImTranslatorBG.set('SL_FAV_LANGS_WPT', Llist);
				var Ltmp = WPT_lng.split(",")
				ImTranslatorBG.set('SL_langDst_wpt2', Ltmp[0]);

			}

			if(request.greeting && request.greeting.indexOf("WPT_READ_DB:>") !=-1) {
			   try{
				var DATA = request.greeting.replace("WPT_READ_DB:>","");
				var TMP = DATA.split("|");
				ImTranslatorBG.READ_WPT_DB(TMP[0],TMP[1],TMP[2]);
			   } catch(ex){}
			}

			if(request.greeting && request.greeting.indexOf("WPT_SAVE_D:>") !=-1) {
				var WPT_SAVE = request.greeting.replace("WPT_SAVE_D:>","");
				ImTranslatorBG.WPT_D_UPDATE(WPT_SAVE);
			}

			if(request.greeting && request.greeting.indexOf("WPT_SAVE_L:>") !=-1) {
				var WPT_SAVE = request.greeting.replace("WPT_SAVE_L:>","");
				ImTranslatorBG.WPT_L_UPDATE(WPT_SAVE);
			}

			if(request.greeting && request.greeting.indexOf("WPT_GET_L:>") !=-1) {
				var LNG = request.greeting.replace("WPT_GET_L:>","");
				ImTranslatorBG.WPT_GET_L(LNG);
			}


			if(request.greeting && request.greeting.indexOf("MM_ON:>") !=-1) {
				var MM = request.greeting.replace("MM_ON:>","");
				ImTranslatorBG.set('SL_wpt_MANUAL_MODE_ON', MM);
			}

			if(request.greeting && request.greeting.indexOf("MM_OFF:>") !=-1) {
				var MM = request.greeting.replace("MM_OFF:>","");
				ImTranslatorBG.set('SL_wpt_MANUAL_MODE_OFF', MM);
			}

			if(request.greeting && request.greeting.indexOf("CLEAN_ALL:>") !=-1) {

				chrome.tabs.query( {active:true}, function(tab) {
					if(tab){
						ImTranslatorBG.SL_CleanAllFrames(tab.info, tab);
					}
				});                               
			}

			if(request.greeting && request.greeting.indexOf("RES_OR:>") !=-1){
				ImTranslatorBG.set('SL_WPT_ACT_URL', "blank");
				chrome.tabs.query( {active:true}, function(tab) {
					if(tab){
						ImTranslatorBG.SL_ResetWPT(tab.info, tab);
					}
				});                               
			}



			if(request.greeting && request.greeting.indexOf("ACT_ST:>") !=-1){
	        		var txt = request.greeting.replace("ACT_ST:>","");

				var par = txt.split(",");
				if(ImTranslatorBG.get('SL_WPT_ACT_URL')==par[1]){
					ImTranslatorBG.set('SL_WPT_ST', '1');
				} else {
					ImTranslatorBG.set('SL_WPT_ST', '0');
				}
				ImTranslatorBG.set('SL_WPT_ACT_URL', par[1]);

				chrome.tabs.query( {active:true}, function(tab) {
					if(tab){	
						ImTranslatorBG.SL_AutoWPT(tab.info, tab);
					}
				});
			}


//WPT ----------------------




		 if(ImTranslatorBG.SLIDL==""){
			if(request.greeting && request.greeting.indexOf("DET_GOOGLE:>") !=-1) {
			        var TR_DATA_all = request.greeting.replace("DET_GOOGLE:>","");
				var TR_DATA = TR_DATA_all.split(",");
				ImTranslatorBG.BUBBLE_DET="";
				if(ImTranslatorBG.TRIGGER==0){
					ImTranslatorBG.TRIGGER=1;
					ImTranslatorBG.SL_GOOGLE_WPT_DETECT (TR_DATA[0],TR_DATA[1]);
				        var cnt=0;
					var MAXtr=3000;
					if(ImTranslatorBG.INTERNAL_ONLY==1) MAXtr=2;
					setTimeout(function(){
					    ImTranslatorBG.SLIDL = setInterval(function(){
						if(ImTranslatorBG.BUBBLE_DET!="" || cnt>MAXtr) {
							clearInterval(ImTranslatorBG.SLIDL);
							ImTranslatorBG.SLIDL="";

							FExtension.browser.executeForSelectedTab(null, function(tab) { 
								if(tab){
									ImTranslatorBG.SL_PopUpBubbleActivateResult(tab.info, tab);
								}
							});                                        
						}else{
							if (cnt==(MAXtr-1))ImTranslatorBG.BUBBLE_DET="<#>";
							cnt++;
						} 
					    },1);  
	 		        	},5);  
				}
			}


			if(request.greeting && request.greeting.indexOf("TR_YANDEX:>") !=-1) {
			        var TR_DATA_all = request.greeting.replace("TR_YANDEX:>","");
				var TR_DATA = TR_DATA_all.split(",");
				ImTranslatorBG.BUBBLE_RESP="";
				if(ImTranslatorBG.TRIGGER==0){
					ImTranslatorBG.TRIGGER=1;
					ImTranslatorBG.SL_YANDEX (TR_DATA[0],TR_DATA[1],"BBL");
				        var cnt=0;
					setTimeout(function(){
					    ImTranslatorBG.SLIDL = setInterval(function(){
						if(ImTranslatorBG.BUBBLE_RESP!="" || cnt>50) {
							clearInterval(ImTranslatorBG.SLIDL);
							ImTranslatorBG.SLIDL="";
							FExtension.browser.executeForSelectedTab(null, function(tab) { 
								if(tab){
									ImTranslatorBG.SL_PopUpBubbleActivateResult(tab.info, tab);
								}
							});                                        
						}else cnt++;
					    },50);  
	 	        		},50);  
				}
			}


			if(request.greeting && request.greeting.indexOf("TR_GOOGLE:>") !=-1) {
			        var TR_DATA_all = request.greeting.replace("TR_GOOGLE:>","");
				var TR_DATA = TR_DATA_all.split(",");
				ImTranslatorBG.BUBBLE_RESP="";
				if(ImTranslatorBG.TRIGGER==0){
					ImTranslatorBG.TRIGGER=1;
					ImTranslatorBG.SL_GOOGLE (TR_DATA[0],TR_DATA[1],TR_DATA[2]);
				}
			}

			if(request.greeting && request.greeting.indexOf("LAST_TRANSLATION_GOOGLE:>") !=-1) {
			        var TR_DATA_all = request.greeting.replace("LAST_TRANSLATION_GOOGLE:>","");
				var TR_DATA = TR_DATA_all.split(",");
				ImTranslatorBG.BUBBLE_RESP="";
				ImTranslatorBG.SL_LAST_CHANCE_GOOGLE_TRANSLATE_BBL (TR_DATA[0],TR_DATA[1],TR_DATA[2]);
			}


			if(request.greeting && request.greeting.indexOf("TR_STOP:>") !=-1) {
				//by VK - RESET BUBLE RESULT from CONTENT PAGE
				ImTranslatorBG.BUBBLE_RESP="";
			}

			if(request.greeting && request.greeting.indexOf("CLEAR:>") !=-1) {
				var clear = request.greeting.replace("CLEAR:>","");				
                                ImTranslatorBG.IT_CLEAR=clear;
				ImTranslatorBG.GET_MS_KEY();
			}

			if(request.greeting && request.greeting.indexOf("PUSH:>") !=-1) {
				var text = request.greeting.replace("PUSH:>","");
                         
                                text=text.replace(/%/ig,"`");
				if(text!="") ImTranslatorBG.SL_OnSelection();
				else         ImTranslatorBG.SL_WorkingSet();
                                ImTranslatorBG.PUSH_TXT=text;

			        ImTranslatorBG.set("SL_Dtext", text);

			}


			if(request.greeting && request.greeting.indexOf("POPUP:>") !=-1) {
				if(ImTranslatorBG.DO_ONCE_ONLY==0){
					ImTranslatorBG.DO_ONCE_ONLY=1;
					ImTranslatorBG.ContMenuClickNew();
				}

			}





		   }
		}
                if(ImTranslatorBG.get("SL_TS_LOC")==1){
			ImTranslatorBG.set("SL_TS_LOC",0);
		}

		try {
			if(request.greeting && request.greeting.indexOf("SES:>") !=-1) {
		        	var SES_DATA_all = request.greeting.replace("SES:>","");
				var SES_DATA = SES_DATA_all.split(",");
			        ImTranslatorBG.set("SL_langSrc_bbl2", SES_DATA[0]);
			        ImTranslatorBG.set("SL_langDst_bbl2", SES_DATA[1]);
		        	var FNT = SES_DATA[2];
				if(FNT != undefined && FNT != "")	ImTranslatorBG.set("SL_Fontsize_bbl2", FNT);
			        ImTranslatorBG.set("SL_pin_bbl2", SES_DATA[3]);
			        ImTranslatorBG.set("SL_bbl_loc_langs", SES_DATA[4]);
		        	ImTranslatorBG.set("SL_show_button_bbl2", SES_DATA[5]);
			}

			if(request.greeting && request.greeting.indexOf("SES_IT:>") !=-1) {
			        var SES_DATA_all = request.greeting.replace("SES_IT:>","");
				var SES_DATA = SES_DATA_all.split(",");
			        ImTranslatorBG.set("SL_langDst_it2", SES_DATA[0]);
				ImTranslatorBG.set("SL_langDst_name_it", ImTranslatorBG.GetLongLanguageName(SES_DATA[0]));
				ImTranslatorBG.SL_callbackRequest4LOC();
			}

			if(request.greeting && request.greeting.indexOf("WPT_CURL:>") !=-1) {
				var params = request.greeting.replace("WPT_CURL:>","");
				ImTranslatorBG.set("SL_WPT_TEMP_LANG", params);
			}

			if(request.greeting && request.greeting.indexOf("FAV_BBL:>") !=-1) {
			        var FAV_all = request.greeting.replace("FAV_BBL:>","");
			        ImTranslatorBG.set("SL_FAV_LANGS_BBL", FAV_all);
			}

			if(request.greeting && request.greeting.indexOf("FAV_IT:>") !=-1) {
			        var FAV_all = request.greeting.replace("FAV_IT:>","");
			        ImTranslatorBG.set("SL_FAV_LANGS_IT", FAV_all);
			}

			if(request.greeting && request.greeting.indexOf("FAV_WPT:>") !=-1) {
			        var FAV_all = request.greeting.replace("FAV_WPT:>","");
			        ImTranslatorBG.set("SL_FAV_LANGS_WPT", FAV_all);
			}

			if(request.greeting && request.greeting.indexOf("RCM:>") !=-1) {
				ImTranslatorBG.PREPARE_RCM_CONTENT();
			}

			if(request.greeting && request.greeting.indexOf("OPEN_O:>") !=-1) {
			        var OPEN_O = request.greeting.replace("OPEN_O:>","");
				ImTranslatorBG.OPEN_OPTIONS(OPEN_O);
			}

		} catch (ex){}	


//VK REQUEST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
	},


	Status: function(request, sender, sendResponse) {
	    if (request.method == "getStatus")	      sendResponse({status: ImTranslatorBG.set("SL_Flag","TRUE")});
	},




        SL_callbackRequestToChangeRightClickMenu: function(st){

                if(st == 0){
			if(ImTranslatorBG.get("SL_CM3")==1){
				chrome.contextMenus.remove('child3');
			}
		}

	},

        SL_callbackRequestToAdd_Clear: function(){
	},

	SL_callbackRequestToRemove_Clear: function(){
	},

	SL_callbackRequest: function(){		
	},

	SL_callbackRequest2: function(){
	},


	SL_callbackRequest4: function(){
	},

	SL_PopUpBubbleActivateResult: function(info, tab){
		 clearInterval(ImTranslatorBG.SLIDL);
		 chrome.scripting.executeScript(tab.id, {
		    code: "ImTranslatorDataEvent.mousedown();"
		 });
	},


	SL_PopUpBubble: function(info, tab){
		tab = chrome.tabs;
		var ST = 0;
		if(tab.id==-1) ST=1;  

/*
		if(tab.url.toLowerCase().indexOf("extension://")!=-1) ST=1;
		if(tab.url.toLowerCase().indexOf(".pdf")!=-1) ST=1;
		if(tab.url.toLowerCase().indexOf("chrome://extensions/")!=-1) ST=1;
		if(tab.url.toLowerCase().indexOf("addons.opera.com/")!=-1 && tab.url.indexOf("/extensions")!=-1) ST=1;
		if(tab.url.toLowerCase().indexOf("addons.mozilla.org/")!=-1 && tab.url.indexOf("/firefox")!=-1) ST=1;
		if(tab.url.toLowerCase().indexOf("mensuel.framapad.org")!=-1) ST=1;
		if(tab.url.toLowerCase().indexOf("oasis.sandstorm.io")!=-1) ST=1;
		if(tab.url.toLowerCase().indexOf("chrome.google.com/webstore/")!=-1) ST=1;
		if(tab.url.toLowerCase().indexOf("etherpad.org")!=-1) ST=1;
		if(tab.url.toLowerCase().indexOf("about:")!=-1 && tab.url.toLowerCase().indexOf("://")==-1) ST=1;
		if(tab.url.toLowerCase().indexOf("chrome://settings/")!=-1) ST=1;
		if(tab.url.toLowerCase().indexOf("file:///")!=-1) ST=1;
*/

		if(ST==1){
                      ImTranslatorBG.ContMenuClickNew(info,tab);
		}else{
			chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
			    chrome.tabs.sendMessage(tabs[0].id, {action: "open_dialog_box"}, function(response) {});  
			});
		}		
	},


	SL_InlineActivateResult: function(info, tab){
		 chrome.scripting.executeScript(tab.id, {
		    code: "TranslatorIM.InlineDataTransmitter('"+escape(ImTranslatorBG.INLINE_RESP)+"');"
		 });
	},

	SL_callbackRequest4LOC: function(){

	},


	GetLongLanguageName: function(code){
		var temp=FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extLanguages').split(',');
		var lng="";
		var output="Spanish";
		for(var i=0; i<temp.length; i++){
			lng=temp[i].split(":");
		 	if(lng[0]==code) {
				output=lng[1]; 
				break;
			}
		}
		return (output);
       	},

	ContMenuClickNew: function(info, tab) {

	    	if(ImTranslatorBG.myWindow) {
	        	chrome.windows.remove(ImTranslatorBG.myWindow);
		}

		var HEIGHT = ImTranslatorBG.get("WINDOW_HEIGHT");
		var WIDTH = ImTranslatorBG.get("WINDOW_WIDTH");

		var TOP = ImTranslatorBG.get("WINDOW_TOP");

		if( TOP == null ) TOP = 10; // TOP = (( screen.height - HEIGHT ) / 2);
		var LEFT = ImTranslatorBG.get("WINDOW_LEFT");
		if( LEFT == null ) LEFT = 10; // LEFT = (( screen.width - WIDTH ) / 2);

	        var s="undefined";
/*
		if(chrome.tabs){
	      		chrome.scripting.executeScript( {
			  code: "window.getSelection().toString();"
		      	}, function(selection) {
	        	  	try{
				    s = selection[0].trim();
				} catch(err){}		 
			});
	     	}
*/
		if(ImTranslatorBG.PUSH_TXT==""){
	        	if(typeof info != "undefined"){
		            s=String(info.selectionText);
		//	    s=decodeURIComponent(encodeURIComponent(s).replace(/%20%20/g,"\n\n"))
	        	} else {
	        	    s=String(FExtension.browser.getSelectionText());
		        }
		} else s =ImTranslatorBG.PUSH_TXT;
		
		s = decodeURIComponent(encodeURIComponent(s).replace(/%20%20%20/ig,"%0D%0D"));
		s = s.replace(/Â/ig,"");

		var BACK_VIEW=ImTranslatorBG.get("SL_BACK_VIEW");




		WIDTH=Math.ceil(WIDTH*1+10);


		if(s!='undefined'){
		    setTimeout(function(){

			    //if(ImTranslatorBG.myWindow) ImTranslatorBG.myWindow.blur();
			    s=s.replace(/(^[\s]+|[\s]+$)/g, '');
			    var theQ=s.split(" ").length;

			    if(s.match(/[-/‧·﹕﹗！：，。﹖？:-?!.,:{-~!"^_`\[\]]/g)!=null) theQ=100;
			    if(ImTranslatorBG.get("SL_dict")=="false") theQ=100;

			    s=encodeURIComponent(s);
			    if(s.indexOf("%0A")!=-1) theQ=100;
	 		    if(s.match(/[\u3400-\u9FBF]/) && s.length>1) theQ=100;
	 		    if(ImTranslatorBG.DIC_TRIGGER != 0) theQ = 100;

			    if(s!=""){
		 		    if(ImTranslatorBG.get("SL_SaveText_box_gt")==1) {
//					ImTranslatorBG.set("SL_SavedText_gt",s);
					ImTranslatorBG.set("SL_Dtext_gt",s);
				    }
			    } else theQ=100;

			    s=decodeURIComponent(s);




			    if(theQ==1){
				    var URL = "../content/html/popup/dictionary.html?text="+s;
			    } else {
				if(BACK_VIEW==2) var URL = "../content/html/popup/translation-back.html?text="+s;
				else var URL = "../content/html/popup/translator.html?text="+s; 
							
			    }
			    ImTranslatorBG.CreatePOPUP(HEIGHT,WIDTH,LEFT,TOP,URL);
			   // if(ImTranslatorBG.myWindow)ImTranslatorBG.myWindow.focus(); 

	            },500);
                    ImTranslatorBG.PUSH_TXT="";
		 }else{
		    setTimeout(function(){


		   	window.blur();
		   	if(!ImTranslatorBG.myWindow){
	                	setTimeout(function(){
					if(BACK_VIEW==2) var URL = "../content/html/popup/translation-back.html?text="+s; 
					else var URL = "../content/html/popup/translator.html?text="+s;
				        ImTranslatorBG.CreatePOPUP(HEIGHT,WIDTH,LEFT,TOP,URL);
        	        	},500);

		   	}else {
				if(ImTranslatorBG.myWindow.name==""){
		                    setTimeout(function(){
					if(BACK_VIEW==2) var URL = "../content/html/popup/translation-back.html?text="+s;
					else var URL = "../content/html/popup/translator.html?text="+s;
				        ImTranslatorBG.CreatePOPUP(HEIGHT,WIDTH,LEFT,TOP,URL);
		                    },500);

				}
		   	}	
		  	if(ImTranslatorBG.myWindow)ImTranslatorBG.myWindow.focus(); 


	            },500);

                    ImTranslatorBG.PUSH_TXT="";
		 }
	},




	ContMenuClickNew___: function(info, tab) {
	    	if(ImTranslatorBG.myWindow != "") {
	        	chrome.windows.remove(ImTranslatorBG.myWindow);
		}
		var HEIGHT = ImTranslatorBG.get("WINDOW_HEIGHT");
		var WIDTH = ImTranslatorBG.get("WINDOW_WIDTH");
		var TOP = ImTranslatorBG.get("WINDOW_TOP");
		if( TOP == null ) TOP = 10; // TOP = (( screen.height - HEIGHT ) / 2);
		var LEFT = ImTranslatorBG.get("WINDOW_LEFT");
		if( LEFT == null ) LEFT = 10; // LEFT = (( screen.width - WIDTH ) / 2);
		var BACK_VIEW=ImTranslatorBG.get("SL_BACK_VIEW");
		WIDTH=Math.ceil(WIDTH*1+10);
		var s = ImTranslatorBG.get("SL_Dtext");
		if(s!='undefined'){
			var URL = "../content/html/popup/translation-back.html?text="+s;
			ImTranslatorBG.CreatePOPUP(HEIGHT,WIDTH,LEFT,TOP,URL);
		 }
	},

        CreatePOPUP: function(HEIGHT,WIDTH,LEFT,TOP,URL){
		    chrome.windows.create({
		            url: URL,
		            type: "popup",
		            width: parseInt(WIDTH),
		            height: parseInt(HEIGHT),
		            left: parseInt(LEFT),
		            top: parseInt(TOP)
//		            focused: true
		    },  (window) => {
		      ImTranslatorBG.myWindow = window.id;
		    });
		  ImTranslatorBG.DO_ONCE_ONLY=0;
	},

	SL_WEB_PAGE_TRANSLATION_PRELOAD: function(info, tab){
		 chrome.scripting.executeScript(tab.id, {
		    code: 'TranslatorIM.SL_WPT(0);'
		 });		
	},

	SL_WEB_PAGE_TRANSLATION_MO_PRELOAD: function(info, tab){
		 chrome.scripting.executeScript(tab.id, {
		    code: 'TranslatorIM.SL_WPT(1);'
		 });		
	},

	
	SL_WPT: function (info, tab, url, sl) {
		var URL_host= FExtension.browser.getCurrentUrl(tab);
		if (url!="") URL_host=url;
		var langS=ImTranslatorBG.get("SL_langSrc_wpt");

		langS=sl;
		var langD=ImTranslatorBG.get("SL_langDst_wpt");

		//FLIP
		if(langS == langD && ImTranslatorBG.get("SL_langSrc_wpt")!="auto") langD = ImTranslatorBG.get("SL_langSrc_wpt");

		var LEGO=URL_host.split("&u=");
		if(LEGO.length>1){
			var newLANG1=LEGO[0].split("&tl=");
			var FINALline=newLANG1[0]+"&tl="+langD;
			URL_host=FINALline+"&u="+LEGO[1];
		}
		var GOhead=0;
/*
		if(URL_host.indexOf("https://")>-1) {
			alert(FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extWPTalert1'));GOhead=1;
		}
*/
		if(URL_host.indexOf("file:///")>-1) {
			alert(FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extWPTalert2'));GOhead=1;
		}

		if(GOhead==0){
			var dom = ImTranslatorBG.get("SL_DOM");
			if(dom == "auto") dom = "com";
			ImTranslatorBG.THE_URL = "https://translate.google."+dom+"/translate?sl="+langS+"&tl="+langD+"&u="+URL_host;

			if (ImTranslatorBG.get("SL_TH_3")==1){
				var SLnow = new Date();
				SLnow=SLnow.toString();
	            		var TMPtime=SLnow.split(" ");
	            		var CurDT=TMPtime[1]+" "+TMPtime[2]+" "+TMPtime[3]+", "+TMPtime[4];
	            		var tp=3;
				ImTranslatorBG.THE_URL = decodeURIComponent(ImTranslatorBG.THE_URL);
				URL_host = decodeURIComponent(URL_host);
	            		ImTranslatorBG.setHistory(URL_host + "~~" + ImTranslatorBG.THE_URL + "~~"+langS+"|"+langD+"~~"+ ImTranslatorBG.THE_URL+"~~"+CurDT+"~~"+tp);
			}
			FExtension.browser.openNewTab(ImTranslatorBG.THE_URL);
		}
	},

	SL_WPT_MO: function (info, tab, url, sl) {
		var URL_host= FExtension.browser.getCurrentUrl(tab);
		if (url!="") URL_host=url;
		var langS=ImTranslatorBG.get("SL_langSrc_wpt");

		langS=sl;

		var langD=ImTranslatorBG.get("SL_langDst_wpt");
		//FLIP
		if(langS == langD && ImTranslatorBG.get("SL_langSrc_wpt")!="auto") langD = ImTranslatorBG.get("SL_langSrc_wpt");
		if(langS == langD) langS="auto";
		var LEGO=URL_host.split("&u=");
		if(LEGO.length>1){
			var newLANG1=LEGO[0].split("&tl=");
			var FINALline=newLANG1[0]+"&tl="+langD;
			URL_host=FINALline+"&u="+LEGO[1];
		}
		var GOhead=0;
/*
		if(URL_host.indexOf("https://")>-1) {
			alert(FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extWPTalert1'));GOhead=1;
		}
*/
		if(URL_host.indexOf("file:///")>-1) {
			alert(FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extWPTalert2'));GOhead=1;
		}
		if(GOhead==0){
			var dom = ImTranslatorBG.get("SL_DOM");
			if(dom == "auto") dom = "com";
			ImTranslatorBG.THE_URL = "https://translate.google."+dom+"/translate?sl="+langS+"&tl="+langD+"&u="+URL_host;
			if (ImTranslatorBG.get("SL_TH_3")==1){
				var SLnow = new Date();
				SLnow=SLnow.toString();
	            		var TMPtime=SLnow.split(" ");
	            		var CurDT=TMPtime[1]+" "+TMPtime[2]+" "+TMPtime[3]+", "+TMPtime[4];
	            		var tp=3;
				ImTranslatorBG.THE_URL = decodeURIComponent(ImTranslatorBG.THE_URL);
				URL_host = decodeURIComponent(URL_host);
	            		ImTranslatorBG.setHistory(URL_host + "~~" + ImTranslatorBG.THE_URL + "~~"+langS+"|"+langD+"~~"+ ImTranslatorBG.THE_URL+"~~"+CurDT+"~~"+tp);
			}
			FExtension.browser.openNewTab(ImTranslatorBG.THE_URL);
		}
	},
	

	SL_WEB_PAGE_TRANSLATION: function(info, tab) {
		var URL_host= FExtension.browser.getCurrentUrl(tab);
		ImTranslatorBG.set("SL_GWPTHist","");
		setTimeout(function(){

		 chrome.scripting.executeScript(tab.id, {
		    code: 'TranslatorIM.SL_WEB_PAGE_TRANSLATION_FROM_CM_AND_HK("'+ImTranslatorBG.get("SL_wptGlobAuto")+'","reset");'
		 });
		},500);
	},


	
	SL_SET_TRANSLATION_LNG: function (info, tab){
		FExtension.browser.openNewTab(FExtension.browser.getPopUpURL("options-router.html", true));
	},


	SL_Welcome: function(){
		var version = chrome.runtime.getManifest().version;
		chrome.storage.local.get("SL_Version", function(result){
		    	setTimeout(function() {
				var SKIP = "17000.14000";
				var CURver = result["SL_Version"];
				if(CURver != version){
					ImTranslatorBG.TEMP_UPDATE();
					ImTranslatorBG.set("SL_Version", version);
				        if(ImTranslatorBG.ADVkey<4){
						EXTENSION_DEFAULTS();
						if(CURver!=SKIP) FExtension.browser.openNewTab(ImTranslator_theurl+"imtranslator-extension-for-chrome-new/");
					}
				}
	    		}, 1500);
		});
	},


	SL_Planshet_Reset: function(){
	   try{
		FExtension.store.save_LOC4CONTEXT();
		if(ImTranslatorBG.get("SL_CM1")==1){
			if(ImTranslatorBG.get("SL_langDst2") != null && ImTranslatorBG.get("SL_langDst2") != "" ){
				chrome.contextMenus.update(ImTranslatorBG.the_ID1,{ title: "ImTranslator: "+ FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransSel')+ " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.get("SL_langDst2"))) });
			} else {
				chrome.contextMenus.update(ImTranslatorBG.the_ID1,{ title: "ImTranslator: "+ FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransSel')+ " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.get("SL_langDst2"))) });
			}
		}
	    } catch (ex){}	
	},


	SL_BBL_Reset: function(TMPDATA){
	   try{
		FExtension.store.save_LOC4CONTEXT();
		        if (TMPDATA){
				if(ImTranslatorBG.get("SL_CM3")==1){
					if(ImTranslatorBG.get("SL_ENABLE")!="false"){
						chrome.contextMenus.update(ImTranslatorBG.the_ID3,{ title: "Pop-Up Bubble: "+ FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransSel')+" " + ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(TMPDATA)) });
					}
				}
			}else{
				if(ImTranslatorBG.get("SL_CM3")==1){
					if(ImTranslatorBG.get("SL_ENABLE")!="false"){
						chrome.contextMenus.update(ImTranslatorBG.the_ID3,{ title:    "Pop-Up Bubble: "+ FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransSel')+" " + ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName()) });
					}
				}
			}
	    } catch (ex){}	
	},

	getHttpRequest: function() {
	    var ajaxRequest;
	    try {
        	ajaxRequest = new XMLHttpRequest();
	    } catch (e) {
        	try {
	            ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
        	} catch (e) {
	            try {
        	        ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
	            } catch (e) {
        	        return false;
	            }
        	}
	    }
	    return ajaxRequest;
	},


	SL_Y_INLINE: function(str){
		 var TMP = str.split(":|:");
		 var id = TMP[0];
		 var url = TMP[1];
		 var param = TMP[2];
		 var dictionary = TMP[3];
		 var text = TMP[4];
		 var dir = TMP[5];
		 dir = dir.replace("zh-TW","zt");
		 dir = dir.replace("zh-CN","zh");
		 var lngtmp = dir.split("-");
		 var langSrc = lngtmp[0];
		 var langDst = lngtmp[1];

		 ImTranslatorBG.IT_DetLang = TMP[8];
		 ImTranslatorBG.IT_DetLang = ImTranslatorBG.IT_DetLang.replace("zh-TW","zt");
		 ImTranslatorBG.IT_DetLang = ImTranslatorBG.IT_DetLang.replace("zh-CN","zh");

		 var PR = TMP[7];
		 var INLINEflip = ImTranslatorBG.get("INLINEflip");
	         if(INLINEflip==1){
			if(ImTranslatorBG.IT_DetLang==langDst){
				dir = langDst+"-"+langSrc;
			} else {
				dir = ImTranslatorBG.IT_DetLang+"-"+langDst;
			}
			ImTranslatorBG.SL_IN_YANDEX(dir,text,"IT"); 
		 }else{
			dir = ImTranslatorBG.IT_DetLang+"-"+langDst;
			ImTranslatorBG.SL_IN_YANDEX(dir,text,"IT"); 
		 }




	},




	SL_IN_YANDEX: function (dir, text, TR, KEY){
	       	dir = dir.replace("zh-CN","zh");
		dir = dir.replace("jw","jv");
	        dir = dir.replace("iw","he");
		ImTranslatorBG.getY_INLINE_TRANSLATION(dir,text,TR,KEY);
	},


	getY_INLINE_TRANSLATION: function(dir, text, TR){	
		var SL_langDst=ImTranslatorBG.get("SL_langDst_it2");
                var st = 2;                 
		if(ImTranslatorBG.IT_DetLang!="") {
			st = ImTranslatorBG.IF_TO_AVAILABLE_IN_YANDEX_INLINE(ImTranslatorBG.IT_DetLang, SL_langDst);		
		}

		switch(st){
		   case 2: 
		        dir = dir.replace("zh-CN","zh");
		        dir = dir.replace("jw","jv");
        		dir = dir.replace("iw","he");
			var thedir = dir.replace("_","-")
	        	var baseUrl="https://imtranslator.net/extensions/ytrans-j.php?text="+encodeURIComponent(text)+"&dir="+thedir;

			const fetchPromise = fetch(baseUrl);
			fetchPromise.then(response => {
			  return response.json();
			}).then(response => {
			  var resp = response.text[0];
			  resp=resp.replace(/\n/ig,"<br>");
			  ImTranslatorBG.BUBBLE_RESP = resp;
                          ImTranslatorBG.SaveTransToHistory(text,resp,thedir,5,'T');

		    	  setTimeout(function(){
				chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
				    var my_tabid=tabs[0].id;
				    chrome.tabs.sendMessage(my_tabid, {action: 'inline_trans', res: resp});  
				}); 
			  },20);

			});
			break;
		    case 1: 
			 FExtension.browser.executeForSelectedTab(null, function(tab) { 
				if(tab){
					ImTranslatorBG.SL_InlineActivateResult(tab.info, tab);
			 	}
			 });
			var MSG = FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extLPNotSupported');
			MSG = MSG.replace("XXX",ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.IT_DetLang)));
			MSG = MSG.replace("YYY",ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(dir)));
			ImTranslatorBG.INLINE_RESP=MSG;
			break;
		    case 0: 
			 FExtension.browser.executeForSelectedTab(null, function(tab) { 
				if(tab){
					ImTranslatorBG.SL_InlineActivateResult(tab.info, tab);
			 	}
			 });
			ImTranslatorBG.INLINE_RESP=ImTranslatorBG.Lexicon(ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(dir)))+": "+FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extnotsupported')
			break;
		}

	},



	SL_INLINE: function(str){	 
		 var TMP = str.split(":|:");
		 var id = TMP[0];
		 var url = TMP[1];
		 var param = TMP[2];
		 var dictionary = TMP[3];
		 var text = TMP[4];

		 var dir = TMP[5];
//		 dir = dir.replace("zh-TW","zt");
//		 dir = dir.replace("zh-CN","zh");


		 var lngtmp = dir.split("-");
		 var langSrc = lngtmp[0];
		 var langDst = lngtmp[1];

		 ImTranslatorBG.IT_DetLang = TMP[7];
//		 ImTranslatorBG.IT_DetLang = ImTranslatorBG.IT_DetLang.replace("zh-TW","zt");
//		 ImTranslatorBG.IT_DetLang = ImTranslatorBG.IT_DetLang.replace("zh-CN","zh");


		 ImTranslatorBG.URL = TMP[6];
		 var INLINEflip = ImTranslatorBG.get("INLINEflip");


		 var theQ=text.split(" ").length;
		 if(text.match(/[-/‧·﹕﹗！：，。﹖？:-?!.,:{-~!"^_`\[\]]/g)!=null) theQ=100;
		 if (text.match(/[\u3400-\u9FBF]/) && text.length>1) theQ=100;

		 if(theQ<=1){
		         if(INLINEflip==1){
				if(ImTranslatorBG.IT_DetLang==langDst){
					dir = langDst+"-"+langSrc;
				} else {
					dir = ImTranslatorBG.IT_DetLang+"-"+langDst;
				}
				ImTranslatorBG.INLINE_DICTIONARY(text,url,param,dictionary,dir,INLINEflip);
			 }else{
				dir = ImTranslatorBG.IT_DetLang+"-"+langDst;
				ImTranslatorBG.INLINE_DICTIONARY(text,url,param,dictionary,dir,INLINEflip);
			 }
		  } else {
		         if(INLINEflip==1){
				if(ImTranslatorBG.IT_DetLang==langDst){
					dir = langDst+"-"+langSrc;
				} else {
					dir = ImTranslatorBG.IT_DetLang+"-"+langDst;
				}
				ImTranslatorBG.GOOGLE_INLINE_TR_API(text, dir, 0);
			 }else{
				dir = ImTranslatorBG.IT_DetLang+"-"+langDst;
				ImTranslatorBG.GOOGLE_INLINE_TR_API(text, dir, 0);
			 }
		  }
	},

	INLINE_DICTIONARY: function(text,url,param,dictionary,dir,INLINEflip){
		    dictionary = ImTranslatorBG.get("SL_dictionary");
		    INLINEflip = ImTranslatorBG.get("INLINEflip");
	            text=text.toLowerCase();
		    var SL_langSrc=ImTranslatorBG.get("SL_langSrc_it");
		    var xhr = ImTranslatorBG.getHttpRequest();
		    var dir2save=dir;

		    var tmpdir = dir.split("-");
		    var ln = tmpdir[1];
/*
		    var langDst = ln;
		    if(INLINEflip==1){
			    if(ImTranslatorBG.IT_DetLang==ln) ln = SL_langSrc;	
		    }	
*/
		    var  p1 = param.split("&tl=");
		    var  p2 = p1[1].split('&');
		    param=p1[0]+"&tl="+ln+"&"+p2[1];
	      getTranslation(url, param)
	      .then(function (response) {
        	if (response.error) {
	          fn(response);
        	} else {
		    var trans = response.sentences[0].trans;
		    var resp="";
        	    if(response.dict) resp = response.dict[0].terms;
		    var result = "";
		    if(resp.length>0 && dictionary==="true"){
			for(var i=0; i<response.dict.length; i++){
				for(var j=0; j<response.dict[i].entry.length; j++){
				   //Unique only---------------
				   if(result.indexOf(response.dict[i].entry[j].word+",")==-1)  result = result + response.dict[i].entry[j].word+", ";
				}
			}
			result = result.substring(0, result.length - 2);

		    } else {
			result = trans;
		    }

		    if(result=="") result=FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extnotrsrv');
		    if(result.indexOf("CaptchaRedirect")!=-1 || result.indexOf("<p><b>403.</b>")!=-1) ImTranslatorBG.GOOGLE_INLINE_TR_API(text,ln,0);
		    else result = ImTranslatorBG.translateCallBack(result, dictionary, text);




		    ImTranslatorBG.INLINE_RESP=result;


		    if(SL_langSrc=="auto"){
			SL_langSrc="en";
			if(ImTranslatorBG.IT_DetLang != "") SL_langSrc=ImTranslatorBG.IT_DetLang;	
		    }
		    dir = tmpdir[1]+"-"+ln;
		    var thedir = dir.replace("_","-");
	            ImTranslatorBG.SaveTransToHistory(text,result,dir2save,5);

		    setTimeout(function(){
			chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
			    var my_tabid=tabs[0].id;
			    chrome.tabs.sendMessage(my_tabid, {action: 'inline_trans', res: result});  
			}); 
		    },200);
        	}
	      })
	      .catch((error) => {
        	ImTranslatorBG.GOOGLE_INLINE_TR_API(text,langDst,1);
	      });


	},


	GOOGLE_INLINE_TR_API: function(text,dir,st){
	    var dir2save = dir;
	    var tmpdir = dir.split("-");
	    var lnto = tmpdir[1];
	    var lnfrom = tmpdir[0];		
	    if(lnfrom=="") lnfrom="auto";
	    var reg = new RegExp('^[0-9]$');
	    if(reg.test(text)==true) {
		//AVOID NUMBERS
		chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
		    var my_tabid=tabs[0].id;
		    chrome.tabs.sendMessage(my_tabid, {action: 'inline_trans', res: text});  
		}); 
	    } else {
		ImTranslatorBG.INLINE_RESP="";
  		var num = Math.floor((Math.random() * SL_GEO.length)); 
  		var theRegion = SL_GEO[num];
  		text = text.trim();

		var SL_langSrc=ImTranslatorBG.get("SL_langSrc_it");
		var SL_langDst=ImTranslatorBG.get("SL_langDst_it2");
		var INLINEflip = ImTranslatorBG.get("INLINEflip");
		var baseUrl = 'https://translate.google.'+theRegion+'/translate_a/single';
		if(lnfrom=="zh") lnfrom = "zh-CN";
		if(lnfrom=="zt") lnfrom = "zh-TW";
		if(lnto=="zh") lnto = "zh-CN";
		if(lnto=="zt") lnto = "zh-TW";

		var SL_Params="client=gtx&dt=t&dt=bd&dj=1&source=input&q="+encodeURIComponent(text) + "&sl="+lnfrom+"&tl="+lnto+"&hl=en";

  	

	      getTranslation(baseUrl, SL_Params)
	      .then(function (response) {
        	if (response.error) {
	          fn(response);
        	} else {
		    var result="";
		    for (var i=0; i<response.sentences.length; i++){
	        	    result = result + response.sentences[i].trans;
	            }

		    if(result!="") {
			var dictionary=false;				  
			result = ImTranslatorBG.translateCallBack(result, dictionary, text);
		        ImTranslatorBG.INLINE_RESP=result;

                	if(SL_langSrc=="auto"){
				SL_langSrc="en";
				if(ImTranslatorBG.IT_DetLang != "") SL_langSrc=ImTranslatorBG.IT_DetLang;	
			}

			if(dir2save.indexOf("zh-TW")!=-1) dir2save = dir2save.replace("zh-TW", "zt");
			if(dir2save.indexOf("zh-CN")!=-1) dir2save = dir2save.replace("zh-CN", "zh");

                        ImTranslatorBG.SaveTransToHistory(text,result,dir2save,5);
                	setTimeout(function(){
				chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
				    var my_tabid=tabs[0].id;
				    chrome.tabs.sendMessage(my_tabid, {action: 'inline_trans', res: result});  
				}); 
			},200);
		    } else {
//			ImTranslatorBG.GOOGLE_INLINE_TR_REMOTE(text,lnto,st);
		    }
        	}
	      })
	      .catch((error) => {
		ImTranslatorBG.GOOGLE_INLINE_TR_REMOTE(text,lnto,st);
	      });
        	

           }	
	      
	},


	GOOGLE_INLINE_TR_REMOTE: function (text,ln,st){
				chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
				    var my_tabid=tabs[0].id;
				    chrome.tabs.sendMessage(my_tabid, {action: 'inline_trans', res: '<#>|'+text+"|"+ln});  
				}); 

	},


	translateCallBack: function(result, text, dictionary) {
	    var translation = "";
	    if (dictionary) {
        	try {
	            result = JSON.parse(result);
        	} catch (e) {
	        }
        	if (result.dict) {
	            var dict = result.dict;
        	    if (dict.length > 0 && dict[0].terms) {
                	translation = dict[0].terms.join(', ');
	            }
        	} else {
	   //         translation = result.sentences[0].trans;
	 	        translation = result;
        	}
	    } else {
        	translation = ImTranslatorBG.get_translation(result);
	    }
	    //translation = " " + translation;
	    return(translation)
	},


	SaveTransToHistory: function(text,historyText,dir,view,pr) {

		if(!pr) pr="G";
		else pr="T";
	        if (ImTranslatorBG.get("SL_TH_4") == 1){

		    if(dir.indexOf("_")!=-1){
			    var tmp = dir.split("_");
			    var mySourceLang = tmp[0];
	    		    var myTargetLang = tmp[1];
		    }	
		    if(dir.indexOf("-")!=-1){
			    var tmp = dir.split("-");
			    var mySourceLang = tmp[0];
	    		    var myTargetLang = tmp[1];
		    }	


/*
		    if(mySourceLang!="auto" && ImTranslatorBG.get("SL_no_detect_it")!="true") ImTranslatorBG.IT_DetLang = mySourceLang;

		    if(mySourceLang=="auto" && ImTranslatorBG.IT_DetLang!="") mySourceLang = ImTranslatorBG.IT_DetLang;

		    if(ImTranslatorBG.get("INLINEflip")==0){ 
			if(ImTranslatorBG.IT_DetLang!="") mySourceLang = ImTranslatorBG.IT_DetLang;
			//else mySourceLang = "auto";
		    } else {
			    if(ImTranslatorBG.IT_DetLang==myTargetLang){
				var tmp = myTargetLang;
				myTargetLang = mySourceLang;
				mySourceLang = tmp;
			    }else mySourceLang = ImTranslatorBG.IT_DetLang;
		    }
*/

	            var SLnow = new Date();
        	    SLnow = SLnow.toString();
	            var TMPtime = SLnow.split(" ");
        	    var CurDT = TMPtime[1] + " " + TMPtime[2] + " " + TMPtime[3] + ", " + TMPtime[4];

	            text=text.replace(/~/ig," ");
        	    historyText=historyText.replace(/~/ig," ");
		    ImTranslatorBG.setHistory(text + "~~" + historyText + "~~" + mySourceLang + "|" + myTargetLang + "~~" + ImTranslatorBG.URL + "~~" + CurDT + "~~" + view + "~~"  + pr);
	       }
	       ImTranslatorBG.IT_DetLang="";
	},



	get_translation:function (result){
	 if(result.indexOf('<span id')!=-1){
	    if (result.indexOf('<span id=result_box class="long_text">') > -1)   var ImtranslatorGoogleResult1 = result.split('<span id=result_box class="long_text">');
	    else var ImtranslatorGoogleResult1 = result.split('<span id=result_box class="short_text">');
	    var ImtranslatorGoogleResult2 = ImtranslatorGoogleResult1[1].split('</span></div>');
	    var ImtranslatorGoogleResult3 = ImtranslatorGoogleResult2[0].replace(/<br>/ig, '@');
	    ImtranslatorGoogleResult3 = ImtranslatorGoogleResult3.replace(/&#39;/ig, "'");
	    ImtranslatorGoogleResult3 = ImtranslatorGoogleResult3.replace(/&quot;/ig, "'");
	    ImtranslatorGoogleResult3 = ImtranslatorGoogleResult3.replace(/&amp;/ig, "&");
	    ImtranslatorGoogleResult3 = ImtranslatorGoogleResult3.replace(/(<([^>]+)>)/ig, "");
	    ImtranslatorGoogleResult3 = ImtranslatorGoogleResult3.replace(/@/ig, "<br>");
	    var ImtranslatorGoogleResult4 = ImtranslatorGoogleResult3.replace(/% 20/ig, " ");
	    return ImtranslatorGoogleResult4;
	 } else return result;
	},


	SL_YANDEX: function(dir, text, TR){
	       	dir = dir.replace("zh-CN","zh");
		dir = dir.replace("jw","jv");
	        dir = dir.replace("iw","he");
		ImTranslatorBG.getY_TRANSLATION(dir,text,TR);
	},


 
	IF_TO_AVAILABLE_IN_YANDEX_INLINE: function(from, to){
		var cnt=0;
	       	from = from.replace("zh","zh-CN");
   		var arr = LISTofLANGsets[3].split(",");
		for(var j=0; j<arr.length; j++){
			if(arr[j] == from) cnt++;
			if(arr[j] == to) cnt++;
		}	
		return(cnt);
	},
		


	getY_TRANSLATION: function(dir, text, TR){
	        	var baseUrl="https://imtranslator.net/extensions/ytrans-j.php?text="+text+"&dir="+dir;
			const fetchPromise = fetch(baseUrl);
			fetchPromise.then(response => {
			  return response.json();
			}).then(response => {
			  var resp = response.text[0];
			  resp=resp.replace(/\n/ig,"<br>");

			  ImTranslatorBG.BUBBLE_RESP = resp;

		    	  setTimeout(function(){
				chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
				    var my_tabid=tabs[0].id;
				    chrome.tabs.sendMessage(my_tabid, {action: 'open_bubble', res: resp});  
				}); 
			  },200);
			});

	},


	SL_GOOGLE_WPT_DETECT: function(baseUrl,SL_Params){
			var ajaxRequest;  
			try{
				ajaxRequest = new XMLHttpRequest();
			} catch (e){
				try{
					ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
				} catch (e) {
					try{
						ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
					} catch (e){
						TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extError1"));
						return false;
					}
				}
			}
			ajaxRequest.onreadystatechange = function(){
	                        var resp = "";
				if(ajaxRequest.status == "429") {
					ajaxRequest = null;
				}
				if(ajaxRequest.readyState == 4 && ajaxRequest.status == 200){
		                        resp = ajaxRequest.responseText;
					if(resp.indexOf('[{"trans":"')!=-1){
						resp = JSON.parse(resp);
						if(resp.src=="zh-CN"){
							ImTranslatorBG.BUBBLE_DET="<#>";
						} else 	ImTranslatorBG.BUBBLE_DET=resp.src;
					} else ImTranslatorBG.BUBBLE_DET="<#>";
					ImTranslatorBG.TRIGGER=0;
				}
			}
			baseUrl = baseUrl +"?"+ SL_Params;
			ajaxRequest.open("GET", baseUrl, true);
		        ajaxRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
			ajaxRequest.send(SL_Params);         
	},


	startTimer: function (duration) {
	  let timer = duration, minutes, seconds;
	  setInterval(function () {
	    minutes = parseInt(timer / 60, 10);
	    seconds = parseInt(timer % 60, 10);

	    minutes = minutes < 10 ? "0" + minutes : minutes;
	    seconds = seconds < 10 ? "0" + seconds : seconds;

	    if (--timer < 0) {
	      timer = duration; // Reset the timer if needed
//	        console.log("OVER");
		ImTranslatorBG.MSKEY = "";
	    }
	  }, 1000);
	},

	GET_MS_KEY: function(){
	    if(ImTranslatorBG.MSKEY==""){
       	      var baseUrl = "https://edge.microsoft.com/translate/auth";

	      getMSkey(baseUrl)
	      .then(function (response) {
        	if (response.error) {
	          fn(response);
        	} else {
		   if(response){
			ImTranslatorBG.MSKEY = response;
			ImTranslatorBG.KEYONCE=1;
		   }
        	}
	      })
	      .catch((error) => {
	      });
	    }	        

	},

	SL_GOOGLE_DETECT: function(baseUrl,SL_Params){
              
	      var tmp1 = SL_Params.split("q=");
	      var tmp2 = tmp1[1].split("&");
	      var text = decodeURIComponent(tmp2[0]);		
	      ImTranslatorBG.NEW_GDETECT="<#>";
	      getTranslation(baseUrl, SL_Params)
	      .then(function (response) {
        	if (response.error) {
	          fn(response);
        	} else {
		   if(response.src){
			ImTranslatorBG.NEW_GDETECT = response.src;
			if(response.src=="ja" || response.src=="yue") ImTranslatorBG.NEW_GDETECT = response.src;
			else{
				var big5 = ImTranslatorBG.DetectBig5(text);
				if(big5 == 0) ImTranslatorBG.NEW_GDETECT = response.src;
				else  {
					if(response.src=="en") ImTranslatorBG.NEW_GDETECT="zh-TW";
				}
			}
			chrome.tabs.sendMessage(contentTabId, {
			      	from: "background",
				detected: ImTranslatorBG.NEW_GDETECT
			});

		   }
        	}
	      })
	      .catch((error) => {
	      });
	},


	SL_GOOGLE: function(baseUrl, SL_Params, theQ){
		if(theQ == 1 && ImTranslatorBG.get("SL_dict_bbl")=="false") theQ=0;
		if(theQ != 1) ImTranslatorBG.SL_GOOGLE_TRANSLATE(baseUrl, SL_Params, theQ);
		else  ImTranslatorBG.SL_GOOGLE_DICTIONARY(baseUrl, SL_Params, theQ);
	},

	SL_GOOGLE_TRANSLATE: function(baseUrl, SL_Params, theQ){
	      getTranslation(baseUrl, SL_Params)
	      .then(function (response) {
        	if (response.error) {
	          fn(response);
        	} else {
		    var resp = "";
        	    if(response.sentences.length<2) resp = response.sentences[0].trans;
		    else{
			for(var i=0; i<response.sentences.length; i++){
				resp = resp + response.sentences[i].trans;
			}
		    }	
		    ImTranslatorBG.BUBBLE_RESP=resp.replace(/\n/ig, '<br>');
        	}
	      })
	      .catch((error) => {});
	},



	SL_LAST_CHANCE_GOOGLE_TRANSLATE_BBL: function(baseUrl, SL_Params, theQ){

	      getTranslation(baseUrl, SL_Params)
	      .then(function (response) {
        	if (response.error) {
	          fn(response);
        	} else {
		    var resp = "";
        	    if(response.sentences.length<2) resp = response.sentences[0].trans;
		    else{
			for(var i=0; i<response.sentences.length; i++){
				resp = resp + response.sentences[i].trans;
			}
		    }	
		    ImTranslatorBG.BUBBLE_RESP=resp.replace(/\n/ig, '<br>');
        	}
	      })
	      .catch((error) => { });
	},

	SL_GOOGLE_DICTIONARY: function(baseUrl, SL_Params, theQ){
	      getTranslation(baseUrl, SL_Params)
	      .then(function (response) {
        	if (response.error) {
	          fn(response);
        	} else {
		  if(response.dict){
		    var RESP = "SL_DICT["+response.src+"^"+response.sentences[0].orig+"]#";
		    var POS = "";	    	
			for(var i=0; i<response.dict.length; i++){
				POS =  response.dict[i].pos+":";
		  	        var TERMS = "";
				for(var j=0; j<response.dict[i].entry.length; j++){
					TERMS = TERMS + "|"+ response.dict[i].terms[j]+">";
					for(var g=0; g<response.dict[i].entry[j].reverse_translation.length; g++){
						TERMS = TERMS + response.dict[i].entry[j].reverse_translation[g]+",";
					}
					TERMS = TERMS.substring(0, TERMS.length - 1);
					
				}
				RESP = RESP + POS + TERMS + ";"
			}
		    RESP = RESP.substring(0, RESP.length - 1);
		    ImTranslatorBG.BUBBLE_RESP=RESP;
		  } else {
			ImTranslatorBG.BUBBLE_RESP=response.sentences[0].trans;
	          }
        	}
	      })
	      .catch((error) => {
        	fn({ error: error });
	      });

	},




	INLINE_DETECTOR: function(text){
		var resp = ImTranslatorBG.i18n_LanguageDetect(text);
		if(resp==""){
			ImTranslatorBG.G_INLINE_DETECT(text);
		} else {
                  ImTranslatorBG.IT_DetLang=resp;
	 	}
	},




	G_INLINE_DETECT: function(text){

		text = text.substring(0,100);
		var num = Math.floor((Math.random() * SL_GEO.length)); 
  		var theRegion = SL_GEO[num];
		if(ImTranslatorBG.get("SL_DOM")!="auto") theRegion=ImTranslatorBG.get("SL_DOM");
		var baseUrl ="https://translate.google."+theRegion+"/translate_a/single";
		var SL_Params = "client=gtx&dt=t&dt=bd&dj=1&source=input&q="+encodeURIComponent(text)+"&sl=auto&tl=en&hl=en";
		var apiUrl = baseUrl +"?"+ SL_Params;

		fetch(apiUrl)
		  .then(response => {
		    if (!response.ok) {
		      throw new Error('Network response was not ok');
		    }
		    return response.json();
		  })
		  .then(userData => {
		    // Process the retrieved user data
			if(userData.src){
				

				var big5 = ImTranslatorBG.DetectBig5(text);
				ImTranslatorBG.IT_DetLang=userData.src;
				if(big5 == 1) {
					if(ImTranslatorBG.IT_DetLang=="en") ImTranslatorBG.SL_INLINE_DETECT(text);
				}
			}
		  })
		  .catch(error => {
//		    ImTranslatorBG.SL_INLINE_DETECT(text);
		  });
	},

	SL_INLINE_DETECT: function(text){
		ImTranslatorBG.IT_DetLang="zh-TW";
	},



	SL_NEW_GTRANSLATE: function(baseUrl, SL_Params, theQ){
		if(theQ == 1 && ImTranslatorBG.get("SL_dict_bbl")=="false") theQ=0;
		var ajaxRequest;	
		try{
			ajaxRequest = new XMLHttpRequest();
		} catch (e){
			try{
				ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
			} catch (e) {
				try{
					ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
				} catch (e){
					TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extError1"));
					return false;
				}
			}
		  }
		  ajaxRequest.onreadystatechange = function(){
                        var resp = "";
			if(ajaxRequest.readyState == 4 && ajaxRequest.status == 200){
	                        resp = ajaxRequest.responseText;
				if(resp.indexOf('[{"trans":"')!=-1){ 
					if(theQ==0){
						var tmp1 = resp.split('"trans":"');
						var tmp2 = tmp1[1].split('","');
						ImTranslatorBG.NEW_GTRANSLATE=tmp2[0];
					}
					else ImTranslatorBG.NEW_GTRANSLATE=resp;
			                ImTranslatorBG.NEW_GTRANSLATE=ImTranslatorBG.NEW_GTRANSLATE.replace(/~/g,"^");
				} else ImTranslatorBG.NEW_GTRANSLATE="<#>";
				ImTranslatorBG.TRIGGER=0;
			}

		  }
		  var METHOD = "GET";
		  if(theQ==1) baseUrl = baseUrl + "?" + SL_Params;
		  else METHOD = "POST";

		  ajaxRequest.open(METHOD, baseUrl, true);
		  ajaxRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		  //if(navigator.userAgent) ajaxRequest.setRequestHeader("User-Agent", navigator.userAgent);
		  ajaxRequest.send(SL_Params);
	},


	i18n_LanguageDetect: function(text){
		return ("");
	},

	Shifter: function(n, str) {
        	for (var i = 0; i < str.length - 2; i += 3) {
	            var acc = str.charAt(i + 2);
        	    if ('a' <= acc) acc = acc.charCodeAt(0) - 87;
	            else acc = Number(acc);
        	    if (str.charAt(i + 1) == '+') acc = n >>> acc;
	            else acc = n << acc;
        	    if (str.charAt(i) == '+') n += acc & 4294967295;
	            else n ^= acc;
        	}
	        return n;
    	},

    	TQmaker: function(q) {
	        var bArr = [], idx = [];
	        for (var i = 0; i < q.length; i++) {
        	    var CC = q.charCodeAt(i);
	            if (128 > CC) bArr[idx++] = CC;
        	    else {
                	if (2048 > CC) bArr[idx++] = CC >> 6 | 192;
	                else {
        	            if (55296 == (CC & 64512) && i + 1 < q.length && 56320 == (q.charCodeAt(i + 1) & 64512)) {
                	        CC = 65536 + ((CC & 1023) << 10) + (q.charCodeAt(++i) & 1023);
                        	bArr[idx++] = CC >> 18 | 240;
	                        bArr[idx++] = CC >> 12 & 63 | 128;
        	            } else bArr[idx++] = CC >> 12 | 224;
                	    bArr[idx++] = CC >> 6 & 63 | 128;
	                }
        	        bArr[idx++] = CC & 63 | 128;
	            }
        	}
	        return bArr;
    	},

     	GetHash: function(q, w) {
	        var SplTK = w.split('.');
        	var indTK = Number(SplTK[0]) || 0;
	        var TK = Number(SplTK[1]) || 0;
        	var bArr = ImTranslatorBG.TQmaker(q);
	        var TMPr = indTK;
        	for (var i = 0; i < bArr.length; i++) {
	            TMPr += bArr[i];
        	    TMPr = ImTranslatorBG.Shifter(TMPr, '+-a^+6');
	        }
        	TMPr = ImTranslatorBG.Shifter(TMPr, '+-3^+b+-f');
	        TMPr ^= TK;
        	if (TMPr <= 0) TMPr = (TMPr & 2147483647) + 2147483648;
	        var Out = TMPr % 1000000;
        	return Out.toString() + '.' + (Out ^ indTK);
    	},



        STOP_PLAY_HANDLER: function(BTNcur){
		var st = 0
		if(ImTranslatorBG.BTNstatus!=2){
			if(ImTranslatorBG.BTNstatus==BTNcur){
				if(ImTranslatorBG.audioElement){
					if(!ImTranslatorBG.audioElement.ended){
						st = 1;
						ImTranslatorBG.audioElement.pause();
						ImTranslatorBG.audioElement = false;
					}
				}
			} else {
				st = 0; 
				if(ImTranslatorBG.audioElement) ImTranslatorBG.audioElement.pause();
				ImTranslatorBG.audioElement = false;
			}
		}  else st = 0;
		if(st==0) ImTranslatorBG.BTNstatus = BTNcur;
		return st;
        },

	uniqFAV: function(FAV) {
		var OUT = "";
		var SL_FAV_MAX = ImTranslatorBG.get("SL_FAV_MAX");
		var array = FAV.split(",");
		const uniqueArray = array.filter((value, index, self) => {
			return self.indexOf(value) === index;
		});
		for(var i=0;i<SL_FAV_MAX; i++) {
			OUT = OUT + uniqueArray[i]+",";	
		}
 		return(OUT);
	},


	SL_SAVE_FAVORITE_LANGUAGES: function (ln, TR){
		var OUT = "";
		var OUT2 = "";
		var SL_FAV_LANGS = ImTranslatorBG.get(TR);
		var SL_FAV_MAX = ImTranslatorBG.get("SL_FAV_MAX");
		if(SL_FAV_LANGS!=null){
			if(SL_FAV_LANGS.indexOf(ln)!=-1){
				SL_FAV_LANGS = SL_FAV_LANGS.replace(ln+",",""); 
				SL_FAV_LANGS = SL_FAV_LANGS.replace(ln,"");
			}
			OUT = ln + ",";	
			var ARR = SL_FAV_LANGS.split(",");
			for (var i = 0; i < ARR.length; i++){
				if(ARR[i]!="undefined") OUT = OUT + ARR[i]+",";
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
			OUT = ImTranslatorBG.uniqFAV(OUT);
			ImTranslatorBG.set(TR, OUT);
		}
	},

	PREPARE_RCM_CONTENT: function(){
		var SL_FAV_LANGS = ImTranslatorBG.get("SL_FAV_LANGS_IT");
		if(SL_FAV_LANGS!=""){
			var favArr=SL_FAV_LANGS.split(","); 
		    	ImTranslatorBG.set("SL_langDst_it2",favArr[0]);  
		}
		var SL_FAV_LANGS = ImTranslatorBG.get("SL_FAV_LANGS_BBL");
		if(SL_FAV_LANGS!=""){
			var favArr=SL_FAV_LANGS.split(","); 
		    	ImTranslatorBG.set("SL_langDst_bbl2",favArr[0]);  
		}
		var SL_FAV_LANGS = ImTranslatorBG.get("SL_FAV_LANGS_WPT");
		if(SL_FAV_LANGS!=""){
			var favArr=SL_FAV_LANGS.split(","); 
		    	ImTranslatorBG.set("SL_langDst_wpt2",favArr[0]);  
		}


		ImTranslatorBG.SL_WorkingSet();

	},

	OPEN_OPTIONS: function(st){
		switch(st){
		   case "": FExtension.browser.openNewTab('../content/html/options/options.html'); break;
		   case "bbl": FExtension.browser.openNewTab('../content/html/options/options.html?bbl'); break;
		   case "hist": FExtension.browser.openNewTab('../content/html/options/options.html?hist'); break;
		   case "wpt": FExtension.browser.openNewTab('../content/html/options/options.html?wpt'); break;
		   case "donate": FExtension.browser.openNewTab('https://imtranslator.net'+_CGI+'&a=0'); break;
		   case "router": FExtension.browser.openNewTab('../content/html/options/options-router.html'); break;
		   default: FExtension.browser.openNewTab('../content/html/options/options.html'); break;
		}
		
//		FExtension.browser.openPopUpByURL('../../html/options/options.html');
	},

	DetectBig5: function(myTransText){
		var all = myTransText.length;
    		var count = 0;
    		for (var i = 0, len = myTransText.length; i < len; i++) {
			var rr = myTransText[i].match(/[\u3400-\u9FBF]/);
			if(rr) count ++;
    		}
    		var other = all-count;
    		var OUT = 0	
    		if(other<=count) OUT=1
    		return(OUT);
	},


	SET_DEFAULT_DATA: function(){
		  if(CACHE_PACK_PARAMS.length==0){
			for(var i=0; i<PACK_PARAMS.length; i++){
				var arr = PACK_PARAMS[i].split(";");
				CACHE_PACK_PARAMS[i] = arr[0] + "^" + arr[1];
				ImTranslatorBG.set(arr[0], arr[1]);
			}
		  }
	},

	GET_STORE_DATA: function(){
		chrome.storage.local.get(null, function(items) {
		    var allKeys = Object.keys(items);
		    var allValues = Object.values(items);
			for(var i=0; i<allKeys.length; i++){
				CACHE_PACK_PARAMS[i] = allKeys[i] + "^" + allValues[i];
			}
		});
	},


	UPDATE_CACHE: function (data){
		var TMP1 = data.split(";"); 
	 	for(var i=0; i<CACHE_PACK_PARAMS.length; i++){
		 	for(var j=0; j<TMP1.length; j++){
		         	var TMP2 = TMP1[j].split("^");
				var TMP3 = CACHE_PACK_PARAMS[i].split("^");
				if(TMP3[0]==TMP2[0]) CACHE_PACK_PARAMS[i] = TMP1[j];
			}
		}  
	},

	setHistory: function(content){
		//content=content.replace("^^","");
		if(content!=""){
			chrome.storage.local.get("SL_History", function(result){
			    var val = result["SL_History"];
			    if(val == "") chrome.storage.local.set({ 'SL_History': content });
			    else 	chrome.storage.local.set({ 'SL_History': content + "^^"+val });               
			});
		} else chrome.storage.local.set({ 'SL_History': '' });
	},

	updateHistory: function(content){
		if(content!="")	chrome.storage.local.set({ 'SL_History': content });
		else chrome.storage.local.set({ 'SL_History': '' });
	},


	SL_WorkingSet: function(){
	     try{
		ImTranslatorBG.GET_STORE_DATA();	
		chrome.contextMenus.removeAll();
			var CNT=0;
			for(var i=1; i<=8; i++){
				CNT = CNT + ImTranslatorBG.get("SL_CM"+i)*1;
			}

			if(CNT!=0){
				if(ImTranslatorBG.get("SL_CM1")==1){
					chrome.contextMenus.create({title: "ImTranslator", id: 'child0' });
				}
				if(ImTranslatorBG.get("SL_CM4")==1){
					chrome.contextMenus.create({title: FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransPageTo')+ " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.get("SL_langDst_wpt2"))), id: 'child1' });
			    	}
				if(ImTranslatorBG.get("SL_CM5")==1){
					chrome.contextMenus.create({title: FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMMouseOverTransTo') + " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.get("SL_langDst_wpt2"))), id: 'child2' });
				}
				if(ImTranslatorBG.get("SL_CM6")==1){
					chrome.contextMenus.create({title: FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extOptions')+" ("+FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMcl')+")", id: 'child3' });
				}

				if(ImTranslatorBG.get("SL_CM7")==1){
				    if(ImTranslatorBG.IT_CLEAR==1){
					chrome.contextMenus.create({title: FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMct'), id: 'child14' });
				    }	
				}
			}
	    } catch (ex){}	
	},

	SL_OnSelection: function(){
	     try{		
		ImTranslatorBG.GET_STORE_DATA();	
		chrome.contextMenus.removeAll();
			var CNT=0;
			for(var j=1; j<=8; j++){
				CNT = CNT + ImTranslatorBG.get("SL_CM"+j)*1;
			}

			if(CNT>1){

				    let parent = chrome.contextMenus.create({
				    	title: chrome.runtime.getManifest().name,
					id: 'parent',
				        contexts: ['selection','page','link','editable','image','video','audio']
				    });

					if(ImTranslatorBG.get("SL_CM1")==1){
					    chrome.contextMenus.create({
					      title: "ImTranslator: "+ FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransSel')+ " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.get("SL_langDst2"))),
					      parentId: parent,
					      contexts: ['selection','page','link','editable','image','video','audio'],
					      id: 'child11'
					    });
					}
					if(ImTranslatorBG.get("SL_CM2")==1){
					    chrome.contextMenus.create({
					      title: "Inline translator: "+ FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransSel')+ " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.get("SL_langDst_it2"))),
					      parentId: parent,
					      contexts: ['selection','page','link','editable','image','video','audio'],
					      id: 'child12'
					    });
					}
					if(ImTranslatorBG.get("SL_CM3")==1){
					    chrome.contextMenus.create({
					      title: "Pop-Up Bubble: "+ FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransSel')+ " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.get("SL_langDst_bbl2"))),
					      parentId: parent,
					      contexts: ['selection','page','link','editable','image','video','audio'],
					      id: 'child13'
					    });
					}

					if(ImTranslatorBG.get("SL_CM7")==1){
					    if(ImTranslatorBG.IT_CLEAR==1){
						    chrome.contextMenus.create({
						      title: FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMct'),
						      parentId: parent,
						      contexts: ['selection','page','link','editable','image','video','audio'],
						      id: 'child14'
						    });
					    }
					}
					if(ImTranslatorBG.get("SL_CM4")==1){
					    chrome.contextMenus.create({
					      title: FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransPageTo')+ " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.get("SL_langDst_wpt2"))),
					      parentId: parent,
					      contexts: ['selection','page','link','editable','image','video','audio'],
					      id: 'child1'
					    });
					}

					if(ImTranslatorBG.get("SL_CM5")==1){
					    chrome.contextMenus.create({
					      title: FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMMouseOverTransTo') + " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.get("SL_langDst_wpt2"))),
					      parentId: parent,
					      contexts: ['selection','page','link','editable','image','video','audio'],
					      id: 'child2'
					    });
					}

			} else {

					if(ImTranslatorBG.get("SL_CM1")==1){
					    chrome.contextMenus.create({
					      title: "ImTranslator: "+ FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransSel')+ " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.get("SL_langDst2"))),
					      contexts: ['selection','page','link','editable','image','video','audio'],
					      id: 'child11'
					    });
					}
					if(ImTranslatorBG.get("SL_CM2")==1){
					    chrome.contextMenus.create({
					      title: "Inline translator: "+ FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransSel')+ " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.get("SL_langDst_it2"))),
					      contexts: ['selection','page','link','editable','image','video','audio'],
					      id: 'child12'
					    });
					}
					if(ImTranslatorBG.get("SL_CM3")==1){
					    chrome.contextMenus.create({
					      title: "Pop-Up Bubble: "+ FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMTransSel')+ " " +ImTranslatorBG.Lexicon(ImTranslatorBG.GetLongLanguageName(ImTranslatorBG.get("SL_langDst_bbl2"))),
					      contexts: ['selection','page','link','editable','image','video','audio'],
					      id: 'child13'
					    });
					}
					if(ImTranslatorBG.get("SL_CM7")==1){
					    if(ImTranslatorBG.IT_CLEAR==1){
						    chrome.contextMenus.create({
						      title: FExtension.element(ImTranslatorBG.get("SL_LOCALIZATION"),'extCMct'),
						      contexts: ['selection','page','link','editable','image','video','audio'],
						      id: 'child14'
						    });
					    }
					}

			}
	    } catch (ex){}	
	},



	READ_WPT_DB: function(DOM, LNG, SD){
		var RESPD = DOM + "|";
		//DOMAIN
		var RECS = ImTranslatorBG.get("SL_wptDHist").split(":");

		for(var I=0; I<RECS.length; I++){
			var TMP = RECS[I].replace("{","");
			TMP = TMP.replace("}","");
			var RES = TMP.split(",");
	        	    	if(DOM == RES[0]){
        		    	 	RESPD = RESPD + RES[1]+"|";
        		    	 	RESPD = RESPD + RES[2]+"|";
        	    		 	RESPD = RESPD + RES[3]+"|";
        	    	 		RESPD = RESPD + RES[4]+"|";
	        	    	 	RESPD = RESPD + RES[5]+"|";
        		    	 	RESPD = RESPD + RES[6]+"|";
        		    	 	RESPD = RESPD + RES[7];
				}
		}
                var CHECK1 = RESPD.split("|");
		if(CHECK1.length<=2 && SD=="true"){
			var CHECK2 = CHECK1[0].split(".");
			var OUT="";
			for(var J = 1; J<CHECK2.length; J++){
				if(J<CHECK2.length-1) OUT=OUT+CHECK2[J]+".";
				else OUT=OUT+CHECK2[J];
			}
			for(var I=0; I<RECS.length; I++){
				var TMP = RECS[I].replace("{","");
				TMP = TMP.replace("}","");
				var RES = TMP.split(",");
	        	    	if(RES[0].indexOf(OUT)!=-1){
				   if(RES[1]==1){
        		    	 	RESPD = RESPD + RES[1]+"|";
        		    	 	RESPD = RESPD + RES[2]+"|";
        	    		 	RESPD = RESPD + RES[3]+"|";
        	    	 		RESPD = RESPD + RES[4]+"|";
	        	    	 	RESPD = RESPD + RES[5]+"|";
        		    	 	RESPD = RESPD + RES[6]+"|";
        		    	 	RESPD = RESPD + RES[7];
				   }
				}
			}
		}


		//LANGUAGE
		var RESPL = "";
		var RECS = ImTranslatorBG.get("SL_wptLHist").split(":");
		for(var I=0; I<RECS.length; I++){
			var TMP = RECS[I].replace("{","");
			TMP = TMP.replace("}","");
			var RES = TMP.split(",");
        	    	if(LNG == RES[0]){
        	    	 	RESPL = RESPL + RES[0]+"|";
        	    	 	RESPL = RESPL + RES[1]+"|";
        	    	 	RESPL = RESPL + RES[2]+"|";
        	    	 	RESPL = RESPL + RES[3];
			}
		}

		    setTimeout(function(){
			chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
			    var my_tabid=tabs[0].id;
			    chrome.tabs.sendMessage(my_tabid, {action: RESPD +"`"+RESPL});  
			}); 
		    },20);
	},


	WPT_D_UPDATE: function(DATA){
	        var TMP = DATA.replace("{","");
	        var TMP = TMP.split(",");
	        var DOM = TMP[0];
		var R = ImTranslatorBG.get("SL_wptDHist").replace(/WPT_/g,"");
		if(R != ""){
			var NEWrecs = "";
			var RECS = R.split(":");
			for(var I=0; I<RECS.length; I++){
				var TMP = RECS[I].replace("{","");
				TMP = TMP.replace("}","");
				var RES = TMP.split(",");
        		    	if(DOM == RES[0]){
					NEWrecs = R.replace(RECS[I],DATA);
					ImTranslatorBG.set("SL_wptDHist",NEWrecs);
				}
			}
			if(NEWrecs==""){
				DATA = ImTranslatorBG.get("SL_wptDHist")+":"+DATA;
				ImTranslatorBG.set("SL_wptDHist",DATA);
			}
		} else { 
			ImTranslatorBG.set("SL_wptDHist",DATA);
		}
	},



	WPT_L_UPDATE: function(DATA){
	        var TMP = DATA.replace("{","");
	        var TMP = TMP.split(",");
	        var LNG = TMP[0];
		var R = ImTranslatorBG.get("SL_wptLHist").replace(/WPT_/g,"");
	
		if(R != ""){
			var NEWrecs = "";
			var RECS = R.split(":");
			for(var I=0; I<RECS.length; I++){
				var TMP = RECS[I].replace("{","");
				TMP = TMP.replace("}","");
				var RES = TMP.split(",");
        		    	if(LNG == RES[0]){
					NEWrecs = R.replace(RECS[I],DATA);
					ImTranslatorBG.set("SL_wptLHist",NEWrecs);
				}
			}
			if(NEWrecs==""){
				DATA = ImTranslatorBG.get("SL_wptLHist")+":"+DATA;
				ImTranslatorBG.set("SL_wptLHist",DATA);
			}
		} else { 
			ImTranslatorBG.set("SL_wptLHist",DATA);
		}

	},

	WPT_GET_L: function(lng){
		var L = ImTranslatorBG.get("SL_wptLHist");
		var OUT = "#";
		if(L != ""){
			var RECS = L.split(":");
			for(var I=0; I<RECS.length; I++){
				var TMP = RECS[I].replace("{","");
				TMP = TMP.replace("}","");
				var RES = TMP.split(",");
        		    	if(lng == RES[0]){
					OUT = TMP;
				}
			}	
		}

		chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
			chrome.runtime.sendMessage(tabs[0].id, {langset: OUT});  
		});
 	
	},

	SL_AutoWPT: function(info, tab){
		try {
			chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
			    	my_tabid=tabs[0].id;
				chrome.scripting.executeScript({
					    target: {tabId: my_tabid},
					    files: ['content/js/wpt/wpt-settler.js'],
				});
			}); 
		} catch(ex){}
	},

	SL_ResetWPT: function(info, tab){
		try {
			chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
			    	my_tabid=tabs[0].id;
				chrome.scripting.executeScript({
				    target: {tabId: my_tabid},
				    files: ['content/js/wpt/wpt-reset.js'],
				});
			}); 
		} catch(ex){}
	},




	SL_CleanAllFrames: function(info, tab){
		try {
			ImTranslatorBG.set("SL_wpt_MANUAL_MODE_ON","stop");
			chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
			    	my_tabid=tabs[0].id;
				chrome.scripting.executeScript({
				    target: {tabId: my_tabid},
				    files: ['content/js/wpt/wpt-cleaner.js'],
				});
			}); 
		} catch(ex){}
	},

	ADD_WPT_HIST: function(host,dir){
			var tmp = dir.split("/");
			var dom = ImTranslatorBG.get("SL_DOM");
			if(dom == "auto") dom = "com";
			ImTranslatorBG.THE_URL = host;
			if (ImTranslatorBG.get("SL_TH_3")==1){
				var SLnow = new Date();
				SLnow=SLnow.toString();
	            		var TMPtime=SLnow.split(" ");
	            		var CurDT=TMPtime[1]+" "+TMPtime[2]+" "+TMPtime[3]+", "+TMPtime[4];
	            		var tp=4;
				ImTranslatorBG.THE_URL = decodeURIComponent(ImTranslatorBG.THE_URL);
				var URL_host = decodeURIComponent(host);
				var langS=tmp[0];
				var langD=tmp[1];
	            		ImTranslatorBG.setHistory(URL_host + "~~" + ImTranslatorBG.THE_URL + "~~"+langS+"|"+langD+"~~"+ ImTranslatorBG.THE_URL+"~~"+CurDT+"~~"+tp+"^^");
			}

	},

	TEMP_UPDATE: function(){

       		//!!!!!!!! TEMP blocked starting for 17.12 version.
		ImTranslatorBG.set("SL_SLVoices",1); 
       		//!!!!!!!! TEMP blocked starting for 17.12 version.


		//!!!!!!!! For 17.12 version only. Remove it for 17.13
		var LIST_IT = ImTranslatorBG.get("SL_ALL_PROVIDERS_IT").split(",");
		if(LIST_IT.length<3){
			var IT_out = ImTranslatorBG.get("SL_ALL_PROVIDERS_IT")+",Translator";
			ImTranslatorBG.set("SL_ALL_PROVIDERS_IT", IT_out);
		}
		//!!!!!!!! For 17.12 version only. Remove it for 17.13	


		//!!!!!!!! For 17.11 version  Removed Yandex
		var LIST_GT = ImTranslatorBG.get("SL_ALL_PROVIDERS_GT").split(",");
		var GT_out = "";
		for(var I = 0; I < LIST_GT.length; I++){
			if(LIST_GT[I] != "Yandex") GT_out=GT_out+LIST_GT[I]+",";
		}
		GT_out = GT_out.slice(0, -1);
		ImTranslatorBG.set("SL_ALL_PROVIDERS_GT", GT_out);

		var LIST_BBL = ImTranslatorBG.get("SL_ALL_PROVIDERS_BBL").split(",");
		var BBL_out = "";
		for(var I = 0; I < LIST_BBL.length; I++){
			if(LIST_BBL[I] != "Yandex") BBL_out=BBL_out+LIST_BBL[I]+",";
		}
		BBL_out = BBL_out.slice(0, -1);
		ImTranslatorBG.set("SL_ALL_PROVIDERS_BBL", BBL_out);


		var LIST_IT = ImTranslatorBG.get("SL_ALL_PROVIDERS_IT").split(",");
		var IT_out = "";
		for(var I = 0; I < LIST_IT.length; I++){
			if(LIST_IT[I] != "Yandex") IT_out=IT_out+LIST_IT[I]+",";
		}
		IT_out = IT_out.slice(0, -1);
		ImTranslatorBG.set("SL_ALL_PROVIDERS_IT", IT_out);
		//!!!!!!!! For 17.11 version  Removed Yandex

	    if(ImTranslatorBG.get("SL_DOM") == "cn") ImTranslatorBG.set("SL_DOM", "auto");
	}




}

chrome.storage.local.get("ADV", function(result){
	
	PRESET = result["ADV"];
	if(PRESET !=0 && PRESET !=1) { 
		EXTENSION_DEFAULTS();
		ImTranslatorBG.SET_DEFAULT_DATA();
	}else{
		ImTranslatorBG.GET_STORE_DATA();	
		setTimeout(function(){	
			ImTranslatorBG.init(1);
		},20);
	}
});


function EXTENSION_DEFAULTS(){
	try{
	    var winWidth = 480 ;
	    var winHeight = 650 ;
            var layers="en,zh,zt,cs,nl,tl,fr,de,el,hi,it,ja,ko,pl,pt,ro,ru,sr,es,sv,tr,uk,vi,bg,sk";
	    var SL_PR_ALL = "Microsoft,Translator,Google";
	    var SL_PR_KEYS = "Google:1,Microsoft:0,Translator:0";


	        var BRlanguage = "en";
		var BRloc=chrome.i18n.getUILanguage();

        	BRloc = BRloc.replace("zh-TW","zt");
	        BRloc = BRloc.replace("zh-CN","zh");
	        BRloc = BRloc.replace("fil","tl");

		BRloc=BRloc.substr(0,2);

		if(BRloc!=""){
		   var Arr = LISTofPRpairsDefault.split(",")
		   for(var I=0; I<Arr.length; I++){
	        	var lng = Arr[I].replace("zh-TW","zt");
		        lng = lng.replace("zh-CN","zh");
		   	if(BRloc==lng){
			  BRlanguage=lng;
			  break;
			}
		   }
		}

		var LOC_LANG = BRlanguage;

		if(layers.indexOf(LOC_LANG)==-1) LOC_LANG="en";
	     	BRlanguage = BRlanguage.replace("zh","zh-CN");
	     	BRlanguage = BRlanguage.replace("zt","zh-TW");
            var SL_BR_LN=BRlanguage;
	
	    PACK_PARAMS[0] = "SL_session;0";
//            var version = chrome.runtime.getManifest().version;
//            if(version) PACK_PARAMS[1] = "SL_Version;"+ version;
//	    else	    PACK_PARAMS[1] = "SL_Version;0";
	    PACK_PARAMS[1] = "SL_Version;0";

	    //ADV
	    PACK_PARAMS[2] = "ADV;0";
	    PACK_PARAMS[3] = "FRUN;0";
            PACK_PARAMS[4] = "ran_before;0";
 	    //------------------------------- History ------------------------------------
	    PACK_PARAMS[5] = "SL_History;";
	    PACK_PARAMS[6] = "SL_TH_1;0";
	    PACK_PARAMS[7] = "SL_TH_2;0";
	    PACK_PARAMS[8] = "SL_TH_3;0";
	    PACK_PARAMS[9] = "SL_TH_4;0";
            //------------------------------- option gt ----------------------------------
	    PACK_PARAMS[10] = "SL_global_lng;true";
	    PACK_PARAMS[11] = "SL_Fontsize;17px";
	    PACK_PARAMS[12] = "SL_langSrc;auto";
	    PACK_PARAMS[13] = "SL_langDst;"+ SL_BR_LN;
	    PACK_PARAMS[14] = "SL_no_detect;true";
	    PACK_PARAMS[15] = "SL_other_gt;1";
	    PACK_PARAMS[16] = "SL_dict;true";
	    PACK_PARAMS[17] = "SL_show_back;false";
	    PACK_PARAMS[18] = "SL_show_back2;false";
	    PACK_PARAMS[19] = "SL_HKset;3|90|true";
	    PACK_PARAMS[20] = "SL_HKset_inv;3|90|true";
	    PACK_PARAMS[21] = "SL_langDst_name;Spanish";
	    //??
	    PACK_PARAMS[22] = "SL_Flag;FALSE";
            //------------------------------- option bbl ---------------------------------
	    PACK_PARAMS[23] = "SL_ENABLE;true";
	    PACK_PARAMS[24] = "SL_show_button_bbl;true";
	    PACK_PARAMS[25] = "SL_global_lng_bbl;true";
	    PACK_PARAMS[26] = "SL_Fontsize_bbl;14px";
	    PACK_PARAMS[27] = "SL_langSrc_bbl;auto";
	    PACK_PARAMS[28] = "SL_langDst_bbl;"+ SL_BR_LN;
	    PACK_PARAMS[29] = "SL_no_detect_bbl;true";
	    PACK_PARAMS[30] = "SL_other_bbl;1";
	    PACK_PARAMS[31] = "SL_dict_bbl;true";
	    PACK_PARAMS[32] = "SL_translation_mos_bbl;true";
	    PACK_PARAMS[33] = "SL_pin_bbl;false";

	    PACK_PARAMS[34] = "SL_langDst_name_bbl;Spanish";
	    PACK_PARAMS[35] = "SL_DBL_bbl;false";
	    PACK_PARAMS[36] = "SL_Timing;3";
	    PACK_PARAMS[37] = "SL_Delay;0";

            //------------------------------- option it ----------------------------------
	    PACK_PARAMS[38] = "SL_langSrc_it;auto";
	    PACK_PARAMS[39] = "SL_langDst_it;"+ SL_BR_LN;
	    PACK_PARAMS[40] = "SL_global_lng_it;true";
	    PACK_PARAMS[41] = "SL_style;239e23";
	    PACK_PARAMS[42] = "SL_inject_brackets;true";
	    PACK_PARAMS[43] = "SL_inject_before;false";
	    PACK_PARAMS[44] = "SL_line_break;false";
	    PACK_PARAMS[45] = "SL_whole_word;true";
	    PACK_PARAMS[46] = "SL_hide_translation;false";
	    PACK_PARAMS[47] = "SL_dictionary;true";
	    PACK_PARAMS[48] = "SL_no_detect_it;true";
	    PACK_PARAMS[49] = "SL_other_it;1";
	    PACK_PARAMS[50] = "SL_langDst_name_it;Spanish";
	    PACK_PARAMS[51] = "SL_FK_box1;true";
	    PACK_PARAMS[52] = "SL_FK_box2;true";

            //------------------------------- option wpt ---------------------------------
	    PACK_PARAMS[53] = "SL_global_lng_wpt;true";
	    PACK_PARAMS[54] = "SL_langSrc_wpt;auto";
	    PACK_PARAMS[55] = "SL_langDst_wpt;" + SL_BR_LN;
	    PACK_PARAMS[56] = "SL_langDst_wpt2;" + SL_BR_LN;
	    PACK_PARAMS[57] = "SL_other_wpt;1";
	    PACK_PARAMS[58] = "SL_langDst_name_wpt;Spanish";

	    //-----------------------HK for All Translators-------------------------------
	    PACK_PARAMS[59] = "SL_HK_gt1;Ctrl + Alt + Z";
	    PACK_PARAMS[60] = "SL_HK_gt2;Alt + Z";


	    if(SL_isLinux()==true) PACK_PARAMS[61] = "SL_HK_it1;Ctrl + Alt + C";
	    else PACK_PARAMS[61] = "SL_HK_it1;Alt + C";

	    if(SL_isLinux()==true) PACK_PARAMS[62] = "SL_HK_it2;Ctrl + Alt + X";
	    else PACK_PARAMS[62] = "SL_HK_it2;Alt + X";

	    if(SL_isLinux()==true) PACK_PARAMS[63] = "SL_HK_bb1;Ctrl + Alt";
	    else PACK_PARAMS[63] = "SL_HK_bb1;Alt";

	    PACK_PARAMS[64] = "SL_HK_bb2;Escape";
	    PACK_PARAMS[65] = "SL_HK_bb2box;true";
	    PACK_PARAMS[66] = "SL_HK_wptbox1;true";

	    if(SL_isLinux()==true) PACK_PARAMS[67] = "SL_HK_wpt1;Ctrl + Alt + P";
	    else PACK_PARAMS[67] = "SL_HK_wpt1;Alt + P";

	    PACK_PARAMS[68] = "SL_HK_wptbox2;true";

	    if(SL_isLinux()==true) PACK_PARAMS[69] = "SL_HK_wpt2;Ctrl + Alt + M";
	    else PACK_PARAMS[69] = "SL_HK_wpt2;Alt + M";

	    PACK_PARAMS[70] = "SL_HK_optbox;true";
	    PACK_PARAMS[71] = "SL_HK_opt;Ctrl + Alt + O";
	    PACK_PARAMS[72] = "SL_HK_btnbox;true";

	    if(SL_isLinux()==true) PACK_PARAMS[73] = "SL_HK_btn;Ctrl + Alt + A";
	    else PACK_PARAMS[73] = "SL_HK_btn;Ctrl + Alt + A";

            //--------------------NEW PARAMS PROVIDERs---------------------------------------
	    PACK_PARAMS[74] = "SL_pr_gt;1";
	    PACK_PARAMS[75] = "SL_pr_bbl;1";

	    //??
	    PACK_PARAMS[76] = "SL_Dtext;";

            //********************SET OF THE ADVANCES****************************
	    PACK_PARAMS[77] = "SL_GVoices;1";
//	    PACK_PARAMS[78] = "SL_SLVoices;0";
// TEMP blocked	
	    PACK_PARAMS[78] = "SL_SLVoices;1";
            //********************SET OF THE ADVANCES****************************

	    PACK_PARAMS[79] = "SL_SaveText_box_gt;1";
	    PACK_PARAMS[80] = "SL_SavedText_gt;";
	    PACK_PARAMS[81] = "SL_SaveText_box_bbl;0";
	    PACK_PARAMS[82] = "SL_LNG_LIST;all";
	    PACK_PARAMS[83] = "SL_BACK_VIEW;2";
	    PACK_PARAMS[84] = "SL_BACK_VIEW;2";
	    PACK_PARAMS[85] = "SL_PrefTrans;1";
	    PACK_PARAMS[86] = "SL_CM1;1";
	    PACK_PARAMS[87] = "SL_CM2;1";
	    PACK_PARAMS[88] = "SL_CM3;1";
	    PACK_PARAMS[89] = "SL_CM4;1";
	    PACK_PARAMS[90] = "SL_CM5;1";
	    PACK_PARAMS[91] = "SL_CM6;1";
	    PACK_PARAMS[92] = "SL_CM7;1";
	    PACK_PARAMS[93] = "SL_DOM;auto";
	    PACK_PARAMS[94] = "SL_wptDHist;";
	    PACK_PARAMS[95] = "SL_wptLHist;";
	    PACK_PARAMS[96] = "SL_wptGlobAuto;0";
	    PACK_PARAMS[97] = "SL_wptGlobTb;1";	
	    PACK_PARAMS[98] = "SL_wptGlobTip;1";	
	    PACK_PARAMS[99] = "SL_wptGlobLang;"+ SL_BR_LN;

	    PACK_PARAMS[100] = "SL_ALL_PROVIDERS_GT;"+ SL_PR_ALL;
	    PACK_PARAMS[101] = "SL_ALL_PROVIDERS_BBL;"+ SL_PR_ALL;
	    PACK_PARAMS[102] = "SL_DICT_PRESENT;"+ SL_PR_KEYS;

	    PACK_PARAMS[103] = "SL_ALL_PROVIDERS_IT;"+ SL_PR_ALL;
	    PACK_PARAMS[104] = "SL_BTN_X;0";
	    PACK_PARAMS[105] = "SL_BTN_Y;0";
	    PACK_PARAMS[106] = "SL_BBL_X;0";
	    PACK_PARAMS[107] = "SL_BBL_Y;0";

	    //FORSE BUBBLE
	    PACK_PARAMS[108] = "FORSEbubble;0";

	    //FORMER BBL CS
	    PACK_PARAMS[109] = "TTSvolume;10";
	    PACK_PARAMS[110] = "BL_D_PROV;Google";
	    PACK_PARAMS[111] = "BL_T_PROV;Microsoft";

	    //INLINE FLIP
	    PACK_PARAMS[112] = "INLINEflip;0";

	    //THEME MODE
	    PACK_PARAMS[113] = "THEMEmode;0";

	    //FORMER PLANSHET DIC CS
	    PACK_PARAMS[114] = "PLD_TTSvolume;10";
	    PACK_PARAMS[115] = "PLD_DPROV;Google";
	    PACK_PARAMS[116] = "PLD_OLD_TS;0";
	    PACK_PARAMS[117] = "PLD_DIC_FIRSTRUN;dicdone";

	    //FORMER PLANSHET TRANSLATOR CS
	    PACK_PARAMS[118] = "PLT_TTSvolume;10";
	    PACK_PARAMS[119] = "PLT_PROV;Microsoft";
	    PACK_PARAMS[120] = "PLT_OLD_TS_TR;0";
	    PACK_PARAMS[121] = "PLT_TR_FIRSTRUN;done";
	    PACK_PARAMS[122] = "PLT_LOC;false";
	    PACK_PARAMS[123] = "PLD_LOC;false";

	    //FORMER OPTIONS CS
	    PACK_PARAMS[124] = "SL_anchor;0";
	    PACK_PARAMS[125] = "SL_sort;0";

	    PACK_PARAMS[126] = "AVOIDAUTODETECT;0";
	    PACK_PARAMS[127] = "AVOIDAUTODETECT_LNG;en";

	    PACK_PARAMS[128] = "THE_URL;";
	    PACK_PARAMS[129] = "SL_Import_Report;";
	    PACK_PARAMS[130] = "SL_GWPTHist;";
	    PACK_PARAMS[131] = "SL_BBL_TS;0";
	    PACK_PARAMS[132] = "SL_langSrc2;0";
	    PACK_PARAMS[133] = "SL_langDst2;0";

	    //BBL SESSION RESET 
	    PACK_PARAMS[134] = "SL_langSrc_bbl2;auto";
	    PACK_PARAMS[135] = "SL_langDst_bbl2;"+ SL_BR_LN;
	    PACK_PARAMS[136] = "SL_show_button_bbl2;true";
	    PACK_PARAMS[137] = "SL_Fontsize_bbl2;14px";
	    PACK_PARAMS[138] = "SL_bbl_loc_langs;false";

	    //IT CHANGE LANG  
	    PACK_PARAMS[139] = "SL_change_lang_HKbox_it;true";
	    PACK_PARAMS[140] = "SL_change_lang_HK_it;Alt + S";
	    PACK_PARAMS[141] = "SL_langDst_it2;"+ SL_BR_LN;
	    PACK_PARAMS[142] = "SL_TS;"+ Date.now();

	    //-----------------------LOCALIZATION-------------------------------
	    PACK_PARAMS[143] = "SL_LOCALIZATION;"+ LOC_LANG;

	    PACK_PARAMS[144] = "SL_YKEY;0";
	    PACK_PARAMS[145] = "SL_YHIST;";

	    PACK_PARAMS[146] = "MoveBBLX;0";
	    PACK_PARAMS[147] = "MoveBBLY;0";

	    PACK_PARAMS[148] = "SL_HK_SObox_wpt;true";
	    PACK_PARAMS[149] = "SL_HK_SO_wpt;Alt + W";

	    PACK_PARAMS[150] = "SL_HK_CTbox_wpt;true";
	    PACK_PARAMS[151] = "SL_HK_CT_wpt;Escape";
	    PACK_PARAMS[152] = "SL_WPT_TEMP_LANG;"+ SL_BR_LN;
	    PACK_PARAMS[153] = "SL_FAV_START;10";
	    PACK_PARAMS[154] = "SL_FAV_MAX;3";
	    PACK_PARAMS[155] = "SL_FAV_LANGS_BBL;"+SL_BR_LN;
	    PACK_PARAMS[156] = "SL_FAV_LANGS_IT;"+SL_BR_LN;
	    PACK_PARAMS[157] = "SL_FAV_LANGS_WPT;"+SL_BR_LN;
	    PACK_PARAMS[158] = "SL_FAV_LANGS_IMT;"+SL_BR_LN;
	    PACK_PARAMS[159] = "SL_FAV_TRIGGER;0";
   	    //!!!!!!!! For 17.11 version only. Switch it to 0 for 17.12
	    PACK_PARAMS[160] = "WPTflip;1";//0
   	    //!!!!!!!! For 17.11 version only. Switch it to 0 for 17.12
	    PACK_PARAMS[161] = "SL_GotIt;0";
	    PACK_PARAMS[162] = "SL_UNTRUST;"+DO_NOT_TRUST_WORD+":"+DO_NOT_TRUST_TEXT;
//	    PACK_PARAMS[163] = "WINDOW_TOP;"+(( screen.height - winHeight ) / 2);
//	    PACK_PARAMS[164] = "WINDOW_LEFT;"+(( screen.width - winWidth ) / 2 );
	    PACK_PARAMS[163] = "WINDOW_TOP;100";
	    PACK_PARAMS[164] = "WINDOW_LEFT;100";

	    PACK_PARAMS[165] = "WINDOW_WIDTH;480";
	    PACK_PARAMS[166] = "WINDOW_HEIGHT;650";

	    //NEW WPT
	    PACK_PARAMS[167] = "SL_wpt_MANUAL_MODE_OFF;";
	    PACK_PARAMS[168] = "SL_wpt_MANUAL_MODE_ON;";
	    PACK_PARAMS[169] = "SL_pr_it;1";

	} catch(ex){}
}

function  RESET_SOME_DATA_TO_DEFALT(){
        	NEW_SESSION=1;

		// RESET FORMER CS
			// PL TRANSLATOR
			var GTlist = ImTranslatorBG.get("SL_ALL_PROVIDERS_GT").split(",");
		  	ImTranslatorBG.set("SL_Flag","FALSE");
			var GTprov = "Microsoft";
			if(GTlist.length>0) GTprov = GTlist[0];
			ImTranslatorBG.set("PLT_TTSvolume", 10);
			ImTranslatorBG.set("PLT_PROV", GTprov);
			ImTranslatorBG.set("PLT_OLD_TS_TR", "0");
			ImTranslatorBG.set("PLT_TR_FIRSTRUN", "done");
                        if(ImTranslatorBG.get("SL_no_detect")=="false" && ImTranslatorBG.get("SL_langSrc")!="auto") ImTranslatorBG.set("PLT_LOC", "true");
                        else ImTranslatorBG.set("PLT_LOC", "false");

			// PL DICTIONARY
			ImTranslatorBG.set("PLD_TTSvolume", 10);
//			ImTranslatorBG.set("PLD_DPROV", GTprov);
			ImTranslatorBG.set("PLD_DPROV", "Google");
			ImTranslatorBG.set("PLD_OLD_TS", "0");
			ImTranslatorBG.set("PLD_DIC_FIRSTRUN", "dicdone");
                        if(ImTranslatorBG.get("SL_no_detect")=="false" && ImTranslatorBG.get("SL_langSrc")!="auto") ImTranslatorBG.set("PLD_LOC", "true");
                        else ImTranslatorBG.set("PLD_LOC", "false");

			//IMTRANSLATOR SESSION RESET
			ImTranslatorBG.set("SL_langSrc2", ImTranslatorBG.get("SL_langSrc"));
			ImTranslatorBG.set("SL_langDst2", ImTranslatorBG.get("SL_langDst"));

			// OPTIONS
			ImTranslatorBG.set("SL_anchor", "0");
			ImTranslatorBG.set("SL_sort", "0");

			//BBL SESSION RESET

			var BBLlist = ImTranslatorBG.get("SL_ALL_PROVIDERS_BBL").split(",");
			

			var BBLprov = "Microsoft";
			if(BBLlist.length>0) BBLprov = BBLlist[0];
			ImTranslatorBG.set("BL_T_PROV", BBLprov);
			ImTranslatorBG.set("BL_D_PROV", "Google");
			ImTranslatorBG.set("SL_langSrc_bbl2", ImTranslatorBG.get("SL_langSrc"));
			ImTranslatorBG.set("SL_langDst_bbl2", ImTranslatorBG.get("SL_langDst"));
			ImTranslatorBG.set("SL_Fontsize_bbl2", ImTranslatorBG.get("SL_Fontsize"));
			if(ImTranslatorBG.get("SL_pin_bbl")!="true"){
				ImTranslatorBG.set("SL_BBL_X", 0);
				ImTranslatorBG.set("SL_BBL_Y", 0);
			}
			ImTranslatorBG.set("SL_pin_bbl2",ImTranslatorBG.get("SL_pin_bbl"));

			if(ImTranslatorBG.get("SL_no_detect_bbl") != "true") ImTranslatorBG.set("SL_bbl_loc_langs", "true");
			else ImTranslatorBG.set("SL_bbl_loc_langs", "false");
			ImTranslatorBG.set("SL_show_button_bbl2", ImTranslatorBG.get("SL_show_button_bbl"));
			ImTranslatorBG.set("SL_langDst_it2", ImTranslatorBG.get("SL_langDst_it"));

			//WPT SESSION RESET			
			ImTranslatorBG.set("SL_WPT_TEMP_LANG", ImTranslatorBG.get("SL_langDst_wpt"));

			ImTranslatorBG.set("SL_wpt_MANUAL_MODE_OFF","");
			ImTranslatorBG.set("SL_wpt_MANUAL_MODE_ON","stop");



			// Reset FAVs to default

//			ImTranslatorBG.set("SL_FAV_LANGS_BBL", ImTranslatorBG.get("SL_langDst_bbl"));
//			ImTranslatorBG.set("SL_FAV_LANGS_IT", ImTranslatorBG.get("SL_langDst_it"));
//			ImTranslatorBG.set("SL_FAV_LANGS_IMT", ImTranslatorBG.get("SL_langDst"));
//			ImTranslatorBG.set("SL_FAV_LANGS_WPT", ImTranslatorBG.get("SL_langDst_wpt"));

			var NEW_IT = ImTranslatorBG.get("SL_langDst_it")+","+ImTranslatorBG.get("SL_FAV_LANGS_IT");
			NEW_IT = ImTranslatorBG.uniqFAV(NEW_IT);
			ImTranslatorBG.set("SL_FAV_LANGS_IT", NEW_IT);

			var NEW_BBL = ImTranslatorBG.get("SL_langDst_bbl")+","+ImTranslatorBG.get("SL_FAV_LANGS_BBL");
			NEW_BBL = ImTranslatorBG.uniqFAV(NEW_BBL);
			ImTranslatorBG.set("SL_FAV_LANGS_BBL", NEW_BBL);


			var NEW_WPT = ImTranslatorBG.get("SL_langDst_wpt")+","+ImTranslatorBG.get("SL_FAV_LANGS_WPT");
			NEW_WPT = ImTranslatorBG.uniqFAV(NEW_WPT);
			ImTranslatorBG.set("SL_FAV_LANGS_WPT", NEW_WPT);




/*
			ImTranslatorBG.SL_SAVE_FAVORITE_LANGUAGES(ImTranslatorBG.get("SL_langDst_bbl"),"SL_FAV_LANGS_BBL");
			ImTranslatorBG.SL_SAVE_FAVORITE_LANGUAGES(ImTranslatorBG.get("SL_langDst_it"),"SL_FAV_LANGS_IT");
			ImTranslatorBG.SL_SAVE_FAVORITE_LANGUAGES(ImTranslatorBG.get("SL_langDst_wpt"),"SL_FAV_LANGS_WPT");
*/

			// Reset FAVs to default

			ImTranslatorBG.set("WINDOW_WIDTH", 555);
			ImTranslatorBG.set("WINDOW_HEIGHT", 670); //540;
//	    		ImTranslatorBG.set("WINDOW_TOP", (screen.height - ImTranslatorBG.get("WINDOW_HEIGHT") / 2));
//		    	ImTranslatorBG.set("WINDOW_LEFT", (screen.width - ImTranslatorBG.get("WINDOW_WIDTH") / 2));

}

setTimeout(function(){
    try{
        var SLIDL = setInterval(function(){
		if(CACHE_PACK_PARAMS.length==0) {
			ImTranslatorBG.GET_STORE_DATA();
		} 
	},150);  
    } catch (ex){}	
}, 5);





async function getTranslation(baseUrl, SL_Params) {
   
  var theUrl = baseUrl + "?"+ SL_Params;
  const res = await fetch(
    theUrl,
    {
      headers: {
        Accept:
          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      },
    }
  );
  if (!res.ok) {
    return false;
  } else {
    return res.json();
  }
}

async function getMSkey(baseUrl) {
  const res = await fetch(
    baseUrl,
    {
      headers: {
        Accept:
          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      },
    }
  );
  if (!res.ok) {
    return false;
  } else {
    return res.text();
  }
}




chrome.contextMenus.onClicked.addListener(genericOnClick);
// A generic onclick callback function.
function genericOnClick(info) {
  switch (info.menuItemId) {
    case 'child0':  
    case 'child11':  
	ImTranslatorBG.ContMenuClickNew();
      break;
    case 'child1':
	chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
	    var my_tabid=tabs[0].id;
	    chrome.tabs.sendMessage(my_tabid, {action: 'open_wpt'});  
	}); 
      break;
    case 'child2':  
	chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
	    var my_tabid=tabs[0].id;
	    chrome.tabs.sendMessage(my_tabid, {action: 'open_mo'});  
	}); 
      break;
    case 'child12':
	chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
	    var my_tabid=tabs[0].id;
	    chrome.tabs.sendMessage(my_tabid, {action: 'open_inline'});  
	}); 
	break;
    case 'child13':
	chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
	    var my_tabid=tabs[0].id;
	    chrome.tabs.sendMessage(my_tabid, {action: 'open_bubble'});  
	}); 
	break;
    case 'child14':
	chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
	    var my_tabid=tabs[0].id;
	    chrome.tabs.sendMessage(my_tabid, {action: 'clear_inline'});  
	}); 
	break;
    case 'child3':  ImTranslatorBG.OPEN_OPTIONS("router");
      break;
    default:
      // Standard context menu item function
      //console.log('Standard context menu item clicked.');
  }
}


(async () => {
    let { started } = await chrome.storage.session.get("started");    
    if (started === undefined) {
	NEW_SESSION=1;

	setTimeout(function(){	
		ImTranslatorBG.GET_STORE_DATA();	
	},10);        		
	setTimeout(function(){	
	        RESET_SOME_DATA_TO_DEFALT();
		ImTranslatorBG.init(0);
	},1000);        		
        await chrome.storage.session.set({ started: true });
    }
    else {
	NEW_SESSION=0;
    }
})();

function createSessionId() {

    // Generate a unique identifier for the session

    return Date.now().toString(); 

}



// When the browser window opens, store a new session ID

chrome.windows.onCreated.addListener(() => {
    let sessionId = createSessionId();
    chrome.storage.local.set({ 'AAAAAAAAAAAAAAsessionId': sessionId });	
});



chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.message == 'find_key') {
	ImTranslatorBG.GET_MS_KEY();
  }
  if (request.message == 'get_key') {
	sendResponse({key: ImTranslatorBG.MSKEY});
  }

});



