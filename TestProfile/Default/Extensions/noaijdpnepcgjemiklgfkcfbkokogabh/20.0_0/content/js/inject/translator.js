//'use strict'; 
try{
TranslatorIM = {
	inlinerInjectDictionary:"",
	AKEY: "",
	SL_WPT_ACT_URL: "",
	SL_WPT_METHOD: 1,
	STO: "",
	IT_SRC: "",
	IT_DST: "",
	DOC: FExtension.browserInject.getDocument(),
        SL_WPT_ERROR: 0,
	AVOID_SHADOW_ROOT_TEXT: "",
        SL_UNTRUST_WORD: "",
        SL_UNTRUST_TEXT: "",
	globaltheQ: "",
	ONCE_DETECT: "",
	ONLYONCE: 0,
	CONTROL_SUM: "",
        MoveBBLX: 0,
	MoveBBLY: 0,
	TTS_btn_location: 0,
	TTS_status:"on",
	FlippedByAuto: 0,
        AVOIDAUTODETECT: 0,
        TIMEOUT: "",
	THEMEmode: 0,
	SL_DARK: "invert(95%)",
	SL_LIGHT: "invert(0%)",
	TTSvolume: 1,
	BL_D_PROV: "Google",
	BL_T_PROV: "Google",
	AutoFlipState: 1,
	BBL_RESULT: "",
	BBL_DETECT: "",
        FORSEbubble: 0,
        GlobalCorrectionX: 0,
        GlobalCorrectionY: 0,
        GlobalBoxX: 0,
        GlobalBoxY: 0,
	SL_FRAME: 0,
        SL_DICT_PRESENT: "",
	SL_MODE: "",
	synth: window.speechSynthesis,
	TheVolume: 10,
	TheNewText: "",
	TheNewLang: "",
	TTSbackupLangs: "zh,zt,en,de,hi,id,it,nl,pl,es,ru,ja,ko,fr,pt",
        SL_CNT: 0,
        LISTofPR: {},
	bblLISTofPRpairs: {},
    	invalidElements:  {
      		'APPLET': 1,
      		'AREA': 1,
      		'BASE': 1,
      		'BR': 1,
      		'COL': 1,
      		'B': 1,
      		'HR': 1,
      		'IMG': 1,
      		'INPUT': 1,
      		'IFRAME': 1,
      		'ISINDEX': 1,
      		'LINK': 1,
      		'NOFRAMES': 1,
      		'NOSCRIPT': 1,
      		'META': 1,
      		'OBJECT': 1,
      		'PARAM': 1,
      		'SCRIPT': 1,
      		'STYLE': 1,
      		'SELECT': 1
    	},
	SL_IS_SUBDOMAIN: false,
	SL_GWPT_Show_Hide: 0,
	SL_GWPT_Show_Hide_tmp: 0,
	SL_GWHOST: "",
	SL_DETLANG: "",
	SL_D_List: "",
	SL_L_List: "",

	SL_wptDHist: "",
	SL_wptLHist: "",
	SL_wptGlobAuto: "0",
	SL_wptGlobTb: "0",
	SL_wptGlobTip: "0",
	SL_wptGlobLang: "",

	SL_wptGlobAutoTmp: "0",
	SL_wptGlobTbTmp: "1",
	SL_wptGlobTipTmp: "1",
	SL_wptGlobLangTmp: "",

	//WPT D temp params
	SL_wptDp1: "",
	SL_wptDp2: "0",
	SL_wptDp3: "",
	SL_wptDp4: "0",
	SL_wptDp5: "0",
	SL_wptDp6: "0",

	//WPT L temp params
	SL_wptLp1: "",
	SL_wptLp2: "0",
	SL_wptLp3: "0",
	SL_wptLp4: "0",

	SL_WPT_SKIP: 0,
	SL_WPT_IGRORE: 0,
	SL_WPT_TB_DEFAULT: 0,
    	SL_WPT_TEMP_LANG: "",
    	SL_WPT_LANG: "",
        SL_DOM: "auto",
        SL_LNG_LIST: "",
	SL_LNG_CUSTOM_LIST: "",
	ImTranslator_theurl: ImTranslator_theurl,
        SL_WRONGLANGUAGEDETECTED: 0,
	GTTS_length: 200,
	SLIDL:"",
	SL_DBL_FLAG: 0,
        myWindow:null,
        DELAY:0,
        PROV: "",
	SL_TRIGGER:"TRUE",
        SL_storedSelections: [],
        ListProviders: "",
        SL_SHOW_PROVIDERS: "1",
	SL_FLAG: 0,        
        SL_ONETIMERUN: 0,
	SL_SETINTERVAL_ST: 0,
        SL_SETINTERVAL_PROXY: 0,
	SL_BALLON_W: 450,
	SL_BALLON_H: 85,
	SL_MoveX: "-1000px",
	SL_MoveY: "-1000px",
	SL_Xdelta: 0,
	SL_Ydelta: 0,
	SL_FROMlng: "en",
	SL_TEMP_TEXT: "",
	SL_temp_result: "",
	SL_temp_result2: "",
	SL_Balloon_translation_limit: 5000,
	SL_PLANSHET_LIMIT: 5000,
	SL_GLOBAL_X1: 0,
	SL_GLOBAL_X2: 0,
	SL_GLOBAL_Y1: 0,
	SL_GLOBAL_Y2: 0,
	SL_L: 0,
	SL_T: 0,
	SL_R: 0,
	SL_B: 0,
	SL_NEST: "TOP",
	SL_DETECT: "",
	SL_DETECTED: "",
	SL_IS_DICTIONARY: 0,
        SL_EVENT: window.event,
	SL_KEYCOUNT: { length: 0 },
	SL_KEYSTRING: "",
	SL_TEMPKEYSTRING: "",
	SL_MSG: "",
	SL_TEMPREARTEXT: "",
	//-------------------Globals for TRANSFER from BBL to PLANSHET
	SL_TRANSFER_SRC: "en",
	SL_TRANSFER_DST: "es",
	SL_TRANSFER_DET: "true",
	//-------------------Globals for TRANSFER from BBL to PLANSHET
        SL_dict_bbl: "true",
	//-------------------STORAGE
	SL_ENABLE: false,
	SL_OnOff_BTN: "true",
	SL_OnOff_BTN2: "true",
	SL_OnOff_PIN: "",
	SL_OnOff_HK: "",
	SL_langSrc: "",
	SL_langDst: "",
	SL_FontSize_bbl: "",
	SL_TH_2: "",
	SL_TH_4: "",
	SL_HK: "",
	SL_HK2: "",
	SL_actualkey: "",
	LNGforHISTORY: "",
        Timing: 3,
	Delay: 0,
	//-------------------STORAGE

	//-------------------SESSION
	SL_SID_PIN: "",
	SL_SID_TO: "",
	SL_SID_FROM: "",
	SL_FONT: "",
	SL_FONT2: "",
	SL_FONT_SID: "",
	SL_SID_TEMP_TARGET: "",
	SL_SID_TEMP_SOURCE: "",
	SL_TMPbox: "false",
	SL_bbl_loc_langs: "false",
	SL_pin_bbl2: "false",
	//-------------------SESSION

	//-------------------INLINER
	SL_FK_box1: true,
	SL_inlinerFK1: "Alt",
	SL_inliner: "T",
	SL_FK_box2: true,
	SL_inlinerFK2: "Ctrl",
	SL_clean: "X",
	INLINEflip: 0,
	//-------------------INLINER

	//------------------ NEW HOT KEYS
	SL_BBL_CLOSER: true,
	SL_HK_gt1: "Ctrl + Alt + Z",
	SL_HK_gt2: "Alt + Z",
	SL_HK_it1: "Alt + C",
	SL_HK_it2: "Alt + X",
	SL_HK_bb1: "Alt",
	SL_HK_bb2: "Escape",
	SL_WPT1: "Alt + P",
	SL_WPT2: "Alt + M",
	SL_OPT: "Ctrl + Alt + O",
	SL_WPTbox1: true,
	SL_WPTbox2: true,
	SL_OPTbox: true,
	SOWPTbox: true,
	SOWPT: "Alt + W",
	CTWPTbox: true,
	CTWPT: "Alt + Q",


	//------------------ NEW HOT KEYS

        SL_WPTsrclang: "auto",
        SL_WPTdstlang: "es",
	SL_WPTHosts: "",

	//------------------ DBL bbl
	SL_DBL: false,
	//------------------ DBL bbl

        TempActiveObjId: "",
        DBLClick_tempText: "",

	// CHECKBOX FOR BLANK GT
        SL_GT_INV: true,

        SL_LOC: "en",

	// ADVANCES
	SL_GVoices: "1",
	SL_SLVoices: "0",
	SL_ALLvoices: "",
	// ADVANCES
	
        SL_SAVETEXT: 0,

        GOOGLE_TTS_backup_loader: 0,
        SL_ALL_PROVIDERS_BBL: "Google,Microsoft,Translator,Yandex",
        SL_ALL_PROVIDERS_IT: "",

	SL_WPT_TRG_LNG: "",
	SL_WPT_DET_LNG: "",
	SL_WPT_FLAG: 0,

	// BBL session params
	SL_langSrc_bbl2: "auto",
	SL_langDst_bbl2:  "",
	SL_BBL_COORD_TRIGER: 0,
	SL_Fontsize_bbl2: "",

	// IT change lang
	SL_change_lang_it: 0,
	SL_change_lang_HKbox_it: 1,
	SL_change_lang_HK_it: "Alt + S",
        SL_langDst_it: "en",

	//FAVORITE LANGUAGES
	SL_FAV_START: 10,
	SL_FAV_MAX: 3,
	SL_FAV_LANGS_BBL: "",
	SL_FAV_LANGS_IT: "",
	SL_FAV_LANGS_WPT: "",

	WPTflip: 0,

	SL_HK_SObox_wpt: "",
	SL_HK_SO_wpt: "",
	SL_HK_CTbox_wpt: "",
	SL_HK_CT_wpt: "",

	//VACINE
	SL_wpt_MANUAL_MODE_ON : "",
	SL_wpt_MANUAL_MODE_OFF : "",


	MOver_PROVIDERS:function(e){
	    try{
	        var id = e.target.id.replace("SL_PN","");
		if(e.target.id.indexOf("SL_PN")!=-1){
			var doc = TranslatorIM.DOC;                        
		}
	    } catch(ex){}
	},

	MOut_PROVIDERS:function(e){
	    try{
	        var id = e.target.id.replace("SL_PN","");
		if(e.target.id.indexOf("SL_PN")!=-1){
			var doc = TranslatorIM.DOC;
			TranslatorIM.SL_bring_DOWN();
		}
	    } catch(ex){}
	},


	Click_PROVIDERS:function(e){
	    try{	      
	        var id = e.target.id.replace("SL_PN","");
	        if(e.target.parentNode.className!="SL_BL_LABLE_DEACT"){
			if(id=="BBL_OPT") TranslatorIM.SL_OPEN_BG_OPTIONS('bbl');
			if(id=="HIST_OPT") TranslatorIM.SL_OPEN_BG_OPTIONS('hist');
			if(id=="DONATE_OPT") TranslatorIM.SL_OPEN_BG_OPTIONS('donate');
			if(e.target.id.indexOf("SL_PN")!=-1){
				var doc = TranslatorIM.DOC;

				if(TranslatorIM.SL_MODE==1) TranslatorIM.SL_setTMPdata("BL_D_PROV",TranslatorIM.LISTofPR[id]);
				else TranslatorIM.SL_setTMPdata("BL_T_PROV",TranslatorIM.LISTofPR[id]);

                                setTimeout(function() {
					ImTranslatorDataEvent.mousedown();
					TranslatorIM.SET_FIRST_AVAILABLE_PROV();
					TranslatorIM.SL_bring_UP();
	        	                //TranslatorIM.SL_JUMP(doc);
			      	}, 10);
                                
			}
		}

	    } catch(ex){}
	},

// TOUCT SCREEN
	touchstart:function(e){
	      TranslatorIM.SL_HideButton();
	      TranslatorIM.SL_EVENT=e;
	      TranslatorIM.SL_bring_DOWN();
	},


	touchend:function(e){
     	  var doc = TranslatorIM.DOC;	
          TranslatorIM.SL_BBL_OBJ_OFF(0);
	  if(TranslatorIM.SL_ENABLE == "true"){
	    if(TranslatorIM.GET_TEXT()!=""){
		TranslatorIM.SL_OBJ_BUILDER();
                var COORD = TranslatorIM.TSgetSelectionCoords();
		TranslatorIM.SL_ShowButton();
		var ratioX = document.body.clientWidth / window.innerWidth;
		var ratioY = document.body.clientHeight / window.innerHeight;

	        var theX = (COORD.x/ratioX) + window.pageXOffset;
	        var theY = (COORD.y/ratioY) + window.pageYOffset;

		TranslatorIM.SL_MoveX=Math.ceil(theX) + "px";
		TranslatorIM.SL_MoveY=Math.ceil(theY) + "px";
		var SLdivField = doc.getElementById("SL_button");
		SLdivField.style.left = TranslatorIM.SL_MoveX;
		SLdivField.style.top = TranslatorIM.SL_MoveY;
            } else { 
		if(doc && doc.getElementById("SL_button"))doc.getElementById("SL_button").style.display="none"; 
	    }	
	  }

	},


// TOUCT SCREEN

	dblclick:function(e){
	   try{	
	    var doc = TranslatorIM.DOC;
            if(doc.getElementById("SL_shadow_translator").style.display!="block"){
              var txt=TranslatorIM.GET_TEXT();
              
              if(txt!="")TranslatorIM.DBLClick_tempText=txt;

	      var target = e.target || e.srcElement;
              TranslatorIM.SL_DBL_FLAG=1;

	      if(target.className.toString().indexOf("CodeMirror-")==-1){


		if(TranslatorIM.SL_OnOff_HK=="true" && TranslatorIM.SL_ENABLE=="true"){
	                TranslatorIM.getSelectionCoords(e);
			var DBHOTKEYSline1=TranslatorIM.SL_HK_bb1.replace(" + ",":|").toLowerCase()+":|";
			DBHOTKEYSline1=DBHOTKEYSline1.replace(" + ",":|");
			var HOTKEYSline = TranslatorIM.HOTKEYS_line();
			if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSline1,HOTKEYSline)==true) TranslatorIM.SL_ShowBalloon();
                        
			if(doc.getElementById("SL_balloon_obj")){
				TranslatorIM.SL_LNG_LIST = TranslatorIM.CUSTOM_LANGS(FExtension.element(TranslatorIM.SL_LOC,'extLanguages'));
				TranslatorIM.SL_BBL_OBJ_OFF(0);
				TranslatorIM.SL_OBJ_BUILDER();
			}
		        var ext = FExtension.browserInject;
		  	doc.getElementById('SL_button').style.background='url('+ext.getURL('content/img/util/imtranslator-s.png')+')';
			doc.getElementById('SL_button').style.opacity=100;

		}

		if(TranslatorIM.SL_DBL=="true"){
		    	if(TranslatorIM.ONLYONCE==0){
				TranslatorIM.ONLYONCE = 1;
				setTimeout(function() {TranslatorIM.ONLYONCE = 0;}, 500);
				setTimeout(function() {TranslatorIM.SL_ShowBalloon();}, 50); 	                      	
			}
		}else TranslatorIM.SL_ShowButton();
	      }	
	    }
	  } catch(ex){}
	},

	SL_BTN_mousemove: function(e){
		var id = e.target.id;
	  	if(id=="SL_button") TranslatorIM.unfade();
	},
	SL_BTN_mouseout: function(e){
		TranslatorIM.dofade();
	},

	mousedown: function(e){
		try{
			var target = e.target || e.srcElement;
			var doc = TranslatorIM.DOC;
                        TranslatorIM.FlippedByAuto = 0;
			//EXCEPTIONS
			var ROUT = 0;

			if(e.target.className.indexOf("ytp-fullscreen-button")!=-1) ROUT = 1;
			if(e.target.tagName.toLowerCase()=="button") ROUT = 1;
			if(e.target.tagName.toLowerCase()=="video") ROUT = 1;
			if(e.target.hasAttribute("onclick")==true) ROUT = 1;
			if(e.which == 3) {
				//if(doc.getElementById("SL_shadow_translator").style.display!="block") 
				chrome.runtime.sendMessage({greeting: "RCM:>"}, function(response) {});
			}
			if(e.which != 3 && target.type=="file") ROUT = 1;
			if(e.which == 2) ROUT = 1;

			//EXCEPTIONS

			//IT change target menu

		    	var txt = TranslatorIM.GET_TEXT();
	    		if(txt == "" && TranslatorIM.AVOID_SHADOW_ROOT_TEXT!="") txt=TranslatorIM.AVOID_SHADOW_ROOT_TEXT;
	    		if(txt!=""){		

			        if(e.which != 3){
					if(e.target.id.indexOf("_MENU")==-1) TranslatorIM.CloseIT_target_lang();
					else{
						if(e.target.id!="SL_IT_MENU") e.preventDefault();
						TranslatorIM.SL_addEvent(doc.getElementById("SL_IT_MENU"), 'change', TranslatorIM.SL_IT_retranslate);
						TranslatorIM.SL_addEvent(doc.getElementById("SL_MENU_CLOSE"), 'click', TranslatorIM.SL_IT_retranslate_and_close);
					}
				} else e.preventDefault();

				if(TranslatorIM.SL_SAVETEXT == 1 && TranslatorIM.BL_T_PROV==""){
				    if(TranslatorIM.ListProviders!=""){
					TranslatorIM.SL_BBL_OBJ_OFF(1);
					TranslatorIM.SL_OBJ_BUILDER();
				    }	
				}
			}

			if(e.target.id!="SL_BBL_VOICE" && e.target.id!="SL_TTS_voice")	{TranslatorIM.synth.cancel();TranslatorIM.REMOTE_Voice_Close();}

			if(TranslatorIM.SL_ENABLE == "true"){

	        	     	chrome.runtime.sendMessage({greeting: 1}, function(response) {
       					if(response && response.farewell){

       	        				var theresponse = response.farewell.split("~");
				                var theresponse2 = theresponse[2].split("|");
       				        	TranslatorIM.SL_OnOff_BTN=theresponse2[3];
						TranslatorIM.SL_OnOff_BTN2=theresponse[62];

						TranslatorIM.SL_langSrc_bbl2=theresponse[60];
						TranslatorIM.SL_langDst_bbl2=theresponse[61];
				                TranslatorIM.SL_langSrc=theresponse2[0];
				                TranslatorIM.SL_langDst=theresponse2[1];

						TranslatorIM.SL_bbl_loc_langs=theresponse[65];
						if(TranslatorIM.SL_bbl_loc_langs=="true") TranslatorIM.SL_TMPbox="true";
						else TranslatorIM.SL_TMPbox="false";
						TranslatorIM.SL_Fontsize_bbl2=theresponse[63];
                                                TranslatorIM.SL_FONT_SID=TranslatorIM.SL_Fontsize_bbl2;

						TranslatorIM.SL_ALL_PROVIDERS_BBL=theresponse[42];
						TranslatorIM.SL_LOC=theresponse[22];
						TranslatorIM.SL_LNG_CUSTOM_LIST=theresponse[29];
						TranslatorIM.SL_pin_bbl2=theresponse[69];
                                                TranslatorIM.SL_OnOff_PIN=TranslatorIM.SL_pin_bbl2;
						TranslatorIM.SL_FAV_MAX=theresponse[79];
						TranslatorIM.SL_FAV_LANGS_BBL=theresponse[80];
						TranslatorIM.SL_FAV_LANGS_IT=theresponse[81];
						TranslatorIM.SL_FAV_LANGS_WPT=theresponse[82];
						TranslatorIM.WPTflip=theresponse[83];
	             			}
					TranslatorIM.SL_LNG_LIST = TranslatorIM.CUSTOM_LANGS(FExtension.element(TranslatorIM.SL_LOC,'extLanguages'));
					TranslatorIM.LISTofPR = TranslatorIM.SL_ALL_PROVIDERS_BBL.split(",");


       				});
			}

			if(ROUT == 0){


				//by VK - SENDING A REQUEST TO BG to reset bubble result data exchange buffer ------
			        chrome.runtime.sendMessage({greeting: "TR_STOP:>"}, function(response) {});
	        		//by VK ----------------------------------------------------------------------------
		                TranslatorIM.SL_ONETIMERUN=0;

				if(TranslatorIM.SL_ENABLE == "true"){

					var id = target.id;

					if(target.className.toString().indexOf("CodeMirror-")==-1){
						TranslatorIM.SL_LNG_LIST = TranslatorIM.CUSTOM_LANGS(FExtension.element(TranslatorIM.SL_LOC,'extLanguages'));	       
					        if(e.which != 3){


							if(id == "SL_button"){                                        
								e.preventDefault();
								TranslatorIM.SL_ShowBalloon();
							} else {
								var id2 = TranslatorIM.BBL_IfMouseIsInside(e);

								if(id2==0){
									TranslatorIM.SL_BBL_OBJ_OFF(0);
                                                                        if(doc.location.href.indexOf("rsa.com/") != -1){
										if (window.getSelection().empty) {  // Chrome
											window.getSelection().empty();
										} else if (window.getSelection().removeAllRanges) {  // Firefox
											window.getSelection().removeAllRanges();
										}
									}
								}
							}

							FExtension.browserInject.setEvent(e);
							TranslatorIM.TempActiveObjId = id;                

							if(id == "SLHKclose" || id == "SL_alert_cont" || id == "SL_alert_bbl" || id == "SL_shadow_translation_result" || id == "SL_shadow_translation_result2" || id=="") TranslatorIM.SLShowHideAlert();
							if(id == "SL_BBL_VOICE") {
								TranslatorIM.SL_BBL_VOICE();
							}
							if(id != "SL_button" || id !="SL_TTS_voice" || id !="SL_BBL_VOICE") {

								TranslatorIM.SL_GLOBALPosition(e, 0);
								TranslatorIM.SL_HideButton();
					                	TranslatorIM.SL_EVENT=e;
								if(id.indexOf("SL")==-1 || id=="") TranslatorIM.SL_CloseBalloon();	

							}
							if(id != "SL_button") {
								TranslatorIM.SL_HideButton();
						                TranslatorIM.SL_EVENT=e;
								TranslatorIM.SL_bring_DOWN();
							}
						}else {
							chrome.runtime.sendMessage({greeting: "RCL:>"}, function(response) {}); 
							if(doc.getElementById("SL_button")) doc.getElementById("SL_button").style.display="none"; 
						}

				       } 


				}else TranslatorIM.SL_BBL_OBJ_OFF(0);
			} //else inlinerInjectClean();

		  } catch(ex){}
	          TranslatorIM.CleanUpAll(e);
	},


	
	mouseup:function(e){
	   setTimeout(function() {
		ImTranslatorDataEvent.init();
		if(e.which != 3){
			//EXCEPTIONS
			var ROUT = 0;
			if(e.target){
				if(e.target.tagName.toLowerCase()=="video") ROUT=1;
				if(e.target.tagName.toLowerCase()=="img") ROUT=1;
		                try{
					if(e.target.className.indexOf("ytp-")!=-1) ROUT = 1;
				} catch (e){chrome.runtime.lastError}			
			}
			if(document.location.toString().indexOf("etherpad")!=-1)  ROUT = 1;
			//EXCEPTIONS
			var doc = TranslatorIM.DOC;
			if(e.target.id == "SL_WPT_MENU_CLOSE") {TranslatorIM.closeWPT_ERROR_MSG();}
			if(doc.getElementById("SL_MENU_WPT")){
				if(e.target.id.indexOf("SL_")==-1 && doc.getElementById("SL_MENU_WPT").style.display!='none') {TranslatorIM.closeWPT_ERROR_MSG();}
			}
			if(ROUT==1) TranslatorIM.SL_HideButton();
			else{
                                TranslatorIM.AVOID_SHADOW_ROOT_TEXT="";
				if(TranslatorIM.SL_ENABLE == "true"){
				        TranslatorIM.AVOID_SHADOW_ROOT_TEXT = TranslatorIM.GET_TEXT();
					if(TranslatorIM.GET_TEXT()!=""){		

						try{    				
						        var id = e.target.id;
							if(id.indexOf("SL_")==-1) TranslatorIM.SL_OBJ_BUILDER();

							if(TranslatorIM.SL_SID_TO != "") TranslatorIM.SL_langDst=TranslatorIM.SL_SID_TO;
							else TranslatorIM.SL_langDst=TranslatorIM.SL_langDst_bbl2;
							chrome.runtime.sendMessage({greeting: "CM_BBL:>" + TranslatorIM.SL_langDst}, function(response) {}); 
						} catch (e){chrome.runtime.lastError}	

						if(window.top==window.self)TranslatorIM.SL_FRAME=0;
						else TranslatorIM.SL_FRAME=1;
						var SLdivField = doc.getElementById("SL_shadow_translator");
						if(TranslatorIM.SL_FRAME==1){
							TranslatorIM.SL_EVENT=e;
							TranslatorIM.WINDOW_and_BUBBLE_alignment(doc,SLdivField)
						}
				                TranslatorIM.getSelectionCoords(e);
				                TranslatorIM.unfade();
						var wl = doc.location.href;
						if(wl.indexOf("http")!=-1){
							if(TranslatorIM.SL_SAVETEXT == 1){
							        TranslatorIM.SL_GLOBALPosition(e, 1);
	        						TranslatorIM.SL_EVENT=e;
							        FExtension.browserInject.setEvent(e);
								TranslatorIM.QuickInitTranslators(e);
						                TranslatorIM.SL_GOOGLE_WPT();				
							} else {

								if(SLdivField && SLdivField.style.display!="block"){
							        	TranslatorIM.SL_GLOBALPosition(e, 1);
						        		TranslatorIM.SL_EVENT=e;
								        FExtension.browserInject.setEvent(e);
									TranslatorIM.QuickInitTranslators(e);
						        	        TranslatorIM.SL_GOOGLE_WPT();				
								}
							}
						}


				  	       if(TranslatorIM.SL_OnOff_BTN2=="true") {
						   try{
						        var ext = FExtension.browserInject;
						  	doc.getElementById('SL_button').style.background='url('+ext.getURL('content/img/util/imtranslator-s.png')+')';
							doc.getElementById('SL_button').style.opacity=100;
						   }catch(e){}
						}

				    } else{
					if(TranslatorIM.SL_SAVETEXT == 1 && doc.getElementById("SL_shadow_translator").style.display!="block"){
						TranslatorIM.SL_BBL_OBJ_OFF(1);

					}
			                TranslatorIM.CleanUpAll(e);
				    }
		           } else { 
				if(doc.getElementById("SL_button"))doc.getElementById("SL_button").style.display="none"; 
			   }
		  	}
			var SL_id = e.target.id;
			if(SL_id == "SL_MENU_LINK_OPT") TranslatorIM.SL_OPEN_BG_OPTIONS("it");
			if(SL_id == "SL_MENU_LINK_HIS") TranslatorIM.SL_OPEN_BG_OPTIONS("hist");
	         }
	   }, 10);		
	},


	keydown:function(e){                
		setTimeout(function() {
		        //ALT-Tab handler
			window.onfocus = function() {
			    TranslatorIM.SL_KEYSTRING="";
			    TranslatorIM.SL_TEMPKEYSTRING="";
			}
			//---------------
/*
			if(e.key==TranslatorIM.SL_HK_bb2){
				TranslatorIM.REMOTE_Voice_Close();
		 	        var doc = TranslatorIM.DOC;       
				if(TranslatorIM.SL_BBL_CLOSER=="true"){
					TranslatorIM.SL_CloseBalloonWithLink();
				} else {
					TranslatorIM.SL_BBL_OBJ_OFF(0);
				}


			//IT change target menu
				if(doc.getElementById("SL_MENU")) TranslatorIM.SL_IT_retranslate_and_close();


			}else{
*/
			    	if(!TranslatorIM.SL_KEYCOUNT[e.keyCode] && TranslatorIM.SL_KEYCOUNT.length<3)   {
        				TranslatorIM.SL_KEYCOUNT[e.keyCode] = true;
				        TranslatorIM.SL_KEYCOUNT.length++;
					TranslatorIM.SL_KEYSTRING=TranslatorIM.SL_KEYSTRING+e.keyCode+":|";
                			if(TranslatorIM.SL_KEYSTRING!="") {TranslatorIM.SL_TEMPKEYSTRING=TranslatorIM.SL_KEYSTRING;TranslatorIM.SL_CNT=0;}
				}
//			}
		}, 100);		
        },



	keyup:function(e){ 
		if(e.key=="Escape") {
			TranslatorIM.CloseAnyOpenTranslator();			
		}
		TranslatorIM.QuickInitTranslators(e);
		var HOTKEYSline = TranslatorIM.HOTKEYS_line();
		if(TranslatorIM.SL_MSG.indexOf("~")!=-1){
			var theresponse = TranslatorIM.SL_MSG.split("~");

			var theresponse2 = theresponse[1].split("|");
			var thekey4 = theresponse2[1];
			var theresponse4 = theresponse[4].split("|");
			var INLINER_CLEAN_ONOFF = theresponse4[0];
			var BUBBLE_CLEAN_ONOFF = theresponse[45];
		
			var INL_CL_HK1 = theresponse4[1];
			var INL_CL_HK2 = theresponse4[2];


			//WPT
			if(TranslatorIM.SL_WPT1=="") TranslatorIM.SL_WPTbox1="false";
			var DBHOTKEYSlineWPT1=TranslatorIM.SL_WPT1.replace(/ \+ /g,":|").toLowerCase()+":|";
       			DBHOTKEYSlineWPT1=DBHOTKEYSlineWPT1.replace(/ \+ /g,":|");
			if(TranslatorIM.SL_WPTbox1 == "true"){
	                        if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSlineWPT1,HOTKEYSline)==true) TranslatorIM.SL_WPT(0);
	                }

			//WPT MO
			if(TranslatorIM.SL_WPT2=="") TranslatorIM.SL_WPTbox2="false";
			var DBHOTKEYSlineWPT2=TranslatorIM.SL_WPT2.replace(/ \+ /g,":|").toLowerCase()+":|";
       			DBHOTKEYSlineWPT2=DBHOTKEYSlineWPT2.replace(/ \+ /g,":|");
			if(TranslatorIM.SL_WPTbox2 == "true"){
	                        if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSlineWPT2,HOTKEYSline)==true) TranslatorIM.SL_WPT(1);
	                }

			//OPT
			if(TranslatorIM.SL_OPT=="") TranslatorIM.SL_OPTbox="false";
			var DBHOTKEYSlineOPT=TranslatorIM.SL_OPT.replace(/ \+ /g,":|").toLowerCase()+":|";
       			DBHOTKEYSlineOPT=DBHOTKEYSlineOPT.replace(/ \+ /g,":|");
			if(TranslatorIM.SL_OPTbox == "true"){                                       
	                        if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSlineOPT,HOTKEYSline)==true) TranslatorIM.SL_OPEN_BG_OPTIONS("");
	                }

			//ImTranslator Blank
			if(TranslatorIM.SL_HK_gt2=="") TranslatorIM.SL_GT_INV="false";
			var DBHOTKEYSline1=TranslatorIM.SL_HK_gt2.replace(/ \+ /g,":|").toLowerCase()+":|";
      			DBHOTKEYSline1=DBHOTKEYSline1.replace(/ \+ /g,":|");
			if(TranslatorIM.SL_GT_INV == "true"){
				if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSline1,HOTKEYSline)==true) setTimeout(function() {TranslatorIM.HotKeysWindow(e,0);}, 100);
			}

			//Inline clean
			if(TranslatorIM.SL_HK_it2=="") INLINER_CLEAN_ONOFF="false";
			var DBHOTKEYSline2=TranslatorIM.SL_HK_it2.replace(/ \+ /g,":|").toLowerCase()+":|";
	       		DBHOTKEYSline2=DBHOTKEYSline2.replace(/ \+ /g,":|");
			if(INLINER_CLEAN_ONOFF=="true"){
				if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSline2,HOTKEYSline)==true) inlinerInjectClean();
			}

			//BUBBLE close
			if(TranslatorIM.SL_HK_bb2==""){ BUBBLE_CLEAN_ONOFF="false"}
			var DBHOTKEYSline2=TranslatorIM.SL_HK_bb2.replace(/ \+ /g,":|").toLowerCase()+":|";
		       	DBHOTKEYSline2=DBHOTKEYSline2.replace(/ \+ /g,":|");
			if(BUBBLE_CLEAN_ONOFF=="true"){
				if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSline2,HOTKEYSline)==true){
					TranslatorIM.REMOTE_Voice_Close();
			        	var doc = TranslatorIM.DOC;       
					if(TranslatorIM.SL_BBL_CLOSER=="true"){
						TranslatorIM.SL_CloseBalloonWithLink();
					} else {
						TranslatorIM.SL_BBL_OBJ_OFF(0);
					}
					setTimeout(function() {
						// EXCEL handler
					    try{
						doc.getElementById(e.target.id).focus();
					    } catch(ex){}
					}, 1000);



				}
			}

			//WPT SHOW ORIGINAL
			if(TranslatorIM.SOWPT=="") TranslatorIM.SOWPTbox="false";
			var DBHOTKEYSlineSOWPT=TranslatorIM.SOWPT.replace(/ \+ /g,":|").toLowerCase()+":|";
       			DBHOTKEYSlineSOWPT=DBHOTKEYSlineSOWPT.replace(/ \+ /g,":|");
			if(TranslatorIM.SOWPTbox == "true"){
	                        if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSlineSOWPT,HOTKEYSline)==true) TranslatorIM.SL_SHOW_ORIGINAL();
	                }

			//WPT CLOSE TRANSLATION
			if(TranslatorIM.CTWPT=="") TranslatorIM.CTWPTbox="false";
			var DBHOTKEYSlineCTWPT=TranslatorIM.CTWPT.replace(/ \+ /g,":|").toLowerCase()+":|";
       			DBHOTKEYSlineCTWPT=DBHOTKEYSlineCTWPT.replace(/ \+ /g,":|");
			if(TranslatorIM.CTWPTbox == "true"){
	       			HOTKEYSline=HOTKEYSline.replace(/escape:/g,"esc:");
                                DBHOTKEYSlineCTWPT=DBHOTKEYSlineCTWPT.replace(/escape:/g,"esc:");
	                        if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSlineCTWPT,HOTKEYSline)==true) TranslatorIM.CloseAnyOpenTranslator();
	                }


		}
		TranslatorIM.SL_closer(e);
        },

	QuickInitTranslators: function(e){
 	        var doc = TranslatorIM.DOC;       
                var HOTKEYSline = TranslatorIM.HOTKEYS_line();
		setTimeout(function() {
		  try{
		    if(TranslatorIM.SL_MSG!="" || TranslatorIM.SL_MSG!="undefuned"){
			var theSLtext = window.getSelection().toString();
			theSLtext = theSLtext.replace(/(^\s+|\s+$)/g, '');

			var theresponse = TranslatorIM.SL_MSG.split("~");
			var theresponse1 = theresponse[0].split("|");
			var thekey2 = theresponse1[1];

                        if(theresponse[3].indexOf("|")!=-1){
				var theresponse3 = theresponse[3].split("|");
				var INLINER_ONOFF = theresponse3[0];
				var INL_HK1 = theresponse3[1];
				var INL_HK2 = theresponse3[2];
				var theresponse4 = theresponse[4].split("|");
			}

			//Balloon
			if(TranslatorIM.SL_HK_bb1=="") TranslatorIM.SL_OnOff_HK = "false";
                        var SLdivField = doc.getElementById("SL_shadow_translator");

			if(TranslatorIM.SL_SAVETEXT==0){
				if(SLdivField && SLdivField.style.display!="block"){
					var DBHOTKEYSline1=TranslatorIM.SL_HK_bb1.replace(/ \+ /g,":|").toLowerCase()+":|";
					DBHOTKEYSline1=DBHOTKEYSline1.replace(/ \+ /g,":|");
				} else DBHOTKEYSline1="";
			} else {
				var DBHOTKEYSline1=TranslatorIM.SL_HK_bb1.replace(/ \+ /g,":|").toLowerCase()+":|";
				DBHOTKEYSline1=DBHOTKEYSline1.replace(/ \+ /g,":|");
			}

			//ImTranslator Blank
			if(TranslatorIM.SL_HK_gt1=="") theresponse1[2] = "false";
			if(theSLtext!=""){
				var DBHOTKEYSline2=TranslatorIM.SL_HK_gt1.replace(/ \+ /g,":|").toLowerCase()+":|";
				DBHOTKEYSline2=DBHOTKEYSline2.replace(/ \+ /g,":|");
			}

			//Inline Translation
			if(TranslatorIM.SL_HK_it1=="") INLINER_ONOFF = "false";
			var DBHOTKEYSline3=TranslatorIM.SL_HK_it1.replace(/ \+ /g,":|").toLowerCase()+":|";
			DBHOTKEYSline3=DBHOTKEYSline3.replace(/ \+ /g,":|");

			//Inline Translation with target lang selection
			var DBHOTKEYSline4=TranslatorIM.SL_change_lang_HK_it.replace(/ \+ /g,":|").toLowerCase()+":|";
			DBHOTKEYSline4=DBHOTKEYSline4.replace(/ \+ /g,":|");


			if(theSLtext!=""){

			   	if(TranslatorIM.SL_OnOff_BTN2=="true" && theSLtext.indexOf("Google - Map Data")==-1 && theSLtext!="." && theSLtext!="," && theSLtext!="?" && theSLtext!="!" && theSLtext!=":" && theSLtext!=";" && theSLtext!="-"){
				 	if(TranslatorIM.SL_ENABLE=="true"){
						if(TranslatorIM.TempActiveObjId!="SL_button")	TranslatorIM.SL_ShowButton();
					}
				}



				if((TranslatorIM.SL_OnOff_HK=="true" && TranslatorIM.SL_ENABLE=="true") && TranslatorIM.FORSEbubble!=1){
					if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSline1,HOTKEYSline)==true){
						if(doc.getElementById("SL_balloon_obj")){
							TranslatorIM.SL_LNG_LIST = TranslatorIM.CUSTOM_LANGS(FExtension.element(TranslatorIM.SL_LOC,'extLanguages'));
							TranslatorIM.SL_BBL_OBJ_OFF(0);
							TranslatorIM.SL_OBJ_BUILDER();
						} 
						TranslatorIM.SL_ShowBalloon();
					}
				}
				if(TranslatorIM.FORSEbubble==1){
					if(doc.getElementById("SL_balloon_obj")){
						TranslatorIM.SL_LNG_LIST = TranslatorIM.CUSTOM_LANGS(FExtension.element(TranslatorIM.SL_LOC,'extLanguages'));
						TranslatorIM.SL_BBL_OBJ_OFF(0);
						TranslatorIM.SL_OBJ_BUILDER();
					}
					TranslatorIM.SL_ShowBalloon();
				}
			}	
			if(theresponse1[2]=="true"){
				if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSline2,HOTKEYSline)==true) TranslatorIM.HotKeysWindow(e, 1);
			}

			if(INLINER_ONOFF=="true"){
				if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSline3,HOTKEYSline)==true){
					if(TranslatorIM.SL_ONETIMERUN==0) {runinliner();TranslatorIM.SL_ONETIMERUN=1;}
			        }
			}
			if(theresponse[66]=="true" && theresponse[67]!=""){
        				if(TranslatorIM.SL_SYNC_FILTER(DBHOTKEYSline4,HOTKEYSline)==true) {
					if(TranslatorIM.SL_ONETIMERUN==0) {TranslatorIM.InitiateIT_target_lang();/*runinliner();*/TranslatorIM.SL_ONETIMERUN=1;}
				}
			}


			
		    }	
		  }catch(e){
			//alter(e);
		  }
		}, 20); //VK: was 200 
		setTimeout(function() {
			TranslatorIM.SL_closer(e);
			HOTKEYSline="";
		}, 500);
	},

	SL_SYNC_FILTER: function (l1,l2){
		if(l1=="auto translate:|") return true;
	        if(l1!=":|"){
		        var LINE1 = l1.split(":|");
		        var LINE2 = l2.split(":|");
	        	var CNT1 = LINE1.length-1;
		        var CNT2 = LINE2.length-1; 
		        var cnt=0;
                	var CNTlimit=3;
		        if(CNT1 == CNT2){
				CNTlimit = CNT1;
	        		for(var i=0; i<CNT1; i++){
		        		for(var j=0; j<CNT2; j++){
						if(LINE1[i]==LINE2[j]){
							cnt++; 	
						}
					}
				}
			}
			if(cnt>=CNTlimit) return true;
			else return false;
		} else {
		 if(l2=="") return true;
		 else return false;
		}
	},

	SL_closer:function(e){
		setTimeout(function() {TranslatorIM.SL_KEYCOUNT = { length: 0 }; TranslatorIM.SL_KEYSTRING="";TranslatorIM.SL_TEMPKEYSTRING="";}, 300);
        },


	HOTKEYS_line: function(){
                TranslatorIM.SL_TEMPKEYSTRING=TranslatorIM.SL_TEMPKEYSTRING.replace("18:|","Alt:|");
                TranslatorIM.SL_TEMPKEYSTRING=TranslatorIM.SL_TEMPKEYSTRING.replace("17:|","Ctrl:|");
                TranslatorIM.SL_TEMPKEYSTRING=TranslatorIM.SL_TEMPKEYSTRING.replace("16:|","Shift:|");
                TranslatorIM.SL_TEMPKEYSTRING=TranslatorIM.SL_TEMPKEYSTRING.replace("27:|","Escape:|");
		var TMP1= TranslatorIM.SL_TEMPKEYSTRING.split(":|");
		var NUM = TMP1.length-1;
		var HOTKEY = Array();
		var HOTKEYSline="";
		var cnt=0;
		for(var x=0; x<NUM; x++){
		    if(TMP1[x]!="Alt" && TMP1[x]!="Ctrl" && TMP1[x]!="Shift" && TMP1[x]!="Escape") HOTKEY[x]=String.fromCharCode(TMP1[x]);
		    else HOTKEY[x]=TMP1[x];
                    HOTKEYSline=HOTKEYSline+HOTKEY[x]+":|";
                    if(TMP1[x]=="Alt")cnt++;
                    if(TMP1[x]=="Ctrl")cnt++;
                    if(TMP1[x]=="Escape")cnt++;
		}
		if(cnt==2){
                  HOTKEYSline=HOTKEYSline.replace("Alt:|","");
                  HOTKEYSline=HOTKEYSline.replace("Ctrl:|","");
                  HOTKEYSline="Ctrl:|Alt:|"+HOTKEYSline;
		}
		return HOTKEYSline.toLowerCase();
	},


	SL_setTMPdata: function(name, value) {
       		chrome.runtime.sendMessage({greeting: "SAVE_DATA:>"+name+":"+value}, function(response) {});
		switch(name){
		 	case "BL_T_PROV": TranslatorIM.BL_T_PROV=value; break;
		 	case "BL_D_PROV": TranslatorIM.BL_D_PROV=value; break;
		 	case "TTSvolume": TranslatorIM.TTSvolume=value; break;
		}
	},

	init: function(){
   	   var doc = TranslatorIM.DOC;	   

      	
        	doc.addEventListener('mousedown', TranslatorIM.mousedown,!1);
        	doc.addEventListener('dblclick', TranslatorIM.dblclick,!1);

	        doc.addEventListener('mouseup', TranslatorIM.mouseup,!1);

        	doc.addEventListener('keydown', TranslatorIM.keydown,!1);
        	doc.addEventListener('keyup', TranslatorIM.keyup,!1);


        	doc.addEventListener('touchstart', TranslatorIM.touchstart,!1);
        	doc.addEventListener('touchend', TranslatorIM.touchend,!1);


        	doc.addEventListener('mouseover', TranslatorIM.MOver_PROVIDERS,!1);
        	doc.addEventListener('mouseout', TranslatorIM.MOut_PROVIDERS,!1);
        	doc.addEventListener('click', TranslatorIM.Click_PROVIDERS,!1);



		try{
			top.onload = function () {
			  const TOmins = 60 * 5;
			  TranslatorIM.startTimer(TOmins);
			};
		}catch(e){}


	
		(function(){                 


			var SL_d=!0,SL_e=null,SL_g=!1,SL_j,
			SL_k=function(SL_a){
				return SL_a.replace(/^\s+|\s+$/g,"")
			},
			SL_o=function(SL_a,SL_b){
				return function(){
					return SL_b.apply(SL_a,arguments)
					}
			 },
			 SL_p=function(SL_a){
			  if(SL_a&&SL_a.tagName){
				  var SL_b=SL_a.tagName.toLowerCase();
				  if("input"==SL_b||"textarea"==SL_b)
					  return SL_d;
			  }
			  for(;SL_a;SL_a=SL_a.parentNode)
				  if(SL_a.isContentEditable)
					  return SL_d;
			  	   return SL_g;
			  },
			  SL_r=/[0-9A-Za-z]/,
			  SL_A=function(){
				  FExtension.browserInject.extensionSendRequest({type:"initialize"},SL_o(this,
				  function(SL_a){
					  this.SL_B=SL_a.instanceId;
					  FExtension.browserInject.addOnRequestListener(SL_z);

				  })
			  )}
			  var SL_x=function(SL_a,SL_b,SL_c){
				  TranslatorIM.DOC.addEventListener?SL_c.addEventListener(SL_a,SL_b,SL_g):SL_c.attachEvent("on"+SL_a,SL_b)
			  },
			  SL_w=function(){};
			  var SL_z=function(SL_a,SL_b,SL_c){
		                      "get_selection"==SL_a.type&&(SL_a=SL_k(TranslatorIM.GET_TEXT()))&&SL_c({selection:SL_a})
			  };
			  window.SLInstance=new SL_A;  

/*
			  try{
				if(document.location.href.indexOf('acid3.acidtests.org')!=-1){
					setTimeout('TranslatorIM.SL_OBJ_BUILDER()',1000); 
				} else TranslatorIM.SL_OBJ_BUILDER();
			  }catch(e){
				//alter(e);
			  }

*/

			  chrome.runtime.sendMessage({greeting: 1}, function(response) {
				  FExtension.browserInject.setStyle();
		      });

		})();


	},


    addEvent: function (element, eventName, callback) {
        if (element.addEventListener) {
            element.addEventListener(eventName, callback, false);
        } else if (element.attachEvent) {
            element.attachEvent("on" + eventName, callback);
        }
    },

	
	SL_Links: function(ob,todo){
		TranslatorIM.DOC.getElementById(ob).style.display=todo;
	},
