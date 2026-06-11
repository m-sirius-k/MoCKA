'use strict';
var SERVICES=1;
var SL_DARK="invert(95%)";
var PACK_PARAMS; 
setTimeout(function() {	
	var SL_Languages = CUSTOM_LANGS(FExtension.element(GET("SL_LOCALIZATION"),'extLanguages'));

	(function(){GEBI("SRV3").addEventListener("click",function(){SL_ACTIVE = GEBI("SRV3"); SL_TMP=SL_ACTIVE.value; SL_ACTIVE.focus();SL_MSG_HANDLER(event);},!1); } )();
	(function(){GEBI("SRV3").addEventListener("mouseout",function(){NoneColor(3);},!1); } )();
	(function(){GEBI("SL_del3").addEventListener("click",function(){SL_DEL_AUTO(3);},!1);} )();
	(function(){GEBI("SRV3").addEventListener("paste",function(){ PREVENT_PASTE(event); },!1);} )();

	(function(){GEBI("SRV4").addEventListener("click",function(){SL_ACTIVE = GEBI("SRV4"); SL_TMP=SL_ACTIVE.value; SL_ACTIVE.focus();SL_MSG_HANDLER(event);},!1); } )();
	(function(){GEBI("SRV4").addEventListener("mouseout",function(){NoneColor(4);},!1); } )();
	(function(){GEBI("SRV4").addEventListener("paste",function(){ PREVENT_PASTE(event); },!1);} )();

	(function(){GEBI("SRV11").addEventListener("click",function(){SL_ACTIVE = GEBI("SRV11"); SL_TMP=SL_ACTIVE.value; SL_ACTIVE.focus();SL_MSG_HANDLER(event);},!1); } )();
	(function(){GEBI("SRV11").addEventListener("mouseout",function(){NoneColor(11);},!1); } )();
	(function(){GEBI("SRV11").addEventListener("paste",function(){ PREVENT_PASTE(event); },!1);} )();

	(function(){GEBI('SL_inject_before').addEventListener("click",function(){ OneOfTwo(1); },!1);} )();
	(function(){GEBI('SL_hide_translation').addEventListener("click",function(){ OneOfTwo(2); },!1);} )();
//	(function(){GEBI("SL_OtherTr").addEventListener("click",function(){ SL_SHOWHIDEPROVIDERS(); },!1); } )();

	(function(){window.addEventListener("mousemove",function(){NoneColor(3);},!1);} )();
	(function(){GEBI("SL_info").addEventListener("click",function(){FExtension.browserPopup.openNewTab(this.href);},!1);} )();

	(function(){GEBI("SL_FK_box1").addEventListener("click",function(){ SL_HIDE_HK("SL_FK_box1","SL_HIDE3");},!1); } )();
	(function(){GEBI("SL_FK_box2").addEventListener("click",function(){ SL_HIDE_HK("SL_FK_box2","SL_HIDE4");},!1); } )();
	(function(){GEBI("SL_FK_box11").addEventListener("click",function(){ SL_HIDE_HK("SL_FK_box11","SL_HIDE11");},!1); } )();

	(function(){GEBI("SL_LOC").addEventListener("change",function(){SL_SAVE_LOC();},!1);} )();
	(function(){GEBI("SL_LNG_STATUS").addEventListener("click",function(){ SL_LANGS(); },!1); } )();

	(function(){GEBI("SL_THEME").addEventListener("change",function(){SL_SAVE_THEME();},!1);} )();


	(function(){GEBI("reset_all3").addEventListener("click",function(){ RESET_ALL_HK(3);},!1);} )();
	(function(){GEBI("reset_all4").addEventListener("click",function(){ RESET_ALL_HK(4);},!1);} )();
	(function(){GEBI("reset_all11").addEventListener("click",function(){ RESET_ALL_HK(11);},!1);} )();

	(function(){window.addEventListener("mousemove",function(){
		BUILD_RESET_ICN(3);
		BUILD_RESET_ICN(4);
		BUILD_RESET_ICN(11);
	},!1);} )();

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
	var OB = GEBI('SL_langSrc_it');
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

	var OB3 = GEBI('SL_langDst_it');
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
}, TIME_OUT);