/*
	SL_Hider: function(){
		if(TranslatorIM.DOC.getElementById("SL_shadow_translator")){
			TranslatorIM.DOC.getElementById("SL_shadow_translator").style.display='none';
		}
	},
*/
	StartImTranslatorWindow: function(){
		 var tmpSLstr = TranslatorIM.GET_TEXT();
		 if(tmpSLstr=="")  tmpSLstr=" ";

		 chrome.runtime.sendMessage({greeting: tmpSLstr}, function(response) {
			 //chrome.runtime.sendMessage({greeting: tmpSLstr}, function(response) {
             if(response){
			    //console.log(response.farewell);
             }
		 });
	},

	//---------------BUTTON

	SL_ShowButton: function(){
         clearTimeout(TranslatorIM.TIMEOUT);
	 TranslatorIM.TIMEOUT = setTimeout(function() {
	   if(TranslatorIM.SL_OnOff_BTN2 == "true"){
	        var doc = TranslatorIM.DOC;
		 if(TranslatorIM.SL_SAVETEXT == 0){
			if(doc.getElementById('SL_shadow_translator') && doc.getElementById('SL_shadow_translator').style.display!="block"){
				TranslatorIM.SL_ShowButtonEXEC(doc);
			}
		 } else TranslatorIM.SL_ShowButtonEXEC(doc);	 	
	   }
	 }, TranslatorIM.Delay*1000);
	},


	SL_ShowButtonEXEC: function(doc){
	  	TranslatorIM.dofade();
		   if(doc.getElementById("SL_shadow_translator")){
			if(doc.getElementById("SL_shadow_translator").style.backgroundColor==''){
				var theSLtext=TranslatorIM.GET_TEXT();
				if(theSLtext!=""){
					doc.getElementById("SL_shadow_translator").style.backgroundColor="";					
					doc.getElementById('SL_button').style.display="block";
					doc.getElementById('SL_button').style.opacity=1;
				    	TranslatorIM.SL_addEvent(doc.getElementById('SL_button'), 'mousemove', TranslatorIM.SL_BTN_mousemove);
				    	TranslatorIM.SL_addEvent(doc.getElementById('SL_button'), 'mouseover', TranslatorIM.SL_BTN_mousemove);
				    	TranslatorIM.SL_addEvent(doc.getElementById('SL_button'), 'mouseout', TranslatorIM.SL_BTN_mouseout);
		        	        if(TranslatorIM.SL_DBL_FLAG==1){
					   var TN = TranslatorIM.SL_EVENT.target.tagName.toLowerCase();
					   if(TN == "input" || TN == "textarea"){
					     var corrector=-3;
					     TranslatorIM.SL_GLOBAL_Y1=TranslatorIM.SL_GLOBAL_Y1+corrector;
					     TranslatorIM.SL_GLOBAL_Y2=TranslatorIM.SL_GLOBAL_Y2+corrector;
					   }
					   TranslatorIM.SL_DBL_FLAG=0;
					}
					TranslatorIM.SL_GetButtonCurPosition(TranslatorIM.SL_GLOBAL_X1, TranslatorIM.SL_GLOBAL_Y1, TranslatorIM.SL_GLOBAL_X2, TranslatorIM.SL_GLOBAL_Y2);
				} else doc.getElementById('SL_button').style.display="none";
			}
		   }
	},

	SL_HideButton: function(){
	         var doc = TranslatorIM.DOC;
		 var SLdivField=doc.getElementById("SL_button");
		 if(SLdivField){
			 TranslatorIM.SL_addEvent(SLdivField, 'mouseover', TranslatorIM.SL_addButtonColor);
			 TranslatorIM.SL_addEvent(SLdivField, 'mouseout', TranslatorIM.SL_removeButtonColor);
			 SLdivField.style.display="none"; 		   
		 }
	},



	SL_addButtonColor: function() {
		TranslatorIM.unfade();
	},
	SL_removeButtonColor: function() {
		TranslatorIM.fade();
	},



	SL_GetButtonCurPosition: function (X1,Y1,X2,Y2) {
	        var doc = TranslatorIM.DOC;
	        var SLdivField = doc.getElementById("SL_button");

                var delta1=-25;
                if(X1<X2) delta1=10;
                var delta2=-5;

              //  if(Y1<Y2) delta2=10;
                var pos = "top";
                if(Y1<Y2) pos="bottom";

                //VK BUTTON MOVER

                var correctionX = Math.ceil(TranslatorIM.GlobalCorrectionX/2);
                var correctionY = Math.ceil(TranslatorIM.GlobalCorrectionY/2);

		if(PLATFORM=="Opera"){
			if(correctionY==0) correctionY = correctionY-10;
		}else{
			if(correctionX==0) correctionX = correctionX-15;
		}

                if(pos=="top"){
	                //correctionX = correctionX * -1;
        	        correctionY =  correctionY * -1;
		}
                var AL = TranslatorIM.SL_AlignCoordL(doc,delta1,correctionX);
                var AT = TranslatorIM.SL_AlignCoordT(doc,delta2,correctionY);

		var bodyScrollLeft = doc.documentElement.scrollLeft || doc.body.scrollLeft;
		var NEWleft = ((X2-delta2+AL)+correctionX);

		if(delta2<0){
			if((bodyScrollLeft+window.innerWidth-40)<=NEWleft) NEWleft=((bodyScrollLeft+window.innerWidth)-40);
		}

		if(NEWleft<5) NEWleft=(bodyScrollLeft+5);
	        SLdivField.style.left = NEWleft+"px";

		var bodyScrollTop = doc.documentElement.scrollTop || doc.body.scrollTop;

		//NEW BUTTON CORRECTION
		correctionY = correctionY-7; 
		//-----------------------

		
	       	if(pos=="top"){
	        	SLdivField.style.top = ((Y2+delta1+AT)+correctionY)+"px";
        		if(((Y2+delta1+AT)+correctionY)<=bodyScrollTop)	SLdivField.style.top = (bodyScrollTop+2)+"px";
        		if(((Y2+delta1+AT)+correctionY)>=(bodyScrollTop+window.innerHeight-25))	SLdivField.style.top = (bodyScrollTop+window.innerHeight-25)+"px";
		} else {
			if(correctionY<0){
				SLdivField.style.top = ((Y2-delta1-AT)-correctionY)+"px";
	        		if(SLdivField.style.top.replace("px","")>=(bodyScrollTop+window.innerHeight-25)){
					SLdivField.style.top = (bodyScrollTop+window.innerHeight-45)+"px";
				}
			}else{
				SLdivField.style.top = ((Y2-AT)-correctionY)+"px";
				if((Y1-delta1-AL-TranslatorIM.GlobalCorrectionY)<=(bodyScrollTop)) SLdivField.style.top = (bodyScrollTop+2)+"px";
			}
		}



	},

        SL_AlignCoordT: function(doc,delta,correction){
		var T=0;
		var bodyScrollTop = doc.documentElement.scrollTop || doc.body.scrollTop;
		if(correction>0){
			if(bodyScrollTop>(TranslatorIM.SL_T+bodyScrollTop+delta) && delta < 0){
				if(correction>25) T=correction;
				else              T=25;
			}
			var screen = window.innerHeight;
			var r = (TranslatorIM.SL_B+bodyScrollTop+correction-(bodyScrollTop+screen));
			if(r<0)	if((bodyScrollTop+screen)<(TranslatorIM.SL_B+bodyScrollTop+correction) ) T=correction+delta-r;
			if(T==0) T = T + correction;
			else{
				if(T==10) T = -5;
			}
		}else{
			var r = correction+TranslatorIM.SL_T+bodyScrollTop-bodyScrollTop;
			if(bodyScrollTop>(TranslatorIM.SL_T+bodyScrollTop+correction)) T=correction-r-delta*2;
			else T=correction; 
		}
		return(T);
	},

        SL_AlignCoordL: function(doc,delta,correction){
		var L=delta;
		var bodyScrollLeft = doc.documentElement.scrollLeft || doc.body.scrollLeft;
		if(correction>=0){
			if(bodyScrollLeft<(TranslatorIM.SL_R+bodyScrollLeft)) L=correction;
			var screen = window.innerWidth;
			r = TranslatorIM.SL_R+bodyScrollLeft+correction-(bodyScrollLeft+screen);
			if(r>delta) r=delta*2;			
			if((bodyScrollLeft+screen)<(TranslatorIM.SL_R+bodyScrollLeft+correction-delta)){
				L=correction+r;
			}
		}else{
			L=correction; 
			if(bodyScrollLeft>(TranslatorIM.SL_R+bodyScrollLeft+correction)) L=5;
			if(TranslatorIM.SL_L<Math.abs(correction)) L=5;
		}
		return(L);
	},

	SL_GLOBALPosition: function(e, state) {

		if(!e) e = TranslatorIM.SL_EVENT;
	        var doc = TranslatorIM.DOC;
		var posx = 0;
		var posy = 0;
		if (!e) var e = window.event;

		if(e){
			if (e.pageX || e.pageY){
				posx = e.pageX;
				posy = e.pageY;
			}
			else if (e.clientX || e.clientY){
				posx = e.clientX + doc.body.scrollLeft + doc.documentElement.scrollLeft;
				posy = e.clientY + doc.body.scrollTop + doc.documentElement.scrollTop;
			}
		}


		if(state==0){
			TranslatorIM.SL_GLOBAL_X1 = posx;
			TranslatorIM.SL_GLOBAL_Y1 = posy;
		}else{
			TranslatorIM.SL_GLOBAL_X2 = posx;
			TranslatorIM.SL_GLOBAL_Y2 = posy;
		}
	},
	//---------------BUTTON
	//---------------BALLOON
        SL_quikCloseBalloon: function(){
		TranslatorIM.SL_removeBalloonColor();
		TranslatorIM.SL_CloseBalloon();
	},

	SL_ShowBalloon: function(){

		TranslatorIM.SL_BBL_locer_settler();
	        TranslatorIM.SL_HideButton();

	        var doc = TranslatorIM.DOC;
		try{
			doc.onmousemove = null;			
		}catch(e){}

		//HANDLER: http://www.legislation.gov.uk/ukpga/2008/22/contents
		var theurl = String(doc.location);
		if(doc.body.innerHTML.indexOf("/1999/xhtml")!=-1 && theurl.indexOf("legislation.gov.uk")!=-1) {	
			//runinliner();
			var theSLtext = TranslatorIM.GET_TEXT();
			if(theSLtext=="" && TranslatorIM.DBLClick_tempText!="") theSLtext = TranslatorIM.DBLClick_tempText;
		        chrome.runtime.sendMessage({greeting: "PUSH:>"+theSLtext}, function(response) {});
			return false;
		}
   		//-------------------------------------------------------------

		var SL_tb = doc.getElementById("SL_TB");
		var SLdivField = doc.getElementById("SL_shadow_translator");
		var SLdivField2 = doc.getElementById("SL_button");
		SLdivField2.style.display = "none";

                if(TranslatorIM.SL_TRIGGER=="FALSE"){
			doc.getElementById("SL_lng_to").value=TranslatorIM.SL_langDst;
			doc.getElementById("SL_lng_from").value=TranslatorIM.SL_langSrc;
			chrome.runtime.sendMessage({method: "getStatus"}, function(response) {
			 // console.log(response.status);
			});
		}


		doc.getElementById('SL_planshet').style.background = "#efefef";
		doc.getElementById('SL_Balloon_options').style.background = "#efefef";


		var SLselect = doc.getElementById("SL_lng_to");
		var SLselectFROM = doc.getElementById("SL_lng_from");
		var SL_locer = doc.getElementById("SL_locer");
		var SLswitch = doc.getElementById('SL_switch_b');

		var SL_P0 = doc.getElementById("SL_PN0");
		var SL_P1 = doc.getElementById("SL_PN1");
		var SL_P2 = doc.getElementById("SL_PN2");
		var SL_P3 = doc.getElementById("SL_PN3");

		if(SLdivField.style.backgroundColor==""){

	                TranslatorIM.SLShowHideAlert();
		        TranslatorIM.SL_DETECT = "";
			TranslatorIM.SL_GetTransCurPosition();
			var theSLtext = TranslatorIM.GET_TEXT();

			if(theSLtext=="" && TranslatorIM.DBLClick_tempText!="") theSLtext = TranslatorIM.DBLClick_tempText;
			TranslatorIM.DBLClick_tempText="";
			if(theSLtext == "" && TranslatorIM.AVOID_SHADOW_ROOT_TEXT != "") theSLtext = TranslatorIM.AVOID_SHADOW_ROOT_TEXT;

			if(theSLtext != ""){
				theSLtext = theSLtext.substring(0, TranslatorIM.SL_Balloon_translation_limit);
				var OBJ = doc.getElementById('SL_pin');

				if(theSLtext.length > TranslatorIM.SL_Balloon_translation_limit) {
					TranslatorIM.SL_FLOATER();
				}else{
					var evt = window.event;
					SLdivField.style.backgroundColor = "#FEFEFE";
					if(TranslatorIM.SL_SID_TEMP_TARGET != "") SLselect.value = TranslatorIM.SL_SID_TEMP_TARGET;

				}
				var bodyScrollTop = doc.documentElement.scrollTop || doc.body.scrollTop;
				var bodyScrollLeft = doc.documentElement.scrollLeft || doc.body.scrollLeft;

				var OBJ = doc.getElementById('SL_pin');

				if(TranslatorIM.SL_FRAME==0){
					if(TranslatorIM.SL_SAVETEXT == 1){
						TranslatorIM.SL_NEST="FLOAT";
						TranslatorIM.SL_SID_PIN="true";
					}
				}

                                theSLtext = theSLtext.trim();
				//theSLtext = theSLtext.replace(/\n/ig," @ "); 

				theSLtext = theSLtext.replace(/(^\s+|\s+$)/g, '');

				TranslatorIM.SL_TEMP_TEXT = theSLtext;
				var win = null;

				TranslatorIM.SL_BALLOON_TRANSLATION(theSLtext,evt,0, win);
				
				        if(TranslatorIM.GlobalBoxX!=0 && TranslatorIM.GlobalBoxY != 0) TranslatorIM.SL_NEST = "FLOAT";

					// TO HANDLE INVOKING FROM CM
				        if(TranslatorIM.SL_NEST=="") TranslatorIM.SL_NEST="TOP";
				        //---------------------------

	                                switch(TranslatorIM.SL_NEST){
						case "TOP":  	SLdivField.style.top=TranslatorIM.SL_T+bodyScrollTop-164+"px"; 
								TranslatorIM.SL_arrows('up'); 
								OBJ.style.background="url("+FExtension.browserInject.getURL('content/img/util/pin-off.png')+")";
								OBJ.title=FExtension.element(TranslatorIM.SL_LOC,"extPin_ttl");
								break;
						case "BOTTOM": 	SLdivField.style.top=TranslatorIM.SL_B+bodyScrollTop+9+"px"; 
								TranslatorIM.SL_arrows('down'); 
								OBJ.style.background="url("+FExtension.browserInject.getURL('content/img/util/pin-off.png')+")";
								OBJ.title=FExtension.element(TranslatorIM.SL_LOC,"extPin_ttl");
								break;
						case "FLOAT": 	TranslatorIM.SL_arrows('all');
								OBJ.style.background="url("+FExtension.browserInject.getURL('content/img/util/pin-on.png')+")";
								OBJ.title=FExtension.element(TranslatorIM.SL_LOC,"extUnPin_ttl");
								TranslatorIM.SL_FLOATER();
								break;
					}				


					var situation = 0;
					var setleft=(TranslatorIM.SL_L+TranslatorIM.SL_R)/2-448/2;
					if(setleft+473>window.innerWidth){
						setleft=window.innerWidth-467-18;
						var situation = 1;
					}
					if(setleft<25){
						setleft=25;
						var situation = 2;
					}
					var ArrowLeft='3px';

					if(TranslatorIM.SL_NEST!="FLOAT") SLdivField.style.left=(bodyScrollLeft*1)+setleft +"px";

        	                        var textCenter=Math.ceil((TranslatorIM.SL_R-TranslatorIM.SL_L)/2);
					switch(situation){
					  case 0:ArrowLeft='214px'; break;
					  case 1:var obj = (SLdivField.style.left.replace("px","")*1)
						 var coord = TranslatorIM.SL_L-obj+bodyScrollLeft+textCenter-10;
						 var delta=0;
						 if(bodyScrollLeft!=0) delta=5;
						 if(coord>obj) ArrowLeft = coord-delta+"px";
						 else ArrowLeft=coord+'px'; 
						 break;
					  case 2:if(TranslatorIM.SL_L<25){
							if(textCenter<25) ArrowLeft='3px';
                	                                else ArrowLeft=textCenter-25 + 'px';
						 }else ArrowLeft=TranslatorIM.SL_L+textCenter-35+'px'; 
						 break;
					}

					doc.getElementById("SL_arrow_down").style.left=ArrowLeft;
					doc.getElementById("SL_arrow_up").style.left=ArrowLeft;

                                TranslatorIM.SL_Bubble_Reposition();

                               
				TranslatorIM.SL_NotAllowed();

				TranslatorIM.SL_addEvent(SLdivField, 'mouseup', TranslatorIM.SL_ShowBalloon);
			    	TranslatorIM.SL_addEvent(SLdivField, 'mousedown', TranslatorIM.SL_CloseBalloon);
			    	TranslatorIM.SL_addEvent(SLdivField, 'mouseover', TranslatorIM.SL_addBalloonColor);
			    	TranslatorIM.SL_addEvent(SLdivField, 'mouseout', TranslatorIM.SL_removeBalloonColor);

			    	TranslatorIM.SL_addEvent(SLselect, 'change', TranslatorIM.SL_retranslate);
			    	TranslatorIM.SL_addEvent(SLselectFROM, 'change', TranslatorIM.SL_retranslate);
			    	TranslatorIM.SL_addEvent(SL_switch_b, 'click', TranslatorIM.SL_flip);
			    	TranslatorIM.SL_addEvent(SL_locer, 'click', TranslatorIM.SL_locker);  

			    	TranslatorIM.SL_addEvent(SL_P0, 'click', TranslatorIM.SL_retranslate);  
			    	TranslatorIM.SL_addEvent(SL_P1, 'click', TranslatorIM.SL_retranslate);  
			    	TranslatorIM.SL_addEvent(SL_P2, 'click', TranslatorIM.SL_retranslate);  
			    	TranslatorIM.SL_addEvent(SL_P3, 'click', TranslatorIM.SL_retranslate);  

			    	TranslatorIM.SL_addEvent(SL_BBL_locer, 'click', TranslatorIM.SL_BBL_locer);  

			    	if(theSLtext.indexOf(' ')!=-1){
				    TranslatorIM.SL_addEvent(doc.getElementById("SL_shadow_translation_result"), 'mousedown', TranslatorIM.ClickInside);				    
				    TranslatorIM.SL_addEvent(doc.getElementById("SL_shadow_translation_result"), 'mousedown', TranslatorIM.SL_bring_UP);
				    TranslatorIM.SL_addEvent(doc.getElementById("SL_shadow_translation_result2"), 'mouseout', TranslatorIM.SL_addBalloonColor);
			    	}else{
				    TranslatorIM.SL_addEvent(doc.getElementById("SL_shadow_translation_result"), 'mousedown', TranslatorIM.ClickInside);
				    TranslatorIM.SL_addEvent(doc.getElementById("SL_shadow_translation_result"), 'mousedown', TranslatorIM.SL_bring_UP);
				    TranslatorIM.SL_addEvent(doc.getElementById("SL_shadow_translation_result2"), 'mouseout', TranslatorIM.SL_bring_DOWN);
			    	}

				



//			    	TranslatorIM.SL_addEvent(doc.getElementById("SL_alert100"), 'mousedown', TranslatorIM.SL_ALERTPROTECT);
			    	TranslatorIM.SL_addEvent(doc.getElementById("SL_lng_to"), 'mousedown', TranslatorIM.SL_SCROLL);
			    	TranslatorIM.SL_addEvent(doc.getElementById("SL_lng_to"), 'mouseout', TranslatorIM.SL_bring_DOWN);
			    	TranslatorIM.SL_addEvent(doc.getElementById("SL_TTS_voice"), 'click', TranslatorIM.SL_Voice);
			    	TranslatorIM.SL_addEvent(doc.getElementById("SL_BBL_VOICE"), 'click', TranslatorIM.SL_Voice);
			    	TranslatorIM.SL_addEvent(doc.getElementById("SL_copy"), 'click', TranslatorIM.SL_CopyToClipBoard);
			    	TranslatorIM.SL_addEvent(doc.getElementById("SL_bbl_font"), 'click', TranslatorIM.SL_Font);
			    	TranslatorIM.SL_addEvent(doc.getElementById("SL_pin"), 'click', TranslatorIM.SL_pinme);
			    	TranslatorIM.SL_addEvent(doc.getElementById("SL_bbl_help"), 'click', TranslatorIM.SL_bbl_help);
			    	TranslatorIM.SL_addEvent(doc.getElementById("SL_Balloon_Close"), 'click', TranslatorIM.SL_CloseBalloonWithLink);
			    	TranslatorIM.SL_addEvent(doc.getElementById("SL_Balloon_Close"), 'mouseover', TranslatorIM.SL_bring_DOWN);



			    	TranslatorIM.SL_addBalloonColor();
			    	TranslatorIM.SL_removeBalloonColor();
			    	setTimeout(function() { 
				    	doc.getElementById("SL_button").style.display = "none";
				}, 10);    
			}
			
		}		 
		var OBJ = doc.getElementById('SL_shadow_translation_result');
		var OBJ2 = doc.getElementById('SL_shadow_translation_result2');
		// FONT SIZE icon
		var OBJ3 = doc.getElementById('SL_bbl_font');




		if(TranslatorIM.SL_FONT_SID==""){
		 	TranslatorIM.SL_FontSize_bbl = TranslatorIM.SL_FONT;
			TranslatorIM.SL_FONT2 = TranslatorIM.SL_FONT;
		}else TranslatorIM.SL_FontSize_bbl = TranslatorIM.SL_FONT_SID;

		if(TranslatorIM.SL_FontSize_bbl != OBJ.style.fontSize){
			if(TranslatorIM.SL_FontSize_bbl == "16px"){
				OBJ.style.fontSize = "16px";
				OBJ.style.lineHeight = "22px";
				OBJ2.style.fontSize = "16px";
				OBJ2.style.lineHeight = "22px";
			}else{
				OBJ.style.fontSize = "14px";
			   	OBJ.style.lineHeight = "20px";
			   	OBJ2.style.fontSize = "14px";
			   	OBJ2.style.lineHeight = "20px";
			}
			TranslatorIM.SL_FontSize_bbl = OBJ.style.fontSize;
		}

		if(TranslatorIM.SL_FontSize_bbl == "14px")   OBJ3.className="SL_font_on";
		if(TranslatorIM.SL_FontSize_bbl == "16px")   OBJ3.className="SL_font_off";

		// COPY icon
		doc.getElementById('SL_copy').className="SL_copy_hand";
		// TRANSLATION HISTORY icon
		//doc.getElementById('SL_TH').className="SL_TH";


		setTimeout(function() { 
                        var SLdivField2=TranslatorIM.DOC.getElementById("SL_button");
			if(SLdivField2) SLdivField2.style.display = "none";
		}, 1300); 
		if(TranslatorIM.SL_SHOW_PROVIDERS!="1"){
			doc.getElementById("SL_Bproviders").style.visibility = "hidden";
		} else 	doc.getElementById("SL_Bproviders").style.visibility = "visible";

              

		setTimeout(function() { 
	            try {
			if(doc.getElementById('SL_lng_from')){
			 	if(doc.getElementById('SL_lng_from').value=="auto"){
					doc.getElementById('SL_switch_b').title=FExtension.element(TranslatorIM.SL_LOC,"extDisabled");
					doc.getElementById('SL_switch_b').style.cursor="not-allowed";
				} else {
					doc.getElementById('SL_switch_b').title=FExtension.element(TranslatorIM.SL_LOC,"extSwitch_languages_ttl");
					doc.getElementById('SL_switch_b').style.cursor="pointer";
				}
			}
		     } catch (ex){}
	 	}, 1300); 

		setTimeout(function() { 
	        	 var obj_1="Tn"+"IT"+"Tt"+"w-t"+"oo"+"lt"+"ip"+"-wr"+"ap";
		         var zi=Math.floor((Math.random() * 100) + 1);
			 if(doc.getElementById(obj_1)) doc.getElementById(obj_1).style.zIndex=zi;
		}, 10); 


        	if(doc.doctype){
	             doc.getElementById("SL_shadow_translator").style.width="467px";
		}
		TranslatorIM.ACTIVATE_THEMEbbl(TranslatorIM.THEMEmode);
	},

	SL_BBL_VOICE: function(){	
	   TranslatorIM.TTS_btn_location=0;	
           var doc = TranslatorIM.DOC;	
//	   doc.getElementById('SL_alert100').style.display="none";	
	   var SL_to= doc.getElementById("SL_lng_to").value;	

//	   SL_to= SL_to.replace("-TW","");	
//	   SL_to= SL_to.replace("-CN","");	


	   var TTStext=TranslatorIM.SL_temp_result.replace(/<br>/g, " ");	
	   var text = TTStext;		   
	   text = TranslatorIM.truncStrByWord(text,1200);	
	   switch(TranslatorIM.SL_SLVoices){	
		case "0": if(TranslatorIM.SL_ALLvoices.indexOf(SL_to)!=-1){	
                              if(SL_TTS.indexOf(SL_to)!=-1){	
				if(text.length>TranslatorIM.GTTS_length) {
					if(SL_to == "en-gb") SL_to = "g_en-UK_f";
					if(SL_to == "pt-PT") SL_to = "pt";
					if(SL_to == "fr-CA") SL_to = "fr";
					if(SL_to == "zh-TW") SL_to = "g_zh-TW_f";
					if(SL_to == "lzh") SL_to = "g_zh-HK_f";
					if(SL_to == "zh-CN") SL_to = "zh";
					if(SL_to == "yue") SL_to = "zh";

					window.open("https://text-to-speech.imtranslator.net/?dir="+SL_to+"&text="+encodeURIComponent(text)); 	
				} else TranslatorIM.Google_TTS(text,SL_to);	
			      } else TranslatorIM.Google_TTS(text,SL_to);	
			  } else TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNo_Voice"));	
			  break;	
		case "1": if(TranslatorIM.SL_ALLvoices.indexOf(SL_to)!=-1){	
				if(G_TTS.indexOf(SL_to)!=-1) TranslatorIM.Google_TTS(text,SL_to);	
				else TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNo_Voice"));	
			  } else TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNo_Voice"));	
			  break;	
		case "2": if(TranslatorIM.SL_ALLvoices.indexOf(SL_to)!=-1){	
                              if(SL_TTS.indexOf(SL_to)!=-1) {
					if(SL_to == "en-gb") SL_to = "g_en-UK_f";
					if(SL_to == "pt-PT") SL_to = "pt";
					if(SL_to == "fr-CA") SL_to = "fr";
					if(SL_to == "zh-TW") SL_to = "g_zh-TW_f";
					if(SL_to == "lzh") SL_to = "g_zh-HK_f";
					if(SL_to == "zh-CN") SL_to = "zh";
					if(SL_to == "yue") SL_to = "zh";

					window.open("https://text-to-speech.imtranslator.net/?dir="+SL_to+"&text="+encodeURIComponent(text));	
			      }else TranslatorIM.Google_TTS(text,SL_to);	
			  } else TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNo_Voice"));	
			  break;	
	   }	
	},	

	SL_BBL_locer_settler: function(){
          var doc = TranslatorIM.DOC;
	 if(TranslatorIM.SL_OnOff_BTN2=="true") doc.getElementById('SL_BBL_locer').checked=true;
	 else doc.getElementById('SL_BBL_locer').checked=false;
	},

	SL_BBL_locer: function(){
		if(TranslatorIM.SL_EVENT){ 
			var ev = TranslatorIM.SL_EVENT;
		        var doc = TranslatorIM.DOC;

				if(doc.getElementById('SL_BBL_locer')) {
					if(ev.target.id == "SL_BBL_locer") TranslatorIM.SL_OnOff_BTN2 = doc.getElementById('SL_BBL_locer').checked.toString();
				}
			TranslatorIM.SAVE_SES_PARAMS();
		}
	},

	SL_bbl_help: function(){
		switch(PLATFORM){
			 case "Opera" : var slurl="https://imtranslator.net/tutorials/presentations/imtranslator-for-opera/opera-bubble-translator/"; break;
			 case "Chrome": var slurl="https://imtranslator.net/tutorials/presentations/imtranslator-for-chrome/chrome-bubble-translator/"; break;
			 default      : var slurl="https://imtranslator.net/tutorials/presentations/";break;
		}
		window.open(slurl,"ImTranslator:Bubble");
	},


	SL_locker: function(){	
	        var doc = TranslatorIM.DOC;
		var ev = TranslatorIM.SL_EVENT;
		if(doc.getElementById('SL_locer')) {
			if(ev.target.id == "SL_locer"){
				if(doc.getElementById('SL_locer').checked==false){
					TranslatorIM.SL_TMPbox="false";
				} else {
					TranslatorIM.SL_TMPbox="true";
				}
				TranslatorIM.SL_MAKE_FROM();
			}
		}

	},

	SL_locker_settler: function(){
	        var doc = TranslatorIM.DOC;
		if(TranslatorIM.SL_TMPbox=="true") {
			doc.getElementById('SL_locer').checked=true;
			TranslatorIM.SL_TMPbox="true";
		}else{ 
			doc.getElementById('SL_locer').checked=false;
			TranslatorIM.SL_TMPbox="false";
		}		
	},


        SL_ALERTPROTECT: function(){
                TranslatorIM.SL_quikCloseBalloon();
	},

	SL_flip: function(){
	        var doc = TranslatorIM.DOC;
		try{ doc.onmousemove = null; }catch(e) { console.log(e); }
		var SLselTO=doc.getElementById("SL_lng_to");
		var SLselFROM=doc.getElementById("SL_lng_from");
		if(SLselFROM.value!="auto"){
 		 if(TranslatorIM.SL_DETECT != SLselFROM.value || doc.getElementById('SL_locer').checked==true){
		   var TMP = SLselTO.value;
		   SLselTO.value=SLselFROM.value;
		   SLselFROM.value=TMP;  		   
		 }
		 TranslatorIM.SL_retranslate();
		}
	},

        SL_hist: function(){
		window.open(FExtension.browserInject.getURL('options.html?hist', true),"ImTranslator:Translation_History");
	},

	SL_SYN: function(ob){
		TranslatorIM.SL_retranslate();
	},

	SL_bring_UP: function(){
	    try{
		var doc = TranslatorIM.DOC;

       	   	doc.getElementById('SL_alert100').style.display="none";

		if(window.event && window.event.which==1){
			var theMainOBJ = doc.getElementById('SL_shadow_translator');
			var theOBJ = doc.getElementById('SL_shadow_translation_result');
			var theOBJ2 = doc.getElementById('SL_shadow_translation_result2');
			var ToLng = doc.getElementById('SL_lng_to').value;
			theOBJ2.style.display = 'block';
			theOBJ2.style.marginTop = theMainOBJ.offsetTop + 30 + "px";
			theOBJ2.style.marginLeft = theMainOBJ.offsetLeft + 1 + "px";
			theOBJ.style.visibility = "hidden";


                        theOBJ2.style.direction="ltr";
                        theOBJ2.style.textAlign="left";

			if(ToLng=="ar" || ToLng=="iw" || ToLng=="fa" || ToLng=="yi" || ToLng=="ur" || ToLng=="ps" || ToLng=="sd" || ToLng=="ckb" || ToLng=="ug" || ToLng=="dv" || ToLng=="prs"){
                          theOBJ2.style.direction="rtl";
                          theOBJ2.style.textAlign="right";
			}
		}
	     }catch(ex){}
	},

	SL_bring_DOWN: function(){
		var theOBJ = TranslatorIM.DOC.getElementById('SL_shadow_translation_result');
		var theOBJ2 = TranslatorIM.DOC.getElementById('SL_shadow_translation_result2');
	        if(theOBJ2){
			theOBJ2.style.display = 'none';
			theOBJ.style.visibility = "visible";
		}
	},

	SL_MAKE_FROM:function(){     
	        var doc = TranslatorIM.DOC;
		var SLselFROM = doc.getElementById("SL_lng_from");
		var SLselTO = doc.getElementById("SL_lng_to");
		if(doc.getElementById('SL_locer').checked!=true){
		     if(TranslatorIM.SL_Finde_Lang()==1){
 			if(TranslatorIM.LNGforHISTORY == SLselTO.value){
			   var TMP = SLselTO.value;
			   SLselTO.value=SLselFROM.value;
			   SLselFROM.value=TMP;  		   
			}else{
				SLselFROM.value = TranslatorIM.LNGforHISTORY;
			}
		     }  else {
 			if(TranslatorIM.LNGforHISTORY == SLselTO.value){
			   var TMP = SLselTO.value;
			   SLselTO.value=SLselFROM.value;
			   SLselFROM.value=TMP;  		   
			}

		     }
		}
		TranslatorIM.SL_retranslate();
	},

	SL_Finde_Lang(){
		var out = 0;
		var ln = TranslatorIM.LNGforHISTORY;
		var MENU = TranslatorIM.SL_LNG_LIST.split(",");
		for(var i = 0; i<MENU.length; i ++){
			if(MENU[i]==ln) out = 1;
		}
		return out;
	},

	SL_retranslate:function(){  
	   setTimeout(function(){
	     if(TranslatorIM.SL_EVENT.target.parentNode.className!="SL_BL_LABLE_DEACT"){
		TranslatorIM.AutoFlipState=0;
		TranslatorIM.FlippedByAuto=0;
	        var doc = TranslatorIM.DOC;
	   	doc.getElementById('SL_alert100').style.display="none";
		TranslatorIM.SL_bring_DOWN();
		TranslatorIM.SL_bring_UP();
		
		var theSLtext = TranslatorIM.GET_TEXT();
                //theSLtext = theSLtext.replace("\n","");
		if(theSLtext == "") theSLtext = TranslatorIM.SL_TEMP_TEXT;
		//theSLtext=theSLtext.replace(/\n/ig," @ "); 

		TranslatorIM.SL_BALLOON_TRANSLATION(theSLtext,window.event, 1);	
		if(doc.getElementById('SL_lng_from').value=="auto"){
			doc.getElementById('SL_switch_b').title=FExtension.element(TranslatorIM.SL_LOC,"extDisabled");
			doc.getElementById('SL_switch_b').style.cursor="not-allowed";
		} else { 
			doc.getElementById('SL_switch_b').title=FExtension.element(TranslatorIM.SL_LOC,"extSwitch_languages_ttl");
			doc.getElementById('SL_switch_b').style.cursor="pointer";
		}
		
                switch(TranslatorIM.SL_NEST){
			case "TOP": TranslatorIM.SL_arrows('up'); break;
			case "BOTTOM": TranslatorIM.SL_arrows('down'); break;
			case "FLOAT": TranslatorIM.SL_arrows('all'); break;
		}
                TranslatorIM.SL_HideShowTTSicon();
//                TranslatorIM.SL_DETECT="";
		TranslatorIM.SL_NotAllowed();
		TranslatorIM.SET_FIRST_AVAILABLE_PROV();
		TranslatorIM.SAVE_SES_PARAMS();
	     }	
	   }, 20);  
	},

        SL_HideShowTTSicon: function(){
	         var doc = TranslatorIM.DOC;
		 var SL_from = doc.getElementById('SL_lng_from').value;
		 if(doc.getElementById('SL_locer').checked==false || doc.getElementById('SL_lng_from').value=="auto") SL_from = TranslatorIM.SL_DETECT;
		 if(TranslatorIM.SL_ALLvoices.indexOf(SL_from)!=-1) doc.getElementById('SL_TTS_voice').style.visibility="visible";
		 else doc.getElementById('SL_TTS_voice').style.visibility="hidden";
	},

	SL_CloseBalloonWithLink: function(){
	    	try{
		 	var doc = TranslatorIM.DOC;
		  	doc.getElementById('SL_shadow_translator').style.display='none';		
                        TranslatorIM.SL_BBL_OBJ_OFF(1);
		}catch (ex){}
	},

	SL_CloseBalloon: function() {
	 try{
           var doc = TranslatorIM.DOC;
	   var bodyScrollLeft = doc.documentElement.scrollLeft || doc.body.scrollLeft;
	   if((window.innerWidth+bodyScrollLeft-window.event.pageX)>20){

		var SLdivField = doc.getElementById("SL_shadow_translator");
		if(doc.getElementById('SL_shadow_translation_result2').style.display == "none"){
			TranslatorIM.SL_Xdelta = window.event.pageX - SLdivField.offsetLeft;
			TranslatorIM.SL_Ydelta = window.event.pageY - SLdivField.offsetTop;

			TranslatorIM.SL_addEvent(SLdivField, 'mouseover', TranslatorIM.SL_addBalloonColor);
			TranslatorIM.SL_addEvent(SLdivField, 'mouseout', TranslatorIM.SL_removeBalloonColor);

			if(SLdivField.style.backgroundColor == ""){
				if(TranslatorIM.SL_SAVETEXT == 0){
					doc.getElementById("SL_shadow_translation_result").innerText="";
					doc.getElementById("SL_shadow_translation_result2").innerText="";
	                              	SLdivField.style.left="-10000px";
	                                SLdivField.style.top="-10000px";
					SLdivField.style.display = 'none';
				}
                                doc.getElementById('SL_balloon_obj').alt="0";
			}else{
				var evt = window.event;
				TranslatorIM.SL_MoveX = evt.pageX + "px";
				TranslatorIM.SL_MoveY = evt.pageY + "px";
				try{
				    if(evt.target.id!="SL_pin")	doc.onmousemove = TranslatorIM.SL_GetTransCurPosition;
				}catch(e){}
			}
		}
	    }
	 } catch(ex){}
	},

	SL_addBalloonColor: function() {
	        var doc = TranslatorIM.DOC;
		var SLdivField = doc.getElementById("SL_shadow_translator");
		if(SLdivField){
			SLdivField.style.backgroundColor = "#FEFEFE";
			SLdivField.style.boxShadow = "0px 0px 0px #000";
		}
	},
	SL_removeBalloonColor: function() {
        	var doc = TranslatorIM.DOC;
		var SLdivField = doc.getElementById("SL_shadow_translator");
		if(SLdivField){
			SLdivField.style.backgroundColor = "";
			SLdivField.style.boxShadow = "0px 0px 0px #BAB9B5";
		}
	},


	SL_addEvent: function( obj, type, fn ) {
		if (obj) {
			if ( obj.attachEvent ) {
				obj['e'+type+fn] = fn;
				obj[type+fn] = function(){ obj['e'+type+fn]( window.event ); }
				obj.attachEvent( 'on'+type, obj[type+fn] );
			} else 	obj.addEventListener(type, fn, false);
		}
	},



	SL_Bubble_Reposition: function() {
		setTimeout(function(){
			var doc = TranslatorIM.DOC;
			var SLdivField = doc.getElementById("SL_shadow_translator");
			var bodyScrollTop = doc.documentElement.scrollTop || doc.body.scrollTop;
			var bodyScrollLeft = doc.documentElement.scrollLeft || doc.body.scrollLeft;
			var position = SLdivField.getBoundingClientRect();
			var x = position.left;
			var y = position.top;
			var DELTAy = 1;
			if (doc.body.offsetHeight < window.innerHeight)	var DELTAy = 17;

			var DELTAx = 1;
			if (doc.body.offsetWidth < window.innerWidth)	var DELTAx = 17;

			if((x+SLdivField.offsetWidth)>(bodyScrollLeft+window.innerWidth-DELTAx)){
				TranslatorIM.SL_MoveX = (bodyScrollLeft+window.innerWidth-SLdivField.offsetWidth-DELTAx) +"px";
                                SLdivField.style.left = TranslatorIM.SL_MoveX;
			}
		}, 50);  
	},

	SL_GetTransCurPosition: function(e) {
	 try{
	  if(e){
		var doc = TranslatorIM.DOC;
		var posx = 0;
		var posy = 0;
		if (!e) var e = window.event;
		var id = e.target.id;
		var cl = e.target.className;
		var SLdivField = doc.getElementById("SL_shadow_translator");
		if(cl!="SL_options" && (id.indexOf("SL_")==-1 || id=="SL_button")){
			if (e.pageX || e.pageY)	{
				posx = e.pageX;
				posy = e.pageY;
			}
			else if (e.clientX || e.clientY) {
				posx = e.clientX + doc.body.scrollLeft + doc.documentElement.scrollLeft;
				posy = e.clientY + doc.body.scrollTop + doc.getDocument().documentElement.scrollTop;
			}


			var bodyScrollTop = doc.documentElement.scrollTop || doc.body.scrollTop;
			var bodyScrollLeft = doc.documentElement.scrollLeft || doc.body.scrollLeft;

			var DELTAy = 1;
			if (doc.body.offsetHeight < window.innerHeight)	var DELTAy = 17;

			var DELTAx = 1;
			if (doc.body.offsetWidth < window.innerWidth)	var DELTAx = 17;

			TranslatorIM.SL_MoveX = posx - TranslatorIM.SL_Xdelta + "px";
			if((posx - TranslatorIM.SL_Xdelta) < bodyScrollLeft) {
				TranslatorIM.SL_MoveX = (bodyScrollLeft+DELTAx) +"px";
			}
			if((posx - TranslatorIM.SL_Xdelta) > (bodyScrollLeft+window.innerWidth - SLdivField.offsetWidth-DELTAx) ) {
				TranslatorIM.SL_MoveX = (bodyScrollLeft+window.innerWidth - SLdivField.offsetWidth-DELTAx) +"px";
			}
		
			TranslatorIM.SL_MoveY = posy - TranslatorIM.SL_Ydelta + "px";
			if((posy - TranslatorIM.SL_Ydelta) < bodyScrollTop) {
				TranslatorIM.SL_MoveY = bodyScrollTop +"px";
			}
			if((posy - TranslatorIM.SL_Ydelta) > (bodyScrollTop+window.innerHeight - SLdivField.offsetHeight-DELTAy) ) {
				TranslatorIM.SL_MoveY = (bodyScrollTop+window.innerHeight - SLdivField.offsetHeight-DELTAy) +"px";
			}



			if(TranslatorIM.SL_FRAME==0){
				TranslatorIM.GlobalBoxY=TranslatorIM.SL_MoveY.replace("px","")-bodyScrollTop;
				TranslatorIM.GlobalBoxX=TranslatorIM.SL_MoveX.replace("px","")-bodyScrollLeft;
	               		chrome.runtime.sendMessage({greeting: "SAVE_COORD:>"+TranslatorIM.GlobalBoxX+","+TranslatorIM.GlobalBoxY}, function(response) {});
			}
			SLdivField.style.left = TranslatorIM.SL_MoveX;
			SLdivField.style.top = TranslatorIM.SL_MoveY;


			var OBJ = doc.getElementById('SL_pin');

			if(TranslatorIM.SL_FRAME==0){
				if(cl!="SL_options"){
					OBJ.style.background="url("+FExtension.browserInject.getURL('content/img/util/pin-on.png')+")";
					OBJ.title=FExtension.element(TranslatorIM.SL_LOC,"extUnPin_ttl");
					TranslatorIM.SL_NEST="FLOAT";
					TranslatorIM.SL_arrows('all');
					TranslatorIM.SL_SID_PIN="true";
					TranslatorIM.SL_FLOATER();
				} 
			}

			if(id!="" || cl!=""){
				//STOPS MOUSE EVENT WHEN A CURSOR IS PRESSED ON THE ARROWS
				if(id=="SL_arrow_down" || id=="SL_arrow_up" || id=="SL_Balloon_Close" || cl=="SL_options"){ 
					var sel = window.getSelection ? window.getSelection() : document.selection;
					SLdivField.style.backgroundColor = "#FEFEFE";
					TranslatorIM.SL_ShowBalloon();
					sel.removeAllRanges();
				}

				//STOPS MOUSE EVENT WHEN A CURSOR IS OUT OF VIEWPORT

				var OUTofVIEWport=5; // was: 50;
				if(e.clientX<=OUTofVIEWport || e.clientY<10 || (e.clientX+OUTofVIEWport) >= (window.innerWidth-DELTAx) || (e.clientY+OUTofVIEWport) >= (window.innerHeight-DELTAy)){
					var sel = window.getSelection ? window.getSelection() : document.selection;
					SLdivField.style.backgroundColor = "#FEFEFE";
					TranslatorIM.SL_ShowBalloon();
					sel.removeAllRanges();
					if (e.stopPropagation) {
					      e.stopPropagation();
					}
				}
			}
		}
	   }
	 }catch(ex){}
	},

	SL_IMG_LOADER: function(){
		TranslatorIM.LISTofPR = TranslatorIM.SL_ALL_PROVIDERS_BBL.split(",");
		for (var SL_I = 0; SL_I < TranslatorIM.LISTofPR.length; SL_I++){
		    switch(TranslatorIM.LISTofPR[SL_I]){
			case "Google": TranslatorIM.bblLISTofPRpairs[SL_I]=LISTofLANGsets[0];break;
			case "Microsoft": TranslatorIM.bblLISTofPRpairs[SL_I]=LISTofLANGsets[1];break;
			case "Translator": TranslatorIM.bblLISTofPRpairs[SL_I]=LISTofLANGsets[2];break;
			case "Yandex": TranslatorIM.bblLISTofPRpairs[SL_I]=LISTofLANGsets[3];break;
		    }	
		}
	        var ext = FExtension.browserInject;
		var doc = ext.getDocument()
            	doc.getElementById('SL_pin').style.background='url('+ext.getURL('content/img/util/pin-on.png')+')';

       		doc.getElementById('SL_TTS_voice').style.background='url('+ext.getURL('content/img/util/ttsvoice.png')+')';
            	doc.getElementById('SL_switch_b').style.background='url('+ext.getURL('content/img/util/switchb.png')+')';
       	    	doc.getElementById('SL_copy').style.background='url('+ext.getURL('content/img/util/copy.png')+')';
               	doc.getElementById('SL_bbl_font').style.background='url('+ext.getURL('content/img/util/font.png')+')';
            	doc.getElementById('SL_bbl_help').style.background='url('+ext.getURL('content/img/util/bhelp.png')+')';
	    	doc.getElementById('SL_Balloon_options').style.background="#FFF url('"+ext.getURL('content/img/util/bg3.png')+"')";
    		doc.getElementById('SL_loading').style.background="url('"+ext.getURL('content/img/util/loading.gif')+"')";
	    	doc.getElementById('SLHKclose').style.background="url('"+ext.getURL('content/img/util/delete.png')+"')";
	    	doc.getElementById('SL_arrow_down').style.background="url('"+ext.getURL('content/img/util/down.png')+"')";
    		doc.getElementById('SL_arrow_up').style.background="url('"+ext.getURL('content/img/util/up.png')+"')";
	    	doc.getElementById('SL_BBL_IMG').style.background="url('"+ext.getURL('content/img/util/bbl-logo.png')+"')";
	},

	//---------------BALLOON

        CONTROL_SUM_SYN: function (text){
           if(TranslatorIM.SL_DETECT == "") TranslatorIM.CONTROL_SUM="";
	},

	DODetection: function(myTransText) {
 	   myTransText = myTransText.replace(/@/ig,"")
	   myTransText = myTransText.trim();
	   var doc = TranslatorIM.DOC;
	   TranslatorIM.SL_SETINTERVAL_ST=0;
	   var AUTO = doc.getElementById('SL_locer').checked;
	   var isAuto=0;

	   //DETECTION ONLY ONCE-------------------
           TranslatorIM.CONTROL_SUM_SYN(myTransText);
	   if(TranslatorIM.CONTROL_SUM == myTransText){
		AUTO = true;
		isAuto = 0;
	   } else TranslatorIM.CONTROL_SUM = myTransText;
	   //DETECTION ONLY ONCE-------------------
	   if(doc.getElementById('SL_lng_from').value=="auto"){AUTO = false; isAuto=1;}
	   if(AUTO==false || isAuto==1){
		  if(myTransText!=""){

			    myTransText = myTransText.replace(/|/g,"");
			    myTransText = myTransText.replace(/&/g,"");
			    myTransText = myTransText.replace(/$/g,"");
			    myTransText = myTransText.replace(/^/g,"");
			    myTransText = myTransText.replace(/~/g,"");
			    myTransText = myTransText.replace(/`/g,"");
			    myTransText = myTransText.replace(/@/g,"");
			    myTransText = myTransText.replace(/%/g," ");
			    var a=Math.floor((new Date).getTime()/36E5)^123456;
			    var tk = a+"|"+Math.floor((Math.sqrt(5)-1)/2*(a^654321)%1*1048576);
			    var num = Math.floor((Math.random() * SL_GEO.length)); 
			    var theRegion = SL_GEO[num];
			    var cntr = myTransText.split(" ");
                	    var newTEXT = truncStrByWord(myTransText,100);
			    if(TranslatorIM.SL_DOM!="auto") theRegion=TranslatorIM.SL_DOM;


			    var baseUrl ="https://translate.google."+theRegion+"/translate_a/single";
			    var SL_Params = "client=gtx&dt=t&dt=bd&dj=1&source=input&q="+encodeURIComponent(newTEXT)+"&sl=auto&tl=en&hl=en";
			   chrome.runtime.sendMessage({from:"content_detect", url: baseUrl, cgi:SL_Params,});
			   chrome.runtime.onMessage.addListener(function(msg) {
			   if (msg.from == "background") {
				TranslatorIM.BBL_DETECT = msg.detected;

				//Verify if the DETECTION is an active language
				var checkresult=TranslatorIM.VerifyDetectedLang(TranslatorIM.BBL_DETECT);
				if(checkresult==0) TranslatorIM.BBL_DETECT="<#>";
				//-----------------------------------------------------------

						if(TranslatorIM.BBL_DETECT==undefined)  TranslatorIM.BBL_DETECT="<#>";
						chrome.runtime.onMessage.removeListener(arguments.callee);
						if(TranslatorIM.BBL_DETECT!="" && TranslatorIM.BBL_DETECT!="<#>") {
						   if (TranslatorIM.BBL_DETECT=="zh-CN"){
							TranslatorIM.BBL_DETECT="zh-CN";
							TranslatorIM.MS_DETECTOR(TranslatorIM.SL_TEMP_TEXT);
						   }else{

							var resp = TranslatorIM.BBL_DETECT;
							if(doc.getElementById("SL_shadow_translator").style.display=='block'){	
							       	var myTransText = TranslatorIM.GET_TEXT();
								if(myTransText == "") myTransText = TranslatorIM.SL_TEMP_TEXT;
								var AUTO = doc.getElementById('SL_locer').checked;
								DetLang = resp;
								var Det=DetLang;



								// NOT TRUSTED LANGUAGES
								myTransText = myTransText.trim();
								TranslatorIM.globaltheQ = myTransText.split(" ").length;


					                        if(TranslatorIM.SL_UNTRUST_WORD.indexOf(Det)!=-1 && TranslatorIM.globaltheQ==1){
									TranslatorIM.MS_DETECTOR(myTransText);
									return false;
								}	

					                        if(Det==TranslatorIM.SL_UNTRUST_TEXT){
									TranslatorIM.CONTROL_SUM="";TranslatorIM.MS_DETECTOR(myTransText);
									return false;
								}
								//----------------------


					                        TranslatorIM.SL_DETECT = DetLang;
					                        TranslatorIM.SL_DETECTED = DetLang;
				        	                TranslatorIM.SL_FLAG=0;
				                	        var cnt=0;

								var LANGSALL = FExtension.element(TranslatorIM.SL_LOC,'extLanguages').split(",");
								var LANGS = TranslatorIM.SL_LNG_LIST.split(",");

								for (var i = 0; i < LANGSALL.length; i++){
									var templang = LANGSALL[i].split(":");
									if(DetLang == templang[0]){ 
									        var tmp = doc.getElementById('SL_lng_from').value;
										if(tmp == "" || tmp == "auto") tmp = TranslatorIM.SL_langSrc;
										//DetLang=tmp;
										TranslatorIM.SL_FLAG=1;
										cnt=1;
									}
								}

			                        	        TranslatorIM.SL_WRONGLANGUAGEDETECTED=0;
								if(cnt==0){
			        	                                TranslatorIM.SL_DETECT = DetLang;
						                        TranslatorIM.SL_DETECTED = DetLang;
									TranslatorIM.SL_setTMPdata("BL_D_PROV","Google");
									TranslatorIM.SL_setTMPdata("BL_T_PROV","Google");
									TranslatorIM.SL_WRONGLANGUAGEDETECTED=1;
								}

				                                TranslatorIM.SL_HideShowTTSicon(); 
			        	                	TranslatorIM.LNGforHISTORY = DetLang;

				        	                TranslatorIM.SL_SID_FROM = doc.getElementById('SL_lng_from').value;
								TranslatorIM.SL_SID_TO   = doc.getElementById('SL_lng_to').value;

							        if(TranslatorIM.SL_SID_TO!=""){
									doc.getElementById('SL_lng_from').value=TranslatorIM.SL_SID_FROM;
									doc.getElementById('SL_lng_to').value=TranslatorIM.SL_SID_TO;
								}

						                if(doc.getElementById('SL_lng_to').value==resp && doc.getElementById('SL_lng_from').value!="auto"){
						                        var TMP=doc.getElementById('SL_lng_to').value;
						                        doc.getElementById('SL_lng_to').value = doc.getElementById('SL_lng_from').value;
					        	                doc.getElementById('SL_lng_from').value = TMP;
									TranslatorIM.SL_SID_FROM=doc.getElementById('SL_lng_from').value;
									TranslatorIM.SL_SID_TO=doc.getElementById('SL_lng_to').value;
                                                                        TranslatorIM.AutoFlipState=1;
									TranslatorIM.FlippedByAuto=1;
					       	        	}else{
									// AVOIDING AUTO DETETECT TAG 
									var autopattern = TranslatorIM.AUTOhandler(doc,AUTO,DetLang);
			                       	        		if(doc.getElementById('SL_lng_from').value!=autopattern){
				                       	                cnt=0;
									for (var i = 0; i < LANGS.length; i++){
										var templang = LANGS[i].split(":");
										if(DetLang == templang[0]) cnt=1;
									}
									if(cnt==1){TranslatorIM.FlippedByAuto=1; doc.getElementById('SL_lng_from').value=DetLang;}
								}
							}

						        TranslatorIM.SL_SETINTERVAL_ST=1;
						      }
						    }
			        	    	}  else {
							TranslatorIM.MS_DETECTOR(TranslatorIM.SL_TEMP_TEXT);
						}

			  }
			});


	          }
	 }else{



	     	TranslatorIM.SL_SID_FROM = doc.getElementById('SL_lng_from').value;
		TranslatorIM.SL_SID_TO  = doc.getElementById('SL_lng_to').value;
       		if(TranslatorIM.SL_SID_TO!=""){
			doc.getElementById('SL_lng_from').value=TranslatorIM.SL_SID_FROM;
			doc.getElementById('SL_lng_to').value=TranslatorIM.SL_SID_TO;
		}
		if(TranslatorIM.SL_SID_FROM=="auto" && TranslatorIM.SL_DETECT!="" && doc.getElementById('SL_locer').checked==false) doc.getElementById('SL_lng_from').value=TranslatorIM.SL_DETECT;

		TranslatorIM.SL_SETINTERVAL_ST=1;


	 }

         TranslatorIM.FlipNonStandartDir(doc);
	},


	FlipNonStandartDir: function(doc){

		if(doc.getElementById('SL_lng_from').value != "auto" && doc.getElementById('SL_locer').checked==false){
		        if(TranslatorIM.SL_DETECT == "zh") TranslatorIM.SL_DETECT="zh-CN";
			if(TranslatorIM.SL_DETECT == "zt") TranslatorIM.SL_DETECT="zh-TW";
			if(TranslatorIM.SL_DETECT == "or-IN") TranslatorIM.SL_DETECT="or";
			if(TranslatorIM.SL_DETECT == "ku-Latn") TranslatorIM.SL_DETECT="ku";
			if(TranslatorIM.SL_DETECT == "ku-Arab") TranslatorIM.SL_DETECT="ckb";
			if(TranslatorIM.SL_DETECT == "sr-Latn-RS") TranslatorIM.SL_DETECT="sr-Latn";


		  	if(doc.getElementById("SL_lng_to").value == "tlsl" && TranslatorIM.SL_DETECT == "tl") TranslatorIM.SL_DETECT = "tlsl";
			if(doc.getElementById("SL_lng_to").value == "srsl" && TranslatorIM.SL_DETECT == "sr") TranslatorIM.SL_DETECT = "srsl";
		  	if(doc.getElementById("SL_lng_to").value == "tl" && TranslatorIM.SL_DETECT == "tlsl") TranslatorIM.SL_DETECT = "tl";
		  	if(doc.getElementById("SL_lng_to").value == "sr" && TranslatorIM.SL_DETECT == "srsl") TranslatorIM.SL_DETECT = "sr";

		  if(doc.getElementById("SL_lng_to").value == TranslatorIM.SL_DETECT){
			var TMP=doc.getElementById('SL_lng_to').value;
			doc.getElementById('SL_lng_to').value = doc.getElementById('SL_lng_from').value;
			doc.getElementById('SL_lng_from').value = TMP;
			doc.getElementById('SL_lng_from').title=FExtension.element(TranslatorIM.SL_LOC,'extDetected') + " " + TranslatorIM.SL_GetLongName(TranslatorIM.SL_DETECT);
		  }
		}

	},


	MS_DETECTOR: function(text){

  	   var doc = TranslatorIM.DOC;
           var AUTO = doc.getElementById('SL_locer').checked;
	   if(AUTO==false || doc.getElementById('SL_lng_from').value=="auto"){


		var TM = 0;
		var doc = FExtension.browserInject.getDocument();
		TranslatorIM.SL_SETINTERVAL_ST=0;
		var AUTO = doc.getElementById('SL_locer').checked;


		setTimeout(function(){
		    if(TranslatorIM.AKEY!=""){
		        var baseUrl = "https://api-edge.cognitive.microsofttranslator.com/translate?api-version=3.0&includeSentenceLength=false&to=en";
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
				if(ajaxRequest.readyState == 4){

		             		var resp = ajaxRequest.responseText;

					if(resp.indexOf('{"error":{"code"')==-1){
						var DetLang = "en";
				             	var R1=resp.split('language":"');
						var R2=R1[1].split('","score"');
						DetLang = R2[0];
						if(DetLang == "zh-Hans") DetLang = "zh-CN";
						if(DetLang == "zh-Hant") DetLang = "zh-TW";
						if(DetLang == "he") DetLang = "iw";
					        if(DetLang == "sr-Cyrl") DetLang = "srsl";
						if(DetLang == "fil") DetLang = "tl";
						if(DetLang == "mww") DetLang = "hmn";
						if(DetLang == "ku") DetLang = "ckb"; 
						TranslatorIM.SL_DETECTED=DetLang;
                                                TranslatorIM.SL_FLAG=0;
						var LANGSALL = FExtension.element(TranslatorIM.SL_LOC,'extLanguages').split(",");
						var LANGS = TranslatorIM.SL_LNG_LIST.split(",");
						var cnt=0;
						for (var i = 0; i < LANGSALL.length; i++){
							var templang = LANGSALL[i].split(":");
							if(DetLang == templang[0]){ 
							        var tmp = doc.getElementById('SL_lng_from').value;
								if(tmp == "" || tmp == "auto") tmp = TranslatorIM.SL_langSrc;
								cnt=1;
								TranslatorIM.SL_FLAG=1;
							}
						}
                                                TranslatorIM.SL_WRONGLANGUAGEDETECTED=0;

						if(cnt==0){
							if(doc.getElementById('SL_lng_from').value!="auto") DetLang=doc.getElementById('SL_lng_from').value;
						        else DetLang="";
							TranslatorIM.SL_WRONGLANGUAGEDETECTED=1;
							TranslatorIM.SL_setTMPdata("BL_D_PROV","Google");
							TranslatorIM.SL_setTMPdata("BL_T_PROV","Google");
						} 
						
                                                TranslatorIM.SL_DETECT =  DetLang;
		                        	TranslatorIM.LNGforHISTORY = DetLang;
		                        	
			                        TranslatorIM.SL_SID_FROM = doc.getElementById('SL_lng_from').value;
						TranslatorIM.SL_SID_TO   = doc.getElementById('SL_lng_to').value;
					        if(TranslatorIM.SL_SID_TO!=""){
							doc.getElementById('SL_lng_from').value=TranslatorIM.SL_SID_FROM;
							doc.getElementById('SL_lng_to').value=TranslatorIM.SL_SID_TO;
						}
			                        if(doc.getElementById('SL_lng_to').value==DetLang && doc.getElementById('SL_lng_from').value!="auto"){
			                                var TMP=doc.getElementById('SL_lng_to').value;
	        		                        doc.getElementById('SL_lng_to').value = doc.getElementById('SL_lng_from').value;
        	                		        doc.getElementById('SL_lng_from').value = TMP;
		                	        }else{
							// AVOIDING AUTO DETETECT TAG 
							var autopattern = TranslatorIM.AUTOhandler(doc,AUTO,DetLang);
	                       			        if(doc.getElementById('SL_lng_from').value!=autopattern){
                        	                		cnt=0;
								for (var i = 0; i < LANGS.length; i++){
									var templang = LANGS[i].split(":");
									if(DetLang == templang[0]) cnt=1;
								}
								if(cnt==1) {
									doc.getElementById('SL_lng_from').value=DetLang;
									doc.getElementById('SL_lng_from').title=FExtension.element(TranslatorIM.SL_LOC,'extDetected') + " " + TranslatorIM.SL_GetLongName(TranslatorIM.SL_DETECT);
								}
							}
						}
					        TranslatorIM.SL_SETINTERVAL_ST=1;
				        	SYS=1;
					}else SYS = 0;
				}
			}

			text=text.replace(/"/g,"'");
			ajaxRequest.open("POST", baseUrl, true);
			ajaxRequest.setRequestHeader("Content-Type", "application/json");
			ajaxRequest.setRequestHeader("authorization", TranslatorIM.AKEY);
			ajaxRequest.send('[{"text":"'+text+'"}]'); 
		  }
		},TM);
	   }
	},



	truncStrByWord: function(str, length){
		if(str != "undefined"){
			if(str.length > 25){
				length = length - 25;
				var thestr = str;
				if (str.length > length) {
					str = str.substring(0, length);
					str = str.replace(new RegExp("/(.{1,"+length+"})\b.*/"), "$1");    // VK - cuts str to max length without splitting words.
					var str2 = thestr.substring(length, (length+25));
					var tempstr = str2.split(" ");
					var tmp = "";
					for (var i = 0; i < tempstr.length - 1; i++){
						tmp = tmp + tempstr[i] + " ";
					} 
					str = str + tmp;
				}
			} else 
				str = str + " ";
		}
		return str;
	},

	SL_IF_DETECT_IS_PRESENT: function(dl, ob){
		var resp=dl, out=0;
		var doc = TranslatorIM.DOC;
		if(doc.getElementById('SL_locer').checked==true){
			dl = "";
			TranslatorIM.SL_DETECTED="";
			for(var i=0; i < ob.length; i++) if(ob[i].value == dl) out=1;
			if(out==0 && ob.value != "auto") resp = ob.value;
		} else resp = dl;
		return resp;
	},



	SL_Voice: function(){
	   TranslatorIM.TTS_btn_location=1;
           var doc = TranslatorIM.DOC;

	   var TTStext=TranslatorIM.SL_TEMP_TEXT.replace(/@/g, " ");
	   var text = TTStext;
	   text = TranslatorIM.truncStrByWord(text,1200);

	   var SL_from = TranslatorIM.SL_IF_DETECT_IS_PRESENT(TranslatorIM.SL_DETECTED, doc.getElementById("SL_lng_from"));

	   SL_from = SL_from.replace("-TW","");
	   SL_from = SL_from.replace("-CN","");
	   switch(TranslatorIM.SL_SLVoices){
		case "0": if(TranslatorIM.SL_ALLvoices.indexOf(SL_from)!=-1){
                              if(SL_TTS.indexOf(SL_from)!=-1){
				if(text.length>TranslatorIM.GTTS_length) {
					if(SL_from == "en-gb") SL_from = "g_en-UK_f";
					if(SL_from == "pt-PT") SL_from = "pt";
					if(SL_from == "fr-CA") SL_from = "fr";
					if(SL_from == "zh-TW") SL_from = "g_zh-TW_f";
					if(SL_from == "lzh") SL_from = "g_zh-HK_f";
					if(SL_from == "zh-CN") SL_from = "zh";
					if(SL_from == "yue") SL_from = "zh";

					window.open("https://text-to-speech.imtranslator.net/?dir="+SL_from+"&text="+encodeURIComponent(text)); 
				}else TranslatorIM.Google_TTS_ON_TOP(text,SL_from);
			      } else TranslatorIM.Google_TTS_ON_TOP(text,SL_from);
			  } else TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNo_Voice"));
			  break;
		case "1": if(TranslatorIM.SL_ALLvoices.indexOf(SL_from)!=-1){
				if(G_TTS.indexOf(SL_from)!=-1) TranslatorIM.Google_TTS_ON_TOP(text,SL_from);
				else TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNo_Voice"));
			  } else TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNo_Voice"));
			  break;
		case "2": if(TranslatorIM.SL_ALLvoices.indexOf(SL_from)!=-1){
                              if(SL_TTS.indexOf(SL_from)!=-1) {
					if(SL_from == "en-gb") SL_from = "g_en-UK_f";
					if(SL_from == "pt-PT") SL_from = "pt";
					if(SL_from == "fr-CA") SL_from = "fr";
					if(SL_from == "zh-TW") SL_from = "g_zh-TW_f";
					if(SL_from == "lzh") SL_from = "g_zh-HK_f";
					if(SL_from == "zh-CN") SL_from = "zh";
					if(SL_from == "yue") SL_from = "zh";

					window.open("https://text-to-speech.imtranslator.net/?dir="+SL_from+"&text="+encodeURIComponent(text));
			      }else TranslatorIM.Google_TTS_ON_TOP(text,SL_from);
			  } else TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNo_Voice"));
			  break;
	   }

	},

	SetTTStextLimit: function(text,limit){
	 text=text.replace(/(\r\n|\n|\r)/gm,"");
	 var ttstexttmp=text.split(" ");
	 var OutPut="";
	 var OutPut_="";
	 for(var i=0; i<ttstexttmp.length; i++){
	     OutPut=OutPut+ttstexttmp[i]+" ";
	     if(OutPut.length>limit) break;
	     else OutPut_=OutPut_+ttstexttmp[i]+" ";
	 }
	 return(OutPut_);
	},


	REMOTE_Voice: function(dir, text){
	   TranslatorIM.synth.cancel();TranslatorIM.REMOTE_Voice_Close();
           setTimeout(function() {


	   TranslatorIM.GOOGLE_TTS_backup_loader=0;
	   var BackUpDir = dir;
	   var BackUpText = text;

//	   dir = dir.replace("-TW","");
//	   dir = dir.replace("-CN","");
	   if(dir=="en") dir = dir.replace("en","en-BR");
	   dir = dir.replace("es","es-419");
	   if(dir=="fr-CA") dir="fr";
	   if(dir=="lzh") dir="zh";
	   //if(dir=="yue") dir="zh";
	   if(dir=="pt") dir="pt-BR";


	   var a=Math.floor((new Date).getTime()/36E5)^123456;
	   var TK = a+"|"+Math.floor((Math.sqrt(5)-1)/2*(a^654321)%1*1048576);

	   var length = text.length;
	   var num = Math.floor((Math.random() * SL_GEO.length)); 
	   var theRegion = SL_GEO[num];
           if(TranslatorIM.SL_DOM!="auto") theRegion=TranslatorIM.SL_DOM;
	   var baseUrl = "https://translate.google."+theRegion;

           var doc = TranslatorIM.DOC;

	   if(text=="") text=doc.getElementById("SL_shadow_translation_result").outerHTML.replace(/<[^>]*>?/g,'').substring(0,100);

	   var client = "tw-ob";

//	   if(BackUpDir=="es") client="t";


 	   baseUrl = baseUrl+'/translate_tts?tk='+TK+'&ie=UTF-8&tl='+dir+'&total=1&idx=0&textlen='+length+'&client='+client+'&q='+encodeURIComponent(text);  


//	  if(doc.getElementById("lbframe")!=null) {TranslatorIM.synth.cancel();TranslatorIM.REMOTE_Voice_Close();}

	  
          var frame = doc.getElementById('lbframe');

	  if(frame)	frame.parentNode.removeChild(frame);
	  if(!doc.getElementById("lbframe")){
            if(doc.getElementById("SL_player2")) doc.getElementById("SL_player2").innnerHTML="";
	    var die=doc.createElement("iframe");
	    die.src="";
	    die.name="lbframe";
	    die.id="lbframe";
	    die.width="461px";

	    die.height="40px";
	    die.scrolling="no";
	    die.frameBorder="0";
	    doc.getElementById('SL_player2').appendChild(die);

	     var audioElement = doc.createElement('audio');
	     audioElement.setAttribute('src', baseUrl);
	     audioElement.setAttribute('preload', 'auto');
	     audioElement.setAttribute('controls', '');
	     audioElement.setAttribute('autoplay', '');
	     audioElement.setAttribute('id', 'SLmedia');
	     audioElement.setAttribute('name', 'SLmedia');
	     audioElement.setAttribute('style', 'width:510px;margin-top:-15px;margin-left:-20px;');
//	     doc.getElementById('SL_player2').style.display="block";
	     doc.getElementById('SL_player2').style.display="none";
	     doc.getElementById('SL_player2').style.height="0px";
	     doc.getElementById('SL_player2').style.width="0px";
	     doc.getElementById('SL_player2').style.overflow="hidden";
	     doc.getElementById('SL_player2').style.marginLeft="2px";
	     doc.getElementById('SL_player2').appendChild (audioElement);
             var ifr = window.frames["lbframe"];
	     ifr.document.body.appendChild (audioElement);
	     if(doc.getElementById('noplmsg')) doc.getElementById('noplmsg').style.display='none';
	     if(doc.getElementById("PL_lbplayer")){
		doc.getElementById("PL_lbplayer").style.display='none';
		TranslatorIM.synth.cancel();
	     }

		setTimeout(function(){
		   try{
		     var TTSstatus = String((window.frames["lbframe"].document.getElementById("SLmedia").duration));
	        	 if(TTSstatus=="NaN") {					
				if(PLATFORM=="Chrome" && TranslatorIM.TTSbackupLangs.indexOf(BackUpDir)!=-1)TranslatorIM.GOOGLE_TTS_backup(BackUpText,BackUpDir);
				else{
					doc.getElementById("SL_player2").innerHTML=DOMPurify.sanitize("<div id='noplmsg' align=center><font color='#BD3A33'>"+FExtension.element(TranslatorIM.SL_LOC,"extADVstu")+"</font></div>");     
				     	doc.getElementById('SL_player2').style.height="35px";
				     	if(doc.getElementById("SL_alert100")) doc.getElementById("SL_alert100").style.display="none";
				}
			 }
		   } catch (ex) {if(PLATFORM=="Chrome" && TranslatorIM.TTSbackupLangs.indexOf(BackUpDir)!=-1 && TranslatorIM.GOOGLE_TTS_backup_loader==0)TranslatorIM.GOOGLE_TTS_backup(BackUpText,BackUpDir);}
		}, 3000);  

	  }
      	 }, 1000);
	},


	REMOTE_Voice_Close: function(){
	    try{
	       chrome.runtime.sendMessage({greeting: "TTS_BBL_off:>"}, function(response) {}); 

	       if(window.event.target.lang==""){
	  	  var doc = TranslatorIM.DOC;
		  TranslatorIM.synth.cancel();
		  if(window.event.target.id!="SL_volume" && window.event.target.id!="SL_controls"){
			  if(doc.getElementById("PL_lbplayer"))doc.getElementById("PL_lbplayer").style.display='none';
//			  if(doc.getElementById('SL_alert100')) doc.getElementById('SL_alert100').style.display="none";
			  if(doc.getElementById('SL_player2')) doc.getElementById('SL_player2').style.display="none";
		  }
		  var frame = doc.getElementById('lbframe');

		  if(frame)	frame.parentNode.removeChild(frame);
	          var target = window.event.target || window.event.srcElement;
	          var id = target.id;

	          if(id!="SL_controls" && id!="SL_volume" && id!="SL_myRange"){
			  doc.getElementById("SL_player2").innerText="";
		  } else {
			if(id=="SL_controls"){
				if(doc.getElementById(id).className=="SL_play") TranslatorIM.handleSpeechResume();
				else TranslatorIM.handleSpeechPause();
			}
			if(id=="SL_volume") TranslatorIM.handleSpeechVolume();
		  }
		}
//		if(doc.getElementById('SL_alert100')) doc.getElementById('SL_alert100').style.display="none";
		if(doc.getElementById('SL_player2')) doc.getElementById('SL_player2').style.display="none";
	    } catch (ex){}
            TranslatorIM.GOOGLE_TTS_backup_loader=1;
	},


	SL_CopyToClipBoard: function(){
	  	var doc = TranslatorIM.DOC;
		var OBJ = doc.getElementById('SL_shadow_translation_result');
		OBJ.contentEditable = true;
		OBJ.unselectable = "off";
		OBJ.focus();
		var ZIPtext = DOMPurify.sanitize(OBJ.innerHTML);
		//This line is for plant text only
		var preZIPtext = ZIPtext.replace(/<br>/ig,'~');
		preZIPtext = preZIPtext.replace(/(<([^>]+)>)/ig,'').replace(/&nbsp;/ig,'');
		preZIPtext = preZIPtext.replace(/~/ig,'<br>');
		OBJ.innerHTML = DOMPurify.sanitize(preZIPtext);
	        TranslatorIM.DOC.execCommand('SelectAll');
		TranslatorIM.DOC.execCommand("Copy", false, null);
		OBJ.innerHTML = DOMPurify.sanitize(ZIPtext);
                OBJ.style.opacity=0.2;
		setTimeout(function(){ 
			OBJ.style.opacity=1; 
			if (TranslatorIM.DOC.getSelection) {
			    if (TranslatorIM.DOC.getSelection().empty) {  // Chrome
			        TranslatorIM.DOC.getSelection().empty();
			    } else if (TranslatorIM.DOC.getSelection().removeAllRanges) {  // Firefox
			        TranslatorIM.DOC.getSelection().removeAllRanges();
			    }
			} else if (TranslatorIM.DOC.selection) {  // IE?
			    TranslatorIM.DOC.selection.empty();
			}
       	                doc.getElementById('SL_copy_tip').style.display="block";
               	        doc.getElementById('SL_copy_tip').innerHTML=DOMPurify.sanitize(FExtension.element(TranslatorIM.SL_LOC,"extTextCopied"));
			setTimeout(function(){ 
	       	                doc.getElementById('SL_copy_tip').style.display="none";
			}, 1500);
		}, 350);
		OBJ.contentEditable = false;
	},

	SL_Font: function(){
	  	var doc = TranslatorIM.DOC;
		var OBJ = doc.getElementById('SL_shadow_translation_result');
		var OBJ2 = doc.getElementById('SL_shadow_translation_result2');
		var OBJ3 = doc.getElementById('SL_bbl_font');
		if(TranslatorIM.SL_FontSize_bbl == OBJ.style.fontSize){
			if(TranslatorIM.SL_FontSize_bbl=="14px"){
				OBJ.style.fontSize = "16px";
				OBJ.style.lineHeight = "22px";
				OBJ2.style.fontSize = "16px";
				OBJ2.style.lineHeight = "22px";
				OBJ3.className = "SL_font_off";
				OBJ3.style.background="url("+FExtension.browserInject.getURL('content/img/util/font-on.png')+")";
				TranslatorIM.SL_FontSize_bbl = "16px";
			}else{
				OBJ.style.fontSize = "14px";
				OBJ.style.lineHeight = "20px";
				OBJ2.style.fontSize = "14px";
				OBJ2.style.lineHeight = "20px";
				OBJ3.className = "SL_font_on";
				OBJ3.style.background="url("+FExtension.browserInject.getURL('content/img/util/font.png')+")";
				TranslatorIM.SL_FontSize_bbl = "14px";
			}

			TranslatorIM.SL_FONT_SID = TranslatorIM.SL_FontSize_bbl;
		}
                TranslatorIM.SL_JUMP(doc);
		TranslatorIM.SAVE_SES_PARAMS();

	},
	SL_pinme: function(){                 
	  if(TranslatorIM.SL_FRAME==0){
	        var doc = TranslatorIM.DOC;
		var OBJ = doc.getElementById('SL_pin');
		var SLdivField = doc.getElementById("SL_shadow_translator");
		if(OBJ.style.background.indexOf("pin-off.png")!=-1){
			setTimeout(function() {
				OBJ.style.background="url("+FExtension.browserInject.getURL('content/img/util/pin-on.png')+")";
				OBJ.className = "SL_pin_on";
				OBJ.title = FExtension.element(TranslatorIM.SL_LOC,"extUnPin_ttl");
				TranslatorIM.SL_NEST="FLOAT";
				TranslatorIM.SL_FLOATER();
			        var bodyScrollTop = doc.documentElement.scrollTop || doc.body.scrollTop;
				var bodyScrollLeft = doc.documentElement.scrollLeft || doc.body.scrollLeft;
				TranslatorIM.SL_MoveY=Math.ceil(SLdivField.style.top.replace("px",""))+"px";
				TranslatorIM.SL_MoveX=Math.ceil(SLdivField.style.left.replace("px",""))+"px";
				TranslatorIM.GlobalBoxY=(parseInt(TranslatorIM.SL_MoveY.replace("px",""))-bodyScrollTop);
//				TranslatorIM.GlobalBoxX=(parseInt(TranslatorIM.SL_MoveX.replace("px",""))-bodyScrollLeft+SLdivField.offsetWidth);
				TranslatorIM.GlobalBoxX=3000;
		               	chrome.runtime.sendMessage({greeting: "SAVE_COORD:>"+TranslatorIM.GlobalBoxX+","+TranslatorIM.GlobalBoxY}, function(response) {});
			}, 100);
		    TranslatorIM.SL_SID_PIN="true";
		}else{
			TranslatorIM.SL_NEST="";
			OBJ.className = "SL_pin_off";
			OBJ.title = FExtension.element(TranslatorIM.SL_LOC,"extPin_ttl");
			OBJ.style.background="url("+FExtension.browserInject.getURL('content/img/util/pin-off.png')+")";
			TranslatorIM.SL_SID_PIN="false";
	               	chrome.runtime.sendMessage({greeting: "SAVE_COORD:>0,0"}, function(response) {});
			TranslatorIM.SL_MoveY="-10000px";
			TranslatorIM.SL_MoveX="-10000px";
//			SLdivField.style.left=Math.ceil(SLdivField.style.left.replace("px","")-20)+"px";
			doc.onscroll = function(){}; 
		}   
		TranslatorIM.SAVE_SES_PARAMS();
	    }
	},
	SL_FLOATER: function(){
	  if(TranslatorIM.SL_FRAME==0){
	    	try{ 

			//ALWAYS KEEPS FLOATING MODE FOR 'SAVE RESENT WORK'

			if(TranslatorIM.SL_SAVETEXT == 1) TranslatorIM.SL_NEST= "FLOAT";

			if(TranslatorIM.SL_NEST=="FLOAT"){
			        var doc = TranslatorIM.DOC;
				var THEobj = doc.getElementById("SL_shadow_translator");
				if(TranslatorIM.GlobalBoxY<0)TranslatorIM.GlobalBoxY=1;
				if(parseInt(TranslatorIM.SL_MoveX.replace("px",""))<0) TranslatorIM.SL_MoveX = TranslatorIM.GlobalBoxX +"px";
				if(TranslatorIM.GlobalBoxX>0){
					THEobj.style.top = TranslatorIM.SL_getScrollY() + TranslatorIM.GlobalBoxY + "px";
					THEobj.style.left = TranslatorIM.SL_MoveX;
				}else{
					THEobj.style.top = TranslatorIM.SL_getScrollY() + (window.innerHeight / 2 - 150) + "px";
					THEobj.style.left = (window.innerWidth - 460 - 30) + "px";
				}
				TranslatorIM.WINDOW_and_BUBBLE_alignment(doc,THEobj);
				doc.onscroll = TranslatorIM.SL_FLOATER; 
				window.addEventListener("resize", TranslatorIM.SL_FLOATER);
				doc.getElementById("SL_arrow_up").style.display="none";
			} else doc.onscroll = function(){}; 
		} catch(e){}
	  }
	},

	SL_getScrollX: function(){
		var scrOfX = 0;
	        var doc = TranslatorIM.DOC;
		if( doc.body && doc.body.scrollLeft ) scrOfX = doc.body.scrollLeft;
		else if( doc.documentElement && doc.documentElement.scrollLeft  ) scrOfX = doc.documentElement.scrollLeft;
		return scrOfX;
	},

	SL_getScrollY: function(){
		var scrOfY = 0;
	        var doc = TranslatorIM.DOC;
		if( doc.body && doc.body.scrollTop ) scrOfY = doc.body.scrollTop;
		else if( doc.documentElement && doc.documentElement.scrollTop  ) scrOfY = doc.documentElement.scrollTop;
		return scrOfY;
	},

	SL_GOOGLE_WPT: function(){
		if(TranslatorIM.DOC.getElementById("wtgbr")){ 
			TranslatorIM.DOC.getElementById("wtgbr").style.display = 'none';
			TranslatorIM.DOC.getElementById("gt-bbar").style.display = 'none';
			TranslatorIM.DOC.getElementById("clp-btn").style.display = 'none';
			TranslatorIM.DOC.getElementById("contentframe").style.marginTop = '-60px';

			var frames = TranslatorIM.DOC.getElementsByTagName('iframe');
			for(var i = 0; i < frames.length; i++){
			   if(frames[i].name=='c'){ frames[i].sandbox="allow-same-origin allow-forms allow-scripts allow-top-navigation"; break; }
			}

		} 
	},
	HotKeysWindow: function(e, st){
		 var s = TranslatorIM.GET_TEXT();

		 s=s.substring(0,TranslatorIM.SL_PLANSHET_LIMIT);
//		 if(st==0) s="";
//		 if(s!=""){
		  chrome.runtime.sendMessage({greeting: "hello"}, function(response) {
	              if(response){
		        //console.log(response.farewell);
        	      }
		  });
		  s=s.replace(/(^[\s]+|[\s]+$)/g, '');
		  var theQ=s.split(" ").length;
	          if(s.match(/[-/‧·﹕﹗！：，。﹖？:-?!.,:{-~!"^_`、\[\]]/g)!=null) theQ=100;
		  
 		  //if(TranslatorIM.SL_dict_bbl=="false") theQ=100;
		  if (s.match(/[\u3400-\u9FBF]/) && s.length>1) theQ=100;

		  if(theQ==1 && s!=""){
			  TranslatorIM.SL_MODE=1;
		          chrome.runtime.sendMessage({greeting: "POPUP:>"+s}, function(response) {});
		   }else{
			  TranslatorIM.SL_MODE=0;
		          chrome.runtime.sendMessage({greeting: "POPUP:>"+s}, function(response) {});
		   }
//		 }
	},

	SL_BALLOON_TRANSLATION: function(myTransText,evt,st) {   
//	   chrome.runtime.sendMessage({greeting: "CM_BBL:>" + TranslatorIM.SL_SID_TO}, function(response) {}); 
	   if(myTransText!=""){
		var doc = TranslatorIM.DOC;


		doc.getElementById('SL_loading').style.display='block';
		TranslatorIM.SL_IS_DICTIONARY=0;
		doc.getElementById('SL_TTS_voice').style.display='block';
		doc.getElementById('SL_bbl_font_patch').style.display='none';
			       
		if(TranslatorIM.AVOIDAUTODETECT==0){

//VL: Removed system detector
//		     var resp = TranslatorIM.i18n_LanguageDetect(myTransText,0);
		     var resp = "";		
		     if (resp != ""){
	                TranslatorIM.SL_DETECT = resp;
		        TranslatorIM.SL_FLAG=0;
			var DetLang = resp;

                       	var AUTO = doc.getElementById('SL_locer').checked;
			if(AUTO==false || doc.getElementById('SL_lng_from').value=="auto"){
                                var cnt=0;
                        	var LANGSALL = FExtension.element(TranslatorIM.SL_LOC,'extLanguages').split(",");
				var LANGS = TranslatorIM.SL_LNG_LIST.split(",");


                        	for (var i = 0; i < LANGSALL.length; i++){
					var templang = LANGSALL[i].split(":");
					if(DetLang == templang[0]){ 
					        var tmp = doc.getElementById('SL_lng_from').value;
						if(tmp == "" || tmp == "auto") tmp = TranslatorIM.SL_langSrc;
						TranslatorIM.SL_FLAG=1;
						cnt=1;
					}
				}


                       	        TranslatorIM.SL_WRONGLANGUAGEDETECTED=0;
				if(cnt==0){
       	                                TranslatorIM.SL_DETECT = DetLang;
					TranslatorIM.SL_setTMPdata("BL_D_PROV","Google");
					TranslatorIM.SL_setTMPdata("BL_T_PROV","Google");
					TranslatorIM.SL_WRONGLANGUAGEDETECTED=1;
				}
                                TranslatorIM.SL_HideShowTTSicon(); 
       	                	TranslatorIM.LNGforHISTORY = DetLang;

        	                TranslatorIM.SL_SID_FROM = doc.getElementById('SL_lng_from').value;
				TranslatorIM.SL_SID_TO   = doc.getElementById('SL_lng_to').value;
			        if(TranslatorIM.SL_SID_TO!=""){
					doc.getElementById('SL_lng_from').value=TranslatorIM.SL_SID_FROM;
					doc.getElementById('SL_lng_to').value=TranslatorIM.SL_SID_TO;
				}


		                if(doc.getElementById('SL_lng_to').value==resp && doc.getElementById('SL_lng_from').value!="auto"){
		                        var TMP=doc.getElementById('SL_lng_to').value;
		                        doc.getElementById('SL_lng_to').value = doc.getElementById('SL_lng_from').value;
	        	                doc.getElementById('SL_lng_from').value = TMP;
					TranslatorIM.SL_SID_FROM=doc.getElementById('SL_lng_from').value;
					TranslatorIM.SL_SID_TO=doc.getElementById('SL_lng_to').value;
                                        TranslatorIM.AutoFlipState=1;
					TranslatorIM.FlippedByAuto=1;
	       	        	}else{
				// AVOIDING AUTO DETETECT TAG 
					var autopattern = TranslatorIM.AUTOhandler(doc,AUTO,DetLang);
	       	        		if(doc.getElementById('SL_lng_from').value!=autopattern){
	                       	                cnt=0;
						for (var i = 0; i < LANGS.length; i++){
							var templang = LANGS[i].split(":");
							if(DetLang == templang[0]) cnt=1;
						}
						if(cnt==1) doc.getElementById('SL_lng_from').value=DetLang;
					}
				}
        		        TranslatorIM.SL_SETINTERVAL_ST=1;
        	       } else  TranslatorIM.SL_SETINTERVAL_ST=1;   
		     } else {
 			var big5 = TranslatorIM.DetectBig5(myTransText);
                        big5=0;
			if(big5 == 0){
				if(DET == 0) TranslatorIM.DODetection(myTransText);
				else         TranslatorIM.MS_DETECTOR(myTransText);
			}else{
				TranslatorIM.MS_DETECTOR(myTransText);
			}

		     }
		}else 		TranslatorIM.SL_SETINTERVAL_ST=1;
		TranslatorIM.AVOIDAUTODETECT=0;
		var Tobj = doc.getElementById('SL_shadow_translation_result');
		var Tobj2 = doc.getElementById('SL_shadow_translation_result2');

                var SLdivField=doc.getElementById('SL_shadow_translator');
               	Tobj.innerText = "";
                Tobj2.innerText = "";

       		doc.getElementById('SL_loading').style.display='block';

		SLdivField.style.display='block';

		var cntr = 0;

		setTimeout(function(){
		    var SLIDL = setInterval(function(){
			if(cntr<250) {
			  if(TranslatorIM.SL_SETINTERVAL_ST==1) {
				clearInterval(SLIDL);
                                TranslatorIM.SL_SETINTERVAL_ST=0;
				TranslatorIM.SL_EXECUTE_TRANSLATION(myTransText,evt,st);
					if(Tobj.outerHTML.replace(/<[^>]*>?/g,'')==""){
						doc.getElementById('SL_loading').style.display = 'block';
		                                TranslatorIM.SL_JUMP(doc);
						doc.getElementById('SL_loading').style.display = 'none';
		                        }
				doc.getElementById('SL_loading').style.display = 'none';
				return true;
			  }
			} else {cntr=0;TranslatorIM.SL_SETINTERVAL_ST=1;}
			cntr++;
		    },10);  
 	         },50);  

          }	
	},

	InlineDataTransmitter: function (data){
	    data = unescape(data);
	    inlinerInjectHandleMessage({name: "inlinerSelectionResponse", message: data});
	},



	FIND_PROVIDER: function(list,ln){
	  var arr = list.split(",");
	  var cnt=-1
	  for(var i=0; i<arr.length; i++){
		if(arr[i]==ln) cnt++;
	  }
	  return cnt;
	},


        SL_SET_PROVIDERS: function(mode){
          TranslatorIM.ListProviders="";
 	  var doc = TranslatorIM.DOC;
 	  var from = doc.getElementById("SL_lng_from").value;

	  var list = TranslatorIM.SL_LNG_CUSTOM_LIST;

	  if(list=="all") list = TranslatorIM.bblLISTofPRpairs[0];

	  var L1 = list.split(",");
	  var finded = 0;
	  for(var i=0; i<L1.length; i++){
	  	if(L1[i] == TranslatorIM.SL_DETECT) finded = 1;
	  }


//	  if(finded==0)	  if(TranslatorIM.SL_DETECT!="" && from=="auto") from = TranslatorIM.SL_DETECT;
//	  else	  if(TranslatorIM.SL_DETECT!="") from = TranslatorIM.SL_DETECT;

	  if(finded==1)	  if(TranslatorIM.SL_DETECT!="") from = TranslatorIM.SL_DETECT;


	  if(doc.getElementById("SL_locer").checked==true)  from = doc.getElementById("SL_lng_from").value;

 	  var to = doc.getElementById("SL_lng_to").value;

 	  try{

 	  if(to!=""){
 	   for(var I=0; I<TranslatorIM.LISTofPR.length; I++){
            if(mode==1){
		    if(TranslatorIM.BL_D_PROV == TranslatorIM.LISTofPR[I]) 	doc.getElementById("SL_P"+I).className="SL_BL_LABLE_ON";
		    else doc.getElementById("SL_P"+I).className="SL_BL_LABLE_OFF";
	    }else{
		    if(TranslatorIM.BL_T_PROV == TranslatorIM.LISTofPR[I]) 	doc.getElementById("SL_P"+I).className="SL_BL_LABLE_ON";
		    else doc.getElementById("SL_P"+I).className="SL_BL_LABLE_OFF";
	    }


	    if(from!="auto"){

	     var ftemp = from;
	     if(TranslatorIM.SL_DETECT!=from) ftemp = TranslatorIM.SL_DETECT;
	     if(doc.getElementById('SL_locer').checked==true) ftemp = from;

		     if(TranslatorIM.FIND_PROVIDER(TranslatorIM.bblLISTofPRpairs[I],ftemp) ==-1 || TranslatorIM.FIND_PROVIDER(TranslatorIM.bblLISTofPRpairs[I],to)==-1) doc.getElementById("SL_P"+I).className="SL_BL_LABLE_DEACT";
		     else TranslatorIM.ListProviders=TranslatorIM.ListProviders+TranslatorIM.LISTofPR[I]+",";
	    } else {
		     if(TranslatorIM.FIND_PROVIDER(TranslatorIM.bblLISTofPRpairs[I],TranslatorIM.SL_DETECT) ==-1 || TranslatorIM.FIND_PROVIDER(TranslatorIM.bblLISTofPRpairs[I],to)==-1) doc.getElementById("SL_P"+I).className="SL_BL_LABLE_DEACT";
		     else TranslatorIM.ListProviders=TranslatorIM.ListProviders+TranslatorIM.LISTofPR[I]+",";


	    }
            TranslatorIM.ListProviders=TranslatorIM.ListProviders.replace("Translator,Translator","Translator");
           }
	  }
	  } catch(ex){}

	  if(TranslatorIM.SL_SHOW_PROVIDERS==0) {
	        var PR = "Google";
		TranslatorIM.ListProviders= PR + ",";	  
		TranslatorIM.SL_setTMPdata("BL_D_PROV",PR);
		TranslatorIM.SL_setTMPdata("BL_T_PROV",PR);
	  }           

        },



	FIND_PROVIDER: function(list,ln){
	  var arr = list.split(",");
	  var cnt=-1

	  for(var i=0; i<arr.length; i++){
		if(arr[i]==ln) cnt++;
	  }
	  return cnt;
	},



	SET_FIRST_AVAILABLE_PROV: function(){

	  if(TranslatorIM.SL_SHOW_PROVIDERS!=0) {
	    var doc = TranslatorIM.DOC;
	    var s = TranslatorIM.GET_TEXT();
	    if(s=="" && TranslatorIM.SL_temp_result!="") s=TranslatorIM.SL_temp_result;

	    s=s.replace(/(^[\s]+|[\s]+$)/g, '');
	    var theQ=s.split(" ").length;

  	    if(s.match(/[-/ΓÇº┬╖∩╣ò∩╣ù∩╝ü∩╝Ü∩╝îπÇé∩╣û∩╝ƒ:-?!.,:{-~!"^_`\[\]]/g)!=null) theQ=100;
	    //if(TranslatorIM.SL_dict_bbl=="false") theQ=100;

	    if (s.match(/[\u3400-\u9FBF]/) && s.length>1) theQ=100;

	    TranslatorIM.SL_SET_PROVIDERS(theQ);

	    var theList = TranslatorIM.ListProviders.split(",");

	    if(theQ==1){
	      TranslatorIM.SL_MODE=1;	
	      if(TranslatorIM.BL_D_PROV=="" || TranslatorIM.BL_D_PROV==null || TranslatorIM.BL_D_PROV=="undefined"){
		  if(TranslatorIM.SL_dict_bbl=="true"){
			  var arr1 = TranslatorIM.SL_DICT_PRESENT.split(",");
			  for(I=0; I<(theList.length-1); I++){
			    for(J=0; J<arr1.length; J++){
		        	var arr2=arr1[J].split(":");
				if(arr2[1]==1 && theList[I]==arr2[0]){				
					TranslatorIM.SL_setTMPdata("BL_D_PROV",arr2[0]);
					I=1000;J=1000;
				}
			    }
			  }
		 } else {
			TranslatorIM.SL_setTMPdata("BL_D_PROV",theList[0]);
		 }

		  var arr = TranslatorIM.SL_ALL_PROVIDERS_BBL.split(",");	
		  for(I=0; I<arr.length; I++){
			if(arr[I]==TranslatorIM.BL_D_PROV){
				doc.getElementById("SL_P"+I).className="SL_BL_LABLE_ON";
				I=1000;
			}
		  }
	      } else {
		 if(TranslatorIM.ListProviders.indexOf(TranslatorIM.BL_D_PROV)==-1){
		  var arr1 = TranslatorIM.SL_DICT_PRESENT.split(",");
		  for(I=0; I<(theList.length-1); I++){
		    for(J=0; J<arr1.length; J++){
		        var arr2=arr1[J].split(":");
			if(arr2[1]==1 && theList[I]==arr2[0]){
//				TranslatorIM.SL_setTMPdata("BL_D_PROV",arr2[0]);
				doc.getElementById("SL_P"+I).className="SL_BL_LABLE_ON";
				I=1000;J=1000;
			}
		    }
		  }
		 }
	         if(TranslatorIM.ListProviders.indexOf(TranslatorIM.BL_D_PROV) == -1){
			TranslatorIM.SL_setTMPdata("BL_D_PROV",theList[0]);	
			TranslatorIM.SET_FIRST_AVAILABLE_PROV();
		 }
	      }

	    }else{

	      TranslatorIM.SL_MODE=0;
	      if(TranslatorIM.BL_T_PROV=="" || TranslatorIM.BL_T_PROV==null || TranslatorIM.BL_T_PROV=="undefined"){
		  TranslatorIM.SL_setTMPdata("BL_T_PROV",theList[0]);
		  var arr = TranslatorIM.SL_ALL_PROVIDERS_BBL.split(",");	
		  for(I=0; I<arr.length; I++){
			if(theList[0]==arr[I]){
				doc.getElementById("SL_P"+I).className="SL_BL_LABLE_ON";
				break;
			}
		  }
	      } else {
		 if(TranslatorIM.ListProviders.indexOf(TranslatorIM.BL_T_PROV)!=-1){
		  var arr = TranslatorIM.SL_ALL_PROVIDERS_BBL.split(",");	
		  for(I=0; I<arr.length; I++){
			if(arr[I]==TranslatorIM.BL_T_PROV){
				doc.getElementById("SL_P"+I).className="SL_BL_LABLE_ON";
				I=1000;
			}
		  }
		 } else {
		
		  var arr = TranslatorIM.ListProviders.split(",");	
		  TranslatorIM.SL_setTMPdata("BL_T_PROV",arr[0]);
//		  doc.getElementById("SL_P0").className="SL_BL_LABLE_ON";
	   	  TranslatorIM.SET_FIRST_AVAILABLE_PROV();
		 }
	      }

            }	


	    if(TranslatorIM.SL_WRONGLANGUAGEDETECTED==1){
		var pattern = doc.getElementById("SL_Bproviders").getElementsByTagName("div");
		var cnt=0;
		for(var j=0; j<pattern.length; j++){
		    if(pattern[j].id.indexOf("SL_PN")==-1){
			if(pattern[j].title.toLowerCase()=="google"){
				pattern[j].className="SL_BL_LABLE_ON";
			} else {
				pattern[j].className="SL_BL_LABLE_DEACT";
			}
		    }
		}
		TranslatorIM.SL_setTMPdata("BL_D_PROV","Google");
		TranslatorIM.SL_setTMPdata("BL_T_PROV","Google");
	    }


	 } else{
		TranslatorIM.SL_setTMPdata("BL_D_PROV","Google");
		TranslatorIM.SL_setTMPdata("BL_T_PROV","Google");
	 }

        },

/////////

	SL_EXECUTE_TRANSLATION: function(myTransText,evt,st, win) {
	 TranslatorIM.ONLYONCE = 0;
         var doc = FExtension.browserInject;
 	 var doc2 = doc.getDocument();
	 var tmptext = TranslatorIM.GET_TEXT();
	 if(tmptext !="") myTransText = tmptext;
         else myTransText = TranslatorIM.SL_TEMP_TEXT;

	 if(myTransText != TranslatorIM.SL_TEMP_TEXT) myTransText=TranslatorIM.SL_TEMP_TEXT;
         var t1 = new Date().getTime();
         var S = doc2.getElementById('SL_lng_from').value;
         var T = doc2.getElementById('SL_lng_to').value;
                if(doc2.getElementById("SL_player2")) {
			doc2.getElementById("SL_player2").innerText="";
			doc2.getElementById("SL_player2").style.display="none";
			doc2.getElementById("SL_player2").style.height="0px";
		}
	 var ttl = TranslatorIM.SL_DETECT;
	 if(ttl == "") ttl = 	doc2.getElementById('SL_lng_from').value;
//	 TranslatorIM.SL_DETECT = ttl;

         doc2.getElementById('SL_TTS_voice').title=TranslatorIM.SL_GetLongName(ttl);

   	 TranslatorIM.SET_FIRST_AVAILABLE_PROV();
	 if(TranslatorIM.ListProviders=="" && TranslatorIM.SL_SHOW_PROVIDERS == 1) TranslatorIM.NoProvidersAlert();
	 else {
           var STATUS = TranslatorIM.DETERMIN_IF_LANGUAGE_IS_AVAILABLE_BBL();

	   if(STATUS == 0 && TranslatorIM.SL_SHOW_PROVIDERS == 0) TranslatorIM.NoProvidersAlert();
	   else {
	           if(doc2.getElementById("SL_locer").checked==true){
		 	if(doc2.getElementById('SL_lng_from').value!="auto"){
				doc2.getElementById('SL_lng_from').title="";
			}
		   }



//		   chrome.runtime.sendMessage({greeting: "CM_BBL:>" + T}, function(response) {}); 


		   if(TranslatorIM.SL_DETECT != "" && doc2.getElementById("SL_locer").checked==false && S != "auto") {
			var LANGS = TranslatorIM.SL_LNG_LIST.split(",");
	        	cnt=0;
			for (var i = 0; i < LANGS.length; i++){
				var templang = LANGS[i].split(":");
				if(TranslatorIM.SL_DETECT == templang[0]) cnt=1;
			}
			if(cnt==1) doc2.getElementById('SL_lng_from').value=TranslatorIM.SL_DETECT;		
		   }
		   var PR = TranslatorIM.BL_T_PROV;
		   if(TranslatorIM.SL_MODE==1) PR = TranslatorIM.BL_D_PROV;
		   doc2.getElementById('SL_shadow_translation_result').innerText="";
		   doc2.getElementById('SL_shadow_translation_result2').innerText="";

	           myTransText = myTransText.replace(/\t/g,"");

	 	   if(T!="") TranslatorIM.SL_SAVE_FAVORITE_LANGUAGES(T, 'SL_lng_to', 0, TranslatorIM.SL_FAV_LANGS_BBL, "BBL");
		   else TranslatorIM.SL_SAVE_FAVORITE_LANGUAGES(TranslatorIM.SL_langDst_bbl2, 'SL_lng_to', 0, TranslatorIM.SL_FAV_LANGS_BBL, "BBL");


		   if(PR == "" && TranslatorIM.ListProviders!="") {
			var theList = TranslatorIM.ListProviders.split(",");
			PR = theList[0];
			TranslatorIM.BL_D_PROV = PR;
			TranslatorIM.SET_FIRST_AVAILABLE_PROV();
		   }

		   if(PR.toLowerCase()=="microsoft") { 
			TranslatorIM.MS(S,T,myTransText,st); return false;
		   }

		   if(PR.toLowerCase()=="yandex" || PR.toLowerCase()=="translator" ) { 
			TranslatorIM.SL_YANDEX(myTransText,S,T); return false;
		   }

		   if(PR == "Google"){
			doc2.getElementById('SL_loading').style.display = 'block';
	           	myTransText = myTransText.trim();
//			myTransText = myTransText.replace(/#/g,"");

	                if(myTransText.length<=TranslatorIM.SL_Balloon_translation_limit){
				if(myTransText != ""){

					TranslatorIM.SL_SETINTERVAL_PROXY=0;
        	        	        doc2.getElementById('SL_balloon_obj').alt="1";

			        	myTransText=myTransText.replace(/(^[\s]+|[\s]+$)/g, '');
				       	var theQ=myTransText.split(" ").length;

					if(myTransText.match(/[-/‧·﹕﹗！：，。﹖？:-?!.,:{-~!"^_`\[\]]/g)!=null) theQ=100;
//				        if(TranslatorIM.SL_dict_bbl=="false") theQ=100;

					if(DetectBig5(myTransText)==1 && theQ==1 && myTransText.length>5) theQ=100;

					var num = Math.floor((Math.random() * SL_GEO.length)); 
					var theRegion = SL_GEO[num];
					if(TranslatorIM.SL_DOM!="auto") theRegion=TranslatorIM.SL_DOM;
					var baseUrl ="https://translate.google."+theRegion+"/translate_a/single";
					var Stemp=S;
                		        if(doc2.getElementById("SL_locer").checked==false) Stemp = TranslatorIM.SL_DETECT;

//					if(Stemp=="en" || TranslatorIM.SL_FLAG==0) Stemp="auto";

					if(TranslatorIM.SL_WRONGLANGUAGEDETECTED==1) Stemp="auto";
			
					var a=Math.floor((new Date).getTime()/36E5)^123456;
					var tk = a+"|"+Math.floor((Math.sqrt(5)-1)/2*(a^654321)%1*1048576);

					if(Stemp == "srsl") Stemp = "sr";
					if(Stemp == "tlsl") Stemp = "tl";
					if(T == "srsl") T = "sr";
					if(T == "tlsl") T = "tl";

					var SL_Params = "client=gtx&dt=t&dt=bd&dj=1&source=input&q="+encodeURIComponent(myTransText)+"&sl="+Stemp+"&tl="+T+"&hl=en&tk="+tk;


					if(theQ==1){
						TranslatorIM.SL_MODE=1;
					        if(TranslatorIM.SL_DOM!="auto") theRegion=TranslatorIM.SL_DOM;
						myTransText=myTransText.replace(/\./gi,"");
						myTransText=myTransText.replace(/\)/gi,"");
						myTransText=myTransText.replace(/\(/gi,"");
						myTransText=myTransText.replace(/\"/gi,"");
						SL_Params = "client=gtx&dt=t&dt=bd&dj=1&source=input&q="+encodeURIComponent(myTransText.toLowerCase())+"&sl="+Stemp+"&tl="+T+"&hl=en&tk="+tk;
					}

					SL_Params = SL_Params.replace("sl=&","sl=auto&");

				        chrome.runtime.sendMessage({greeting: "TR_GOOGLE:>"+baseUrl+","+ SL_Params+","+ theQ}, function(response) {});

					var MAX = 10;
				        var tries=0;

					setTimeout(function(){
					    var SLIDL="";
					    clearInterval(SLIDL);
					    SLIDL = setInterval(function(){

					        if(chrome.runtime){
					           chrome.runtime.sendMessage({greeting: 1}, function(response) {


				        	     if(response && response.farewell){
					        	var theresponse = response.farewell.split("~");
							TranslatorIM.BBL_RESULT=theresponse[52].replace(/\^/ig,"~");
					                TranslatorIM.BBL_RESULT=TranslatorIM.BBL_RESULT.replace(/\\"/g,"'");
					                TranslatorIM.BBL_RESULT=TranslatorIM.BBL_RESULT.replace(/\\n/g,"<br>");
					                TranslatorIM.BBL_RESULT=TranslatorIM.BBL_RESULT.replace(/\\u0027/g,"'");
//TranslatorIM.BBL_RESULT="";				

							if(TranslatorIM.BBL_RESULT!="" || tries>=MAX) {
								var resp = TranslatorIM.BBL_RESULT;
								TranslatorIM.BBL_RESULT="";
								clearInterval(SLIDL);
								if(doc2.getElementById("SL_shadow_translator").style.display=='block'){	
									var S = doc2.getElementById('SL_lng_from').value;
							           	var T = doc2.getElementById('SL_lng_to').value;
							           	var myTransText = doc.getSelectionText();
									if(myTransText == "") myTransText = TranslatorIM.SL_TEMP_TEXT;
									if(myTransText != TranslatorIM.SL_TEMP_TEXT) myTransText=TranslatorIM.SL_TEMP_TEXT;
						       	   		var theQ=100;

							       	   	if(resp.indexOf('"reverse_translation":')>-1)theQ=1;
								   	var NoDict=0;
							                if(resp.indexOf('{"trans":')>-1){
							       		 	if(theQ>1){
							                                  var ReadyToUseGoogleText="";
							                                  var Gr1=resp.split('"trans":"');
							                               	  for(var h=1; h<Gr1.length; h++){
							                      	              var Gr2 = Gr1[h].split('","orig"');
							               	                      var Gr3 = Gr2[0].replace(/\\n/ig,"<br>");
							               	                      Gr3 = Gr3.replace(/\\r/ig,"");
						      		                              Gr3 = Gr3.replace(/\\"/ig,"'");
						       	        	                      Gr3 = Gr3.replace(/\\u0026/ig,"&");
						       	                	              Gr3 = Gr3.replace(/\\u003c/ig,"<");
							                        	      Gr3 = Gr3.replace(/\\u003e/ig,">");
								                              Gr3 = Gr3.replace(/\\u0027/ig,"'");
								                              Gr3 = Gr3.replace(/\\u003d/ig,"=");
								                              Gr3 = Gr3.replace(/\\/g,"");
                        	                                                              //Gr3 = Gr3.charAt(0).toUpperCase() + Gr3.slice(1);
							                                      ReadyToUseGoogleText=ReadyToUseGoogleText+Gr3;
							                                   }
											   resp = ReadyToUseGoogleText;
							                       	}
										var HID=2;
									} 
						
									if(resp.indexOf('sentences":')>-1){
							                        TranslatorIM.SL_SETINTERVAL_PROXY++;
							               		if(theQ==1 && resp.indexOf('src":"')==-1){
							       		         	if(resp.indexOf('","')!=-1){
									                      	resp = resp.replace('["',''); 
							        				var R1 = resp.split('","');
							                	                resp = R1[0];
						        	                	} else resp = resp.replace(/"/ig,'');
						                	                NoDict = 1;
										}

									        if(NoDict==0 && resp.indexOf('sentences":')>-1){
											TranslatorIM.SL_SETINTERVAL_PROXY++;
											resp = TranslatorIM.SL_DICTparser(resp);
//											resp = resp.replace(/\"/ig,"'");
											resp = resp.replace(/\''/ig,"'");
											resp = resp.replace(/\\/g,"");
									        } else {
											resp="";
											TranslatorIM.SL_TR_ROUTER(myTransText,st);
										}

										var idtmp="";
										var HID=6;
										if(resp.indexOf('id=_X')==-1) HID=2;
									}else{
										if(resp.indexOf('word_postproc":')>-1){
								                        TranslatorIM.SL_SETINTERVAL_PROXY++;
								               		if(theQ==1 && resp.indexOf('word_postproc":')==-1){
							       			         	if(resp.indexOf('","')!=-1){
										                      	resp = resp.replace('["',''); 
							        					var R1 = resp.split('","');
							                	        	        resp = R1[0];
								                        	} else resp = resp.replace(/"/ig,'');
							        	                        NoDict = 1;
											}
									        	if(NoDict==0 && resp.indexOf('sentences":')>-1){
												TranslatorIM.SL_SETINTERVAL_PROXY++;
												resp = TranslatorIM.SL_DICTparser(resp);
										        } else {
											resp="";
											TranslatorIM.SL_TR_ROUTER(myTransText,st);
											}
											var idtmp="";
											var HID=6;
											if(resp.indexOf('id=_X')==-1) HID=2;
										}
									}
									if(resp.indexOf("SL_DICT")!=-1){
										var HID=6;
										resp = TranslatorIM.SL_DICTparser(resp);
									} else HID=2;

									if(resp != "" && resp != "<#>"){	
								                var resptmp = resp;
										if(resp.indexOf('<div')==-1) resptmp = TranslatorIM.PPB_tts_icon(T,resp);

										resptmp = DOMPurify.sanitize(resptmp);

										doc2.getElementById('SL_shadow_translation_result').innerHTML=resptmp;
										doc2.getElementById('SL_shadow_translation_result2').innerHTML=resptmp;

										TranslatorIM.ACTIVATE_THEMEbbl(TranslatorIM.THEMEmode);
								                TranslatorIM.SL_JUMP(doc2);
						        	                TranslatorIM.SL_temp_result=resp;
										if (TranslatorIM.SL_TH_2 == 1){

											var SLnow = new Date();
											SLnow = SLnow.toString();
											var TMPtime = SLnow.split(" ");
											var CurDT = TMPtime[1] + " " + TMPtime[2] + " " + TMPtime[3] + ", " + TMPtime[4];
								                        var LNGfrom = S;
								                        if(S=="auto" || doc2.getElementById("SL_locer").checked == false) var LNGfrom = TranslatorIM.LNGforHISTORY;
											if(TranslatorIM.SL_WRONGLANGUAGEDETECTED==1) LNGfrom="auto";
						        	                        var ImtranslatorGoogleResult="";
						                	                myTransText=myTransText.replace(/~/ig," ");
						                        		        var ImtranslatorGoogleResult4 = resp.replace(/~/ig," ");
							 				if(theQ==1){
												var TEMresp = ImtranslatorGoogleResult4.split("<br>");
												if(TEMresp.length>2){
													for(var k=0; k<TEMresp.length; k++){
														if(k>0)ImtranslatorGoogleResult = ImtranslatorGoogleResult + TEMresp[k];
													}
												} else ImtranslatorGoogleResult = ImtranslatorGoogleResult4;
											} else ImtranslatorGoogleResult = ImtranslatorGoogleResult4;
									
										        myTransText=myTransText.replace(/\^/g,"@");


											doc.runtimeSendMessage({greeting: "[b]" + myTransText + "~~" + ImtranslatorGoogleResult + "~~" + LNGfrom + "|" + T + "~~"+ doc2.location+"~~"+CurDT+"~~"+HID+"~~G^^"}, function(response) {
												if(response){ 
												//	console.log(response.farewell); 
												}
											});
										}
									} else 	TranslatorIM.SL_TR_ROUTER(myTransText,0);

									doc2.getElementById('SL_shadow_translation_result').style.direction = "ltr";
									doc2.getElementById('SL_shadow_translation_result').style.textAlign = "left";
									if(T=="ar" || T=="iw" || T=="fa" || T=="yi" || T=="ur" || T=="ps" || T=="sd" || T=="ckb" || T=="ug" || T=="dv" || T=="prs"){
										doc2.getElementById('SL_shadow_translation_result').style.direction = "rtl";
										doc2.getElementById('SL_shadow_translation_result').style.textAlign = "right";
									}
									doc2.getElementById('SL_shadow_translator').style.display = 'block';
									TranslatorIM.SL_temp_result = resp;
									if(doc2.getElementById('SL_shadow_translator').offsetHeight > 100) TranslatorIM.SL_BALLON_H = doc2.getElementById('SL_shadow_translator').offsetHeight;
								   }	
				        	    	}else tries++;
						     }
		
					           });
						}
					    },150);  
					  
 		        		 },50);  

				  } 

		            } else TranslatorIM.SL_TR_ROUTER(myTransText,st);
		  }
		}
	      }
	      TranslatorIM.SAVE_SES_PARAMS();
	},

	SL_TR_ROUTER: function(text,st){
	   if(TranslatorIM.ONLYONCE==0){
	     var doc = FExtension.browserInject;
	     var doc2 = doc.getDocument();
	     var T = doc2.getElementById('SL_lng_to').value;
	     var S = doc2.getElementById('SL_lng_from').value;
	     if(S=="auto" && TranslatorIM.SL_DETECT != "") S=TranslatorIM.SL_DETECT;	
      	     if(doc2.getElementById("SL_locer").checked==false && TranslatorIM.SL_DETECT != "") S = TranslatorIM.SL_DETECT;
	     TranslatorIM.LAST_CHANCE_TRANSLATION(S,T,text,"Google");
	     TranslatorIM.ONLYONCE=1;
	   }
	},





	SL_DICTparser: function (resp){

		TranslatorIM.SL_IS_DICTIONARY=1;
	        var ext = FExtension.browserInject;
		var doc = ext.getDocument();
		doc.getElementById('SL_player2').style.display="none";

		var parsedRES="",parsedTRANS="";
		var PARTS = new Array();
		var SL_to = doc.getElementById('SL_lng_to').value;
		var SL_from = doc.getElementById('SL_lng_from').value;
		var ttsurl=ext.getURL('content/img/util/tts.png');


		var SLDetLngCodes =    new Array ();
		var SLDetLngNames =    new Array ();
//		var SL_Lnum = SL_Languages.split(",");
		var SL_Lnum = TranslatorIM.SL_LNG_LIST.split(",");
		for(var i = 0; i < SL_Lnum.length; i++){
		        var SL_tmp = SL_Lnum[i].split(":");
			SLDetLngCodes.push(SL_tmp[0]);
			SLDetLngNames.push(SL_tmp[1]);
		}
		var RESParr = resp.split("#");
		var tmpr = RESParr[0].replace("SL_DICT[","").replace("]","");
		var tmprarr = tmpr.split("~");
		resp=RESParr[1];
		var DETECTEDlng=tmprarr[0];
		var DETECTEDlongName="English";
		for (var z=0; z<SLDetLngCodes.length; z++){
			if(DETECTEDlng==SLDetLngCodes[z]) { DETECTEDlongName=SLDetLngNames[z];break; }
		}
		for (var z=0; z<SLDetLngNames.length; z++){
			if(SL_from==SLDetLngNames[z]) { SL_from=SLDetLngCodes[z];break; }
		}
		var TRANSLATION = tmprarr[1];

//		var Gurl=FExtension.browserInject.getURL('content/html/popup/dictionary.html');
		var Gurl="";
		var WAY = TranslatorIM.SL_TTSicn(DETECTEDlng);

		var WAY2 = TranslatorIM.SL_TTSicn(SL_to);
		var SL_DETECT = DETECTEDlng;

		if(TranslatorIM.SL_ALLvoices.indexOf(SL_DETECT)!=-1){
			if(resp.indexOf("|")!=-1){
				if(WAY == 1) 	parsedTRANS = "<div id=_X><div id=_XL><div class=TTS"+WAY+" id=SL_000 style=\"background:url("+ttsurl+");\" lang=\""+DETECTEDlng+"\" title=\""+TRANSLATION+"\"></div></div><div id=_XR align=left style='margin-left:5px;font-weight:bold;font-size:14px;'>" + TRANSLATION + "</div></div>";
				else    	parsedTRANS = "<div id=_X><div id=_FL><div class=TTS"+WAY+" id=SL_000 style=\"background:url("+ttsurl+");\" lang=\""+DETECTEDlng+"\" title=\""+TRANSLATION+"\"></div></div><div id=_FR>" + TRANSLATION + "</div></div>";
			} else {
				if(WAY == "1") parsedTRANS = "<div dir=rtl>"+TRANSLATION+"</div>";
				else parsedTRANS = "<div dir=ltr>"+TRANSLATION+"</div>";
			}

		} else {
			if(resp.indexOf("|")!=-1){
				if(WAY == 1) 	parsedTRANS = "<div id=_X><div id=_XR align=left style='margin-left:5px;font-weight:bold;font-size:14px;'>" + TRANSLATION + "</div></div>";
				else    	parsedTRANS = "<div id=_X><div id=_FR>" + TRANSLATION + "</div></div>";
			} else {
				if(WAY == "1") parsedTRANS = "<div dir=rtl>"+TRANSLATION+"</div>";
				else parsedTRANS = "<div dir=ltr>"+TRANSLATION+"</div>";
			}
		}



		if(resp.indexOf('|')!=-1){
		   try{
		        var Rline,article;

			const obj = resp.split(";");
			for(var i = 0; i < obj.length; i++){
				var tp = obj[i].split(":");
				parsedRES = parsedRES + "<div id=_Y>" +tp[0] + "</div>";
				var wrd = tp[1].split("|");
				for (var j=1; j < wrd.length; j++){
					var wrd2 = wrd[j].split(">");
				        article="<div id=_ART>" + wrd2[0] + "</div> ";
                               		Rline = "";
					var reverse = wrd2[1].split(",");
					for(var k = 0; k < reverse.length; k++){
						var tmpLNK = reverse[k].replace(/\\'/g,'~');
						tmpLNK = tmpLNK.replace(/\\u0027/g,'~');

						var F = SL_from;
						var T = SL_to;
						if(k < reverse.length-1){
							Rline = Rline + "<a class=_ALNK title=\""+tmpLNK+"\" id='SL_" +i+"_"+ j+"_"+ k + "' href='"+Gurl+"?dir="+ SL_from + "|" + SL_to +"&text=" + encodeURIComponent(tmpLNK) + "'>" + tmpLNK + "</a>, ";
						} else {
							Rline = Rline + "<a class=_ALNK title=\""+tmpLNK+"\" id='SL_" +i+"_"+ j+"_"+ k + "' href='"+Gurl+"?dir="+ SL_from + "|" + SL_to +"&text=" + encodeURIComponent(tmpLNK) + "'>" + tmpLNK + "</a>";
						}
					}


					var REV=reverse;
					var WORD=wrd2[0];
					var SL_myTTS = article;// + REV;
				        if(SL_TTS.indexOf(SL_to)!=-1 || (G_TTS.indexOf(SL_to)!=-1 && TranslatorIM.SL_GVoices!="0")){
					   if(WAY2==1) SL_myTTS = "<div id=_X><div id=_XL><div class=_V id=\"SL_"+i+j+"\" style=\"background:url("+ttsurl+");\" lang=\""+SL_to+"\" title=\"" + WORD + "\"></div></div><div id=_XR>" + article + "</div></div>";
					   else SL_myTTS = "<div id=_X><div id=_FL><div class=TTS"+WAY2+" id=\"SL_"+i+j+"\" style=\"background:url("+ttsurl+");\" lang=\""+SL_to+"\" title=\"" + WORD + "\"></div></div><div id=_XR>" + article + "</div></div>";
					}			
					parsedRES = parsedRES + "<div id=_A><div id=_AL>" + SL_myTTS + "</div><div id=_AR>" + Rline + "</div></div>";

				}
				parsedRES = parsedRES + "<br>";
			}

		        doc.getElementById('SL_TTS_voice').style.display='none';
		        doc.getElementById('SL_bbl_font_patch').style.display='block';

		      } catch(ex){
			const obj = JSON.parse(resp);
		       	parsedRES="";
			parsedTRANS=obj.sentences[0].trans;
		      }	



		    } else {
		   	Tr2=Tr1[0].split('trans":"');
	   		Tr3=Tr2[1].split('"');
		   	parsedTRANS = Tr3[0];
		        doc.getElementById('SL_TTS_voice').style.display='block';
		    }

		 if(parsedRES==""){
		   doc.getElementById('SL_shadow_translation_result').style.direction="ltr";
		   doc.getElementById('SL_shadow_translation_result').style.textAlign="left";
		   if(SL_to=="ar" || SL_to=="iw" || SL_to=="fa" || SL_to=="yi" || SL_to=="ur" || SL_to=="ps" || SL_to=="sd" || SL_to=="ckb" || SL_to=="ug" || SL_to=="dv" || SL_to=="prs"){
			 doc.getElementById('SL_shadow_translation_result').style.direction="rtl";
			 doc.getElementById('SL_shadow_translation_result').style.textAlign="right";
		   }
		 } 
		 parsedRES = parsedTRANS +"<br>"+ parsedRES;
		 SL_temp_result2 = parsedRES;
		 setTimeout(function(){
		     TranslatorIM.SL_ALIGNER1(SL_to);
		     TranslatorIM.SL_ALIGNER2(DETECTEDlng);
		 },5);
		 
		 return parsedRES;

	},


SL_ALIGNER1: function (SL_to){
 var doc = TranslatorIM.DOC;
 var nums=doc.getElementsByTagName("div").length;
 if(SL_to!="ar" && SL_to!="iw" && SL_to!="fa" && SL_to!="yi" && SL_to!="ur" && SL_to!="ps" && SL_to!="sd" && SL_to!="ckb" && SL_to!="ug" && SL_to!="dv" && SL_to!="prs"){
      for(var I = 0; I < nums; I++){
       if(doc.getElementsByTagName("div")[I].id == "_AL")	 doc.getElementsByTagName("div")[I].style.textAlign="left";
      }
 } else {
      for(var I = 0; I < nums; I++){
       if(doc.getElementsByTagName("div")[I].id == "_AL")	 doc.getElementsByTagName("div")[I].style.textAlign="right";
      }
 }
},

SL_ALIGNER2: function (SL_from){
 var doc = TranslatorIM.DOC;
 var nums=doc.getElementsByTagName("div").length;
 if(SL_from!="ar" && SL_from!="iw" && SL_from!="fa" && SL_from!="yi" && SL_from!="ur" && SL_from!="ps" && SL_from!="sd" && SL_from!="ckb" && SL_from!="ug" && SL_from!="dv" && SL_from!="prs"){
      for(var I = 0; I < nums; I++){
       if(doc.getElementsByTagName("div")[I].id == "_AR")	 doc.getElementsByTagName("div")[I].style.textAlign="left";
      }
 } else {
      for(var I = 0; I < nums; I++){
       if(doc.getElementsByTagName("div")[I].id == "_AR")	 doc.getElementsByTagName("div")[I].style.textAlign="right";
      }
 }
},

SL_TTSicn: function (lng){
 var doc = TranslatorIM.DOC;
 var OUT="";
 if(lng!="ar" && lng!="iw" && lng!="fa" && lng!="yi" && lng!="ur" && lng!="ps" && lng!="sd" && lng!="ckb" && lng!="ug" && lng!="dv" && lng!="prs")   OUT=1;
 else   OUT=2;
 return(OUT);
},





	ClickInside: function(event){
		var target = event.target || event.srcElement;
		var id = target.id
           
		var className = target.className;

		if(className == "_V") 	 TranslatorIM.tagClick(event,id);
		if(className == "TTS1") TranslatorIM.tagClick(event,id);
		if(className == "TTS2") TranslatorIM.tagClick(event,id);

		if(className == "_ALNK") {
		    var tags = TranslatorIM.DOC.getElementsByClassName("_ALNK");
		    for (var j=0; j<tags.length; j++){
		         tags[j].href='javascript:void(0);';
			 tags[j].addEventListener('mouseup', function(e){ TranslatorIM.UrltagClick(e) }, false);
			 TranslatorIM.AVOIDAUTODETECT=1;
		    }
		}
	},


	tagClick: function(event,id){
		var doc = TranslatorIM.DOC;
                if(doc.getElementById("SL_player2")) {
			doc.getElementById("SL_player2").innerText="";
			doc.getElementById("SL_player2").style.display="none";
			doc.getElementById("SL_player2").style.height="0px";
		}


		   var SL_from = doc.getElementById('SL_lng_from').value;
		   if(doc.getElementById("SL_000")) doc.getElementById("SL_000").lang=SL_from;
		   event.target.onmousemove = function () {TranslatorIM.SL_ShowBalloon();}
		   var SL_to = doc.getElementById(id).lang;
		   SL_to=SL_to.replace("zh-CN","zh");
		   SL_to=SL_to.replace("zh-TW","zh");

		   if(doc.getElementById('SL_lng_from').value=="auto" || doc.getElementById("SL_locer").checked == false) {if(id=="SL_000") SL_to = TranslatorIM.LNGforHISTORY;}
		   else{ 
			if(id=="SL_000"){
				SL_to = SL_from;

				// By VK . A patch------------------------------------
				if(SL_to.length>7)SL_to="en";
				// By VK . A patch------------------------------------
			}

		   }

	   var text = doc.getElementById(event.target.id).title;
	   text = TranslatorIM.truncStrByWord(text,1200);
	   switch(TranslatorIM.SL_SLVoices){
		case "0": if(TranslatorIM.SL_ALLvoices.indexOf(SL_to)!=-1){
                              if(SL_TTS.indexOf(SL_to)!=-1){
				if(text.length>TranslatorIM.GTTS_length) {
					if(SL_to == "en-gb") SL_to = "g_en-UK_f";
					if(SL_to == "pt-PT") SL_to = "pt";
					if(SL_to == "fr-CA") SL_to = "fr";
					if(SL_to == "zh-TW") SL_to = "g_zh-TW_f";
					if(SL_to == "lzh") SL_to = "g_zh-HK_f";
					if(SL_to == "zh-CN") SL_to = "zh";
					if(SL_to == "yue") SL_to = "zh";

					window.open("https://text-to-speech.imtranslator.net/?dir="+SL_to+"&text="+encodeURIComponent(text)); 
				}else TranslatorIM.Google_TTS(text,SL_to);
			      } else TranslatorIM.Google_TTS(text,SL_to);
			  } else TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNo_Voice"));
			  break;
		case "1": if(TranslatorIM.SL_ALLvoices.indexOf(SL_to)!=-1){
				if(G_TTS.indexOf(SL_to)!=-1) TranslatorIM.Google_TTS(text,SL_to);
				else TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNo_Voice"));
			  } else TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNo_Voice"));
			  break;
		case "2": if(TranslatorIM.SL_ALLvoices.indexOf(SL_to)!=-1){
                              if(SL_TTS.indexOf(SL_to)!=-1) {
					if(SL_to == "en-gb") SL_to = "g_en-UK_f";
					if(SL_to == "pt-PT") SL_to = "pt";
					if(SL_to == "fr-CA") SL_to = "fr";
					if(SL_to == "zh-TW") SL_to = "g_zh-TW_f";
					if(SL_to == "lzh") SL_to = "g_zh-HK_f";
					if(SL_to == "zh-CN") SL_to = "zh";
					if(SL_to == "yue") SL_to = "zh";

					window.open("https://text-to-speech.imtranslator.net/?dir="+SL_to+"&text="+encodeURIComponent(text));
			      }else TranslatorIM.Google_TTS(text,SL_to);
			  } else TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNo_Voice"));
			  break;
	   }

	},



        Google_TTS: function(text,SL_to){
		text = TranslatorIM.truncStrByWord(text,1200);
                var doc = TranslatorIM.DOC;
		if(TranslatorIM.SL_GVoices=="1"){
			if(text.length>TranslatorIM.GTTS_length){
			   text=text.substring(0,TranslatorIM.GTTS_length);
			   doc.getElementById('SL_alert100').style.display="block";
			}
		        TranslatorIM.REMOTE_Voice(SL_to,text);			
		} else {
			if(SL_to == "en-gb") SL_to = "g_en-UK_f";
			if(SL_to == "pt-PT") SL_to = "pt";
			if(SL_to == "fr-CA") SL_to = "fr";
			if(SL_to == "zh-TW") SL_to = "g_zh-TW_f";
			if(SL_to == "lzh") SL_to = "g_zh-HK_f";
			if(SL_to == "zh-CN") SL_to = "zh";
			if(SL_to == "yue") SL_to = "zh";

			window.open("https://text-to-speech.imtranslator.net/?dir="+SL_to+"&text="+encodeURIComponent(text));
		}
	},


        Google_TTS_ON_TOP: function(text,SL_to){
		text = TranslatorIM.truncStrByWord(text,1200);
                var doc = TranslatorIM.DOC;
		if(TranslatorIM.SL_GVoices=="1"){
			if(text.length>TranslatorIM.GTTS_length){
			   text=text.substring(0,TranslatorIM.GTTS_length);
			   doc.getElementById('SL_alert100').style.display="block";
			}
	        	TranslatorIM.REMOTE_Voice(SL_to,text);			
		} else {
			if(SL_to == "en-gb") SL_to = "g_en-UK_f";
			if(SL_to == "pt-PT") SL_to = "pt";
			if(SL_to == "fr-CA") SL_to = "fr";
			if(SL_to == "zh-TW") SL_to = "g_zh-TW_f";
			if(SL_to == "lzh") SL_to = "g_zh-HK_f";
			if(SL_to == "zh-CN") SL_to = "zh";
			if(SL_to == "yue") SL_to = "zh";

			window.open("https://text-to-speech.imtranslator.net/?dir="+SL_to+"&text="+encodeURIComponent(text));
		}
	},


	UrltagClick: function(e){
  	    if(e.which != 3){
		e.target.onmousemove = function () {TranslatorIM.SL_ShowBalloon();}
		TranslatorIM.DOC.getElementById(e.target.id).href='#';
		TranslatorIM.DOC.getElementById(e.target.id).style.cursor='pointer';
		var txt = TranslatorIM.DOC.getElementById(e.target.id).title;
                TranslatorIM.SL_TEMP_TEXT=txt;

		setTimeout(function() {                  
			TranslatorIM.SL_BALLOON_TRANSLATION(txt,null,3); 
		    	TranslatorIM.SL_removeBalloonColor();
		    	TranslatorIM.SL_addBalloonColor();
		}, 150);   
		e.stopPropagation();
		e.cancelBubble = true;       
	    }	
	},



	SL_SCROLL: function(){
		TranslatorIM.SL_bring_UP();
	},


	SL_OBJ_BUILDER: function(){
		if(TranslatorIM.SL_langDst!="undefined" && TranslatorIM.LISTofPR.length>0){
                  ImTranslatorDataEvent.mousedown();

                  var doc = TranslatorIM.DOC;
                  var btn = doc.getElementById('SL_button');
                  if(btn){			
                      return;
                  }

	          var container = doc.body;



                  if(container){

		  var newElem = doc.createElement ("div");
		  var newElemid = doc.createAttribute("id");
		  newElemid.value = "SL_balloon_obj";
	          newElem.setAttributeNode(newElemid);

		  var newElemtp = doc.createAttribute("alt");
		  newElemtp.value = "0";
	          newElem.setAttributeNode(newElemtp);

		  //---------------------------
		  

			  var OB = doc.createElement('div');
			  var id = doc.createAttribute("id");
			  id.value = "SL_button";
		          OB.setAttributeNode(id);
 			  var cl = doc.createAttribute("class");
			  cl.value = "SL_ImTranslatorLogo";
	        	  OB.setAttributeNode(cl);
		          newElem.appendChild(OB);

		        
			  OB1 = doc.createElement('div');
			  id = doc.createAttribute("id");
			  id.value = "SL_shadow_translation_result2";
		          OB1.setAttributeNode(id);
		          newElem.appendChild(OB1);

			  OB2 = doc.createElement('div');
			  id = doc.createAttribute("id");
			  id.value = "SL_shadow_translator";
	        	  OB2.setAttributeNode(id);
		          newElem.appendChild(OB2);

				  OB3 = doc.createElement('div');
				  id = doc.createAttribute("id");
				  id.value = "SL_planshet";
	        		  OB3.setAttributeNode(id);

 				    OBup = doc.createElement('div');
				    OBup.id = "SL_arrow_up";
			            OB3.appendChild(OBup);


					OB4 = doc.createElement('div');
					id = doc.createAttribute("id");
					id.value = "SL_TB";
	        			OB4.setAttributeNode(id);


				        	var OB6 = doc.createElement("div");
						id = doc.createAttribute("id");
						id.value = "SL_tables";
						OB6.setAttributeNode(id);
						var cs = doc.createAttribute("cellspacing");
						cs.value = "1";
						OB6.setAttributeNode(cs);

						        var OB7 = doc.createElement("tr");
						        OB6.appendChild(OB7); 

							        var OB8 = doc.createElement("td");
								cl = doc.createAttribute("class");
								cl.value = "SL_td";
								OB8.setAttributeNode(cl);
								var w = doc.createAttribute("width");
								w.value = "10%";
								OB8.setAttributeNode(w);
								var a = doc.createAttribute("align");
								a.value = "right";
								OB8.setAttributeNode(a);
							        OB7.appendChild(OB8);

								        var OB9 = doc.createElement("input");
									id = doc.createAttribute("id");
									id.value = "SL_locer";
									OB9.setAttributeNode(id);
									var ty = doc.createAttribute("type");
									ty.value = "checkbox";
									OB9.setAttributeNode(ty);
									var va = doc.createAttribute("checked");
									va.value = Boolean(TranslatorIM.SL_TMPbox);

									OB9.setAttributeNode(va);
									var ti = doc.createAttribute("title");
									ti.value = FExtension.element(TranslatorIM.SL_LOC,"extLock_in_language");
									OB9.setAttributeNode(ti);
				        				OB8.appendChild(OB9); 



							        var OB10 = doc.createElement("td");
								cl = doc.createAttribute("class");
								cl.value = "SL_td";
								OB10.setAttributeNode(cl);
								w = doc.createAttribute("width");
								w.value = "20%";
								OB10.setAttributeNode(w);
								a = doc.createAttribute("align");
								a.value = "left";
								OB10.setAttributeNode(a);
							        OB7.appendChild(OB10);

									var OB11 = doc.createElement("select");
									id = doc.createAttribute("id");
									id.value = "SL_lng_from";
									OB11.setAttributeNode(id);

									cl = doc.createAttribute("class");
									cl.value = "SL_lngs";
									OB11.setAttributeNode(cl);


										if(TranslatorIM.SL_LNG_CUSTOM_LIST.indexOf("auto")!=-1 || TranslatorIM.SL_LNG_CUSTOM_LIST=="all"){
											var OB12 = doc.createElement('option');
											var v = document.createAttribute("value");
											v.value = "auto";
											OB12.setAttributeNode(v);
											OB12.appendChild(doc.createTextNode(FExtension.element(TranslatorIM.SL_LOC,"extDetect_language_from_box")));
											OB11.appendChild(OB12); 
										}

										var MENU = TranslatorIM.SL_LNG_LIST.split(",");
										for(var J=0; J < MENU.length; J++){
										    var CURlang3 = MENU[J].split(":");
										    var OB12 = doc.createElement('option');
										    var v = doc.createAttribute("value");
										    v.value = CURlang3[0];
										    OB12.setAttributeNode(v);
										    OB12.appendChild(doc.createTextNode(CURlang3[1]));
										    OB11.appendChild(OB12);
										}							                       

								        OB10.appendChild(OB11);

							        var OB13 = doc.createElement("td");
								cl = doc.createAttribute("class");
								cl.value = "SL_td";
								OB13.setAttributeNode(cl);
								w = doc.createAttribute("width");
								w.value = "3";
								OB13.setAttributeNode(w);
								a = doc.createAttribute("align");
								a.value = "center";
								OB13.setAttributeNode(a);
							        OB7.appendChild(OB13);

									var OB14 = doc.createElement('div');
									id = doc.createAttribute("id");
									id.value = "SL_switch_b";
								        OB14.setAttributeNode(id);
							 		ti = doc.createAttribute("title");
									ti.value = FExtension.element(TranslatorIM.SL_LOC,"extSwitch_languages_ttl");
					        			OB14.setAttributeNode(ti);
								        OB13.appendChild(OB14);

							        var OB15 = doc.createElement("td");
								cl = doc.createAttribute("class");
								cl.value = "SL_td";
								OB15.setAttributeNode(cl);
								w = doc.createAttribute("width");
								w.value = "20%";
								OB15.setAttributeNode(w);
								a = doc.createAttribute("align");
								a.value = "left";
								OB15.setAttributeNode(a);
							        OB7.appendChild(OB15);

									var OB16 = doc.createElement("select");
									id = doc.createAttribute("id");
									id.value = "SL_lng_to";
									OB16.setAttributeNode(id);
									cl = doc.createAttribute("class");
									cl.value = "SL_lngs";
									OB16.setAttributeNode(cl);


									     var SEL = 0
									     if(MENU.length>=TranslatorIM.SL_FAV_START){
										var SL_FAV_LANGS_LONG = TranslatorIM.SL_ADD_LONG_NAMES(TranslatorIM.SL_FAV_LANGS_BBL);

										if(SL_FAV_LANGS_LONG!=""){
											var favArr=SL_FAV_LANGS_LONG.split(","); 
											for(var J=0; J < favArr.length; J++){
											    var CURlang3 = favArr[J].split(":");
											    var OB_FAV = doc.createElement('option');
											    var v = doc.createAttribute("value");
											    v.value = CURlang3[0];

											    if(J == 0){
												    var sel = doc.createAttribute("selected");
												    sel.value = "selected";
												    OB_FAV.setAttributeNode(sel);
												    SEL = 1;
												    TranslatorIM.SL_langDst_bbl2=CURlang3[0];
											    }

											    OB_FAV.setAttributeNode(v);
											    OB_FAV.appendChild(doc.createTextNode(CURlang3[1]));
											    OB16.appendChild(OB_FAV);
											}
											OB_FAV = doc.createElement('option');
											var d = doc.createAttribute("disabled");
											d.value = true;
											OB_FAV.setAttributeNode(d);
											var all = FExtension.element(TranslatorIM.SL_LOC,"extwptDAll");
										    	OB_FAV.appendChild(doc.createTextNode("-------- [ "+ all +" ] --------"));

										    	OB16.appendChild(OB_FAV);
										}
									     }	


									        var thelang = "es";
										if(TranslatorIM.SL_langDst!="" && TranslatorIM.SL_SID_TO=="") thelang = TranslatorIM.SL_langDst_bbl2;
										for(J=0; J < MENU.length; J++){
										    CURlang3 = MENU[J].split(":");
										    option = doc.createElement('option');
										    if(SEL == 0){	
											    if(CURlang3[0] == thelang){
												    var sel = doc.createAttribute("selected");
												    sel.value = "selected";
												    option.setAttributeNode(sel);
											    }
										    }
										    v = doc.createAttribute("value");
										    v.value = CURlang3[0];
										    option.setAttributeNode(v);
										    option.appendChild(doc.createTextNode(CURlang3[1]));
										    OB16.appendChild(option);
										}							                       

								        OB15.appendChild(OB16);									

							        var OB17 = doc.createElement("td");
								cl = doc.createAttribute("class");
								cl.value = "SL_td";
								OB17.setAttributeNode(cl);
								w = doc.createAttribute("width");
								w.value = "5%";
								OB17.setAttributeNode(w);
								a = doc.createAttribute("align");
								a.value = "center";
								OB17.setAttributeNode(a);
							        OB7.appendChild(OB17);

									OB17.appendChild(doc.createTextNode(" "));

							        var OB18 = doc.createElement("td");
								cl = doc.createAttribute("class");
								cl.value = "SL_td";
								OB18.setAttributeNode(cl);
								w = doc.createAttribute("width");
								w.value = "8%";
								OB18.setAttributeNode(w);
								a = doc.createAttribute("align");
								a.value = "center";
								OB18.setAttributeNode(a);
							        OB7.appendChild(OB18);

									var OB19 = doc.createElement('div');
									id = doc.createAttribute("id");
									id.value = "SL_TTS_voice";
								        OB19.setAttributeNode(id);
							 		ti = doc.createAttribute("title");                 
									ti.value = TranslatorIM.SL_GetLongName(TranslatorIM.SL_DETECT);
					        			OB19.setAttributeNode(ti);
								        OB18.appendChild(OB19);

							        var OB20 = doc.createElement("td");
								cl = doc.createAttribute("class");
								cl.value = "SL_td";
								OB20.setAttributeNode(cl);
								w = doc.createAttribute("width");
								w.value = "8%";
								OB20.setAttributeNode(w);
								a = doc.createAttribute("align");
								a.value = "center";
								OB20.setAttributeNode(a);
							        OB7.appendChild(OB20);

									var OB21 = doc.createElement('div');
									id = doc.createAttribute("id");
									id.value = "SL_copy";
								        OB21.setAttributeNode(id);
							 		ti = doc.createAttribute("title");
									ti.value = FExtension.element(TranslatorIM.SL_LOC,"extCopy_ttl");
					        			OB21.setAttributeNode(ti);
							 		cl = doc.createAttribute("class");
									cl.value = "SL_copy";
					        			OB21.setAttributeNode(cl);
								        OB20.appendChild(OB21);
										var OB21tip = doc.createElement('div');
										id = doc.createAttribute("id");
										id.value = "SL_copy_tip";
									        OB21tip.setAttributeNode(id);
								        	OB21.appendChild(OB21tip);


							        var OB22 = doc.createElement("td");
								cl = doc.createAttribute("class");
								cl.value = "SL_td";
								OB22.setAttributeNode(cl);
								w = doc.createAttribute("width");
								w.value = "8%";
								OB22.setAttributeNode(w);
								a = doc.createAttribute("align");
								a.value = "center";
								OB22.setAttributeNode(a);
							        OB7.appendChild(OB22);

									var OB23 = doc.createElement('div');
									id = doc.createAttribute("id");
									id.value = "SL_bbl_font_patch";
								        OB23.setAttributeNode(id);
//							 		var js = doc.createAttribute("onclick");
//									js.value = "TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extNot_available"))";
//					        			OB23.setAttributeNode(js);
								        OB22.appendChild(OB23);

									var OB24 = doc.createElement('div');
									id = doc.createAttribute("id");
									id.value = "SL_bbl_font";
								        OB24.setAttributeNode(id);
							 		ti = doc.createAttribute("title");
									ti.value = FExtension.element(TranslatorIM.SL_LOC,"extFont_Size_ttl");
					        			OB24.setAttributeNode(ti);
							 		cl = doc.createAttribute("class");
									cl.value = "SL_bbl_font";
					        			OB24.setAttributeNode(cl);
								        OB22.appendChild(OB24);

							        var OB25 = doc.createElement("td");
								cl = doc.createAttribute("class");
								cl.value = "SL_td";
								OB25.setAttributeNode(cl);
								w = doc.createAttribute("width");
								w.value = "8%";
								OB25.setAttributeNode(w);
								a = doc.createAttribute("align");
								a.value = "center";
								OB25.setAttributeNode(a);
							        OB7.appendChild(OB25);


									var OB26 = doc.createElement('div');
									id = doc.createAttribute("id");
									id.value = "SL_bbl_help";
								        OB26.setAttributeNode(id);
							 		ti = doc.createAttribute("title");
									ti.value = FExtension.element(TranslatorIM.SL_LOC,"extHelp");
					        			OB26.setAttributeNode(ti);
								        OB25.appendChild(OB26);



							        var OB28 = doc.createElement("td");
								cl = doc.createAttribute("class");
								cl.value = "SL_td";
								OB28.setAttributeNode(cl);
								w = doc.createAttribute("width");
								w.value = "15%";
								OB28.setAttributeNode(w);
								a = doc.createAttribute("align");
								a.value = "right";
								OB28.setAttributeNode(a);
							        OB7.appendChild(OB28);

									var OB29 = doc.createElement('div');
									id = doc.createAttribute("id");
									id.value = "SL_pin";
								        OB29.setAttributeNode(id);
									cl = doc.createAttribute("class");
									cl.value = "SL_pin_off";
								        OB29.setAttributeNode(cl);
							 		ti = doc.createAttribute("title");
									ti.value = FExtension.element(TranslatorIM.SL_LOC,"extPin_ttl");
					        			OB29.setAttributeNode(ti);
								        OB28.appendChild(OB29);


						OB4.appendChild(OB6);


						var OBpr = doc.createElement('div');
						id = doc.createAttribute("id");
						id.value = "SL_Bproviders";
						
						if(TranslatorIM.SL_SHOW_PROVIDERS!="1"){
							st = doc.createAttribute("style");
							st.value = "visibility:hidden;";
							OBpr.setAttributeNode(st);
						}
					        OBpr.setAttributeNode(id);
					        OB4.appendChild(OBpr);

					        for(var p=0; p<TranslatorIM.LISTofPR.length; p++){
							var OBprov = doc.createElement('div');
							id = doc.createAttribute("id");
							id.value = "SL_P"+p;

							cl = doc.createAttribute("class");
							cl.value = "SL_BL_LABLE_ON";
							OBprov.setAttributeNode(cl);

							ti = doc.createAttribute("title");
							ti.value = TranslatorIM.LISTofPR[p];
						        OBprov.setAttributeNode(ti);

						        OBprov.setAttributeNode(id);

							var span = doc.createElement('div');
							span.id = "SL_PN"+p;
						        OBprov.appendChild(span);

                                                        span.appendChild(doc.createTextNode(TranslatorIM.LISTofPR[p][0]));
						        OBpr.appendChild(OBprov);

					        }
						OB3.appendChild(OBpr);

						var OBalert = doc.createElement('div');
						OBalert.id = "SL_alert_bbl";
						OBalert.height = "30px;";
					        OB3.appendChild(OBalert);

							var OBclose = doc.createElement('div');
							OBclose.id = "SLHKclose";
						        OBalert.appendChild(OBclose);

							var OBalertcont = doc.createElement('div');
							OBalertcont.id = "SL_alert_cont";
						        OBalert.appendChild(OBalertcont);



			        	OB3.appendChild(OB4);
		        	OB2.appendChild(OB3);

				var OB30 = doc.createElement('div');
				id = doc.createAttribute("id");
				id.value = "SL_shadow_translation_result";
			        OB30.setAttributeNode(id);

			        OB2.appendChild(OB30);

					        var eUL16 = doc.createElement("div");
						st30 = doc.createAttribute("id");
						st30.value = "SL_loading";
						eUL16.setAttributeNode(st30);
						var st30 = doc.createAttribute("class");
						st30.value = "SL_loading";
						eUL16.setAttributeNode(st30);
						OB2.appendChild(eUL16);


				var OB31 = doc.createElement('div');
				id = doc.createAttribute("id");
				id.value = "SL_player2";
			        OB31.setAttributeNode(id);
			        OB2.appendChild(OB31);

				var OB32 = doc.createElement('div');
				id = doc.createAttribute("id");
				id.value = "SL_alert100";
			        OB32.setAttributeNode(id);
			        OB2.appendChild(OB32);

					OB32.appendChild(doc.createTextNode(FExtension.element(TranslatorIM.SL_LOC,"extTTS_Limit")));


				var OB34 = doc.createElement('div');
				id = doc.createAttribute("id");
				id.value = "SL_Balloon_options";
			        OB34.setAttributeNode(id);
			        OB2.appendChild(OB34);

				  OBdown = doc.createElement('div');
				  OBdown.id = "SL_arrow_down";
			          OB34.appendChild(OBdown);

		var OBtbl = doc.createElement("div");
		id = doc.createAttribute("id");
		id.value = "SL_tbl_opt";
		OBtbl.setAttributeNode(id);
		OBtbl.width = "100%";
		OBtbl.height = "16";


               	        var OBtr = doc.createElement("tr");
		        OBtbl.appendChild(OBtr); 

			        var OBtd3_ = doc.createElement("td");
				cl = doc.createAttribute("class");
				cl.value = "SL_td";
				OBtd3_.setAttributeNode(cl);
				OBtd3_.width = "5%";
				OBtd3_.align = "center";
			        OBtr.appendChild(OBtd3_);

				        var OB9_ = doc.createElement("input");
					id = doc.createAttribute("id");
					id.value = "SL_BBL_locer";
					OB9_.setAttributeNode(id);
					var ty = doc.createAttribute("type");
					ty.value = "checkbox";
					OB9_.setAttributeNode(ty);
					var va = doc.createAttribute("checked");
					va.value = Boolean(TranslatorIM.SL_OnOff_BTN2);
					OB9_.setAttributeNode(va);
					var ti = doc.createAttribute("title");

					ti.value = FExtension.element(TranslatorIM.SL_LOC,'extSTB') + " "+ TranslatorIM.Timing +" " +FExtension.element(TranslatorIM.SL_LOC,'extSeconds');
					OB9_.setAttributeNode(ti);
        				OBtd3_.appendChild(OB9_); 

			        var OBtd3__ = doc.createElement("td");
				cl = doc.createAttribute("class");
				cl.value = "SL_td";
				OBtd3__.setAttributeNode(cl);
				OBtd3__.width = "5%";
				OBtd3__.align = "left";
			        OBtr.appendChild(OBtd3__);
			                          


				        var OB9__ = doc.createElement("div");
					id = doc.createAttribute("id");
					id.value = "SL_BBL_IMG";
					OB9__.setAttributeNode(id);
					var ti = doc.createAttribute("title");
					ti.value = FExtension.element(TranslatorIM.SL_LOC,'extSTB') + " "+ TranslatorIM.Timing +" " +FExtension.element(TranslatorIM.SL_LOC,'extSeconds');
					OB9__.setAttributeNode(ti);
        				OBtd3__.appendChild(OB9__); 






			        var OBtd2 = doc.createElement("td");
				cl = doc.createAttribute("class");
				cl.value = "SL_td";
				OBtd2.setAttributeNode(cl);
				OBtd2.width = "100%";
				OBtd2.align = "center";
			        OBtr.appendChild(OBtd2);


					var OB35 = doc.createElement('span');
			 		var id = doc.createAttribute("id");
					id.value = "BBL_OPT";
	        			OB35.setAttributeNode(id);

					cl = doc.createAttribute("class");
					cl.value = "SL_options";
				        OB35.setAttributeNode(cl);
					ti = doc.createAttribute("title");
					ti.value = FExtension.element(TranslatorIM.SL_LOC,"extOptions_ttl");
				        OB35.setAttributeNode(ti);
				        OBtd2.appendChild(OB35);

					OB35.appendChild(doc.createTextNode(FExtension.element(TranslatorIM.SL_LOC,"extOptions")));

					OBtd2.appendChild(doc.createTextNode(" : "));

					var OB36 = doc.createElement('span');

			 		var id = doc.createAttribute("id");
					id.value = "HIST_OPT";
	        			OB36.setAttributeNode(id);
					cl = doc.createAttribute("class");
					cl.value = "SL_options";
				        OB36.setAttributeNode(cl);
					ti = doc.createAttribute("title");
					ti.value = FExtension.element(TranslatorIM.SL_LOC,"extHistory_ttl");
				        OB36.setAttributeNode(ti);
				        OBtd2.appendChild(OB36);

					OB36.appendChild(doc.createTextNode(FExtension.element(TranslatorIM.SL_LOC,"extHistory")));

					OBtd2.appendChild(doc.createTextNode(" : "));


					var OB38 = doc.createElement('span');
			 		var id = doc.createAttribute("id");
					id.value = "FEED_OPT";
	        			OB38.setAttributeNode(id);


					var OB37 = doc.createElement('span');
			 		var id = doc.createAttribute("id");
					id.value = "DONATE_OPT";
	        			OB37.setAttributeNode(id);

					cl = doc.createAttribute("class");
					cl.value = "SL_options";
				        OB37.setAttributeNode(cl);
					ti = doc.createAttribute("title");
					ti.value = FExtension.element(TranslatorIM.SL_LOC,"extContribution_ttl");
				        OB37.setAttributeNode(ti);
				        OBtd2.appendChild(OB37);

					OB37.appendChild(doc.createTextNode('Donate'));



        				            
			        var OBtd3 = doc.createElement("td");
				cl = doc.createAttribute("class");
				cl.value = "SL_td";
				OBtd3.setAttributeNode(cl);
				OBtd3.width = "15%";
				OBtd3.align = "right";
			        OBtr.appendChild(OBtd3);
				var nw = doc.createAttribute("nowrap");
				nw.value = "nowrap";
				OBtd3.setAttributeNode(nw);



					var OB39 = doc.createElement('span');
					id = doc.createAttribute("id");
					id.value = "SL_Balloon_Close";
				        OB39.setAttributeNode(id);
					cl = doc.createAttribute("class");
					cl.value = "SL_options";
				        OB39.setAttributeNode(cl);

					ti = doc.createAttribute("title");
					ti.value = FExtension.element(TranslatorIM.SL_LOC,"extClose");
				        OB39.setAttributeNode(ti);
				        OBtd3.appendChild(OB39);

					OB39.appendChild(doc.createTextNode(FExtension.element(TranslatorIM.SL_LOC,"extClose")));

			        OBtbl.appendChild(OBtr);

		        OB34.appendChild(OBtbl); 
                        OB2.classList.add("notranslate");

		  //---------------------------
	  
		  TranslatorIM.idleCounter = 0;
                  if(container.tagName == "FRAMESET"){
                      container.parentNode.insertBefore(newElem, container.nextSibling);
                  }else{
                    container.appendChild (newElem);
		    doc.getElementById("SL_balloon_obj").style.display='block';
                  }
                  doc.getElementById('SL_shadow_translation_result2').style.display="none";
		  TranslatorIM.SL_IMG_LOADER();
		  }
                  if(doc.getElementById("SL_balloon_obj")){
			//STOP WORKING ON IFRAMES
			  if(self!=top){
                               if(String(window.location).indexOf('mail.live.')!=-1) container.removeChild (doc.getElementById("SL_balloon_obj"));
			  }

/*
        	          var id = TranslatorIM.TempActiveObjId;                                                                                    
       	        	  if(!window.getSelection().anchorNode && id != "SL_button" && id !="SL_TTS_voice" && id !="SL_lng_from" && id !="SL_lng_to" && id !="SL_locer") container.removeChild (doc.getElementById("SL_balloon_obj"));
	               	  else {doc.getElementById("SL_balloon_obj").style.display='block';}
*/
			  if(doc.getElementById('SL_tables')){						
	        	         var escaper = doc.getElementById('SL_tables').offsetWidth;		
       	          		 if((escaper != 0 && escaper > 410) && TranslatorIM.TempActiveObjId !="SL_button") container.removeChild (doc.getElementById("SL_balloon_obj"));
			  }

		  }

		  //STOP WORKING ON OLD FORUMS
		  if(container.tagName=="BODY" && doc.body.id=="check") container.removeChild (doc.getElementById("SL_balloon_obj"));
		  //STOP WORKING ON WP WIDGETS
		  if(container.tagName=="BODY" && doc.body.id=="tinymce") container.removeChild (doc.getElementById("SL_balloon_obj"));	     


		if(doc.getElementById('SL_lng_from')){
	                doc.getElementById('SL_lng_from').value=TranslatorIM.SL_langSrc_bbl2;
	       	        doc.getElementById('SL_lng_to').value=TranslatorIM.SL_langDst_bbl2;
        		TranslatorIM.SL_locker_settler();
		}
	     }	
	},

	fade: function (){
	 clearTimeout(TranslatorIM.STO);
	 var doc = FExtension.browserInject.getDocument();
	 TranslatorIM.unfade();
	 TranslatorIM.STO = setTimeout(function() { 
		var THEobj = doc.getElementById('SL_button');
		if(THEobj){
			 THEobj.style.visibility="hidden";
			 THEobj.style.transition='visibility 0.01s, opacity 0.01s linear';
		}
	 }, (TranslatorIM.Timing*1000));

	},

	dofade: function (){
	 clearTimeout(TranslatorIM.STO);
	 var doc = FExtension.browserInject.getDocument();
	 if(doc.getElementById("SL_button")){
           doc.getElementById("SL_button").style.opacity=0;
	   TranslatorIM.STO = setTimeout(function() { 
		var THEobj = doc.getElementById('SL_button');
		if(THEobj){
			 THEobj.style.visibility="hidden";
			 THEobj.style.transition='visibility 0.01s, opacity 0.01s linear';
		}
	   }, (TranslatorIM.Timing*1000));
	 }
	},

	unfade: function (){
	 clearTimeout(TranslatorIM.STO);
	 var doc = FExtension.browserInject.getDocument();
	 if(doc.getElementById("SL_button")){
		var THEobj = doc.getElementById('SL_button');
		if(THEobj){
			 THEobj.style.visibility="visible";
			 THEobj.style.transition='';
		}
	 }
	},




	SLShowHideAlert: function(){
	  var doc = TranslatorIM.DOC;
	  if(doc.getElementById('SL_alert_bbl')) doc.getElementById('SL_alert_bbl').style.display='none'; 
	},
                

	SL_alert: function(txt){
	  var doc = TranslatorIM.DOC;
	  if(doc.getElementById('SL_alert_bbl')){
		doc.getElementById('SL_alert_bbl').style.display="block";
		doc.getElementById('SL_alert_bbl').style.marginTop="-1px";
		doc.getElementById('SL_alert_bbl').style.marginLeft="0px";
		doc.getElementById("SL_alert_cont").innerText=txt;
          }
	},

/*
        getObjPosition: function (el){
	    var _x = event.clientX + document.body.scrollLeft - document.body.clientLeft;
	    var _y = event.clientY + document.body.scrollTop - document.body.clientTop;

	    TranslatorIM.SL_L = _x;
	    TranslatorIM.SL_R = _x;
	    TranslatorIM.SL_T = _y;
	    TranslatorIM.SL_B = _y;
	    if(_y<265) {
		TranslatorIM.SL_NEST="BOTTOM";
		TranslatorIM.SL_T=TranslatorIM.SL_T+10;
		TranslatorIM.SL_B=TranslatorIM.SL_B+10;
	    }
	},

*/


	getSelectionCoords: function(e) {
	  var doc = TranslatorIM.DOC;

	  try{
		  var range = doc.getSelection().getRangeAt(0);
		  var rect = range.getBoundingClientRect();

		  var l = Math.ceil(rect.left);
		  var t = Math.ceil(rect.top);
		  var r = Math.ceil(rect.right);
		  var b = Math.ceil(rect.bottom);


		  if(l==0 && t==0 && b==0 && r==0){
			if(TranslatorIM.SL_GLOBAL_X1>TranslatorIM.SL_GLOBAL_X2){
				l = TranslatorIM.SL_GLOBAL_X2;
				r = TranslatorIM.SL_GLOBAL_X1;
			} else {
				l = TranslatorIM.SL_GLOBAL_X1;
				r = TranslatorIM.SL_GLOBAL_X2;
			}

			if(TranslatorIM.SL_GLOBAL_Y1>TranslatorIM.SL_GLOBAL_Y2){
				t = TranslatorIM.SL_GLOBAL_Y2-document.body.scrollTop;
				b = TranslatorIM.SL_GLOBAL_Y1-document.body.scrollTop;
			} else {
				t = TranslatorIM.SL_GLOBAL_Y1-document.body.scrollTop;
				b = TranslatorIM.SL_GLOBAL_Y2-document.body.scrollTop;
			}
			t=t-8;
			b=b+8;
		  }



	//	  if(l!=t){

			  TranslatorIM.SL_L = l; 
			  TranslatorIM.SL_T = t;
			  TranslatorIM.SL_R = r;
			  TranslatorIM.SL_B = b;
			  if(t<265) TranslatorIM.SL_NEST="BOTTOM";
			  else TranslatorIM.SL_NEST="TOP";
			  var bodyScrollTop = doc.documentElement.scrollTop || doc.body.scrollTop;
			  var deltab=window.innerHeight*1-140-b;
			  var deltat=t;


			  if(deltab>deltat && deltat<270)TranslatorIM.SL_NEST="BOTTOM";
			  else if(bodyScrollTop>270)TranslatorIM.SL_NEST="TOP";


			  if((bodyScrollTop+b)>(bodyScrollTop + window.innerHeight-200) && b-t> window.innerHeight-200 && t<260) TranslatorIM.SL_NEST="FLOAT";
			  TranslatorIM.SL_SID_PIN=TranslatorIM.SL_OnOff_PIN;
			  //TranslatorIM.SAVE_SES_PARAMS();
			  if(TranslatorIM.SL_FRAME==0){
			  	if(TranslatorIM.SL_NEST!="FLOAT" && TranslatorIM.SL_SID_PIN == "true") TranslatorIM.SL_NEST="FLOAT";
			  }

	//	  }

	 } catch(e){}
	 },

	 SL_JUMP: function (doc){
/*
		setTimeout(function() {
			TranslatorIM.SL_bring_UP();
			TranslatorIM.SL_bring_DOWN();
        		if(TranslatorIM.SL_NEST!="FLOAT"){
				var SLdivField = doc.getElementById("SL_shadow_translator");

		 		if(TranslatorIM.SL_NEST=="TOP"){
		//			if(TranslatorIM.SL_MoveY.replace("px","") < 0){
				        	var bodyScrollTop = doc.documentElement.scrollTop || doc.body.scrollTop;
						var tp = Math.abs((bodyScrollTop*1)+TranslatorIM.SL_T-(SLdivField.offsetHeight*1)-9);
						if(TranslatorIM.SL_SAVETEXT==0) SLdivField.style.top = tp +"px";
		//			}
				}
				TranslatorIM.WINDOW_and_BUBBLE_alignment(doc,SLdivField);
			} else {
			 	doc.getElementById("SL_arrow_up").style.display="none";
			}
			var e = window.event;
		}, 50);
*/
	},




	WINDOW_and_BUBBLE_alignment: function(doc,SLdivField){
		if(TranslatorIM.SL_FRAME==1 && (TranslatorIM.GlobalBoxX+TranslatorIM.GlobalBoxY)>0){
			TranslatorIM.SL_NEST="";
			var OBJ = doc.getElementById('SL_pin');
			OBJ.className = "SL_pin_off";
			OBJ.title = FExtension.element(TranslatorIM.SL_LOC,"extPin_ttl");
			OBJ.style.background="url("+FExtension.browserInject.getURL('content/img/util/pin-off.png')+")";

			TranslatorIM.SL_SID_PIN="false";

	        	var bodyScrollTop = doc.documentElement.scrollTop || doc.body.scrollTop;
			if(parseInt(TranslatorIM.SL_MoveX.replace("px",""))<0){
				var tp = Math.abs((bodyScrollTop*1)+TranslatorIM.SL_T-(SLdivField.offsetHeight*1)-9);
			}else{
				var tp = TranslatorIM.SL_MoveX;
				TranslatorIM.SL_MoveX="-10000px";
			}
			SLdivField.style.top = tp +"px";			

	        	var bodyScrollLeft = doc.documentElement.scrollLeft || doc.body.scrollLeft;
			if(parseInt(TranslatorIM.SL_MoveY.replace("px",""))<0){
				var lt = Math.abs((bodyScrollLeft*1)+((TranslatorIM.SL_L+TranslatorIM.SL_R)/2)-(SLdivField.offsetWidth*1)/2);
			}else{
				var lt = TranslatorIM.SL_MoveY;
				TranslatorIM.SL_MoveY="-10000px";
			}
			SLdivField.style.left = lt +"px";

			TranslatorIM.SL_arrows('up'); 
		} else {
	        	var bodyScrollTop = doc.documentElement.scrollTop || doc.body.scrollTop;	  	
        	        var Wy1 = bodyScrollTop;
	                var Wy2 = window.innerHeight + bodyScrollTop;
                	var By1 = parseInt(SLdivField.style.top.replace("px",""));
        	        var By2 = By1+SLdivField.offsetHeight;
			var DELTAy = 1;
			if (doc.body.offsetHeight > window.innerHeight)	var DELTAy = 5;
			if (By1 < Wy1) SLdivField.style.top = (Wy1+TranslatorIM.GlobalBoxY) +"px";
			if (By2 > Wy2) SLdivField.style.top = (Wy2-SLdivField.offsetHeight-DELTAy) +"px";

	        	var bodyScrollLeft = doc.documentElement.scrollLeft || doc.body.scrollLeft;	  	
        	        var Wx1 = bodyScrollLeft;
	                var Wx2 = window.innerWidth + bodyScrollLeft;
                	var Bx1 = parseInt(SLdivField.style.left.replace("px",""));
			if(TranslatorIM.SL_NEST == "FLOAT") Bx1 = TranslatorIM.GlobalBoxX;
	                var Bx2 = Bx1+SLdivField.offsetWidth;
			var DELTAx = 1;
			if (doc.body.offsetWidth < window.innerWidth)	var DELTAx = 25;
			var cnt=0;
			if (Bx1 < Wx1) {cnt++;SLdivField.style.left = (Wx1+TranslatorIM.GlobalBoxX+DELTAx) +"px";}
			if (Bx2 > Wx2) {cnt++;SLdivField.style.left = (Wx2-SLdivField.offsetWidth-DELTAx) +"px";}

			if(TranslatorIM.SL_NEST == "FLOAT"){
				if(cnt==0 && TranslatorIM.GlobalBoxX!=0){
					SLdivField.style.left = TranslatorIM.GlobalBoxX+"px";
				}
			}
		}

	},


	SL_arrows: function (st){
		var doc = TranslatorIM.DOC;
		doc.getElementById('SL_arrow_up').style.display='block';
		doc.getElementById('SL_arrow_down').style.display='block';
	   	switch(st){
			case "up": doc.getElementById('SL_arrow_up').style.display='none'; break;
			case "down": doc.getElementById('SL_arrow_down').style.display='none'; break;
	                case "all": doc.getElementById('SL_arrow_up').style.display='none'; doc.getElementById('SL_arrow_down').style.display='none'; break;
	        }
	},


        SL_NotAllowed: function(){
	    var doc = TranslatorIM.DOC;
		 if(doc.getElementById('SL_lng_from').value=="auto"){
			//doc.getElementById('SL_switch_b').title=TranslatorIM.SL_LOC("disabled");
			doc.getElementById('SL_switch_b').style.cursor='not-allowed';
		 }else{
			//doc.getElementById('SL_switch_b').title=TranslatorIM.SL_LOC("switch");
			doc.getElementById('SL_switch_b').style.cursor='pointer';
		 }
	},



	SL_WEB_PAGE_TRANSLATION_FROM_TB: function(st, act, tb, tip){       
		TranslatorIM.SL_set_LNG_TRIGGER("SL_LNG_TRIGGER",0);
		if(TranslatorIM.SL_wptGlobTip!=tip || TranslatorIM.SL_wptGlobTb != tb){
			ImTranslatorDataEvent.mousedown();
			setTimeout(function() {
				TranslatorIM.SL_WEB_PAGE_TRANSLATION(st,act);
			}, 100);
		}else TranslatorIM.SL_WEB_PAGE_TRANSLATION(st,act);
	},


	SL_WEB_PAGE_TRANSLATION_FROM_CM_AND_HK: function(st, act){       
		TranslatorIM.SL_set_LNG_TRIGGER("SL_LNG_TRIGGER",0);
		TranslatorIM.SL_WEB_PAGE_TRANSLATION(st,act);
	},


	SL_WPT: function(st){
		if(st==0) 	TranslatorIM.ACTIVATE_WPT(1, top.location.host);
		else {
	                TranslatorIM.SL_WPT_DETECT_4_GB_CALLS();
			if(TranslatorIM.SL_WPT_TRG_LNG) {
				if(window.top == window.self){
		                	var url = window.location; 	  		  
					chrome.runtime.sendMessage({greeting: "wpt2:>"+url+"*"+TranslatorIM.SL_WPT_TRG_LNG}, function(response) {}); 
				}
			}
		}
	},




	SL_WEB_PAGE_TRANSLATION: function(st, act){       
		TranslatorIM.ACTIVATE_WPT(1, top.location.host);
	},


	SL_BUBBLE_FROM_CM: function(e){
	      	var doc = TranslatorIM.DOC;
		TranslatorIM.SL_BBL_OBJ_OFF(0);
		TranslatorIM.SL_OBJ_BUILDER();
		TranslatorIM.getSelectionCoords(e);
		TranslatorIM.SL_ShowBalloon();
	},


        SL_runinlinerNOW: function(info, tab){
		runinliner();
	},



	MS: function(f,t,text,id){
	        if(t == "zh") t = "zh-CHS";
        	if(t == "zt") t = "zh-CHT";
	        if(t == "iw") t = "he";
        	if(t == "sr") t = "sr-Cyrl";
	        if(t == "tl") t = "fil";
        	if(t == "hmn") t = "mww";
	        if(t == "ku") t = "kmr";
        	if(t == "ckb") t = "ku";
	        if(t == "srsl") t = "sr";
        	if(t == "tlsl") t = "fil";

		var TEXTforhist = text;
		if(f=="auto" && TranslatorIM.SL_DETECT!="") f=TranslatorIM.SL_DETECT;
		if(f=="") f="en";
	     	var doc = FExtension.browserInject;
	     	var doc2 = doc.getDocument();
		var TM = 0;
		setTimeout(function(){
		    if(TranslatorIM.AKEY!=""){
			var baseUrl = "https://api-edge.cognitive.microsofttranslator.com/translate?api-version=3.0&includeSentenceLength=false&to="+t;
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
				if(ajaxRequest.readyState == 4){ 
		        	     	var resp = ajaxRequest.responseText;

					if(resp.indexOf('{"error":{"code"')==-1){
						var R1 = resp.split('"translations":[{"text":"');
						var R2 = R1[1].split('",');
						var RESULT = R2[0].replace(/\\r/g,"");

						RESULT = JSON.parse(`"${RESULT}"`);
						RESULT = RESULT.replace(/\\t/g,"\n");
						RESULT = RESULT.replace(/\\u00A0/g,'');
						var OUT="";
						var OUThist="";
						var RESULTforhist=RESULT;
						if(RESULT.indexOf("[#]")!=-1){
							var ARR1 = RESULT.split("[#]");
							for(var j=1; j<ARR1.length; j++){
								OUT = OUT + ARR1[j].trim()+"<br>";
								OUThist = OUThist + ARR1[j].trim()+"\n";
							}
							RESULT = OUT;

							RESULTforhist = OUThist;
						}

                                        RESULT = RESULT.replace(/\\"/g,'"');
	        	                TranslatorIM.SL_temp_result=RESULT;
			                RESULT = TranslatorIM.PPB_tts_icon(t,RESULT);
					TranslatorIM.TR_ROUTER_RESULT=RESULT;
					RESULT = DOMPurify.sanitize(RESULT);
					doc2.getElementById('SL_shadow_translation_result').innerHTML = RESULT;
					doc2.getElementById('SL_shadow_translation_result2').innerHTML = RESULT;

					doc2.getElementById('SL_shadow_translation_result').style.direction = "ltr";
					doc2.getElementById('SL_shadow_translation_result').style.textAlign = "left";

					if(t == "ar" || t == "he" || t == "fa" || t == "yi" || t == "ur" || t == "ps" || t == "sd" || t == "ku" || t == "ug" || t == "dv" || t == "prs"){
						doc2.getElementById('SL_shadow_translation_result').style.direction = "rtl";
						doc2.getElementById('SL_shadow_translation_result').style.textAlign = "right";
					}
                                        doc2.getElementById('SL_loading').style.display="none";

                                       	TranslatorIM.SL_JUMP(doc2);

					setTimeout(function() {	
         					var HID=2;
					        if (TranslatorIM.SL_TH_2 == 1){

							var SLnow = new Date();
							SLnow = SLnow.toString();
							var TMPtime = SLnow.split(" ");
							var CurDT = TMPtime[1] + " " + TMPtime[2] + " " + TMPtime[3] + ", " + TMPtime[4];
				                        var LNGfrom = f;
				                        if(f=="auto" || doc2.getElementById("SL_locer").checked == false) var LNGfrom = TranslatorIM.LNGforHISTORY;
							if(TranslatorIM.SL_WRONGLANGUAGEDETECTED==1) LNGfrom="auto";

	                                                text=text.replace(/~/ig," ");
        	                                        resp=resp.replace(/~/ig," ");
						        text=text.replace(/\^/g,"@");
						        var DICT = TranslatorIM.BL_T_PROV;
							if(TranslatorIM.SL_MODE==1) DICT = TranslatorIM.BL_D_PROV;
							doc.runtimeSendMessage({greeting:"[b]" + text + "~~" + RESULTforhist + "~~" + LNGfrom + "|" + t + "~~"+ doc2.location+"~~"+CurDT+"~~"+HID+"~~"+DICT[0]+"^^"}, function(response) {
								if(response){ 
								//	console.log(response.farewell); 
								}
							});
					        }
					}, 500);					


					}else TranslatorIM.SL_TR_ROUTER(text,id);
				}
			}
		        var OUT="";
			text = text.replace(/"/g,"'");
			const index = text.indexOf('\n');
			if (index !== -1) {
			  // Carriage return found at index
			  var ARR = text.split("\n");
			  for(var i=0; i<ARR.length; i++){
			   	OUT = OUT + "[#]"+ARR[i];
			  }
			}
		        if(OUT=="") OUT=text;	
			ajaxRequest.open("POST", baseUrl, true);
			ajaxRequest.setRequestHeader("Content-Type", "application/json");
			ajaxRequest.setRequestHeader("authorization", TranslatorIM.AKEY);
			ajaxRequest.send('[{"text":"'+OUT+'"}]'); 
		  }else TranslatorIM.SL_TR_ROUTER(text,id);
		},TM);		

	},

	CUSTOM_LANGS: function(list){
		var OUT = "";
	        //list = list.replace(/&#160;/ig," ");
        	var list2 = TranslatorIM.SL_LNG_CUSTOM_LIST;

		if(list2=="all") OUT = list;
		else{
		    var L1 = list.split(",");
		    for(var i=0; i<L1.length; i++){
	     		var L1base = L1[i].split(":");
		     	var L1short = list2.split(",");
			for(var j=0; j<L1short.length; j++){
			   if(L1base[0] == L1short[j]) OUT=OUT+L1short[j]+":"+L1base[1]+",";
			}
		    }
 		    OUT = OUT.substring(0,OUT.length-1);		    
		}

		var GLOBAL_LANG_LIST=LISTofPRpairsDefault.split(",");

		var tmp = OUT.split(",");
		OUT="";
		for(var i=0; i<tmp.length; i++){
	     		var L1 = tmp[i].split(":");
			for(var X=0; X<GLOBAL_LANG_LIST.length; X++){
				if(L1[0]==GLOBAL_LANG_LIST[X]) OUT=OUT+L1[0]+":"+L1[1]+",";
	        	}	
		}
 		OUT = OUT.substring(0,OUT.length-1);		    
		return OUT;
	},

	CleanUpAll: function(e){
	     try{
		var OBJ_ID = e.target.id;
		if(OBJ_ID.indexOf('SL_')==-1){
		    try{
		        var doc = TranslatorIM.DOC;
		        for(var I = 0; I < doc.getElementsByTagName("iframe").length; I++){
                	    var ID = doc.getElementsByTagName("iframe")[I].id;
	                    if(ID!=""){
				if(doc.getElementById(ID).contentWindow.document.getElementById('SL_balloon_obj')) {
					doc.getElementById(ID).contentWindow.document.getElementById('SL_balloon_obj').remove();
					//window.frames[ID].document.getElementById('SL_balloon_obj').remove();
				}
			    }
			}
		    } catch(e){}
		}
	     } catch(e){}
	},

	TSgetSelectionCoords: function() {
 	    var doc = TranslatorIM.DOC;
	    var sel = doc.selection, range, rect;
	    var x = 0, y = 0;
	    if (sel) {
	        if (sel.type != "Control") {
        	    range = sel.createRange();
	            range.collapse(true);
        	    x = range.boundingLeft;
	            y = range.boundingTop;
        	}
	    } else if (window.getSelection) {
        	sel = window.getSelection();
	        if (sel.rangeCount) {
        	    range = sel.getRangeAt(0).cloneRange();
		    if (range.getClientRects) {
	                range.collapse(true);
        	        if (range.getClientRects().length>0){
                	    rect = range.getClientRects()[0];
	                    x = rect.left;
        	            y = rect.top;
                	}
	            }
        	    // Fall back to inserting a temporary element
	            if (x == 0 && y == 0) {
        	        var span = doc.createElement("span");
                	if (span.getClientRects) {
	                    // Ensure span has dimensions and position by
        	            // adding a zero-width space character
                	    span.appendChild( doc.createTextNode("\u200b") );
	                    range.insertNode(span);
        	            rect = span.getClientRects()[0];
                	    x = rect.left;
	                    y = rect.top;
        	            var spanParent = span.parentNode;
                	    spanParent.removeChild(span);

	                    // Glue any broken text nodes back together
        	            spanParent.normalize();
                	}
	            }
        	}
	    }
	    return { x: x, y: y };
	},




    SL_SAVE_TO_TH: function(sourceLang, targetLang){
	var SLnow = new Date();
	SLnow=SLnow.toString();
	var TMPtime=SLnow.split(" ");
	var CurDT=TMPtime[1]+" "+TMPtime[2]+" "+TMPtime[3]+", "+TMPtime[4];      		
	var URL_host = document.location;
	chrome.runtime.sendMessage({greeting:"[wp]"+ URL_host + "~~" + URL_host + "~~" + sourceLang + "|" + targetLang + "~~"+ URL_host+"~~"+CurDT+"~~4^^"}, function(response) { });
    },


    SL_WPTmsg: function(text){
   	var doc = TranslatorIM.DOC;
	var SL_MSG = doc.createElement("button");
	var SL_MSGid = doc.createAttribute("id");
	SL_MSGid.value = "SL_MSG";
        SL_MSG.setAttributeNode(SL_MSGid);
        SL_MSG.appendChild(doc.createTextNode(text));
        doc.body.appendChild(SL_MSG);
    },


    SL_WPT_DETECT_4_GB_CALLS: function(st){

	      	var rootTranslateNode = TranslatorIM.getRootNode();
	      	var analysisText = TranslatorIM.getAnalysisText(rootTranslateNode);
		TranslatorIM.SL_WPT_DODetection(analysisText);

    },

    SL_WPT_DETECT: function(st){
	var AcumStatus = TranslatorIM.SL_wptDp4*1 + TranslatorIM.SL_wptLp2*1;	
	var LHistStatus = 0;
	if(TranslatorIM.SL_wptLHist!="") LHistStatus = 1;
	if(st==2) {AcumStatus=1;LHistStatus=1;}
	if(st==0) {AcumStatus=0;LHistStatus=0;}
	if(AcumStatus>0 || LHistStatus == 1){
	      	var rootTranslateNode = TranslatorIM.getRootNode();
	      	var analysisText = TranslatorIM.getAnalysisText(rootTranslateNode);
		TranslatorIM.SL_WPT_DODetection(analysisText);
	}else{
		TranslatorIM.SL_DETLANG="skip";
		TranslatorIM.SL_WPT_LANG="skip";
	}
    },





    DETERMIN_IF_LANGUAGE_IS_AVAILABLE: function(lng){
	try{
		var lngarr = LISTofLANGsets[0].split(",");
		var cnt = 0;
		if(lngarr.length>1 && lng!=""){
			for(var i=1; i<lngarr.length; i++){
				if(lngarr[i]==lng) cnt++;
			}
		} else cnt=1;
      		if(cnt==0){
			var LONG_NAME="";
			var MENU = TranslatorIM.SL_LNG_LIST.split(",");
			for(var J=0; J < MENU.length; J++){
			    var CURlang = MENU[J].split(":");		    
			    if(CURlang[0] == lng) LONG_NAME = CURlang[1];
			}

			TranslatorIM.InitiateWPT_target_lang(LONG_NAME);
        	        TranslatorIM.SL_WPT_ERROR=1;
	        }
	} catch(ex){}
    },

    DETERMIN_IF_LANGUAGE_IS_AVAILABLE_BBL: function(){
	try{
		var doc = TranslatorIM.DOC;
		var T = doc.getElementById('SL_lng_to').value;
		var F = doc.getElementById('SL_lng_from').value;
		var lngarr = LISTofLANGsets[0].split(",");
		var cnt = 0;
		var cnt1 = 0;
		var cnt2 = 0;
		if(lngarr.length>1 && T!=""){
			for(var i=1; i<lngarr.length; i++){
				if(lngarr[i]==T) cnt1++;
				if(lngarr[i]==F) cnt2++;
			}
		}
		if(cnt1>0 && cnt2>0) cnt=1;
		return(cnt);
	} catch(ex){}
    },


    SL_SHOW_ORIGINAL: function(){
	WPT_RESTORE_ORIGINAL_NODES();
    },


    getAnalysisText: function (target) {
      var iterator = TranslatorIM.getIterator(target), textnode, analysisText = "";
      while ((textnode = iterator.nextNode())) {
        if(textnode.data.length>20){
	        analysisText += textnode.data + ". ";
        	if (analysisText.length >= 4096) {
	          break;
        	}
	}
      }
      return analysisText;
    },

    getIterator: function(root) {
      var doc = TranslatorIM.DOC;
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
            if (TranslatorIM.invalidElements[tag]) {
              return NodeFilter.FILTER_REJECT;
            }
          }

          return NodeFilter.FILTER_ACCEPT;
        }
      }, false);
    },

    getRootNode: function() {
   	var doc = TranslatorIM.DOC;
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
    },





    SL_WPT_DODetection: function(myTransText) {
	  if(myTransText != "" && TranslatorIM.ONCE_DETECT == ""){
	     var resp = TranslatorIM.i18n_LanguageDetect(myTransText,1);
	     TranslatorIM.BBL_DETECT="";
	     TranslatorIM.SL_setWPT_DET_LNG("SL_WPT_DET_LNG",resp);
             TranslatorIM.SL_WPT_LANG=resp;
	     TranslatorIM.SL_DETLANG=resp;
             TranslatorIM.SL_WPT_TRG_LNG=resp;

	     if(resp == ""){
		    var num = Math.floor((Math.random() * SL_GEO.length)); 
		    var theRegion = SL_GEO[num];
		    var cntr = myTransText.split(" ");
                    var newTXT = truncStrByWord(myTransText,100);

		    var baseUrl ="https://translate.google."+theRegion+"/translate_a/single";
		    var SL_Params = "client=gtx&dt=t&dt=bd&dj=1&source=input&q="+encodeURIComponent(newTXT)+"&sl=auto&tl=en&hl=en";


			    chrome.runtime.sendMessage({greeting: "DET_GOOGLE:>"+baseUrl+","+SL_Params}, function(response) {});

			    setTimeout(function(){
				    var SLIDL = setInterval(function(){
				           chrome.runtime.sendMessage({greeting: 1}, function(response) {

				             if(response && response.farewell){
					        var theresponse = response.farewell.split("~");
						TranslatorIM.BBL_DETECT=theresponse[51];
						clearInterval(SLIDL);
						if(TranslatorIM.BBL_DETECT!="" && TranslatorIM.BBL_DETECT!="<#>") {
							var resp = TranslatorIM.BBL_DETECT;
							TranslatorIM.BBL_DETECT="";
							TranslatorIM.SL_setWPT_DET_LNG("SL_WPT_DET_LNG",resp);
        	                                        TranslatorIM.SL_WPT_LANG=resp;
							TranslatorIM.SL_DETLANG=resp;
                        	                        TranslatorIM.SL_WPT_TRG_LNG=resp;
                                                        TranslatorIM.ONCE_DETECT = 1;

							TranslatorIM.SL_SETINTERVAL_ST=1;
			        	    	}else TranslatorIM.MS_WPT_Detector(myTransText);
					        TranslatorIM.ACTIVATE_THEMEwpt_lng(TranslatorIM.THEMEmode);
					     }
				           });
				    },50);  
 		            },500);  

	     }		
	  }	
	},



	MS_WPT_Detector: function(myTransText) {
		var TM = 0;
		TranslatorIM.SL_SETINTERVAL_ST=0;

		setTimeout(function(){

		    if(TranslatorIM.AKEY!=""){
		        var baseUrl = "https://api-edge.cognitive.microsofttranslator.com/translate?api-version=3.0&includeSentenceLength=false&to=en";
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
				if(ajaxRequest.readyState == 4){

		             		var resp = ajaxRequest.responseText;
					if(resp.indexOf('{"error":{"code"')==-1){
						var DetLang = "en";
				             	var R1=resp.split('language":"');
						var R2=R1[1].split('","score"');
						DetLang = R2[0];
						if(DetLang == "zh-Hans") DetLang = "zh-CN";
						if(DetLang == "zh-Hant") DetLang = "zh-TW";
						if(DetLang == "he") DetLang = "iw";
					        if(DetLang == "sr-Cyrl") DetLang = "srsl";
						if(DetLang == "fil") DetLang = "tl";
						if(DetLang == "mww") DetLang = "hmn";
						if(DetLang == "ku") DetLang = "ckb"; 

						TranslatorIM.SL_setWPT_DET_LNG("SL_WPT_DET_LNG",DetLang);
                                                TranslatorIM.SL_WPT_LANG=DetLang;
						TranslatorIM.SL_DETLANG=DetLang;
                                                TranslatorIM.SL_WPT_TRG_LNG=DetLang;
                                                TranslatorIM.ONCE_DETECT = 1;
					        TranslatorIM.SL_SETINTERVAL_ST=1;
				        	SYS=1;
					}else SYS = 0;
				}
			}

			myTransText=myTransText.replace(/"/g,"'");
			ajaxRequest.open("POST", baseUrl, true);
			ajaxRequest.setRequestHeader("Content-Type", "application/json");
			ajaxRequest.setRequestHeader("authorization", TranslatorIM.AKEY);
			ajaxRequest.send('[{"text":"'+myTransText+'"}]'); 
		  }
		},TM);
	},




	SL_GetLongName: function(code){
		var LANGSALL = FExtension.element(TranslatorIM.SL_LOC,'extLanguages').split(",");
		var LANGS = TranslatorIM.SL_LNG_LIST.split(",");


		for (var i = 0; i < LANGSALL.length; i++){
			var templang = LANGSALL[i].split(":");
			if(code == templang[0]){ 
				return (templang[1]);
			}
		}

	},


    	SL_setWPT_DET_LNG: function(cname, cvalue, exdays) {
	    var s = ""; 
	    if(String(document.location).indexOf('https:')!=-1) s=" secure;"; 
	    document.cookie = cname + "=" + cvalue + "; path=/;"+s;
	    TranslatorIM.SL_WPT_DET_LNG = cvalue; 
    	},


	SL_setSHOW_HIDE_TB_TMP: function(cname, cvalue, exdays) {
	    var s = ""; 
	    if(String(document.location).indexOf('https:')!=-1) s=" secure;"; 
	    document.cookie = cname + "=" + cvalue + "; path=/;"+s;
	},


	SL_getSHOW_HIDE_TB_TMP: function(cname) {
	    var name = cname + "=";
	    var ca = document.cookie.split(';');
	    for(var i=0; i<ca.length; i++) {
	        var c = ca[i];
	        while (c.charAt(0)==' ') c = c.substring(1);
	        if (c.indexOf(name) == 0){
		 var resp = c.substring(name.length,c.length);
		 TranslatorIM.SL_GWPT_Show_Hide=resp;
		 TranslatorIM.SL_GWPT_Show_Hide_tmp=resp;
		 return resp;
		}
	    }
	},

	SL_set_TIP_TRIGGER: function(cname, cvalue, exdays) {
	    var s = ""; 
	    if(String(document.location).indexOf('https:')!=-1) s=" secure;"; 
	    document.cookie = cname + "=" + cvalue + "; path=/;"+s;
	},


	SL_get_TIP_TRIGGER: function(cname) {
	    var name = cname + "=";
	    var ca = document.cookie.split(';');
	    for(var i=0; i<ca.length; i++) {
	        var c = ca[i];
	        while (c.charAt(0)==' ') c = c.substring(1);
	        if (c.indexOf(name) == 0){
		 return c.substring(name.length,c.length);
		}
	    }
	},



	SL_set_LNG_TRIGGER: function(cname, cvalue, exdays) {
	    var s = ""; 
	    if(String(document.location).indexOf('https:')!=-1) s=" secure;"; 
	    document.cookie = cname + "=" + cvalue + "; path=/;"+s;
	},


	SL_get_LNG_TRIGGER: function(cname) {
	    var name = cname + "=";
	    var ca = document.cookie.split(';');
	    for(var i=0; i<ca.length; i++) {
	        var c = ca[i];
	        while (c.charAt(0)==' ') c = c.substring(1);
	        if (c.indexOf(name) == 0){
		 return c.substring(name.length,c.length);
		}
	    }
	},



	GOOGLE_TTS_backup: function(speechText,TTSlang){	        
	     	var doc = TranslatorIM.DOC;
		TranslatorIM.synth.cancel();

			var voices = TranslatorIM.synth.getVoices();
			const utterance = new SpeechSynthesisUtterance();
			var LNG="";
			TranslatorIM.TheNewLang=TTSlang;
			switch(TTSlang){
			 	case "zt":LNG = "zh-HK"; break;
			 	case "zh":LNG = "zh-TW"; break;
//			 	case "en":LNG = "en-GB|Male"; break;
			 	case "en":LNG = "en-US"; break;
			 	case "de":LNG = "de-DE"; break;
			 	case "hi":LNG = "hi-IN"; break;
			 	case "id":LNG = "id-ID"; break;
			 	case "it":LNG = "it-IT"; break;
			 	case "nl":LNG = "nl-NL"; break;
			 	case "pl":LNG = "pl-PL"; break;
			 	case "es":LNG = "es-US"; break;

			 	case "ru":LNG = "ru-RU"; break;
			 	case "ja":LNG = "ja-JP"; break;
			 	case "ko":LNG = "ko-KR"; break;
			 	case "fr":LNG = "fr-FR"; break;
			 	case "pt":LNG = "pt-BR"; break;

			}

                        

			for (var a=0; a<voices.length; a++){
			    if(LNG.indexOf("|")!=-1){
				var ARR=LNG.split("|");
				if(ARR[0]==voices[a].lang && voices[a].name.indexOf(ARR[1])!=-1){
					utterance.voice = voices[a];
				}
			    }else{
				if(LNG==voices[a].lang){
					utterance.voice = voices[a];
				}
			    }
			}
			var SP = 1.0;

			var PLANSHET = doc.getElementById("SL_player2");
		 	PLANSHET.style.display='block';
		        var ext = FExtension.browserInject;
		 	var PLAYER = "<div id='PL_lbplayer'><table width='50' colspan='3' style='padding:6px;' bgcolor='#fff'><tr><td width=20><div id='SL_controls' class='SL_pause'></div></td><td width=5></td><td align='left' width=20><div id='SL_volume' class='SL_volume'></div></td></tr></table></div>";
			PLANSHET.innerHTML=DOMPurify.sanitize(PLAYER);
	            	doc.getElementById('SL_volume').style.background='url('+ext.getURL('content/img/util/volume.png')+')';
	            	doc.getElementById('SL_controls').style.background='url('+ext.getURL('content/img/util/pause.png')+')';


			TranslatorIM.TheNewText = speechText;

			utterance.text = speechText;
			utterance.rate = SP;
                        if(TranslatorIM.TTSvolume==null || TranslatorIM.TTSvolume=="undefined" || TranslatorIM.TTSvolume=="") TranslatorIM.SL_setTMPdata("TTSvolume",TranslatorIM.TheVolume);
			utterance.volume = TranslatorIM.TTSvolume*1/10;


			utterance.addEventListener('end', TranslatorIM.handleSpeechEvent);
			utterance.addEventListener('pause', TranslatorIM.handleSpeechPause);
			utterance.addEventListener('resume', TranslatorIM.handleSpeechResume);

			TranslatorIM.synth.speak(utterance);
                        TranslatorIM.handleSpeechSetVolume();
			setTimeout(function() {
				if(speechText.lenght>=200) doc.getElementById("SL_alert100").style.display="block";				
			}, 500);

	},

	handleSpeechPause: function(){
		var doc = TranslatorIM.DOC;
		var ext = FExtension.browserInject;
            	doc.getElementById('SL_controls').style.background='url('+ext.getURL('content/img/util/play.png')+')';
		doc.getElementById("SL_controls").className="SL_play";			
	},

	handleSpeechResume: function(){
		var doc = TranslatorIM.DOC;
		var ext = FExtension.browserInject;
            	doc.getElementById('SL_controls').style.background='url('+ext.getURL('content/img/util/pause.png')+')';
		doc.getElementById("SL_controls").className="SL_pause";
		TranslatorIM.Reload();
	},

	handleSpeechEvent: function(){
		var doc = TranslatorIM.DOC;
		var ext = FExtension.browserInject;
            	doc.getElementById('SL_controls').style.background='url('+ext.getURL('content/img/util/play.png')+')';
		doc.getElementById("SL_controls").className="SL_play";
	},

	handleSpeechVolume: function(){
	   var doc = TranslatorIM.DOC;
		var ext = FExtension.browserInject;
		if(doc.getElementById("SL_volume").className=="SL_novolume"){
			doc.getElementById('SL_volume').style.background='url('+ext.getURL('content/img/util/volume.png')+')';
			doc.getElementById("SL_volume").className="SL_volume";
			TranslatorIM.SL_setTMPdata("TTSvolume",TranslatorIM.TheVolume);
		} else {
			doc.getElementById('SL_volume').style.background='url('+ext.getURL('content/img/util/novolume.png')+')';
			doc.getElementById("SL_volume").className="SL_novolume";
			TranslatorIM.SL_setTMPdata("TTSvolume",1);
		}
	},

	handleSpeechSetVolume: function(){
	   var doc = TranslatorIM.DOC;
		var ext = FExtension.browserInject;
		if(TranslatorIM.TTSvolume!=TranslatorIM.TheVolume){
			doc.getElementById('SL_volume').style.background='url('+ext.getURL('content/img/util/novolume.png')+')';
			doc.getElementById("SL_volume").className="SL_novolume";
		}else{
			doc.getElementById('SL_volume').style.background='url('+ext.getURL('content/img/util/volume.png')+')';
			doc.getElementById("SL_volume").className="SL_volume";
		}
	},

	Reload: function(ob){
	    var doc = TranslatorIM.DOC;
	    TranslatorIM.synth.cancel();    
	    TranslatorIM.GOOGLE_TTS_backup(TranslatorIM.TheNewText,TranslatorIM.TheNewLang);
	},

	PPB_tts_icon: function (T,resp){
		var doc = FExtension.browserInject;
	   	var doc2 = doc.getDocument();
		var resptmp = resp;
		if(TranslatorIM.SL_ALLvoices.indexOf(T)!=-1){
			var ttsurl=FExtension.browserInject.getURL('content/img/util/tts.png');
			if(T=="ar" || T=="iw" || T=="fa" || T=="yi" || T=="ur" || T=="ps" || T=="sd" || T=="ckb" || T=="ug" || T=="dv" || T=="prs"){
				var tmpTTSicn='<div class="PPB_voice2" title="'+FExtension.element(TranslatorIM.SL_LOC,"extListen_ttl")+'" id="SL_BBL_VOICE" style="background: url('+FExtension.browserInject.getURL("content/img/util/tts.png")+');" lang="'+doc2.getElementById("SL_lng_to").value+'">&nbsp;</div>';
				resptmp = tmpTTSicn+"<div style='margin-right:20px;line-height:19px;'>"+resptmp+"</div>";
			} else {
				var tmpTTSicn='<div class="PPB_voice1" title="'+FExtension.element(TranslatorIM.SL_LOC,"extListen_ttl")+'" id="SL_BBL_VOICE" style="background: url('+FExtension.browserInject.getURL("content/img/util/tts.png")+');" lang="'+doc2.getElementById("SL_lng_to").value+'">&nbsp;</div>';
				resptmp = tmpTTSicn+"<div style='margin-left:20px;line-height:19px;'>"+resptmp+"</div>";
			}
		}

		return resptmp;

	},

	AUTOhandler: function(doc,AUTO,DetLang){
		var LNGlist = FExtension.element(TranslatorIM.SL_LOC,'extLanguages');
		var LNGS = FExtension.element(TranslatorIM.SL_LOC,'extLanguages').split(",");
		for(var I=0; I<LNGS.length; I++){
			var LN = LNGS[I].split(":");
		 	if(LN[0]==DetLang){
				doc.getElementById('SL_lng_from').title=FExtension.element(TranslatorIM.SL_LOC,'extDetected') + " " + LN[1];
				break;
			}
		}			
		var autopattern = "auto";
		if(AUTO != true ) autopattern = "XautoX";
		return autopattern;
	},
	
	ACTIVATE_THEMEwpt_lng: function (st){
	 	if(st==1){
	 	        var bg = "#191919";
			var doc = TranslatorIM.DOC;
			var SL_lng = doc.getElementById("SL_wptLang");
			for(var j=0; j<SL_lng.options.length; j++) SL_lng.options[j].setAttribute("style", "background:"+bg+" !important;color:#fff;");
		}
	},

	ACTIVATE_THEMEwpt_dom: function (st){
	 	if(st==1){
	 	        var bg = "#191919";
			var doc = TranslatorIM.DOC;
			if(doc.getElementById("SL_OPT_MENUid")) doc.getElementById("SL_OPT_MENUid").style.filter=TranslatorIM.SL_DARK;
			if(doc.getElementById("SL_TBpatchid")) doc.getElementById("SL_TBpatchid").style.filter=TranslatorIM.SL_DARK;
			if(doc.getElementById("SL_TBsave1")) doc.getElementById("SL_TBsave1").style.filter=TranslatorIM.SL_DARK;
			if(doc.getElementById("SL_TBsave2")) doc.getElementById("SL_TBsave2").style.filter=TranslatorIM.SL_DARK;
			if(doc.getElementById("SL_WPT_TAB1")) doc.getElementById("SL_WPT_TAB1").style.filter=TranslatorIM.SL_DARK;
			if(doc.getElementById("SL_WPT_TAB2")) doc.getElementById("SL_WPT_TAB2").style.filter=TranslatorIM.SL_DARK;
			if(doc.getElementById("SL_domain")) doc.getElementById("SL_domain").style.filter=TranslatorIM.SL_DARK;
			var SL_lng = doc.getElementById("SL_wptTrTo");
			for(var j=0; j<SL_lng.options.length; j++) SL_lng.options[j].setAttribute("style", "background:"+bg+" !important;color:#fff;");
		}
	},

	ACTIVATE_THEMEwpt: function (st){
	 	if(st==1){
	 	        var bg = "#191919";
			var doc = TranslatorIM.DOC;
			if(doc.getElementById(":0.container")) doc.getElementById(":0.container").style.filter=TranslatorIM.SL_DARK;
		      	var win = top.window.frames[":0.container"].contentWindow;
			var hrefs = win.document.getElementsByClassName('goog-te-button');
			for(var i=0; i<hrefs.length; i++) hrefs[i].setAttribute("style", "filter:"+TranslatorIM.SL_DARK);
			var hrefs = win.document.getElementsByClassName("goog-logo-link");
			for(var i=0; i<hrefs.length; i++) hrefs[i].style.filter=TranslatorIM.SL_DARK;
			win.document.getElementById("SL_TBoptions").style.filter=TranslatorIM.SL_DARK;
			var SL_lng = win.document.getElementById("SL_G_M_to");
			for(var j=0; j<SL_lng.options.length; j++) SL_lng.options[j].setAttribute("style", "background:"+bg+" !important;color:#fff;");
		}
	},

	ACTIVATE_THEMEbbl: function (st){
	 	if(st==1){
	 	        var bg = "#191919";
			var doc = TranslatorIM.DOC;
		        if(doc.getElementById("SL_shadow_translator")){
			doc.getElementById("SL_shadow_translator").style.filter=TranslatorIM.SL_DARK;

			var SL_lng = doc.getElementsByClassName("SL_lngs");
			for(var i=0; i<SL_lng.length; i++) {
				for(var j=0; j<SL_lng[i].options.length; j++) SL_lng[i].options[j].setAttribute("style", "background:"+bg+" !important;color:#fff;");
			}

			var hrefs = doc.getElementsByClassName("SL_options");
			for(var i=0; i<hrefs.length; i++) hrefs[i].setAttribute("style", "filter:"+TranslatorIM.SL_DARK);
			var hrefs = doc.getElementsByClassName("_ALNK");
			for(var i=0; i<hrefs.length; i++) hrefs[i].setAttribute("style", "filter:"+TranslatorIM.SL_DARK);

//			var hrefs = doc.getElementsByClassName("skiptranslate");
//			for(var i=0; i<hrefs.length; i++) hrefs[i].setAttribute("style", "filter:"+TranslatorIM.SL_DARK);

			doc.getElementById("SL_PN0").style.filter=(TranslatorIM.SL_DARK-90);
                        doc.getElementById("SL_PN1").style.filter=(TranslatorIM.SL_DARK-90);
			doc.getElementById("SL_PN2").style.filter=(TranslatorIM.SL_DARK-90);
			//doc.getElementById("SL_PN3").style.filter=(TranslatorIM.SL_DARK-90);

			setTimeout(function() {
				var lbl = doc.getElementsByClassName("SL_BL_LABLE_ON");	
				for(var i=0; i<lbl.length; i++) {
					var ind = lbl[i].id.replace("SL_P","");
					if(lbl[i].id.indexOf(ind)!=-1) doc.getElementById("SL_PN"+ind).style.filter=TranslatorIM.SL_LIGHT;
				}
			}, 700);
			}
		}
	},

	SL_YANDEX: function(text,f,t){
	     	var doc = TranslatorIM.DOC;
	     	var doc2 = FExtension.browserInject;

        	f = f.replace("zh-CN","zh");
        	f = f.replace("jw","jv");
	        f = f.replace("iw","he");
		f = f.replace("srsl","sr");
        	f = f.replace("tlsl","tl");

	        t = t.replace("zh-CN","zh");
	        t = t.replace("jw","jv");
        	t = t.replace("iw","he");
		t = t.replace("srsl","sr");
        	t = t.replace("tlsl","tl");


                if(text.length<=TranslatorIM.SL_Balloon_translation_limit) text = TranslatorIM.truncStrByWord(text,TranslatorIM.SL_Balloon_translation_limit);
                if(text!=""){
		        var dir = f+"-"+t;
			if(f=="auto") dir = t;
		        chrome.runtime.sendMessage({greeting: "TR_YANDEX:>"+dir+","+encodeURIComponent(text) }, function(response) {});
			setTimeout(function(){
			    var SLIDL = setInterval(function(){
			           chrome.runtime.sendMessage({greeting: 1}, function(response) {
			             if(response && response.farewell){
				        var theresponse = response.farewell.split("~");
					TranslatorIM.BBL_RESULT=theresponse[52];
					if(TranslatorIM.BBL_RESULT!="") {
						text = TranslatorIM.BBL_RESULT;
						TranslatorIM.BBL_RESULT="";
						clearInterval(SLIDL);
						//text=text.replace(/#/ig,"'");
					    	if(text!="" && text!="<#>"){
							TranslatorIM.SL_temp_result = text;
							//text=text.replace(/@/ig,'<br>');
	       					        var resptmp = TranslatorIM.PPB_tts_icon(t,text);
							resptmp = DOMPurify.sanitize(resptmp);
        		        			doc.getElementById('SL_shadow_translation_result').innerHTML=resptmp.replace(/\\n/ig,'<br>');
							doc.getElementById('SL_shadow_translation_result2').innerHTML=resptmp.replace(/\\n/ig,'<br>');
	               					doc.getElementById('SL_shadow_translation_result').style.direction = "ltr";
							doc.getElementById('SL_shadow_translation_result').style.textAlign = "left";
							if(t == "ar" || t == "he" || t == "fa" || t == "yi" || t == "ur" || t == "ps" || t == "sd" || t == "ckb" || t == "ug" || t == "dv" || t == "prs"){
								doc.getElementById('SL_shadow_translation_result').style.direction = "rtl";
								doc.getElementById('SL_shadow_translation_result').style.textAlign = "right";
							}
	       					        TranslatorIM.SL_JUMP(doc);
							setTimeout(function() {	
								var HID=2;
							        if (TranslatorIM.SL_TH_2 == 1){
		     							var doc2 = FExtension.browserInject;
									var SLnow = new Date();
									SLnow = SLnow.toString();
									var TMPtime = SLnow.split(" ");
									var CurDT = TMPtime[1] + " " + TMPtime[2] + " " + TMPtime[3] + ", " + TMPtime[4];
		        			                	var LNGfrom = f;
						                        if(f=="auto" || doc.getElementById("SL_locer").checked == false) var LNGfrom = TranslatorIM.LNGforHISTORY;
									if(TranslatorIM.SL_WRONGLANGUAGEDETECTED==1) LNGfrom="auto";
                        						text=text.replace(/~/ig," ");
								        text=text.replace(/\^/g,"@");
								        var DICT = TranslatorIM.BL_T_PROV;
									if(TranslatorIM.SL_MODE==1) DICT = TranslatorIM.BL_D_PROV;
									doc2.runtimeSendMessage({greeting:"[b]" + TranslatorIM.SL_TEMP_TEXT + "~~" + text + "~~" + LNGfrom + "|" + t + "~~"+ doc.location+"~~"+CurDT+"~~"+HID+"~~"+DICT[0]+"^^"}, function(response) {
										if(response){ }
									});
								}
							}, 500);
		    				}else{
							var msg = "Due to too many requests coming from your IP address, access to the free Yandex Translator has been temporarily disabled. Please try again later.";
							msg = DOMPurify.sanitize(msg);
			                		doc.getElementById('SL_shadow_translation_result').innerHTML=msg;
                					doc.getElementById('SL_shadow_translation_result2').innerHTML=msg;
					    	}
						doc.getElementById('SL_loading').style.display = 'none';
			            }
				}
			      });
			    },50);  
 		         },50);  

		}
	},

	SL_BBL_OBJ_OFF: function(st){		
	     	var doc = TranslatorIM.DOC;
		TranslatorIM.CONTROL_SUM="";
		if (st == 0){ 
			if(TranslatorIM.SL_SAVETEXT == 0){
				if(doc.getElementById("SL_balloon_obj")) doc.body.removeChild (doc.getElementById("SL_balloon_obj"));			
			}
		} else{
			if(doc.getElementById("SL_balloon_obj")) doc.body.removeChild (doc.getElementById("SL_balloon_obj"));			
		}
	},

	BBL_IfMouseIsInside: function(e){
		var doc = TranslatorIM.DOC;
		var st = 0;
		var THEobj = doc.getElementById('SL_shadow_translator');
		if(THEobj){
			var divRect = THEobj.getBoundingClientRect();
			if (e.clientX >= (divRect.left-20) && e.clientX <= divRect.right && e.clientY >= divRect.top && e.clientY <= divRect.bottom) st=1;
		}
		return(st);
	},

	InitiateIT_target_lang: function(){
	     	var doc = TranslatorIM.DOC;
	        var container = doc.body;
	        if(TranslatorIM.GET_TEXT()!=""){
                  if(container){
		          var ext = FExtension.browserInject;
			  var theObj = doc.getElementById("SL_MENU");
                          if(theObj) theObj.parentNode.removeChild(theObj);
			  var OB = doc.createElement('div');
			  var id = doc.createAttribute("id");
			  id.value = "SL_MENU";
		          OB.setAttributeNode(id);
			  var cl = doc.createAttribute("class");
			  cl.value = "skiptranslate";
		          OB.setAttributeNode(cl);

        		  container.appendChild (OB);
                          var OB2="";
		          var act = "";
			  var MENU = TranslatorIM.SL_LNG_LIST.split(",");
			  var splt = 0;
		     	  if(MENU.length>=TranslatorIM.SL_FAV_START){
				  var SL_FAV_LANGS_LONG = TranslatorIM.SL_ADD_LONG_NAMES(TranslatorIM.SL_FAV_LANGS_IT);
				  if(SL_FAV_LANGS_LONG!=""){
					var favArr=SL_FAV_LANGS_LONG.split(","); 
					for(var I=0; I < favArr.length; I++){
					    var CURlang = favArr[I].split(":");
					    act = "";
					    if (I==0) {
						act=" selected ";
					        TranslatorIM.SL_langDst_bbl2 = CURlang[0];
						TranslatorIM.SL_SAVE_FAVORITE_LANGUAGES(CURlang[0], '', 1, TranslatorIM.SL_FAV_LANGS_IT, "IT");
					    }
					    OB2 = OB2 + "<option " + act +" value='"+CURlang[0]+"'>"+CURlang[1]+"</option>";
					}
					var all = FExtension.element(TranslatorIM.SL_LOC,"extwptDAll");
				        OB2 = OB2 + "<option disabled value=''>-------- [ "+ all +" ] --------</option>";
				  }
				  splt=1;
			  }

			  TranslatorIM.SL_LNG_LIST = TranslatorIM.CUSTOM_LANGS(FExtension.element(TranslatorIM.SL_LOC,'extLanguages'));
			  var MENU = TranslatorIM.SL_LNG_LIST.split(",");
			  for(var J=0; J < MENU.length; J++){
			    CURlang = MENU[J].split(":");
			    if(splt == 1 ){
				    if(SL_FAV_LANGS_LONG==""){
					    var act2 = "";
					    if(TranslatorIM.SL_langDst_it == CURlang[0] ) act2=" selected ";
				    }
			    } else { 
				    var act2 = "";
				    if(TranslatorIM.SL_langDst_it == CURlang[0] ) act2=" selected ";
			    }
			    OB2 = OB2 + "<option "+ act2 +" value='"+CURlang[0]+"'>"+CURlang[1]+"</option>";
			  }
			  var OBCLOSE = "<div src='#'  title='"+FExtension.element(TranslatorIM.SL_LOC,'extClose')+"' id='SL_MENU_CLOSE'></div>";
			  var OBMENU = "<select id='SL_IT_MENU'>" + OB2 + "</select>";
			  var OBLINKS = "<div id='SL_MENU_LINKS' align=center><a id='SL_MENU_LINK_OPT'>"+FExtension.element(TranslatorIM.SL_LOC,"extOptions")+"</a> : <a id='SL_MENU_LINK_HIS'>"+FExtension.element(TranslatorIM.SL_LOC,"extHistory")+"</a></div>";
			  doc.getElementById("SL_MENU").innerHTML=OBCLOSE+"<span id='SL_MENU_TTL'>" + FExtension.element(TranslatorIM.SL_LOC,"extSeTa")+"</span><br>"+OBMENU + OBLINKS;
		  	  doc.getElementById('SL_MENU_CLOSE').style.background='url('+ext.getURL('content/img/util/close.png')+')';
		  	  doc.getElementById('SL_IT_MENU').style.background='#fff url('+ext.getURL('content/img/util/select.png')+')  no-repeat 100% 0';

		  }
		}
	},




	InitiateWPT_target_lang: function(LN){
	     	var doc = TranslatorIM.DOC;
	        var container = doc.body;
                  if(container){
		          var ext = FExtension.browserInject;
			  var OB = doc.createElement('div');
			  var id = doc.createAttribute("id");
			  id.value = "SL_MENU_WPT";
		          OB.setAttributeNode(id);
			  var cl = doc.createAttribute("class");
			  cl.value = "skiptranslate";
		          OB.setAttributeNode(cl);

        		  container.appendChild (OB);
                          var msg = "<b>'"+LN+"'</b><br>" + FExtension.element(TranslatorIM.SL_LOC,"extnotsupported");
                          //var msg = "Google Translate does not support<br> '<b>"+LN+"</b>' language yet";

			  var OBCLOSE = "<div src='#' title='"+FExtension.element(TranslatorIM.SL_LOC,'extClose')+"' id='SL_WPT_MENU_CLOSE'></div>";
			  doc.getElementById("SL_MENU_WPT").innerHTML=DOMPurify.sanitize(OBCLOSE+"<div id='SL_MENU_TTL' style='margin-top:10px;'>" + msg + "</div><br>");
		  	  doc.getElementById('SL_WPT_MENU_CLOSE').style.background='url('+ext.getURL('content/img/util/close.png')+')';
		  }
	},


	CloseIT_target_lang: function(){
	     	var doc = TranslatorIM.DOC;
		var theObj = doc.getElementById("SL_MENU");
                if(theObj) theObj.parentNode.removeChild(theObj);
	},

	SL_IT_retranslate: function(){
	     	var doc = TranslatorIM.DOC;
		chrome.runtime.sendMessage({greeting: "SES_IT:>" + doc.getElementById("SL_IT_MENU").value}, function(response) {}); 
		TranslatorIM.SL_langDst_it=doc.getElementById("SL_IT_MENU").value;
	        TranslatorIM.SL_SAVE_FAVORITE_LANGUAGES(TranslatorIM.SL_langDst_it, '', 1, TranslatorIM.SL_FAV_LANGS_IT, "IT");
		runinliner();
		TranslatorIM.SL_ONETIMERUN=1;
		TranslatorIM.CloseIT_target_lang();
	},

	SL_IT_retranslate_and_close: function(){
	     	var doc = TranslatorIM.DOC;
		runinliner();
		TranslatorIM.SL_ONETIMERUN=1;
		TranslatorIM.CloseIT_target_lang();
	},

	SAVE_SES_PARAMS: function(){
	     	var doc = TranslatorIM.DOC;
//		if(doc.getElementById("SL_balloon_obj")) {
			//if(TranslatorIM.SL_langDst!=TranslatorIM.SL_langDst_bbl2) doc.getElementById("SL_lng_to").value=TranslatorIM.SL_langDst_bbl2;
			var dofrom = doc.getElementById("SL_lng_from").value;
			var doto = doc.getElementById("SL_lng_to").value;
/*
			if(TranslatorIM.FlippedByAuto == 1){
				var dofrom = TranslatorIM.SL_langSrc;
				var doto = TranslatorIM.SL_langDst;
			}
*/
			if(doto == "") doto = TranslatorIM.SL_langDst;
			chrome.runtime.sendMessage({greeting: "SES:>" + dofrom +","+doto+","+TranslatorIM.SL_FONT_SID+","+TranslatorIM.SL_SID_PIN+","+doc.getElementById('SL_locer').checked+","+TranslatorIM.SL_OnOff_BTN2}, function(response) {}); 

//		}
	},

	i18n_LanguageDetect: function(text, st){
   		var lng="";
		st=1
   		if(st==1){	
	  	      if(text.length>1){
				chrome.i18n.detectLanguage(text, function(result) {
					lng = result.languages[0].language;
				});
				if(lng=="zh") lng = "zh-CN";
				if(lng=="zh-Hant") lng = "zh-TW";
			}
		
			if(lng !=""){
				var LANGSALL = FExtension.element(TranslatorIM.SL_LOC,'extLanguages').split(",");
				var cntr = 0;
       			        for (var i=0;i<LANGSALL.length;i++){
					var templang = LANGSALL[i].split(":");
		   			if(templang[0]==lng) cntr++;
				}
				if(cntr==0) lng="";
			}
		}
	
                TranslatorIM.ONCE_DETECT = 1;
		TranslatorIM.SL_WPT_LANG=lng;
	    	return lng;
	},

	CNTR: function(id,dir,nmb){
	    chrome.runtime.sendMessage({greeting: "CNTR:>"+id+","+dir+","+nmb}, function(response) {}); 
	},

	CNTRP: function(id,dir,nmb){
	    chrome.runtime.sendMessage({greeting: "CNTRP:>"+id+","+dir+","+nmb}, function(response) {}); 
	},

	SL_ADD_LONG_NAMES: function(codes){
		var OUT = "";
		var MENU = TranslatorIM.SL_LNG_LIST.split(",");
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
	},

	SL_SAVE_FAVORITE_LANGUAGES: function(ln, ob, st, TR, TP){
		var OUT = "";
		var OUT2 = "";
		if(TR.indexOf(ln)!=-1){
			TR = TR.replace(ln+",",""); 
			if(TR.indexOf(",")==-1) TR = TR.replace(ln,""); 
		}

		OUT = ln + ",";	
		var ARR = TR.split(",");
		for (var i = 0; i < ARR.length; i++){
		 	OUT = OUT + ARR[i]+",";
		}
		if(OUT.slice(-1)==",") 	OUT = OUT.slice(0, OUT.length - 1);
		var TMP = OUT.split(",");
		if(TMP.length > TranslatorIM.SL_FAV_MAX) {
			for (var j = 0; j < TMP.length-1; j++){
			 	OUT2 = OUT2 + TMP[j]+",";
			}		
			OUT = OUT2 
		}
		OUT = TranslatorIM.uniqFAV(OUT);
		if(OUT.slice(-1)==",") 	OUT = OUT.slice(0, OUT.length - 1);
		chrome.runtime.sendMessage({greeting: "FAV_"+TP+":>" + OUT}, function(response) {}); 

		if(st == 0){
			if(OUT!=""){
				var MENU = TranslatorIM.SL_LNG_LIST.split(",");
				if(MENU.length>=TranslatorIM.SL_FAV_START){
					TranslatorIM.SL_REBUILD_TARGET_LANGUAGE_MENU(OUT,ob);
				}
			}
		}

	},

	uniqFAV: function(FAV) {
		var OUT = "";
		var array = FAV.split(",");
		const uniqueArray = array.filter((value, index, self) => {
			return self.indexOf(value) === index;
		});
		var MAX = uniqueArray.length;
		if(uniqueArray.length>TranslatorIM.SL_FAV_MAX) MAX = TranslatorIM.SL_FAV_MAX;
		for(var i=0;i<MAX; i++) {
			OUT = OUT + uniqueArray[i]+",";	
		}
 		return(OUT);
	},


	SL_REBUILD_TARGET_LANGUAGE_MENU: function (FAV, ob){
		var doc = TranslatorIM.DOC;
		var MENU = TranslatorIM.SL_LNG_LIST.split(",");
		if(MENU.length>=TranslatorIM.SL_FAV_START){
        	        doc.getElementById(ob).innerText="";
			var SEL = 0;
			if(FAV!=""){
                        	FAV = TranslatorIM.SL_ADD_LONG_NAMES(FAV);
				var favArr=FAV.split(","); 
				for(var J=0; J < favArr.length; J++){
				    var CURlang = favArr[J].split(":");
				    var OB_FAV = doc.createElement('option');

				    var v = doc.createAttribute("value");				    		
				    v.value = CURlang[0];
				    OB_FAV.setAttributeNode(v);

				    if(J == 0){
					    var sel = doc.createAttribute("selected");
					    sel.value = "selected";
					    OB_FAV.setAttributeNode(sel);
					    TranslatorIM.SL_langDst = CURlang[0];
					    SEL = 1;	
				    }

				    OB_FAV.appendChild(doc.createTextNode(CURlang[1]));
				    doc.getElementById(ob).appendChild(OB_FAV);
				}
				OB_FAV = doc.createElement('option');
				var d = doc.createAttribute("disabled");
				d.value = true;
				OB_FAV.setAttributeNode(d);
				var all = FExtension.element(TranslatorIM.SL_LOC,"extwptDAll");
			    	OB_FAV.appendChild(doc.createTextNode("-------- [ "+ all +" ] --------"));
			    	doc.getElementById(ob).appendChild(OB_FAV);
			}
			var tmp =favArr[0].split(":");
		        var thelang = tmp[0];
			for(J=0; J < MENU.length; J++){
			    CURlang = MENU[J].split(":");
			    var option = doc.createElement('option');
			    if(SEL == 0){
				    if(CURlang[0] == thelang){
					    var sel = doc.createAttribute("selected");
					    sel.value = "selected";
					    option.setAttributeNode(sel);
				    }
			    }
			    v = doc.createAttribute("value");
			    v.value = CURlang[0];
			    option.setAttributeNode(v);
			    option.appendChild(doc.createTextNode(CURlang[1]));
			    doc.getElementById(ob).appendChild(option);
			}
		} else {
			doc.getElementById(ob).innerText="";
		        var thelang = TranslatorIM.SL_langDst;
			if(TranslatorIM.SL_langDst!="" && TranslatorIM.SL_SID_TO=="") thelang = TranslatorIM.SL_langDst_bbl2;
			for(J=0; J < MENU.length; J++){
			    CURlang = MENU[J].split(":");
			    var option = doc.createElement('option');
			    if(CURlang[0] == thelang){
				    var sel = doc.createAttribute("selected");
				    sel.value = "selected";
				    option.setAttributeNode(sel);
			    }
			    v = doc.createAttribute("value");
			    v.value = CURlang[0];
			    option.setAttributeNode(v);
			    option.appendChild(doc.createTextNode(CURlang[1]));
			    doc.getElementById(ob).appendChild(option);
			}

		}
	},

	SL_OPEN_BG_OPTIONS: function(st){
		chrome.runtime.sendMessage({greeting: "OPEN_O:>"+st}, function(response) {});
        },


	closeWPT_ERROR_MSG: function(){
		var doc = TranslatorIM.DOC;
//		doc.getElementById("SL_MENU_WPT").style.display='none';
		doc.getElementById("SL_MENU_WPT").style.top='-1000px';
	},

	NoProvidersAlert: function(){
		var doc = TranslatorIM.DOC;
		var T = doc.getElementById('SL_lng_to').value;
	   	var msg = FExtension.element(TranslatorIM.SL_LOC,"extLPNotSupported");
	   	var selectDst = doc.getElementById('SL_lng_to');
	   	var selectedDstIndex = selectDst.selectedIndex;
	   	var selectedDstText = selectDst.options[selectedDstIndex].text; 

	   	var selectSrc = doc.getElementById('SL_lng_from');
	   	var selectedSrcIndex = selectSrc.selectedIndex;
	   	var selectedSrcText = selectSrc.options[selectedSrcIndex].text; 
		if(selectSrc.value=="auto") selectedSrcText=TranslatorIM.SL_GetLongName(TranslatorIM.SL_DETECT);
	   	msg = msg.replace("XXX",selectedSrcText);
	   	msg = msg.replace("YYY",selectedDstText);
		if(TranslatorIM.SL_SHOW_PROVIDERS==0) msg = msg + "<br><br>" + "Please activate all providers in the Options";
	   	doc.getElementById('SL_shadow_translation_result').style.visibility="visible";
	   	doc.getElementById('SL_shadow_translation_result2').style.visibility="visible";

	   	doc.getElementById('SL_shadow_translation_result').innerHTML=DOMPurify.sanitize("<div align=center style='color:red;margin-top:20px;'>"+msg+"</div>");
	   	doc.getElementById('SL_shadow_translation_result2').innerHTML=DOMPurify.sanitize("<div align=center style='color:red;margin-top:20px;'>"+msg+"</div>");
	   	TranslatorIM.SL_SAVE_FAVORITE_LANGUAGES(T, 'SL_lng_to', 0, TranslatorIM.SL_FAV_LANGS_BBL, "BBL");
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

	GET_TEXT: function(){
	    let text = "";
	    if (window.getSelection) {
        	text = window.getSelection().toString();
	    } else if (document.selection && document.selection.type != "Control") {
        	text = document.selection.createRange().text;
	    }
	    // IN CLEAR TRANSLATION STATUS
	    chrome.runtime.sendMessage({greeting: "CLEAR:>"+TranslatorIM.DetermineIfNeedsToBeClean()}, function(response) {});
	    
	    chrome.runtime.sendMessage({greeting: "PUSH:>"+text}, function(response) {});
		chrome.runtime.sendMessage({ greeting: 'get-user-data' }, (response) => {
		  //console.log('received user data', response);
	    });
	    return text;
	},

	DetermineIfNeedsToBeClean: function(){
		var obj = TranslatorIM.DOC.getElementsByTagName('inliner');
		if(obj.length > 0) return 1;
		else return 0;
	},

	LAST_CHANCE_TRANSLATION: function(S,T,text,PR){
	        var doc = FExtension.browserInject;
 		var doc2 = doc.getDocument();

		var a=Math.floor((new Date).getTime()/36E5)^123456;
		var tk = a+"|"+Math.floor((Math.sqrt(5)-1)/2*(a^654321)%1*1048576);
	        var num = Math.floor((Math.random() * SL_GEO.length)); 
		var theRegion = SL_GEO[num];
		var baseUrl ="https://translate.google."+theRegion+"/translate_a/single";
		var SL_Params = "client=gtx&dt=t&dt=bd&dj=1&source=input&q="+encodeURIComponent(text)+"&sl=auto&tl="+T+"&hl=en&tk="+tk;
	        chrome.runtime.sendMessage({greeting: "LAST_TRANSLATION_GOOGLE:>"+baseUrl+","+ SL_Params+",100"}, function(response) {});
					setTimeout(function(){
					    var SLIDL="";
					    var MAX_CNT=25;
					    var CNT=0;
					    clearInterval(SLIDL);
					    SLIDL = setInterval(function(){
					        if(chrome.runtime){
					           chrome.runtime.sendMessage({greeting: 1}, function(response) {
                                                     CNT++;
				        	     if(response && response.farewell){
					        	var theresponse = response.farewell.split("~");
							TranslatorIM.BBL_RESULT=theresponse[52].replace(/\^/ig,"~");
					                TranslatorIM.BBL_RESULT=TranslatorIM.BBL_RESULT.replace(/\\"/g,"'");
					                TranslatorIM.BBL_RESULT=TranslatorIM.BBL_RESULT.replace(/\\n/g,"<br>");
					                TranslatorIM.BBL_RESULT=TranslatorIM.BBL_RESULT.replace(/\\u0027/g,"'");
						
							if(TranslatorIM.BBL_RESULT!="" && CNT <= MAX_CNT) {

								var resp = TranslatorIM.BBL_RESULT;
								  TranslatorIM.BBL_RESULT="";
								  clearInterval(SLIDL);
								  if(doc2.getElementById("SL_shadow_translator").style.display=='block'){	
									if(resp != "" && resp != "<#>"){	
								                var resptmp = resp;
										if(resp.indexOf('<div')==-1) resptmp = TranslatorIM.PPB_tts_icon(T,resp);

										resptmp = DOMPurify.sanitize(resptmp);
										doc2.getElementById('SL_shadow_translation_result').innerHTML=resptmp;
										doc2.getElementById('SL_shadow_translation_result2').innerHTML=resptmp;

										TranslatorIM.ACTIVATE_THEMEbbl(TranslatorIM.THEMEmode);
								                TranslatorIM.SL_JUMP(doc2);
						        	                TranslatorIM.SL_temp_result=resp;

										if (TranslatorIM.SL_TH_2 == 1){

											var SLnow = new Date();
											SLnow = SLnow.toString();
											var TMPtime = SLnow.split(" ");
											var CurDT = TMPtime[1] + " " + TMPtime[2] + " " + TMPtime[3] + ", " + TMPtime[4];
								                        var LNGfrom = S;

								                        if(S=="auto" || doc2.getElementById("SL_locer").checked == false) var LNGfrom = TranslatorIM.LNGforHISTORY;
											if(TranslatorIM.SL_WRONGLANGUAGEDETECTED==1) LNGfrom="auto";
						        	                        var ImtranslatorGoogleResult="";
						                	                var myTransText=text.replace(/~/ig," ");
						                        		var ImtranslatorGoogleResult4 = resp.replace(/~/ig," ");
											ImtranslatorGoogleResult = ImtranslatorGoogleResult4;
										        myTransText=myTransText.replace(/\^/g,"@");
											doc.runtimeSendMessage({greeting: "[b]" + myTransText + "~~" + ImtranslatorGoogleResult + "~~" + LNGfrom + "|" + T + "~~"+ doc2.location+"~~"+CurDT+"~~"+HID+"~~"+PR[0]+"^^"}, function(response) {
												if(response){ 
												//	console.log(response.farewell); 
												}
											});
										}
									} 

									doc2.getElementById('SL_shadow_translation_result').style.direction = "ltr";
									doc2.getElementById('SL_shadow_translation_result').style.textAlign = "left";
									if(T=="ar" || T=="iw" || T=="fa" || T=="yi" || T=="ur" || T=="ps" || T=="sd" || T=="ckb" || T=="ug" || T=="dv" || T=="prs"){
										doc2.getElementById('SL_shadow_translation_result').style.direction = "rtl";
										doc2.getElementById('SL_shadow_translation_result').style.textAlign = "right";
									}
									doc2.getElementById('SL_shadow_translator').style.display = 'block';
									TranslatorIM.SL_temp_result = resp;
									if(doc2.getElementById('SL_shadow_translator').offsetHeight > 100) TranslatorIM.SL_BALLON_H = doc2.getElementById('SL_shadow_translator').offsetHeight;
								}
				        	    	}else{
								if(CNT > MAX_CNT){
									clearInterval(SLIDL);
									var MSG = FExtension.element(TranslatorIM.SL_LOC,'extADVstu');
									MSG = DOMPurify.sanitize(MSG);
									doc2.getElementById('SL_shadow_translation_result').innerHTML="* "+MSG;
									doc2.getElementById('SL_shadow_translation_result2').innerHTML="* "+MSG;
								}

							}
						     }
		
					           });
						}
					    },50);  
					  
 		        		 },50);  

		},

	ACTIVATE_WPT: function (st, host){		
	    try{
		RESTORE=0;
		TranslatorIM.SL_setSHOW_HIDE_TB_TMP("SL_GWPT_Show_Hide_tmp",1);

		var OB1 = document.getElementById('wpt_hidden_logo');
		if(OB1)	OB1.parentNode.removeChild(OB1);
		CLOSE_WPT_TB();
		ONCE_ONLY=0;
		TranslatorIM.SL_wpt_MANUAL_MODE_ON = host;		
		INIT_WPT_TB(TranslatorIM.SL_LOC,0);
		WPT_RUN();
	   } catch(ex){}
	},

	CloseAnyOpenTranslator: function(){
	   try{
		if(TranslatorIM.SL_HK_CTbox_wpt == "true"){
			WPT_RESTORE_ORIGINAL_NODES();
			DELETE_WPT_TB();
		        CLOSE_WPT_TB();
			FExtension.browserInject.runtimeSendMessage({greeting: "CLEAN_ALL:>"}, function(response) {});
		}
	   } catch(ex){}
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
		TranslatorIM.AKEY = "";
	    }
	  }, 1000);
	},

	VerifyDetectedLang: function(lng){
	        var out=0;
		var str = TranslatorIM.CUSTOM_LANGS(FExtension.element(TranslatorIM.SL_LOC,'extLanguages')).split(",");
		for(var i=0; i<str.length; i++){
			var list = str[i].split(":");
			if(list[0]==lng) out++;
		}
		return(out);
	}


}


if(FExtension.browser.isLocalStoragePreset()){
	TranslatorIM.init();
}else{
	var appcontent = window.document.getElementById("appcontent");
	appcontent.addEventListener("DOMContentLoaded", function(){
		TranslatorIM.init();
       		init();
	}, false);
}


window.addEventListener("DOMContentLoaded", TranslatorIM.SL_GOOGLE_WPT(), false);

}catch(e){
//	TranslatorIM.SL_alert(FExtension.element(TranslatorIM.SL_LOC,"extError2"));
}


chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  setTimeout(function(){
        try{
		if(message.action=="open_bubble"){
			var doc = TranslatorIM.DOC;
			if(doc.getElementById("SL_shadow_translator").style.display!="block"){
				TranslatorIM.SL_BUBBLE_FROM_CM(window.e, 0);
			}
		}
	} catch(ex){}
	if(message.action=="open_inline"){
		TranslatorIM.SL_runinlinerNOW(window.e, 0);
	}

	if(message.action=="clear_inline"){
		inlinerInjectClean();
	}

	if(message.action=="open_mo"){
		TranslatorIM.SL_WPT(1);
	}

	if(message.action=="open_wpt"){
		try{
			TranslatorIM.ACTIVATE_WPT(1, top.location.host);
		} catch(ex){}
	}

	if(message.action=="inline_trans"){		
		if(message.res.indexOf("<#>")==-1) 	TranslatorIM.InlineDataTransmitter(escape(message.res));
		else {                
			var msg = FExtension.element(TranslatorIM.SL_LOC,'extnotrsrv')
			TranslatorIM.InlineDataTransmitter(escape(msg));			
		}

	}
  },10);
 

});