function CONSTRUCTOR(){
	GEBI('SL_BG_op').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSLBG_op')));
	GEBI('SL_setLS4allTr').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSLsetLS4allTr')));
	GEBI('SLSeSo').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSeSo')));
	GEBI('SLSeTa').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSeTa')));
	GEBI('SL_DetSoLaAu').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extDetSoLaAu')));
	GEBI('SL_TR_op').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extTR_op')));
	GEBI('SL_enable_dict').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extEnable_Dict')));
	GEBI('SL_HotKeys').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extHotKeys')));
	GEBI('SL_TOMS').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extTOMS')));
	GEBI('SL_ClearTr').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extClearTr')));
	GEBI('SL_Appearance').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extAppearance')));
	GEBI('SL_Color').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extColor')));
	GEBI('SL_EIB').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extEIB')));
	GEBI('SL_IBO').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extIBO')));
	GEBI('SL_LB').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extLB')));
	GEBI('SL_ABW').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extABW')));
	GEBI('SL_HO').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extHO')));
	GEBI('SL_TrHi').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extTrHist')));
	GEBI('SL_InTH').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extInTH')));
	GEBI('SL_il').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extLOC')));
	GEBI('SL_L_BOX').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extLangs')+":"));
	GEBI('SL_LNG_STATUS').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extCustomize')));
	GEBI('SL_INLINEflip').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSwitch_languages_ttl')));

	GEBI('SL_LIST_TR_PR').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extLIST_TR_PR')));

	GEBI('SL_SET_TR_PR').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSET_TR_PR')));
	GEBI('SL_SHOWHIDE_TR_PR').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSHOWHIDE_TR_PR')));


	GEBI('SL_theme_ttl').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extTHEME')));
	GEBI('SL_theme_1').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extLIGHT')));
	GEBI('SL_theme_2').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extDARK')));
	GEBI('SL_tr_with_target').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extSeTa')));

	switch(PLATFORM){
	 case "Opera" : GEBI('SL_info').href="https://imtranslator.net/tutorials/presentations/imtranslator-for-opera/opera-inline-translator-options/"; break;
	 case "Chrome": GEBI('SL_info').href="https://imtranslator.net/tutorials/presentations/imtranslator-for-chrome/inline-translator-options/"; break;
	 default      : GEBI('SL_info').href="https://imtranslator.net/tutorials/presentations/";break;
	}


  	var SL_OtherTr = GET("SL_pr_it");
  	if(SL_OtherTr=="1"){
		GEBI("SL_OtherTr").checked = true;
  	}else{
		GEBI("SL_OtherTr").checked = false;
  	}	

  	var SL_pr_it = GET("SL_pr_it");
  	if(SL_pr_it=="1") GEBI("SL_pr_it").checked = true;
  	else	GEBI("SL_pr_it").checked = false;

        SL_SHOWHIDEPROVIDERS();

	PR_BUILDER("SL_ALL_PROVIDERS_IT");

	ACTIVATE_THEME(GET("THEMEmode"));
}


(function(e){
	document.addEventListener("click",function(e){
	      if(e.target.id!="SL_style" && GEBI("SL_CL")){
		 GEBI("SL_CL").style.display='none';
		 GEBI("SL_style").style.background='#'+GEBI("SL_style").value;
	      }
	},!1);
} )();

(function(e){
	GEBI('SL_style').addEventListener("keydown",function(e){
	      GEBI("SL_style").style.background='#'+GEBI("SL_style").value;
	},!1);
} )();

(function(e){
	GEBI('SL_style').addEventListener("keyup",function(e){
	      GEBI("SL_style").style.background='#'+GEBI("SL_style").value;
	},!1);
} )();

(function(e){
	GEBI('SL_style').addEventListener("click",function(e){
		setTimeout(function() {
		      GEBI("SL_style").focus();
		      GEBI("SL_style").select();
		}, 300);

	},!1);
} )();



function INIT(){
  ACTIVATE_MENU_ELEMENT(2);
  GEBI("SL_LOC").value=GET("SL_LOCALIZATION");
  //*************************** inliner ***********************************
  var SL_style = GEBI("SL_style");
  var SL_style_tr = GET("SL_style");
  SL_style.value = SL_style_tr;
  SL_style.style.backgroundColor = "#"+SL_style_tr;
  
  var SL_inject_brackets_tr = GET("SL_inject_brackets"); 
  if(SL_inject_brackets_tr=="true")  GEBI("SL_inject_brackets").checked = true;
  else GEBI("SL_inject_brackets").checked = false;
  
  var SL_inject_before_tr = GET("SL_inject_before"); 
  if(SL_inject_before_tr=="true"){
	GEBI("SL_inject_before").checked = true;
	if(GEBI('SL_hide_translation').checked==true) GEBI('SL_hide_translation').checked = false;
  }else GEBI("SL_inject_before").checked = false;

  var SL_line_break_tr = GET("SL_line_break"); 
  if(SL_line_break_tr=="true")  GEBI("SL_line_break").checked = true;
  else GEBI("SL_line_break").checked = false;
  
  var SL_whole_word_tr = GET("SL_whole_word"); 
  if(SL_whole_word_tr=="true")  GEBI("SL_whole_word").checked = true;
  else GEBI("SL_whole_word").checked = false;
  
  var SL_hide_translation_tr = GET("SL_hide_translation"); 
  if(SL_hide_translation_tr=="true"){
	GEBI("SL_hide_translation").checked = true;
	if(GEBI('SL_inject_before').checked==true) GEBI('SL_inject_before').checked = false;
  }else GEBI("SL_hide_translation").checked = false;
  
  var SL_dictionary_tr = GET("SL_dictionary"); 
  if(SL_dictionary_tr=="true")  GEBI("SL_dictionary").checked = true;
  else GEBI("SL_dictionary").checked = false;

  var SL_no_detect_tr = GET("SL_no_detect_it");
  if(SL_no_detect_tr=="true")  GEBI("SL_no_detect_it").checked = true;
  else GEBI("SL_no_detect_it").checked = false;

  // Hotkeys block
  var SL_FK_box1 = GET("SL_FK_box1"); 
  if(SL_FK_box1=="true")  GEBI("SL_FK_box1").checked = true;
  else GEBI("SL_FK_box1").checked = false;

  var SL_FK_box2 = GET("SL_FK_box2"); 
  if(SL_FK_box2=="true")  GEBI("SL_FK_box2").checked = true;
  else GEBI("SL_FK_box2").checked = false;


  var SL_change_lang_HKbox_it = GET("SL_change_lang_HKbox_it"); 
  if(SL_change_lang_HKbox_it=="true")  GEBI("SL_FK_box11").checked = true;
  else GEBI("SL_FK_box11").checked = false;

  GEBI("SRV11").value = GET("SL_change_lang_HK_it");

  var SL_OtherTr = GET("SL_other_it");
  if(SL_OtherTr=="1"){
	GEBI("SL_OtherTr").checked = true;
  }else{
	GEBI("SL_OtherTr").checked = false;
  }	

  var SL_pr_it = GET("SL_pr_it");
  if(SL_pr_it=="1") GEBI("SL_pr_it").checked = true;
  else	GEBI("SL_pr_it").checked = false;
  SL_SHOWHIDEPROVIDERS();


  // Hotkeys block



  //************************* end inliner *********************************

	if(GET("SL_HK_it1")!=""){
		GEBI('SRV3').value=GET("SL_HK_it1");
	} else {
		GEBI('SRV3').placeholder="Not set";
	}

        GEBI('SRV4').value = GET("SL_HK_it2");


	var mySL_langSrc_it = GET("SL_langSrc_it");
	var mySL_langSrcSelect_it = GEBI("SL_langSrc_it");
	for (var i = 0; i < mySL_langSrcSelect_it.options.length; i++) {
		var mySL_langSrcOption_it = mySL_langSrcSelect_it.options[i];
		if (mySL_langSrcOption_it.value == mySL_langSrc_it) {
			mySL_langSrcOption_it.selected = "true";
			break;
		}
	}

	var mySL_langDst_it = GET("SL_langDst_it");
	var mySL_langDstSelect_it = GEBI("SL_langDst_it");
	for (var i = 0; i < mySL_langDstSelect_it.options.length; i++) {
		var mySL_langDstOption_it = mySL_langDstSelect_it.options[i];
		if (mySL_langDstOption_it.value == mySL_langDst_it) {
			mySL_langDstOption_it.selected = "true";
			break;
		}
	}

        var SL_TH_4 = GET("SL_TH_4");
        if(SL_TH_4=="1")  GEBI("SL_TH_4").checked = true;
        else GEBI("SL_TH_4").checked = false;

	var SL_global_lng_it = GET("SL_global_lng_it");
	if(SL_global_lng_it=="true")  GEBI("SL_global_lng_it").checked = true;
	else GEBI("SL_global_lng_it").checked = false;

	SL_HIDE_HK("SL_FK_box1","SL_HIDE3");
	SL_HIDE_HK("SL_FK_box2","SL_HIDE4");
	SL_HIDE_HK("SL_FK_box11","SL_HIDE11");


	var INLINEflip = GET("INLINEflip");
	if(INLINEflip=="1")  GEBI("INLINEflip").checked = true;
	else GEBI("INLINEflip").checked = false;

        var SL_THEMEmode = GET("THEMEmode");
	if(SL_THEMEmode==0)  GEBI("SL_THEME").value = 0;
	else GEBI("SL_THEME").value = 1;
	save_options(1);
}

function save_options(st) {
 setTimeout(function() {

	var SL_select_S_it = GEBI("SL_langSrc_it");
	var SL_select_T_it = GEBI("SL_langDst_it");

	if(SL_select_S_it.value!=SL_select_T_it.value){

	   	if(GEBI("SL_TH_4").checked==true) SET("SL_TH_4", "1");
		else SET("SL_TH_4","0");

		if(GEBI("SL_OtherTr").checked == true){
			SET("SL_other_it", "1");
		}else{ 
			SET("SL_other_it", "0");
		}

		if(GEBI("SL_pr_it").checked==true){
		   	SAVE_LIST_PROVIDERS_SYN("SL_ALL_PROVIDERS_IT","SL_ALL_PROVIDERS_BBL","SL_ALL_PROVIDERS_GT");
		   	SET("SL_pr_gt", "1");
		   	SET("SL_pr_bbl", "1");
		   	SET("SL_pr_it", "1");
		   	if(GEBI("SL_OtherTr").checked == true) {
				SET("SL_other_gt", "1");
				SET("SL_other_bbl", "1");
				SET("SL_other_it", "1");
		   	}else{
				SET("SL_other_gt", "0");
				SET("SL_other_bbl", "0");
				SET("SL_other_it", "0");
		  	}
		} else {
	   	   	SAVE_LIST_PROVIDERS("SL_ALL_PROVIDERS_IT");
		   	SET("SL_pr_gt", "0");
		   	SET("SL_pr_bbl", "0");
		   	SET("SL_pr_it", "0");
		}               



	   //*************************** inliner ***********************************
	   var SL_style = GEBI("SL_style");
	   SET("SL_style", SL_style.value);
	   
	   var SL_inject_brackets = GEBI("SL_inject_brackets");
	   SET("SL_inject_brackets", SL_inject_brackets.checked+'');
	   
	   var SL_inject_before = GEBI("SL_inject_before");
	   SET("SL_inject_before", SL_inject_before.checked+'');
	   
	   var SL_line_break = GEBI("SL_line_break");
	   SET("SL_line_break", SL_line_break.checked + '');
	   
	   var SL_whole_word = GEBI("SL_whole_word");
	   SET("SL_whole_word", SL_whole_word.checked + '');
	   
	   var SL_hide_translation = GEBI("SL_hide_translation");
	   SET("SL_hide_translation", SL_hide_translation.checked + '');
	   
	   var SL_dictionary = GEBI("SL_dictionary");
	   SET("SL_dictionary", SL_dictionary.checked + '');
	   
	   //************************* end inliner *********************************


		var SL_langSrc_it = SL_select_S_it.children[SL_select_S_it.selectedIndex].value;
		SET("SL_langSrc_it", SL_langSrc_it);
		
		var SL_langDst_it = SL_select_T_it.children[SL_select_T_it.selectedIndex].value;
		SET("SL_langDst_it", SL_langDst_it);
		SET("SL_WPT_TEMP_LANG", SL_langDst_it);		
		var SL_langDst_name_it = SL_select_T_it.children[SL_select_T_it.selectedIndex].text;
		SET("SL_langDst_name_it", SL_langDst_name_it);

		SET("SL_no_detect_it", GEBI("SL_no_detect_it").checked);

		SET("SL_FK_box1", GEBI("SL_FK_box1").checked);
		SET("SL_FK_box2", GEBI("SL_FK_box2").checked);
		SET("SL_change_lang_HKbox_it", GEBI("SL_FK_box11").checked);


		if(GEBI('SRV3').value!="None")	SET("SL_HK_it1", GEBI('SRV3').value);
		else SET("SL_HK_it1", "");

		SET("SL_HK_it2", GEBI('SRV4').value);

		SET("SL_change_lang_HK_it", GEBI('SRV11').value);


		if(GEBI("INLINEflip").checked==true)  SET("INLINEflip",1);
		else SET("INLINEflip",0);

//------TIME STAMP--------------
	new Date().getTime();
	SET("SL_TS", Date.now());
//==============================


		if(GEBI("SL_global_lng_it").checked==true){
			SET("SL_langDst_name", SL_langDst_name_it);
			SET("SL_langDst_name_bbl", SL_langDst_name_it);
			SET("SL_langDst_name_wpt", SL_langDst_name_it);
		}

		if(GEBI("SL_global_lng_it").checked==true){

			SET("SL_global_lng", GEBI("SL_global_lng_it").checked);
			SET("SL_global_lng_bbl", GEBI("SL_global_lng_it").checked);
			SET("SL_global_lng_wpt", GEBI("SL_global_lng_it").checked);
			SET("SL_global_lng_it", GEBI("SL_global_lng_it").checked);

			SET("SL_langSrc", SL_select_S_it.children[SL_select_S_it.selectedIndex].value);
			SET("SL_langSrc2", SL_select_S_it.children[SL_select_S_it.selectedIndex].value);
			SET("SL_langSrc_bbl", SL_select_S_it.children[SL_select_S_it.selectedIndex].value);
			SET("SL_langSrc_wpt", SL_select_S_it.children[SL_select_S_it.selectedIndex].value);
			SET("SL_langSrc_it", SL_select_S_it.children[SL_select_S_it.selectedIndex].value);

			SET("SL_langDst", SL_select_T_it.children[SL_select_T_it.selectedIndex].value);
			SET("SL_langDst2", SL_select_T_it.children[SL_select_T_it.selectedIndex].value);
			SET("SL_langDst_bbl", SL_select_T_it.children[SL_select_T_it.selectedIndex].value);
			SET("SL_langDst_wpt", SL_select_T_it.children[SL_select_T_it.selectedIndex].value);
			SET("SL_langDst_it", SL_select_T_it.children[SL_select_T_it.selectedIndex].value);


			SET("SL_langDst_name", SL_select_T_it.children[SL_select_T_it.selectedIndex].text);
			SET("SL_langDst_name_wpt", SL_select_T_it.children[SL_select_T_it.selectedIndex].text);
			SET("SL_langDst_name_bbl", SL_select_T_it.children[SL_select_T_it.selectedIndex].text);
			SET("SL_langDst_name_it", SL_select_T_it.children[SL_select_T_it.selectedIndex].text);


			SET("SL_no_detect", GEBI("SL_no_detect_it").checked);
			SET("SL_no_detect_bbl", GEBI("SL_no_detect_it").checked);
			SET("SL_no_detect_it", GEBI("SL_no_detect_it").checked);

			var IDS = document.getElementById("SL_langDst_it").value;
	   		SL_SAVE_FAVORITE_LANGUAGES(IDS, "SL_FAV_LANGS_IMT");
	   		SL_SAVE_FAVORITE_LANGUAGES(IDS, "SL_FAV_LANGS_BBL");
	   		SL_SAVE_FAVORITE_LANGUAGES(IDS, "SL_FAV_LANGS_IT");
	   		SL_SAVE_FAVORITE_LANGUAGES(IDS, "SL_FAV_LANGS_WPT");


		} else {
			SL_SAVE_FAVORITE_LANGUAGES(document.getElementById("SL_langDst_it").value, "SL_FAV_LANGS_IT");
			SET("SL_langDst_name_it", SL_select_T_it.children[SL_select_T_it.selectedIndex].text);
			SET("SL_global_lng", GEBI("SL_global_lng_it").checked);
			SET("SL_global_lng_bbl", GEBI("SL_global_lng_it").checked);
			SET("SL_global_lng_wpt", GEBI("SL_global_lng_it").checked);
			SET("SL_global_lng_it", GEBI("SL_global_lng_it").checked);
		}	


		RESET_TEMPS_TO_DEFAULT();
	  	SAVE_LIST_PROVIDERS("SL_ALL_PROVIDERS_IT");

		SET("SL_Flag", "FALSE");
		PREPARE_RCM_CONTENT();
		ACTIVATE_THEME(GET("THEMEmode"));

		if(GEBI('autohotkeys')){
		  var frame = GEBI('autohotkeys');
		  if(frame)	frame.parentNode.removeChild(frame);
		}


	}else 	  alert(FExtension.element(GET("SL_LOCALIZATION"),'extS_T_L_diff'));
 }, 100);
}

function GEBI(id){ return document.getElementById(id);}



function OneOfTwo(st){
 if(st==1){
  if(GEBI('SL_inject_before').checked == true) GEBI('SL_hide_translation').checked = false;
 } else {
  if(GEBI('SL_hide_translation').checked == true) GEBI('SL_inject_before').checked = false;
 }
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
		var E = document.getElementsByClassName("SLMSG");
		for(var j=0; j<E.length; j++) E[j].style.filter=SL_DARK;


		setTimeout(function() {
			var SL_lngSrc_opt = GEBI("SL_langSrc_it").getElementsByTagName("option");
			for(var j=0; j<SL_lngSrc_opt.length; j++) SL_lngSrc_opt[j].setAttribute("style", "background:"+bg+" !important;color:#fff;");
			var SL_lngSrc_opt = GEBI("SL_langDst_it").getElementsByTagName("option");
			for(var j=0; j<SL_lngSrc_opt.length; j++) SL_lngSrc_opt[j].setAttribute("style", "background:"+bg+" !important;color:#fff;");
		}, 1000);

		if(GEBI("item-0")) GEBI("item-0").style.borderRight="10px solid "+clr;	
		if(GEBI("item-1")) GEBI("item-1").style.borderRight="10px solid "+clr;
		
		GEBI("SL_style").style.filter=SL_DARK;	
		GEBI("SL_AUTOKEYS").style.filter=SL_DARK;	
	}
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



function BUILD_RESET_ICN(ob){
	GEBI("reset_all"+ob).title="Reset to default";
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
         case 3: st = 'SL_HK_it1'; break;
         case 4: st = 'SL_HK_it2'; break;
         case 11: st = 'SL_change_lang_HK_it'; break;

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
		GEBI("SRV"+id).value=GET(st);
	}, TIME_OUT);
}

